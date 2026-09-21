"""Offline tests only: all HTTP calls are mocked."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import check_openai_env as checker


SECRET = "secret-without-required-prefix-TESTONLY"
MODEL = "private-model-value-TESTONLY"
TEXT = "private-response-value-TESTONLY"


class MockResponse(io.BytesIO):
    pass


class MockOpener:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((request, timeout))
        if self.error:
            raise self.error
        return MockResponse(json.dumps(self.result).encode())


def completed(text=TEXT):
    return {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}]}


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / ".env.local"
        self.values = {"OPENAI_API_KEY": SECRET, "OPENAI_MODEL": MODEL, "LLM_MODE": "live"}
        self.write_values()

    def write_values(self):
        self.path.write_text("\n".join(f"{key}={value}" for key, value in self.values.items()))

    def run_main(self, *flags, environ=None, opener=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = checker.main(["--env-file", str(self.path), *flags], environ={} if environ is None else environ, opener=opener)
        printed = output.getvalue()
        for sensitive in (SECRET, MODEL, TEXT):
            self.assertNotIn(sensitive, printed)
        report = json.loads(printed)
        self.assertIs(report["ready_for_goal"], False)
        return code, report

    def test_default_offline_and_no_prefix_assumption(self):
        with patch.object(checker.urllib.request, "build_opener", side_effect=AssertionError("network not allowed")):
            code, report = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "CONFIGURED")
        self.assertEqual(report["live"], "not_run")

    def test_process_environment_overrides_file_even_when_empty(self):
        code, report = self.run_main(environ={"OPENAI_API_KEY": ""})
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "MISSING")
        values, _ = checker.load_config(self.path, {"OPENAI_MODEL": "override-model"})
        self.assertEqual(values["OPENAI_MODEL"], "override-model")

    def test_missing_file_can_use_environment_only(self):
        self.path.unlink()
        self.assertEqual(self.run_main(environ=self.values)[0], 0)
        self.assertEqual(self.run_main()[1]["status"], "MISSING")

    def test_placeholders_and_invalid_mode(self):
        for key, value in (("OPENAI_API_KEY", "your_api_key"), ("OPENAI_MODEL", "<model>"), ("LLM_MODE", "automatic")):
            with self.subTest(key=key):
                code, report = self.run_main(environ={key: value})
                self.assertEqual(code, 2)
                self.assertIn(key, report["fields"])

    def test_header_controls_rejected(self):
        for char in ("\n", "\r", "\x00", "\x7f", " "):
            self.assertEqual(self.run_main(environ={"OPENAI_API_KEY": SECRET + char})[0], 2)

    def test_duplicate_and_invalid_syntax_fail_without_disclosure(self):
        for extra, reason in (("OPENAI_MODEL=second", "ENV_DUPLICATE_KEY"), ("invalid " + SECRET, "ENV_SYNTAX_INVALID"), ('OPENAI_EXTRA="unclosed', "ENV_SYNTAX_INVALID")):
            with self.subTest(reason=reason):
                self.write_values()
                with self.path.open("a") as handle:
                    handle.write("\n" + extra)
                code, report = self.run_main()
                self.assertEqual(code, 2)
                self.assertEqual(report["reason"], reason)

    def test_quotes_comments_export_and_no_expansion(self):
        self.path.write_text(f'# config\nexport OPENAI_API_KEY="{SECRET}" # key\nOPENAI_MODEL=\'{MODEL}\'\nLLM_MODE=live # mode\n')
        self.assertEqual(self.run_main()[0], 0)
        for value in ("$(touch /tmp/never-run)", "${OTHER_KEY}", "`secret-command`"):
            self.path.write_text(f"OPENAI_API_KEY='{value}'")
            self.assertEqual(self.run_main()[1]["reason"], "ENV_EXPANSION_UNSUPPORTED")

    def test_escaped_newline_in_key_rejected(self):
        self.path.write_text('OPENAI_API_KEY="key\\nvalue"\nOPENAI_MODEL=model\nLLM_MODE=live')
        self.assertEqual(self.run_main()[1]["status"], "INVALID")

    def test_fixture_live_forbidden(self):
        opener = MockOpener(result=completed())
        code, report = self.run_main("--live", environ={"LLM_MODE": "fixture"}, opener=opener)
        self.assertEqual(code, 3)
        self.assertEqual(report["live"], "FIXTURE_LIVE_FORBIDDEN")
        self.assertFalse(opener.calls)

    def test_live_success_one_request_no_response_disclosure(self):
        opener = MockOpener(result=completed())
        code, report = self.run_main("--live", opener=opener)
        self.assertEqual((code, report["status"]), (0, "CONNECTED"))
        self.assertEqual(len(opener.calls), 1)
        request, timeout = opener.calls[0]
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
        self.assertEqual(request.get_header("Authorization"), "Bearer " + SECRET)
        body = json.loads(request.data)
        self.assertEqual(body["model"], MODEL)
        self.assertIs(body["store"], False)
        self.assertEqual(body["max_output_tokens"], 1024)
        self.assertEqual(timeout, 30)

    def test_incomplete_refused_empty_malformed(self):
        cases = [
            ({"status": "incomplete", "output": []}, "RESPONSE_NOT_COMPLETED"),
            ({"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal", "refusal": TEXT}]}]}, "RESPONSE_REFUSED"),
            (completed("  "), "RESPONSE_EMPTY"),
            ({"status": "completed", "output": None}, "RESPONSE_INVALID"),
            ([], "RESPONSE_INVALID"),
        ]
        for result, reason in cases:
            with self.subTest(reason=reason):
                code, report = self.run_main("--live", opener=MockOpener(result=result))
                self.assertEqual((code, report["live"]), (4, reason))

    def test_http_status_and_quota_classification(self):
        cases = [(401, None, "AUTHENTICATION_FAILED"), (403, None, "ACCESS_DENIED"), (404, None, "MODEL_OR_ENDPOINT_UNAVAILABLE"), (429, "insufficient_quota", "QUOTA_EXHAUSTED"), (429, "rate_limit_exceeded", "RATE_LIMITED"), (429, "unknown", "RATE_OR_QUOTA_LIMITED"), (500, None, "PROVIDER_UNAVAILABLE"), (307, None, "REDIRECT_BLOCKED")]
        for status, detail, expected in cases:
            with self.subTest(status=status, detail=detail):
                body = json.dumps({"error": {"code": detail, "message": SECRET + TEXT}}).encode()
                error = urllib.error.HTTPError("https://api.openai.com/v1/responses", status, SECRET, {}, io.BytesIO(body))
                opener = MockOpener(error=error)
                code, report = self.run_main("--live", opener=opener)
                self.assertEqual((code, report["live"]), (4, expected))
                self.assertEqual(len(opener.calls), 1)

    def test_timeout_and_network_error(self):
        for error, reason in ((TimeoutError(SECRET), "TIMEOUT"), (urllib.error.URLError(TimeoutError(SECRET)), "TIMEOUT"), (urllib.error.URLError(SECRET), "NETWORK_ERROR")):
            code, report = self.run_main("--live", opener=MockOpener(error=error))
            self.assertEqual((code, report["live"]), (4, reason))

    def test_redirect_handler_rejects_every_destination(self):
        request = checker.urllib.request.Request("https://api.openai.com/v1/responses", headers={"Authorization": "Bearer " + SECRET})
        self.assertIsNone(checker.NoRedirect().redirect_request(request, None, 302, "redirect", {}, "https://example.org/steal"))

    def test_unreadable_env_file_is_sanitized(self):
        self.path.unlink()
        self.path.mkdir()
        self.assertEqual(self.run_main()[1]["reason"], "ENV_FILE_UNREADABLE")


if __name__ == "__main__":
    unittest.main()
