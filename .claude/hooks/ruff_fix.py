"""Claude Code hook: after Claude edits a Python file, run Ruff on it (fix + format)."""

import json
import shutil
import subprocess
import sys

path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
ruff = shutil.which("ruff")
if path.endswith(".py") and ruff:
    subprocess.run([ruff, "check", "--fix", "--quiet", path], check=False)  # noqa: S603
    subprocess.run([ruff, "format", "--quiet", path], check=False)  # noqa: S603
