# ...existing code...
import txtai
import numpy as np
import pandas as pd
import importlib
import os
import sys
from typing import List, Iterable, Any

# Ensure repository root is on sys.path so GuidedPrompt package can be imported
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# { changed code }
# defaults for DB loader
DEFAULT_DB_MODULE = "GuidedPrompt.mysql.connection"
DEFAULT_DB_FUNC = "get_scriptures"

# ...existing code...

def load_texts_from_csv(csv_path: str = "seth-data.csv", column: str = "content_plain") -> List[str]:
    """Load text list from CSV (fallback to first column)."""
    try:
        df = pd.read_csv(csv_path).dropna()
    except Exception as e:
        raise FileNotFoundError(f"Could not read CSV '{csv_path}': {e}")
    if column in df.columns:
        return df[column].astype(str).tolist()
    return df.iloc[:, 0].astype(str).tolist()


def load_texts_from_db(module_path: str = DEFAULT_DB_MODULE, func_name: str = DEFAULT_DB_FUNC) -> List[str]:
    """
    Import DB module and return a list of strings.
    Try several common function names (fallbacks) if the preferred one is missing.
    """
    mod = importlib.import_module(module_path)
    # try preferred then fallbacks
    candidates = [func_name, "get_scriptures", "get_all_verses", "get_verses", "get_all"]
    fn = None
    for name in candidates:
        if hasattr(mod, name):
            maybe = getattr(mod, name)
            if callable(maybe):
                fn = maybe
                break
    if fn is None:
        raise AttributeError(f"{module_path} has no callable among {candidates}")

    records = fn()
    out: List[str] = []
    for r in records:
        if isinstance(r, str):
            out.append(r)
        elif isinstance(r, dict):
            for k in ("content_plain", "content", "text", "body", "verse"):
                if k in r and r[k]:
                    out.append(str(r[k]))
                    break
            else:
                out.append(str(next(iter(r.values()))))
        else:
            for attr in ("content_plain", "content", "text", "body", "verse"):
                if hasattr(r, attr):
                    val = getattr(r, attr)
                    if val:
                        out.append(str(val))
                        break
            else:
                out.append(str(r))
    return out
# ...existing code...

def build_or_load_embeddings(csv_path: str = "seth-data.csv",
                             embeddings_path: str = "embeddings_seth.tar.gz",
                             model: str = "sentence-transformers/all-MiniLM-L6-v2",
                             texts: List[str] | None = None):
    embeddings = txtai.Embeddings({"path": model})
    if texts is None:
        texts = load_texts_from_csv(csv_path)
    if os.path.exists(embeddings_path):
        embeddings.load(embeddings_path)
        return embeddings, texts
    embeddings.index(texts)
    embeddings.save(embeddings_path)
    return embeddings, texts


def search_query(embeddings, content: List[str], query: str, limit: int = 5):
    results = embeddings.search(query=query, limit=limit)
    return [(r[1], content[r[0]]) for r in results]


if __name__ == "__main__":
    # Try to load texts from DB first (default GuidedPrompt.mysql.connection), fallback to CSV
    try:
        texts = load_texts_from_db()
        print(f"Loaded {len(texts)} texts from DB ({DEFAULT_DB_MODULE}.{DEFAULT_DB_FUNC}).")
    except Exception as e:
        print(f"DB load failed ({e}), falling back to CSV.")
        texts = load_texts_from_csv()

    emb, content = build_or_load_embeddings(texts=texts)
    print(f"Embeddings ready. Indexed {len(content)} items.")
    # quick demo search
    demo_query = "faith"
    for score, text in search_query(emb, content, demo_query, limit=5):
        print(f"{score:.4f} - {text[:200]}")
# ...existing code...