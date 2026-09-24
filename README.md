# 🧠 Smart Study Resource Finder

An AI-powered, full-stack study resource discovery platform built with **Python (Flask)**, **MongoDB Atlas**, and **Atlas Vector Search**. 

The system enables students to search for study materials using natural language semantic queries (e.g. *"I want beginner-friendly material to understand processes and pipes in Operating Systems"*) as well as traditional keyword matching.

---

## 📋 Table of Contents
- [Problem Statement](#-problem-statement)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Database Design & Schema](#-database-design--schema)
- [How Vector Search Works](#-how-vector-search-works)
- [Setup & Installation Guide](#-setup--installation-guide)
- [MongoDB Atlas Setup](#-mongodb-atlas-setup)
- [How to Run the Application](#-how-to-run-the-application)
- [Example Searches](#-example-searches)
- [🎓 College Viva Preparation Guide](#-college-viva-preparation-guide)
- [License](#-license)

---

## ❓ Problem Statement

Students often struggle to find relevant study materials because traditional database keyword searches require exact string matches. If a student searches using natural language—for example:

> *"I want beginner-friendly material to understand processes and pipes in Operating Systems"*

A normal SQL or MongoDB string search looking for exact keywords might fail if the document title is *"Inter-Process Communication and POSIX Pipes Tutorial"*.

**Solution:** By converting study resources and student queries into high-dimensional vector embeddings, our application calculates the **semantic similarity** between concepts using MongoDB Atlas Vector Search. This enables the system to retrieve relevant materials even when search terms do not match verbatim.

---

## ✨ Key Features

- **Full CRUD Operations**:
  - **Create**: Add new study resources with automatic vector embedding generation.
  - **Read**: View all resources in a card grid or detailed modal popups.
  - **Update**: Edit existing resource details with automatic vector recalculation.
  - **Delete**: Safely delete resources from MongoDB.
- **Dual Search Engine**:
  - **Semantic AI Search**: Uses 384-dimensional vector embeddings and MongoDB Atlas `$vectorSearch` with Cosine Similarity.
  - **Keyword Text Search**: Uses MongoDB native Text Index (`$text`) across title, description, topic, and tags.
- **Dynamic Multi-Filtering**:
  - Filter resources instantly by **Subject**, **Difficulty Level** (Beginner, Intermediate, Advanced), and **Resource Format** (Article, Video, Book, Notes, Interactive).
- **Modern Glassmorphism UI**:
  - Clean, dark-mode single-page interface with responsive grid layout, micro-animations, loading skeletons, and interactive modals.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **Python 3.10+ / Flask** | REST API endpoints, routing, request handling |
| **Database** | **MongoDB Atlas** (Free M0 Tier) | Cloud document store and vector search engine |
| **Database Driver** | **PyMongo** | Python client library for database interactions |
| **Vector Model** | **HuggingFace Inference API** / `all-MiniLM-L6-v2` | Converts text into 384-dimensional numerical dense vectors |
| **Frontend** | **HTML5, CSS3, Vanilla JavaScript** | Responsive glassmorphism dashboard using Fetch API |
| **Configuration** | **python-dotenv** | Manages environment variables securely |

---

## 🏗️ System Architecture

```
                                +-----------------------------------+
                                |        Student Browser UI         |
                                | (HTML / CSS / JavaScript Fetch API)|
                                +-----------------+-----------------+
                                                  |
                                                  | REST API Requests (JSON)
                                                  v
                                +-----------------+-----------------+
                                |      Flask Application Server     |
                                |            (app.py)               |
                                +--------+----------------+---------+
                                         |                |
                Generates 384-dim        |                | PyMongo Queries
                Vector Embedding         v                v
        +----------------------------------+            +----------------------------------+
        |   HuggingFace Embedding Utility  |            |       MongoDB Atlas Cloud        |
        |   (all-MiniLM-L6-v2 Model)       |            |       (smart_study_db)           |
        +----------------------------------+            +----------------+-----------------+
                                                                         |
                                                                         | $vectorSearch / $text
                                                                         v
                                                        +----------------------------------+
                                                        |        resources Collection      |
                                                        |     + Atlas Vector Search Index  |
                                                        +----------------------------------+
```

---

## 🗄️ Database Design & Schema

### Database & Collection
- **Database Name**: `smart_study_db`
- **Collection Name**: `resources`

### Document Structure (JSON Schema)
```json
{
  "_id": "ObjectId('65f1a2b3c4d5e6f7a8b9c0d1')",
  "title": "Understanding Processes and Pipes in OS",
  "subject": "Operating Systems",
  "topic": "Process Management & IPC",
  "difficulty": "Beginner",
  "resource_type": "Article",
  "description": "A beginner-friendly guide explaining operating system processes, IPC, and POSIX pipes.",
  "content": "A process is an executing program instance. Inter-process communication (IPC) enables processes...",
  "tags": ["operating systems", "processes", "pipes", "ipc"],
  "url": "https://example.com/os-processes-pipes",
  "created_at": "2026-09-24T22:58:19Z",
  "embedding": [ -0.0412, 0.0823, -0.0129, "... (384 float numbers)" ]
}
```

### MongoDB Indexes
1. **Scalar B-Tree Indexes**: `subject`, `difficulty`, `resource_type`, `created_at`.
2. **Multi-Field Text Index**: `{ title: "text", description: "text", topic: "text", tags: "text" }`.
3. **Atlas Vector Search Index**:
   ```json
   {
     "fields": [
       { "type": "vector", "path": "embedding", "numDimensions": 384, "similarity": "cosine" },
       { "type": "filter", "path": "subject" },
       { "type": "filter", "path": "difficulty" },
       { "type": "filter", "path": "resource_type" }
     ]
   }
   ```

---

## 🔍 How Vector Search Works

1. **Embedding Generation**: When a study resource is created or updated, its `title`, `topic`, `description`, and `content` are combined and passed to the `sentence-transformers/all-MiniLM-L6-v2` neural network model via HuggingFace API. The model outputs a **384-dimensional dense vector**.
2. **Query Vectorization**: When a student enters a search query like *"Explain CPU scheduling algorithms for beginners"*, the query is converted into a 384-dimensional vector in real time.
3. **Atlas `$vectorSearch` Aggregation**: MongoDB Atlas compares the query vector against all document embedding vectors stored in the database using **Cosine Similarity**:
   $$\text{Cosine Similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$
4. Documents with the highest similarity score (closest vector direction) are returned as top matches.

---

## ⚡ Setup & Installation Guide

### Prerequisites
- Python 3.10+
- MongoDB Atlas Cloud Account
- Free HuggingFace API Access Token

### 1. Clone & Navigate to Repository
```powershell
cd MongoDB_Projects
```

### 2. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Create `.env` Environment File
Create a `.env` file in the root folder with the following contents:

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
DB_NAME=smart_study_db
COLLECTION_NAME=resources
HUGGINGFACE_API_KEY=hf_your_actual_token_here
```

---

## 🌐 MongoDB Atlas Setup

1. Log in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create an **M0 Free Cluster**.
2. Under **Database Access**, create a user with read/write permissions.
3. Under **Network Access**, add IP `0.0.0.0/0` (Allow Access from Anywhere).
4. Create database `smart_study_db` and collection `resources`.
5. Under **Atlas Vector Search**, create an index named `vector_index` using the JSON definition:
   ```json
   {
     "fields": [
       { "type": "vector", "path": "embedding", "numDimensions": 384, "similarity": "cosine" },
       { "type": "filter", "path": "subject" },
       { "type": "filter", "path": "difficulty" },
       { "type": "filter", "path": "resource_type" }
     ]
   }
   ```

---

## 🚀 How to Run the Application

### Step 1: Seed Sample Resources (15 Resources)
```powershell
python seed_data.py
```

### Step 2: Start Flask Application
```powershell
python app.py
```

Open your browser and visit: **`http://127.0.0.1:5000`**

---

## 💡 Example Searches

| Search Query | Mode | Expected Top Result |
| :--- | :--- | :--- |
| *"I want to understand processes and pipes in OS"* | **Semantic AI** | *Understanding Processes and Pipes in OS* |
| *"Explain CPU scheduling algorithms for beginners"* | **Semantic AI** | *CPU Scheduling Algorithms: FCFS, SJF, and Round Robin* |
| *"How to prevent deadlocks?"* | **Semantic AI** | *Deadlock Detection and Prevention: Banker's Algorithm* |
| *"normalization"* | **Keyword** | *Relational Database Normalization: 1NF to 3NF & BCNF* |
| *"OOP principles in Java"* | **Semantic / Keyword** | *Object-Oriented Programming (OOP) Principles in Java* |

---

## 🎓 College Viva Preparation Guide

Here are 10 commonly asked viva questions and ideal answers for this project:

### Q1: What is MongoDB and how does it differ from SQL databases?
> **Answer:** MongoDB is a NoSQL document-oriented database. Instead of storing data in rigid rows and tables with fixed schemas like SQL databases, MongoDB stores data in flexible JSON-like documents (BSON). This allows dynamic fields and hierarchical arrays (such as `tags` and `embedding` vectors) to be stored in a single document without complex SQL JOINs.

### Q2: What is PyMongo and how is it used in this project?
> **Answer:** PyMongo is the official Python driver for MongoDB. In our project ([`utils/db.py`](file:///c:/Users/Hp/OneDrive/Desktop/MongoDB_Projects/utils/db.py)), PyMongo handles connecting to MongoDB Atlas (`MongoClient`), managing collection handles, creating text and scalar indexes, executing CRUD queries (`insert_one`, `find`, `update_one`, `delete_one`), and running aggregation pipelines (`aggregate`).

### Q3: What is the difference between Keyword Search and Vector/Semantic Search?
> **Answer:** 
> - **Keyword Search** relies on exact string or token matching using MongoDB's `$text` index. If the search term is not present in the document text, no match is found.
> - **Semantic/Vector Search** converts query text into a high-dimensional vector representation capturing contextual meaning. It finds documents whose mathematical vector directions are closest to the query vector, enabling semantic understanding even without word-for-word matching.

### Q4: What is a Vector Embedding?
> **Answer:** A vector embedding is an array of floating-point numbers generated by a machine learning language model (e.g., `sentence-transformers/all-MiniLM-L6-v2`). It represents semantic concepts as points in a 384-dimensional vector space where semantically similar phrases are located close to each other.

### Q5: How does MongoDB Atlas `$vectorSearch` work?
> **Answer:** `$vectorSearch` is an Atlas aggregation pipeline stage that uses Approximate Nearest Neighbor (ANN) search algorithms (such as HNSW) to compare a query vector against stored document embeddings using distance metrics like Cosine Similarity or Euclidean distance.

### Q6: Why did you use Cosine Similarity instead of Euclidean Distance?
> **Answer:** Cosine Similarity measures the angle between two high-dimensional vectors regardless of their length magnitude. It is ideal for text embeddings because text length variations do not distort semantic direction similarity.

### Q7: What are MongoDB Indexes and why did you create them?
> **Answer:** Indexes speed up query execution by allowing MongoDB to locate documents without scanning the entire collection. We created:
> 1. B-Tree Indexes on `subject`, `difficulty`, and `resource_type` for fast dropdown filtering.
> 2. Text Index on `title`, `description`, `topic`, and `tags` for keyword search.
> 3. Atlas Vector Search Index on `embedding` for semantic vector queries.

### Q8: How is complete CRUD implemented in your project?
> **Answer:**
> - **Create**: `POST /api/resources` inserts a document via PyMongo `insert_one()` and computes its vector embedding.
> - **Read**: `GET /api/resources` fetches documents via PyMongo `find()` or `aggregate()` with `$vectorSearch`.
> - **Update**: `PUT /api/resources/<id>` updates document fields via `update_one()` and recalculates embeddings.
> - **Delete**: `DELETE /api/resources/<id>` removes the document via `delete_one()`.

### Q9: Why is `python-dotenv` used in this project?
> **Answer:** `python-dotenv` keeps database connection strings and HuggingFace secret API keys out of source code by storing them in a local `.env` file, adhering to security best practices and preventing accidental credential leaks on GitHub.

### Q10: What is the role of Flask in this architecture?
> **Answer:** Flask serves as the lightweight Python web server and REST API bridge. It handles HTTP routing, parses incoming JSON payloads from the frontend JavaScript Fetch API, invokes utility functions for vector generation and MongoDB queries, and returns JSON responses back to the browser.

---

## 📄 License
This project is open source and available under the MIT License.
