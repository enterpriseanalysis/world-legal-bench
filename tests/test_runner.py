"""Runner tests use an in-process local HTTP fixture, never a model provider."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from world_legal_bench.dataset import load_questions, read_jsonl
from world_legal_bench.runner import completion_url, run


class Handler(BaseHTTPRequestHandler):
    received = []

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.received.append(data)
        raw = json.dumps({"choices": [{"message": {"content": "Answer: A"}, "finish_reason": "stop"}],
                          "usage": {"prompt_tokens": 10, "completion_tokens": 2}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args):
        pass


class RunnerTest(unittest.TestCase):
    def test_invalid_configuration_fails_before_writing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "predictions.jsonl"
            config = dict(output=output, base_url="http://127.0.0.1:1/v1", model="fixture")
            for override in ({"qpm": 0}, {"qpm": float("nan")}, {"extra_body": []},
                             {"extra_body": {"messages": []}}, {"extra_body": {"api_key": "secret"}},
                             {"extra_body": {"headers": {"Authorization": "secret"}}}):
                with self.subTest(override=override), self.assertRaises(ValueError):
                    run([], **{**config, **override})
                self.assertFalse(output.exists())
                self.assertFalse(output.with_suffix(".jsonl.run.json").exists())

    def test_url_rejects_embedded_credentials_and_query(self):
        for url in ["https://user:password@example.org/v1", "https://example.org/v1?api_key=x", "file:///tmp/api"]:
            with self.assertRaises(ValueError):
                completion_url(url)

    def test_mock_inference_resume_and_credential_isolation(self):
        Handler.received = []
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"OPENAI_API_KEY": "mock-secret"}):
                output = Path(tmp) / "predictions.jsonl"
                questions = load_questions(ROOT)[:2]
                config = dict(output=output, base_url=f"http://127.0.0.1:{server.server_port}/v1",
                              model="local-fixture", qpm=60000, workers=2)
                result = run(questions, **config)
                self.assertEqual(result["written"], 2)
                self.assertEqual(len(Handler.received), 2)
                self.assertTrue(all("answer" not in payload for payload in Handler.received))
                self.assertNotIn("mock-secret", output.read_text() + output.with_suffix(".jsonl.run.json").read_text())
                self.assertEqual(len(read_jsonl(output)), 2)
                self.assertEqual(run(questions, resume=True, **config)["written"], 0)
                self.assertEqual(len(Handler.received), 2)
                with self.assertRaisesRegex(ValueError, "configuration differs"):
                    run(questions, resume=True, **{**config, "temperature": 1})
                with self.assertRaisesRegex(ValueError, "already exists"):
                    run(questions, **config)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
