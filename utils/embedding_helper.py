import requests
import time
from config import Config

def generate_embedding(text: str) -> list[float]:
    """
    Generates a 384-dimensional vector embedding for a given text string.
    Uses Hugging Face Inference API with sentence-transformers/all-MiniLM-L6-v2.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    api_key = Config.HUGGINGFACE_API_KEY
    if not api_key or api_key == "your_huggingface_api_token_here":
        print("[WARNING] No valid HuggingFace API key found in .env. Falling back to simple vector representation.")
        # Fallback pseudo-embedding (384 dimensions) for offline/testing mode
        import random
        random.seed(hash(text) % (2**32))
        return [round(random.uniform(-1, 1), 6) for _ in range(Config.EMBEDDING_DIMENSION)]

    # Hugging Face Feature Extraction API Endpoint
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{Config.EMBEDDING_MODEL}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": text.strip(),
        "options": {"wait_for_model": True}
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)
        
        # Retry if model is loading (503 response)
        if response.status_code == 503:
            print("[INFO] Model loading on Hugging Face... waiting 5 seconds.")
            time.sleep(5)
            response = requests.post(api_url, headers=headers, json=payload, timeout=15)

        if response.status_code != 200:
            raise Exception(f"HuggingFace API error: HTTP {response.status_code} - {response.text}")

        result = response.json()

        # Handle nested list structure if returned as [[float, ...]]
        if isinstance(result, list):
            if len(result) > 0 and isinstance(result[0], list):
                # Mean pooling if token-level embeddings are returned
                if isinstance(result[0][0], float):
                    return result[0]
                elif isinstance(result[0][0], list):
                    # Compute mean across token embeddings
                    dims = len(result[0][0])
                    mean_vector = [0.0] * dims
                    for token_vector in result[0]:
                        for i in range(dims):
                            mean_vector[i] += token_vector[i]
                    count = len(result[0])
                    return [round(v / count, 6) for v in mean_vector]
            elif isinstance(result[0], float):
                return result

        raise Exception(f"Unexpected response format from HuggingFace API: {result}")

    except Exception as e:
        print(f"[ERROR] Embedding generation failed: {e}")
        # Return fallback vector so application doesn't hard crash
        import random
        random.seed(hash(text) % (2**32))
        return [round(random.uniform(-1, 1), 6) for _ in range(Config.EMBEDDING_DIMENSION)]
