import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "smart_study_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "resources")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Model details for Vector Embeddings
    # sentence-transformers/all-MiniLM-L6-v2 produces 384-dimensional dense vectors
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION = 384
