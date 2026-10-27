#!/usr/bin/env python3
"""Read-only checks for the public workspace and optional imported manifest."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md", "README.md", ".gitignore", "Makefile",
    "docs/LOCAL-WORKFLOW.md", "projects/README.md", "shared/INDEX.md",
    "shared/decisions.md", "shared/templates/session.md",
    "shared/sessions/README.md", "scripts/check_workspace.py",
)


def git(*args, **kwargs):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True,
        check=True, **kwargs
    ).stdout


def private_path(name):
    path = Path(name)
    return (
        path.parts[0] in {".local", ".codex", "config-review", "records"}
        or path.parts[0].startswith("WG03 Mac Setting ")
        or path.name in {".DS_Store", "config.toml"}
        or (path.name.startswith(".env") and path.name != ".env.example")
        or path.suffix.lower() in {".pcap", ".pcapng", ".bundle", ".key", ".pem"}
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path,
                        help="Validate an imported MANIFEST.json without modifying it")
    args = parser.parse_args()
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            errors.append("Missing required file: " + name)
    tracked = git("ls-files", "-z").decode().split("\0")
    unsafe = [name for name in tracked if name and private_path(name)]
    if unsafe:
        errors.append("Private file paths are tracked by Git: " + ", ".join(unsafe))
    for name in (".local/probe", ".codex/probe", ".DS_Store",
                 "WG03 Mac Setting 2026-10-09/probe", ".env", "capture.pcapng"):
        result = subprocess.run(["git", "-C", str(ROOT), "check-ignore",
                                 "--no-index", "-q", "--", name])
        if result.returncode != 0:
            errors.append("Expected exclusion missing: " + name)
    for extra in ([], ["--cached"]):
        check = subprocess.run(["git", "-C", str(ROOT), "diff", "--check", *extra],
                               capture_output=True, text=True)
        if check.returncode:
            errors.append("Whitespace errors: " + check.stdout.strip())
    if args.manifest:
        manifest = args.manifest.resolve()
        base = manifest.parent
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for item in data["files"]:
            file = (base / item["path"]).resolve()
            if not file.is_relative_to(base) or not file.is_file():
                errors.append("Invalid or missing manifest path: " + item["path"])
                continue
            content = file.read_bytes()
            if len(content) != item["bytes"] or hashlib.sha256(content).hexdigest() != item["sha256"]:
                errors.append("Manifest mismatch: " + item["path"])
        print("Manifest entries checked:", len(data["files"]))
    branch = git("branch", "--show-current").decode().strip()
    print("Branch:", branch)
    print("Tracked files checked:", len([name for name in tracked if name]))
    for error in errors:
        print("FAIL:", error, file=sys.stderr)
    if errors:
        return 1
    print("PASS: required files, private path exclusions, tracked file paths, whitespace")
    print("This check does not determine whether arbitrary file contents are safe to publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
