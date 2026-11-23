"""Record helpers generated from the canonical evaluator."""

import json
from pathlib import Path

def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

def read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line, object_pairs_hook=_unique_object)
            except ValueError as exc:
                raise ValueError(f"{Path(path).name}:{number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{Path(path).name}:{number}: expected a JSON object")
            rows.append(row)
    return rows

def unique_by_id(rows, label):
    result = {}
    for row in rows:
        qid = row.get("id")
        if not isinstance(qid, str) or not qid:
            raise ValueError(f"{label}: missing string id")
        if qid in result:
            raise ValueError(f"{label}: duplicate id {qid}")
        result[qid] = row
    return result
