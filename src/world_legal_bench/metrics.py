"""Score prediction records with explicit coverage and format-error accounting."""

from .dataset import unique_by_id
from .parser import extract_final_choice, PARSER_VERSION


def score(questions, answers, predictions, *, allow_partial=False):
    qs = unique_by_id(questions, "questions")
    if not qs:
        raise ValueError("question set is empty")
    gold = unique_by_id(answers, "answers")
    preds = unique_by_id(predictions, "predictions")
    if set(gold) != set(qs):
        raise ValueError("question and answer ids do not match")
    unknown = set(preds) - set(qs)
    if unknown:
        raise ValueError(f"unknown prediction ids: {sorted(unknown)[:3]}")
    missing = set(qs) - set(preds)
    if missing and not allow_partial:
        raise ValueError(f"missing {len(missing)} predictions; use --allow-partial for debugging")
    by_country = {}
    cases = []
    for qid, question in qs.items():
        country = question["country"]
        row = by_country.setdefault(country, {"country": country, "total": 0, "submitted": 0,
            "correct": 0, "incorrect": 0, "invalid": 0, "inference_errors": 0, "missing": 0})
        row["total"] += 1
        if qid not in preds:
            row["missing"] += 1
            continue
        prediction = preds[qid]
        text = prediction.get("prediction")
        if not isinstance(text, str):
            raise ValueError(f"prediction must be a string: {qid}")
        status = prediction.get("status", "ok")
        if status not in ("ok", "error"):
            raise ValueError(f"unsupported prediction status: {qid}")
        row["submitted"] += 1
        if status == "error":
            choice, error = None, "inference_error"
            row["inference_errors"] += 1
        else:
            choice, error = extract_final_choice(text)
        expected = gold[qid]["answer"]
        outcome = "invalid" if error else "correct" if choice == expected else "incorrect"
        row[outcome] += 1
        cases.append({"id": qid, "country": country, "choice": choice, "answer": expected,
                      "outcome": outcome, "format_error": error})
    for row in by_country.values():
        row["accuracy"] = 100 * row["correct"] / row["submitted"] if row["submitted"] else None
        row["coverage"] = row["submitted"] / row["total"]
    submitted = len(preds)
    correct = sum(r["correct"] for r in by_country.values())
    complete = not missing
    country_scores = [row["accuracy"] for row in by_country.values()]
    return {
        "parser_version": PARSER_VERSION, "complete": complete, "total": len(qs),
        "submitted": submitted, "missing": len(missing), "coverage": submitted / len(qs),
        "correct": correct, "incorrect": sum(r["incorrect"] for r in by_country.values()),
        "invalid": sum(r["invalid"] for r in by_country.values()),
        "inference_errors": sum(r["inference_errors"] for r in by_country.values()),
        "accuracy": 100 * correct / submitted if submitted else None,
        "macro_accuracy": sum(country_scores) / len(country_scores) if complete else None,
        "worst_country_accuracy": min(country_scores) if complete else None,
        "country_gap": max(country_scores) - min(country_scores) if complete else None,
        "by_country": list(by_country.values()), "cases": cases,
    }
