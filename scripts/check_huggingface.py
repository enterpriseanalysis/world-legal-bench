"""Check the local Hub card and load the declared split with networking disabled."""

import os
from pathlib import Path
import json
from collections import Counter
import importlib.metadata
import tempfile

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

from datasets import load_dataset
from huggingface_hub import DatasetCard

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "huggingface"
card = DatasetCard.load(BUNDLE / "README.md")
config = card.data.to_dict()["configs"]
assert config == [{"config_name": "default", "default": True,
                   "data_files": [{"split": "test", "path": "data/test.jsonl"}]}]

with tempfile.TemporaryDirectory(prefix="wlb-hf-cache-") as cache:
    dataset = load_dataset(str(BUNDLE), name="default", split="test", cache_dir=cache)
    assert len(dataset) == 360
    counts = Counter(dataset["country"])
    assert len(counts) == 12 and dict(counts) == json.loads((ROOT/'data/v2.0/manifest.json').read_text())['country_counts']
    assert len(set(dataset["language"])) == 9
    assert len(set(dataset["question_id"])) == 360
    for row in dataset:
        assert len(row["choices"]) == 4
        assert row["choices"]["ABCD".index(row["answer"])] == row["answer"] + ". " + row["answer_text"]
    result = {"scope": "local_metadata_and_dataset_loading", "hosted_viewer_verified": False,
              "networking_disabled": True, "split": "test", "rows": len(dataset),
              "columns": dataset.column_names, "country_counts": dict(counts),
              "datasets_version": importlib.metadata.version("datasets"),
              "huggingface_hub_version": importlib.metadata.version("huggingface-hub")}
    print(json.dumps(result, ensure_ascii=False, indent=2))
