from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[2]
LOCAL_MODEL_PATH = BASE_DIR / "models" / "all-MiniLM-L6-v2"

if not LOCAL_MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Local embedding model not found at: {LOCAL_MODEL_PATH}\n"
        "Copy the cached Hugging Face model snapshot into models/all-MiniLM-L6-v2"
    )

_embedding_model = SentenceTransformer(str(LOCAL_MODEL_PATH))


def embed_text(text: str):
    return _embedding_model.encode(text).tolist()