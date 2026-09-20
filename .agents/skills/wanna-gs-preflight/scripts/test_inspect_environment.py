import contextlib
import importlib.util
import io
import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

module_path = Path(__file__).with_name("inspect_environment.py")
spec = importlib.util.spec_from_file_location("inspector", module_path)
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


class InventoryTests(unittest.TestCase):
    def test_credentials_are_not_part_of_remote_identity(self):
        expected = {"host": "github.com", "repository": "example/demo"}
        self.assertEqual(inspector.github_identity("https://user:SECRET@github.com/example/demo.git?token=SECRET"), expected)
        self.assertEqual(inspector.github_identity("git@github.com:example/demo.git"), expected)
        self.assertIsNone(inspector.github_identity("https://[broken"))
        self.assertIsNone(inspector.github_identity("/local/repository"))

    def test_missing_directory_is_blocked_without_commands(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(inspector, "execute") as run:
                result = inspector.collect(Path(temporary) / "missing")
        self.assertEqual(result["status"], "BLOCKED")
        run.assert_not_called()

    def test_missing_tools_do_not_crash(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(inspector.shutil, "which", return_value=None):
                result = inspector.collect(temporary, check_auth=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["ready_for_goal"])

    def test_docs_only_authenticated_inventory_never_means_live_ready(self):
        secret = "SENTINEL_DO_NOT_PRINT"

        def run(argv, cwd, timeout=20):
            if argv[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
                return 0, "true\n", "ok"
            if argv[:3] == ["git", "remote", "get-url"]:
                return 0, "https://user:" + secret + "@github.com/example/demo.git?token=" + secret, "ok"
            if argv[:2] == ["git", "status"]:
                return 0, "?? " + secret, "ok"
            if "--version" in argv:
                return 0, "tool 22.1.0 " + secret, "ok"
            return 0, secret, "ok"

        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(inspector.shutil, "which", return_value="/fake/bin"), patch.object(inspector, "execute", side_effect=run), patch.dict(os.environ, {"GH_TOKEN": secret}):
                result = inspector.collect(temporary, check_auth=True)
        serialized = json.dumps(result)
        self.assertNotIn(secret, serialized)
        self.assertEqual(result["status"], "PARTIAL")
        self.assertFalse(result["ready_for_goal"])
        self.assertFalse(result["production_execution_verified"])
        statuses = {entry["id"]: entry["status"] for entry in result["checks"]}
        self.assertEqual(statuses["package.json"], "bootstrap_required")
        self.assertEqual(statuses["github_auth"], "available")

    def test_command_timeout_does_not_expose_partial_output(self):
        timeout = subprocess.TimeoutExpired(["gh", "auth", "status"], 20, output="SECRET")
        with patch.object(inspector.subprocess, "run", side_effect=timeout):
            result = inspector.execute(["gh", "auth", "status"], "/tmp")
        self.assertEqual(result, (None, "", "timeout"))

    def test_existing_report_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / "report.json"
            report.write_text("keep")
            argv = ["inspect_environment.py", "--project", temporary, "--output", str(report)]
            with patch.object(inspector.sys, "argv", argv), patch.object(inspector, "collect", return_value={"status": "PARTIAL"}), contextlib.redirect_stderr(io.StringIO()):
                code = inspector.main()
            self.assertEqual(code, 3)
            self.assertEqual(report.read_text(), "keep")

    @unittest.skipUnless(shutil.which("git"), "Git required for isolated local integration")
    def test_real_temporary_git_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            subprocess.run(["git", "init", "-q", temporary], check=True)
            subprocess.run(["git", "-C", temporary, "config", "user.name", "Test Author"], check=True)
            subprocess.run(["git", "-C", temporary, "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", temporary, "remote", "add", "origin", "https://user:SECRET@github.com/example/demo.git"], check=True)
            Path(temporary, "README.md").write_text("docs only")
            result = inspector.collect(temporary, check_auth=False)
        statuses = {entry["id"]: entry["status"] for entry in result["checks"]}
        self.assertEqual(statuses["git_repository"], "available")
        self.assertEqual(statuses["git_author"], "available")
        self.assertEqual(statuses["package.json"], "bootstrap_required")
        self.assertFalse(result["ready_for_goal"])
        self.assertNotIn("SECRET", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
