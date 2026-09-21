#!/usr/bin/env python3
"""Read-only local inventory; it never certifies live integrations or deploys."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from urllib.parse import urlsplit


def sqlite_inventory():
    """Probe only an in-memory Python connection; never opens a project DB."""
    try:
        import sqlite3
        connection = sqlite3.connect(":memory:")
        try:
            version = connection.execute("SELECT sqlite_version()").fetchone()[0]
        finally:
            connection.close()
        return "available", "Python SQLite " + version + "; sql.js/WASM, seed and browser storage not tested."
    except (ImportError, OSError):
        return "unavailable", "Python SQLite unavailable; select a supported local seed builder during bootstrap."
    except Exception:
        # Extension failures may contain paths or data. Suppress raw errors.
        return "unverified", "In-memory Python SQLite probe failed; raw error suppressed."


def execute(argv, cwd, timeout=20):
    try:
        result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                                timeout=timeout, check=False)
        # Raw output is internal only. Never include stdout/stderr in a report.
        return result.returncode, result.stdout, "ok" if result.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        return None, "", "timeout"
    except (OSError, UnicodeError):
        return None, "", "unavailable"


def github_identity(value):
    """Return only safe host/owner/repo; strip credentials and query strings."""
    value = value.strip()
    if "://" in value:
        try:
            parsed = urlsplit(value)
            host, path = parsed.hostname or "", parsed.path
        except ValueError:
            return None
    else:
        match = re.fullmatch(r"(?:[^@\s]+@)?([A-Za-z0-9.-]+):([^\s]+)", value)
        if not match:
            return None
        host, path = match.groups()
        path = path.split("?", 1)[0].split("#", 1)[0]
    path = path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
        return None
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", path):
        return None
    return {"host": host, "repository": path}


def collect(project, check_auth=False, remote="origin"):
    project = Path(project).resolve()
    checks = []

    def item(name, status, detail):
        checks.append({"id": name, "status": status, "detail": detail})

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "local_inventory_with_auth_probes" if check_auth else "local_inventory",
        "project": str(project),
        "status": "PARTIAL",
        "ready_for_goal": False,
        "production_execution_verified": False,
        "checks": checks,
        "live_checks": "not_run",
        "storage_mode": "browser_sqlite_single_tab",
        "note": "Inventory alone cannot prove push, PR, CI, deployment, sql.js, browser persistence, model, or agents.",
    }
    if not project.is_dir():
        item("project", "failed", "Project directory does not exist.")
        report["status"] = "BLOCKED"
        return report
    item("project", "available", "Project directory exists.")
    sqlite_status, sqlite_detail = sqlite_inventory()
    item("python_sqlite", sqlite_status, sqlite_detail)
    item("browser_sqlite", "unverified", "Verify sql.js/WASM export/import in P06 and Preview persistence in P07; no external DB account is required.")

    binaries = {}
    for command in ("git", "node", "npm", "gh", "vercel"):
        binaries[command] = shutil.which(command)
        if not binaries[command]:
            item(command, "missing", "CLI missing; a supported connector may replace gh/vercel after live verification.")
            continue
        code, output, state = execute([command, "--version"], project)
        version = re.search(r"(?<![A-Za-z0-9])v?(\d+\.\d+(?:\.\d+)?)(?![A-Za-z0-9])", output)
        item(command, "available" if code == 0 else state,
             "Version " + version.group(1) if code == 0 and version else "Version probe completed without captured version." if code == 0 else "CLI version probe failed; raw output suppressed.")

    repo_identity = None
    git_ok = False
    if binaries.get("git"):
        code, output, state = execute(["git", "rev-parse", "--is-inside-work-tree"], project)
        git_ok = code == 0 and output.strip() == "true"
        item("git_repository", "available" if git_ok else state if state != "ok" else "failed",
             "Git worktree verified." if git_ok else "Not verified as a Git worktree.")
        if git_ok:
            code, output, state = execute(["git", "status", "--porcelain"], project)
            item("working_tree", "available" if code == 0 else state,
                 "Uncommitted entries: " + str(len(output.splitlines())) if code == 0 else "Status unreadable.")
            code, output, state = execute(["git", "remote", "get-url", remote], project)
            repo_identity = github_identity(output) if code == 0 else None
            item("remote", "available" if repo_identity else "unverified",
                 "Remote identity parsed; push access not tested." if repo_identity else "Remote absent or identity cannot be safely parsed.")
            if repo_identity:
                report["remote_identity"] = repo_identity
            code, output, state = execute(["git", "config", "user.name"], project)
            name_ready = code == 0 and bool(output.strip())
            code, output, state = execute(["git", "config", "user.email"], project)
            item("git_author", "available" if name_ready and code == 0 and output.strip() else "missing",
                 "Only author configuration presence checked; values suppressed.")
    if not git_ok:
        report["status"] = "BLOCKED"
    if not binaries.get("node"):
        report["status"] = "BLOCKED"

    for rel in ("package.json", ".github/workflows"):
        item(rel, "available" if (project / rel).exists() else "bootstrap_required",
             "Found." if (project / rel).exists() else "Expected in docs-only start; the bootstrap task creates this.")
    link = project / ".vercel/project.json"
    linked = False
    if link.is_file():
        try:
            data = json.loads(link.read_text())
            linked = isinstance(data, dict) and bool(data.get("projectId")) and bool(data.get("orgId"))
        except (ValueError, OSError):
            pass
    item("vercel_local_link", "available" if linked else "unverified",
         "Project/org linkage fields present; target correctness unverified." if linked else "No valid local Vercel link; a connector or explicit target can supply it.")
    report["environment_names_present"] = [name for name in (
        "OPENAI_API_KEY", "OPENAI_MODEL", "LLM_MODE",
        "VERCEL_TOKEN", "VERCEL_OIDC_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"
    ) if bool(os.environ.get(name))]
    # Do not read .env files or dump environment values. Presence is not authentication.
    if check_auth:
        if binaries.get("gh"):
            argv = ["gh", "auth", "status"]
            if repo_identity:
                argv += ["--hostname", repo_identity["host"]]
            code, output, state = execute(argv, project)
            item("github_auth", "available" if code == 0 else state,
                 "Auth probe succeeded; write/merge/Actions access untested." if code == 0 else "Auth/network probe failed; diagnose separately without exposing raw logs.")
        else:
            item("github_auth", "unverified", "Use an available GitHub connector or install/authenticate gh.")
        if binaries.get("vercel"):
            code, output, state = execute(["vercel", "whoami"], project)
            item("vercel_auth", "available" if code == 0 else state,
                 "Identity probe succeeded; project/deploy permissions untested." if code == 0 else "Auth/network probe failed; diagnose separately without exposing raw logs.")
        else:
            item("vercel_auth", "unverified", "Use an available Vercel connector or install/authenticate the CLI.")
    else:
        item("remote_auth", "unverified", "Not probed. --check-auth performs read-only network probes.")
    report["next_action"] = "Resolve confirmed blockers, then use the skill's isolated live smoke matrix."
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--check-auth", action="store_true")
    parser.add_argument("--output", help="New JSON file, never overwrites an existing report.")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.remote):
        parser.error("Remote must be a simple configured remote name.")
    report = collect(args.project, args.check_auth, args.remote)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        destination = Path(args.output).expanduser()
        try:
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as stream:
                stream.write(payload)
        except OSError as exc:
            print("Report not written: " + exc.__class__.__name__, file=sys.stderr)
            return 3
    print(payload, end="")
    return 1 if report["status"] == "BLOCKED" else 2


if __name__ == "__main__":
    sys.exit(main())
