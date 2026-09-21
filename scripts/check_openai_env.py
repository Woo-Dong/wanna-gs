#!/usr/bin/env python3
"""Check only .env.local (or --env-file) plus overriding process environment.

This is NOT Next.js's complete dotenv resolution algorithm. No shell expansion,
command substitution, or variable interpolation is performed. Default checks are
offline. --live performs one small, billable Responses API request without retries.
No configuration values, HTTP bodies, or generated text are printed.

Exit codes: 0 configured/connected; 2 missing/invalid config; 3 live unavailable;
4 connection rejected/failed. A zero exit code is not application readiness.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import socket
import sys
import urllib.error
import urllib.request


FIELDS = ("OPENAI_API_KEY", "OPENAI_MODEL", "LLM_MODE")
PLACEHOLDERS = {
    "placeholder", "your_api_key", "your-api-key", "your_openai_api_key",
    "your-openai-api-key", "sk-your-key", "sk-your-api-key", "changeme",
    "replace_me", "replace-me", "todo", "xxx", "...", "<api-key>",
}


class ConfigError(ValueError):
    """Has a safe reason code, never includes config input."""


def parse_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        content = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        raise ConfigError("ENV_FILE_UNREADABLE") from None
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)", line)
        if not match:
            raise ConfigError("ENV_SYNTAX_INVALID")
        name, raw = match.groups()
        if name in result:
            raise ConfigError("ENV_DUPLICATE_KEY")
        if raw.startswith(("'", '"')):
            quote = raw[0]
            value, pos = "", 1
            closed = False
            while pos < len(raw):
                char = raw[pos]
                if char == quote:
                    closed = True
                    pos += 1
                    break
                if quote == '"' and char == "\\":
                    pos += 1
                    if pos >= len(raw):
                        raise ConfigError("ENV_SYNTAX_INVALID")
                    escaped = raw[pos]
                    if escaped not in {'"', "\\", "n", "r", "t"}:
                        raise ConfigError("ENV_UNSUPPORTED_ESCAPE")
                    char = {"n": "\n", "r": "\r", "t": "\t"}.get(escaped, escaped)
                value += char
                pos += 1
            if not closed or (raw[pos:].strip() and not raw[pos:].strip().startswith("#")):
                raise ConfigError("ENV_SYNTAX_INVALID")
        else:
            # Unquoted values cannot contain whitespace except before comments.
            value = raw.split("#", 1)[0].rstrip()
            if any(char.isspace() for char in value):
                raise ConfigError("ENV_SYNTAX_INVALID")
        if "${" in value or "$(" in value or "`" in value:
            raise ConfigError("ENV_EXPANSION_UNSUPPORTED")
        result[name] = value
    return result


def is_placeholder(value: str) -> bool:
    lower = value.casefold()
    return lower in PLACEHOLDERS or lower.startswith(("<", "your-", "your_", "sk-placeholder", "sk-..."))


def load_config(path: Path, environ: dict[str, str]) -> tuple[dict, dict]:
    try:
        file_values = parse_env(path)
    except ConfigError as exc:
        return {}, {"status": "INVALID", "reason": str(exc)}
    values = {name: environ.get(name, file_values.get(name, "")) for name in FIELDS}
    missing = [name for name, value in values.items() if not value.strip()]
    invalid = []
    for name in ("OPENAI_API_KEY", "OPENAI_MODEL"):
        value = values[name]
        if value and (is_placeholder(value) or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value)):
            invalid.append(name)
    if values["LLM_MODE"] and values["LLM_MODE"] not in {"live", "fixture"}:
        invalid.append("LLM_MODE")
    if invalid:
        return values, {"status": "INVALID", "reason": "INVALID_VALUES", "fields": invalid}
    if missing:
        return values, {"status": "MISSING", "reason": "REQUIRED_VALUES_MISSING", "fields": missing}
    return values, {"status": "CONFIGURED"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward an Authorization header to redirected destinations.
        return None


def classify_http(error: urllib.error.HTTPError) -> str:
    if error.code in (301, 302, 303, 307, 308):
        return "REDIRECT_BLOCKED"
    if error.code == 401:
        return "AUTHENTICATION_FAILED"
    if error.code == 403:
        return "ACCESS_DENIED"
    if error.code == 404:
        return "MODEL_OR_ENDPOINT_UNAVAILABLE"
    if error.code == 429:
        try:
            body = json.loads(error.read(65536))
            detail = body.get("error", {}) if isinstance(body, dict) else {}
            code = detail.get("code") if isinstance(detail, dict) else None
            kind = detail.get("type") if isinstance(detail, dict) else None
            if code == "insufficient_quota" or kind == "insufficient_quota":
                return "QUOTA_EXHAUSTED"
            if code == "rate_limit_exceeded" or kind == "rate_limit_exceeded":
                return "RATE_LIMITED"
        except (ValueError, OSError, TypeError):
            pass
        return "RATE_OR_QUOTA_LIMITED"
    if error.code >= 500:
        return "PROVIDER_UNAVAILABLE"
    return "HTTP_REQUEST_FAILED"


def live_check(values: dict, opener=None) -> tuple[str, int]:
    if values["LLM_MODE"] != "live":
        return "FIXTURE_LIVE_FORBIDDEN", 3
    body = {
        "model": values["OPENAI_MODEL"],
        "input": "연결 확인입니다. 확인이라고 짧게 답하세요.",
        "store": False,
        "max_output_tokens": 1024,
    }
    try:
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": "Bearer " + values["OPENAI_API_KEY"], "Content-Type": "application/json"},
            method="POST",
        )
        if opener is None:
            opener = urllib.request.build_opener(NoRedirect())
        with opener.open(request, timeout=30) as response:
            data = response.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                return "RESPONSE_TOO_LARGE", 4
        result = json.loads(data)
        if not isinstance(result, dict):
            return "RESPONSE_INVALID", 4
        if result.get("status") != "completed":
            return "RESPONSE_NOT_COMPLETED", 4
        output = result.get("output")
        if not isinstance(output, list):
            return "RESPONSE_INVALID", 4
        nonempty = False
        refused = False
        for item in output:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            contents = item.get("content", [])
            if not isinstance(contents, list):
                return "RESPONSE_INVALID", 4
            for content in contents:
                if not isinstance(content, dict):
                    continue
                if content.get("type") == "refusal":
                    refused = True
                if content.get("type") == "output_text" and isinstance(content.get("text"), str) and content["text"].strip():
                    nonempty = True
        if refused:
            return "RESPONSE_REFUSED", 4
        return ("CONNECTED", 0) if nonempty else ("RESPONSE_EMPTY", 4)
    except urllib.error.HTTPError as exc:
        return classify_http(exc), 4
    except (TimeoutError, socket.timeout):
        return "TIMEOUT", 4
    except urllib.error.URLError as exc:
        return ("TIMEOUT" if isinstance(exc.reason, (TimeoutError, socket.timeout)) else "NETWORK_ERROR"), 4
    except (ValueError, UnicodeError, TypeError):
        return "RESPONSE_OR_REQUEST_INVALID", 4
    except OSError:
        return "NETWORK_ERROR", 4


def main(argv=None, *, environ=None, opener=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path.cwd() / ".env.local")
    parser.add_argument("--live", action="store_true", help="Send one billable OpenAI request; never enabled by default")
    args = parser.parse_args(argv)
    values, report = load_config(args.env_file, os.environ if environ is None else environ)
    report.update({"live": "not_run", "ready_for_goal": False})
    code = 0 if report["status"] == "CONFIGURED" else 2
    if args.live and code == 0:
        status, code = live_check(values, opener=opener)
        report["live"] = status
        if code == 0:
            report["status"] = "CONNECTED"
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
