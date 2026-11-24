"""Explicit opt-in runner for OpenAI-compatible Chat Completions endpoints."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from .dataset import messages_for, read_jsonl, unique_by_id


def completion_url(base_url):
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("base URL must be an HTTP(S) endpoint")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("base URL must not contain credentials, query parameters, or fragments")
    return base_url.rstrip("/") + "/chat/completions"


class RateLimiter:
    def __init__(self, qpm):
        if qpm <= 0:
            raise ValueError("qpm must be positive")
        self.interval = 60 / qpm
        self.next_time = 0.0
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = time.monotonic()
            scheduled = max(now, self.next_time)
            self.next_time = scheduled + self.interval
        time.sleep(max(0, scheduled - now))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, new_url):
        return None


def _contains_credentials(value):
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = key.lower().replace("-", "_")
            if normalized in {"api_key", "apikey", "access_token", "token", "authorization",
                              "password", "secret", "credentials", "credential"}:
                return True
            if _contains_credentials(item):
                return True
    elif isinstance(value, list):
        return any(_contains_credentials(item) for item in value)
    return False


def request_case(question, *, url, api_key, model, max_tokens, temperature,
                 timeout, retries, limiter, extra_body, messages=None):
    payload = {"model": model, "messages": messages if messages is not None else messages_for(question),
               "temperature": temperature, "max_tokens": max_tokens}
    payload.update(extra_body)
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    opener = urllib.request.build_opener(NoRedirect)
    started = time.monotonic()
    for attempt in range(retries + 1):
        limiter.wait()
        request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
        try:
            with opener.open(request, timeout=timeout) as response:
                obj = json.load(response)
            content = obj["choices"][0]["message"].get("content")
            if content is None:
                content = ""
            if not isinstance(content, str):
                raise ValueError("endpoint returned non-string message content")
            return {"id": question["id"], "prediction": content, "status": "ok", "model": model,
                    "attempts": attempt + 1, "elapsed_seconds": round(time.monotonic() - started, 3),
                    "finish_reason": obj["choices"][0].get("finish_reason"),
                    "usage": obj.get("usage")}
        except urllib.error.HTTPError as exc:
            retryable = exc.code == 429 or 500 <= exc.code < 600
            error = f"http_{exc.code}"
            exc.close()
        except (urllib.error.URLError, TimeoutError):
            retryable, error = True, "transport_error"
        except (ValueError, KeyError, IndexError, TypeError):
            retryable, error = False, "invalid_endpoint_response"
        if not retryable or attempt == retries:
            return {"id": question["id"], "prediction": "", "status": "error", "model": model,
                    "error": error, "attempts": attempt + 1,
                    "elapsed_seconds": round(time.monotonic() - started, 3)}
        time.sleep(min(2 ** attempt, 8))


def run(questions, *, output, base_url, model, workers=4, qpm=60, max_tokens=131072,
        temperature=0.0, timeout=600, retries=2, resume=False, extra_body=None):
    if workers <= 0 or max_tokens <= 0 or timeout <= 0 or retries < 0:
        raise ValueError("workers/max_tokens/timeout must be positive; retries must be nonnegative")
    extra_body = {} if extra_body is None else extra_body
    if not model or not isinstance(extra_body, dict):
        raise ValueError("model is required and extra body must be a JSON object")
    if not all(math.isfinite(value) for value in (qpm, temperature, timeout)):
        raise ValueError("qpm, temperature, and timeout must be finite")
    if {"model", "messages", "temperature", "max_tokens"} & set(extra_body):
        raise ValueError("extra body cannot override model, messages, temperature, or max_tokens")
    limiter = RateLimiter(qpm)
    url = completion_url(base_url)
    output = Path(output)
    if output.exists() and not resume:
        raise ValueError("output already exists; use --resume or a new output path")
    existing = unique_by_id(read_jsonl(output), "existing predictions") if output.exists() else {}
    expected = unique_by_id(questions, "questions")
    if set(existing) - set(expected):
        raise ValueError("existing prediction ids are outside this release")
    if any(row.get("model") != model for row in existing.values()):
        raise ValueError("resume requires the same recorded model")
    config = {"model": model, "base_url": base_url, "workers": workers, "qpm": qpm,
              "max_tokens": max_tokens, "temperature": temperature, "timeout": timeout,
              "retries": retries, "extra_body": extra_body,
              "question_ids": [q["id"] for q in questions]}
    # Credentials belong in OPENAI_API_KEY, never in provider-specific JSON.
    if _contains_credentials(config["extra_body"]):
        raise ValueError("credentials must use OPENAI_API_KEY, not --extra-body")
    config_path = output.with_suffix(output.suffix + ".run.json")
    if existing:
        if not config_path.exists():
            raise ValueError("resume requires the original run configuration")
        previous = json.loads(config_path.read_text(encoding="utf-8"))
        if any(previous.get(key) != value for key, value in config.items()):
            raise ValueError("resume configuration differs from the original run")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps({**config, "started_at": datetime.now(timezone.utc).isoformat()},
                                         ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending = [q for q in questions if q["id"] not in existing]
    kwargs = dict(url=url, api_key=os.environ.get("OPENAI_API_KEY", ""), model=model,
                  max_tokens=max_tokens, temperature=temperature, timeout=timeout,
                  retries=retries, limiter=limiter, extra_body=extra_body)
    errors = 0
    with output.open("a", encoding="utf-8") as handle, ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(request_case, q, **kwargs) for q in pending]
        for future in as_completed(futures):
            row = future.result()
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            errors += row["status"] == "error"
    return {"written": len(pending), "previous": len(existing), "inference_errors": errors,
            "output": str(output)}
