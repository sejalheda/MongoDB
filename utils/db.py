from pymongo import MongoClient, TEXT, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
from config import Config

client = None
db = None
collection = None

def get_db_connection():
    """
    Initializes and returns the MongoDB Atlas collection object.
    Automatically creates necessary text and scalar indexes on startup.
    """
    global client, db, collection

    if collection is not None:
        return collection

    try:
        print(f"[INFO] Connecting to MongoDB database: {Config.DB_NAME}...")
        
        # Check if user is still using placeholder URI
        if "<username>" in Config.MONGO_URI or "YOUR_PASSWORD_HERE" in Config.MONGO_URI:
            print("\n" + "="*70)
            print("[NOTICE] You are currently using the default placeholder MONGO_URI in .env.")
            print("Please update your MONGO_URI in the .env file with your actual MongoDB Atlas cluster connection string.")
            print("="*70 + "\n")

        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Verify connection with ping
        client.admin.command('ping')
        print("[SUCCESS] Connected to MongoDB Atlas successfully!")

        db = client[Config.DB_NAME]
        collection = db[Config.COLLECTION_NAME]

        # Ensure standard scalar B-Tree indexes exist
        collection.create_index([("subject", ASCENDING)])
        collection.create_index([("difficulty", ASCENDING)])
        collection.create_index([("resource_type", ASCENDING)])
        collection.create_index([("created_at", DESCENDING)])

        # Ensure text index exists for Keyword Search
        existing_indexes = collection.index_information()
        text_index_exists = False
        for idx_info in existing_indexes.values():
            key_tuples = idx_info.get("key", [])
            if any(val == "text" for field_name, val in key_tuples):
                text_index_exists = True
                break
        
        if not text_index_exists:
            print("[INFO] Creating MongoDB Text Index on title, description, topic, and tags...")
            collection.create_index(
                [
                    ("title", TEXT),
                    ("description", TEXT),
                    ("topic", TEXT),
                    ("tags", TEXT)
                ],
                name="keyword_text_index",
                weights={
                    "title": 10,
                    "topic": 5,
                    "tags": 3,
                    "description": 1
                }
            )
            print("[SUCCESS] Text Index created successfully!")

        return collection

    except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError) as e:
        print(f"[ERROR] Failed to connect to MongoDB: {e}")
        raise RuntimeError(
            "MongoDB connection failed. Please ensure your MongoDB Atlas cluster is active "
            "and your MONGO_URI in .env contains valid credentials."
        )

def test_connection():
    """Quick helper to verify database status."""
    try:
        col = get_db_connection()
        doc_count = col.count_documents({})
        return True, f"Connected to collection '{Config.COLLECTION_NAME}' with {doc_count} documents."
    except Exception as e:
        return False, str(e)
