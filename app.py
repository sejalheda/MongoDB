from flask import Flask, render_template, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
import traceback

from config import Config
from utils.db import get_db_connection
from utils.embedding_helper import generate_embedding

app = Flask(__name__)

def format_doc(doc):
    """
    Helper function to convert MongoDB document format into JSON-serializable dictionary.
    Converts ObjectId to string and datetime objects to ISO format strings.
    """
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    if "created_at" in doc and isinstance(doc["created_at"], datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc

# -----------------------------------------------------------------------------
# PAGE ROUTES
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Renders the main dashboard page."""
    return render_template("index.html")

# -----------------------------------------------------------------------------
# API ROUTES (CRUD + SEARCH)
# -----------------------------------------------------------------------------

@app.route("/api/resources", methods=["GET"])
def get_resources():
    """
    READ / SEARCH endpoint:
    Fetch study resources with support for:
    - Subject, Difficulty, and Resource Type filtering
    - Keyword Search (using MongoDB Text Index $text)
    - Semantic / Vector Search (using MongoDB Atlas $vectorSearch)
    """
    try:
        col = get_db_connection()
        
        search_query = request.args.get("search", "").strip()
        search_mode = request.args.get("mode", "keyword").lower()  # 'keyword' or 'semantic'
        subject_filter = request.args.get("subject", "").strip()
        difficulty_filter = request.args.get("difficulty", "").strip()
        resource_type_filter = request.args.get("resource_type", "").strip()

        # Build standard match filters
        filter_query = {}
        if subject_filter:
            filter_query["subject"] = subject_filter
        if difficulty_filter:
            filter_query["difficulty"] = difficulty_filter
        if resource_type_filter:
            filter_query["resource_type"] = resource_type_filter

        resources = []

        # MODE A: Semantic / Vector Search using $vectorSearch
        if search_query and search_mode == "semantic":
            print(f"[SEARCH] Running Atlas Vector Search for query: '{search_query}'")
            
            # 1. Generate query vector embedding
            query_vector = generate_embedding(search_query)

            # 2. Build Atlas $vectorSearch aggregation pipeline
            vector_search_stage = {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": 20
                }
            }

            # Apply pre-filter inside $vectorSearch if filters selected
            if filter_query:
                # Format compound filter for $vectorSearch
                filter_clauses = []
                for key, val in filter_query.items():
                    filter_clauses.append({key: {"$eq": val}})
                if len(filter_clauses) == 1:
                    vector_search_stage["$vectorSearch"]["filter"] = filter_clauses[0]
                else:
                    vector_search_stage["$vectorSearch"]["filter"] = {"$and": filter_clauses}

            pipeline = [vector_search_stage]

            # Project score and exclude heavy raw embeddings from payload
            pipeline.append({
                "$project": {
                    "embedding": 0,
                    "score": {"$meta": "vectorSearchScore"}
                }
            })

            try:
                results = list(col.aggregate(pipeline))
                resources = [format_doc(doc) for doc in results]
            except Exception as vec_err:
                print(f"[WARNING] Atlas $vectorSearch failed or index not active yet: {vec_err}")
                print("[FALLBACK] Executing keyword search fallback...")
                search_mode = "keyword"  # Fallback to keyword search

        # MODE B: Normal Keyword Search using $text or standard filter
        if not resources and (not search_query or search_mode == "keyword"):
            if search_query:
                print(f"[SEARCH] Running Keyword Text Search for query: '{search_query}'")
                filter_query["$text"] = {"$search": search_query}

            cursor = col.find(filter_query, {"embedding": 0}).sort("created_at", -1).limit(50)
            resources = [format_doc(doc) for doc in cursor]

        return jsonify({"success": True, "count": len(resources), "data": resources}), 200

    except Exception as e:
        print(f"[ERROR] Error in get_resources: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/resources/<resource_id>", methods=["GET"])
def get_resource_by_id(resource_id):
    """READ endpoint: Get single resource details by ID."""
    try:
        col = get_db_connection()
        if not ObjectId.is_valid(resource_id):
            return jsonify({"success": False, "error": "Invalid Resource ID format."}), 400

        doc = col.find_one({"_id": ObjectId(resource_id)}, {"embedding": 0})
        if not doc:
            return jsonify({"success": False, "error": "Resource not found."}), 404

        return jsonify({"success": True, "data": format_doc(doc)}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/resources", methods=["POST"])
def add_resource():
    """
    CREATE endpoint:
    Inserts a new study resource and automatically generates vector embedding.
    """
    try:
        data = request.get_json() or {}
        
        # Validation for required fields
        required_fields = ["title", "description", "subject", "topic", "difficulty", "resource_type"]
        missing = [field for field in required_fields if not data.get(field, "").strip()]
        if missing:
            return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400

        # Extract values
        title = data["title"].strip()
        description = data["description"].strip()
        subject = data["subject"].strip()
        topic = data["topic"].strip()
        difficulty = data["difficulty"].strip()
        resource_type = data["resource_type"].strip()
        content = data.get("content", "").strip()
        url = data.get("url", "").strip()

        # Parse tags
        tags_raw = data.get("tags", "")
        if isinstance(tags_raw, list):
            tags = [t.strip().lower() for t in tags_raw if t.strip()]
        else:
            tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]

        # Combined text for embedding representation
        text_for_embedding = f"{title}. {topic}. {description}. {content}"
        
        print(f"[CREATE] Generating vector embedding for new resource: '{title}'...")
        embedding = generate_embedding(text_for_embedding)

        # Build document
        new_resource = {
            "title": title,
            "description": description,
            "subject": subject,
            "topic": topic,
            "difficulty": difficulty,
            "resource_type": resource_type,
            "content": content,
            "tags": tags,
            "url": url,
            "created_at": datetime.utcnow(),
            "embedding": embedding
        }

        col = get_db_connection()
        result = col.insert_one(new_resource)

        new_resource["id"] = str(result.inserted_id)
        del new_resource["_id"]
        del new_resource["embedding"]
        new_resource["created_at"] = new_resource["created_at"].isoformat()

        return jsonify({"success": True, "message": "Study resource created successfully!", "data": new_resource}), 201

    except Exception as e:
        print(f"[ERROR] Error adding resource: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/resources/<resource_id>", methods=["PUT"])
def update_resource(resource_id):
    """
    UPDATE endpoint:
    Modifies an existing resource document and updates embedding if content changed.
    """
    try:
        if not ObjectId.is_valid(resource_id):
            return jsonify({"success": False, "error": "Invalid Resource ID format."}), 400

        data = request.get_json() or {}
        col = get_db_connection()

        existing = col.find_one({"_id": ObjectId(resource_id)})
        if not existing:
            return jsonify({"success": False, "error": "Resource not found."}), 404

        update_fields = {}
        for field in ["title", "description", "subject", "topic", "difficulty", "resource_type", "content", "url"]:
            if field in data and data[field].strip():
                update_fields[field] = data[field].strip()

        if "tags" in data:
            tags_raw = data["tags"]
            if isinstance(tags_raw, list):
                update_fields["tags"] = [t.strip().lower() for t in tags_raw if t.strip()]
            else:
                update_fields["tags"] = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]

        # Check if text fields changed to re-generate embedding
        title = update_fields.get("title", existing["title"])
        topic = update_fields.get("topic", existing["topic"])
        description = update_fields.get("description", existing["description"])
        content = update_fields.get("content", existing.get("content", ""))

        text_for_embedding = f"{title}. {topic}. {description}. {content}"
        print(f"[UPDATE] Re-generating vector embedding for resource ID: {resource_id}...")
        update_fields["embedding"] = generate_embedding(text_for_embedding)

        col.update_one({"_id": ObjectId(resource_id)}, {"$set": update_fields})

        return jsonify({"success": True, "message": "Resource updated successfully!"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/resources/<resource_id>", methods=["DELETE"])
def delete_resource(resource_id):
    """DELETE endpoint: Removes a study resource document from MongoDB."""
    try:
        if not ObjectId.is_valid(resource_id):
            return jsonify({"success": False, "error": "Invalid Resource ID format."}), 400

        col = get_db_connection()
        result = col.delete_one({"_id": ObjectId(resource_id)})

        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Resource not found."}), 404

        return jsonify({"success": True, "message": "Resource deleted successfully!"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    """Returns a list of distinct subjects present in MongoDB for filter dropdowns."""
    try:
        col = get_db_connection()
        subjects = sorted(col.distinct("subject"))
        return jsonify({"success": True, "data": subjects}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("[INIT] Starting Flask server on http://127.0.0.1:5000...")
    app.run(host="127.0.0.1", port=5000, debug=True)
