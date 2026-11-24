"""Load the frozen release, check integrity, and assemble gold-free prompts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import DATASET_VERSION


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


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


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def release_dir(root, version=DATASET_VERSION):
    if version != DATASET_VERSION:
        raise ValueError(f"unsupported release: {version}")
    return Path(root).resolve() / "data" / ("v" + version)


def load_questions(root):
    return read_jsonl(release_dir(root) / "questions.jsonl")


def load_answers(root):
    return read_jsonl(release_dir(root) / "answers.jsonl")


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


def validate_release(root):
    root = Path(root).resolve()
    folder = release_dir(root)
    manifest = read_json(folder / "manifest.json")
    if manifest.get("version") != DATASET_VERSION:
        raise ValueError("dataset version does not match this evaluator")
    for name, expected in manifest["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError("manifest path escapes repository")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"SHA-256 mismatch: {name}")
    questions = unique_by_id(load_questions(root), "questions")
    answers = unique_by_id(load_answers(root), "answers")
    sources = unique_by_id(read_jsonl(folder / "sources.jsonl"), "sources")
    jurisdictions = read_json(root / manifest.get("jurisdictions_file", "data/jurisdictions.json"))
    countries = {row["code"]: row for row in jurisdictions}
    if len(countries) != 12 or len(jurisdictions) != 12:
        raise ValueError("expected twelve unique jurisdictions")
    if len(questions) != manifest["case_count"] or set(answers) != set(questions):
        raise ValueError("expected aligned question and answer ids matching the manifest")
    counts = {country: 0 for country in countries}
    signatures = set()
    for qid, question in questions.items():
        country = question["country"]
        if country not in countries or question["language"] != countries[country]["language"]:
            raise ValueError(f"country/language mismatch: {qid}")
        counts[country] += 1
        choices = question["choices"]
        if set(choices) != set("ABCD") or len(set(choices.values())) != 4:
            raise ValueError(f"four distinct labeled choices required: {qid}")
        if not question["question"].strip() or any(not value.strip() for value in choices.values()):
            raise ValueError(f"empty question/choice: {qid}")
        if set(question) & {"answer", "answer_text", "private_gold", "option_rationales"}:
            raise ValueError(f"gold field in questions: {qid}")
        answer = answers[qid]
        if answer["answer"] not in choices or choices[answer["answer"]] != answer["answer_text"]:
            raise ValueError(f"gold/choice mismatch: {qid}")
        if ("option_rationales" in answer and set(answer["option_rationales"]) != set("ABCD")) or not (answer.get("option_rationales") or answer.get("statement_reviews")):
            raise ValueError(f"missing option rationale: {qid}")
        if not question["source_ids"] or any(s not in sources for s in question["source_ids"]):
            raise ValueError(f"missing source reference: {qid}")
        if any(sources[s]["country"] != country for s in question["source_ids"]):
            raise ValueError(f"cross-country source binding: {qid}")
        signature = (country, " ".join(question["question"].split()), tuple(sorted(choices.values())))
        if signature in signatures:
            raise ValueError(f"duplicate question: {qid}")
        signatures.add(signature)
    expected_counts = manifest.get("country_counts", {country: 60 for country in countries})
    if counts != expected_counts:
        raise ValueError(f"country quota mismatch: {counts}")
    provenance = root / manifest.get("provenance_dir", "provenance")
    selected = unique_by_id(read_jsonl(provenance / "selection.jsonl"), "selection")
    if set(selected) != set(questions):
        raise ValueError("incomplete selection coverage")
    profile = read_json(provenance / "reference_selection.json")
    actual = {"correct": 0, "incorrect": 0, "invalid_output": 0}
    for qid, item in selected.items():
        if item["answer"] != answers[qid]["answer"]:
            raise ValueError(f"selection/gold mismatch: {qid}")
        outcome = item["reference_outcome"]
        if outcome not in actual:
            raise ValueError(f"unsupported selection outcome: {qid}")
        choice = item["reference_choice"]
        if outcome != "invalid_output":
            expected = "correct" if choice == item["answer"] else "incorrect"
            if choice not in "ABCD" or expected != outcome:
                raise ValueError(f"selection outcome mismatch: {qid}")
        actual[outcome] += 1
    if manifest["version"] == "2.0":
        if actual != {key: profile[key] for key in actual}:
            raise ValueError("reference profile differs from selected outcomes")
        from .geography import COUNTRY_REGION
        if any(q.get("region") != COUNTRY_REGION[q["country"]] for q in questions.values()):
            raise ValueError("region assignment mismatch")
    return {"version": DATASET_VERSION, "cases": len(questions), "jurisdictions": len(counts),
            "languages": len({q["language"] for q in questions.values()}), "by_country": counts,
            "verified_files": len(manifest["files"])}


def messages_for(question):
    """The model receives the question and options only; no source or gold fields."""
    text = question["question"] + "\n\n" + "\n".join(
        f"{label}. {question['choices'][label]}" for label in "ABCD"
    )
    return [
        {"role": "system", "content": "Choose the single best answer to the legal question. "
         "Use the legal version and assumptions stated in the question. "
         "Return only one uppercase letter: A, B, C, or D."},
        {"role": "user", "content": text},
    ]
