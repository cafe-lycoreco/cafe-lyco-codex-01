#!/usr/bin/env python3
"""Validate package invariants and produce one self-contained plugin ZIP."""
import hashlib
import json
from pathlib import Path
import re
import zipfile


def main():
    project = Path(__file__).resolve().parents[1]
    source = project / "plugin/computer-use-mcp"
    manifest = json.loads((source / "plugin.json").read_text())
    compatibility = json.loads((source / ".codex-plugin/plugin.json").read_text())
    interface = manifest["extensions"]["com.openai"]["interface"]
    if manifest["name"] != source.name or len(manifest["name"]) > 64:
        raise ValueError("Plugin identity does not match its root")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", manifest["version"]):
        raise ValueError("Expected a three-part semantic version")
    if len(interface["shortDescription"]) > 30:
        raise ValueError("Listing subtitle exceeds 30 characters")
    for key in ("name", "version", "description", "author"):
        if manifest[key] != compatibility[key]:
            raise ValueError(f"Compatibility manifest mismatch: {key}")
    if interface != compatibility["interface"]:
        raise ValueError("Compatibility presentation mismatch")
    mcp = json.loads((source / "mcp.json").read_text())
    legacy_mcp = json.loads((source / ".mcp.json").read_text())
    servers = mcp["mcpServers"]
    if len(servers) != 1:
        raise ValueError("Expected one MCP server")
    for name, server in servers.items():
        legacy = {key: value for key, value in server.items() if key != "type"}
        if server["type"] != "stdio" or legacy != legacy_mcp["mcpServers"][name]:
            raise ValueError("MCP compatibility mismatch")
        if server["command"] != "/bin/sh":
            raise ValueError("Unexpected server command")
        for arg in server["args"]:
            if arg.startswith("${PLUGIN_ROOT}/") and not (source / arg[len("${PLUGIN_ROOT}/"):]).is_file():
                raise ValueError("Missing server entrypoint")
    for key in ("logo", "composerIcon"):
        asset = (source / interface[key]).resolve()
        if source.resolve() not in asset.parents or not asset.is_file():
            raise ValueError("Missing or escaping icon path")
    skill = (source / "skills/computer-use/SKILL.md").read_text()
    if not skill.startswith("---\nname: computer-use\ndescription:"):
        raise ValueError("Missing skill frontmatter")
    files = sorted(path for path in source.rglob("*") if path.is_file())
    for path in source.rglob("*"):
        if path.is_symlink() or path.name in {"node_modules", "__pycache__", ".venv"}:
            raise ValueError("Package contains a symlink or dependency cache")
    outputs = project / "outputs"
    outputs.mkdir(exist_ok=True)
    archive = outputs / f"{manifest['name']}-{manifest['version']}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for path in files:
            entry = zipfile.ZipInfo(str(path.relative_to(source.parent)), date_time=(2026, 10, 10, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            package.writestr(entry, path.read_bytes())
    with zipfile.ZipFile(archive) as package:
        if package.testzip() is not None or len(package.namelist()) != len(set(package.namelist())):
            raise ValueError("Corrupt archive or duplicate paths")
        for path in files:
            if package.read(str(path.relative_to(source.parent))) != path.read_bytes():
                raise ValueError("Archive content mismatch")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (outputs / f"{archive.name}.sha256").write_text(f"{digest}  {archive.name}\n")
    print(json.dumps({"archive": str(archive), "files": len(files), "bytes": archive.stat().st_size,
                      "sha256": digest, "validation": "package structure and byte roundtrip passed"}, indent=2))


if __name__ == "__main__":
    main()
