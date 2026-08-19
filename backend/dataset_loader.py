import os
import json
from typing import List, Dict, Any

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "msmarco_sample.json")

def load_dataset() -> List[Dict[str, Any]]:
    """Loads the MSMARCO dataset passages."""
    if not os.path.exists(DATASET_PATH):
        return []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_dataset(passages: List[Dict[str, Any]]):
    """Saves updated passages to dataset."""
    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(passages, f, indent=2)

def add_passage(title: str, text: str, category: str = "General") -> Dict[str, Any]:
    """Adds a new passage to the dataset."""
    passages = load_dataset()
    new_doc = {
        "id": f"custom_doc_{len(passages) + 1}",
        "title": title,
        "text": text,
        "category": category,
        "url": "https://huggingface.co/datasets/ai4bharat/MSMARCO-XI"
    }
    passages.append(new_doc)
    save_dataset(passages)
    return new_doc
