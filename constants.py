import os
from pathlib import Path

CONFIG_DIR = Path(os.getcwd())
MODEL = "text-embedding-3-small"

CHROMA_DB_PATH = CONFIG_DIR / "vectordb" / "chroma"
FAISS_INDEX_PATH = CONFIG_DIR / "vectordb" / "faiss_index"
DATA_PATH = CONFIG_DIR / "data"
RECREATE_EMBEDDINGS = False  # True
PROMPT_TEMPLATE = CONFIG_DIR / "prompt" / "template.json"

MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.5