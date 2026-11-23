"""Generate synthetic gold predictions to check the scorer, never model performance."""

import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
answers = [json.loads(line) for line in (root / "data/v1.4.1-release/answers.jsonl").open(encoding="utf-8")]
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open("w", encoding="utf-8") as handle:
    for answer in answers:
        handle.write(json.dumps({"id": answer["id"], "prediction": answer["answer"],
                                 "model": "synthetic-gold-smoke-test"}) + "\n")
