#!/usr/bin/env python3
"""Bounded stdio MCP verification; never print app history or screenshot bodies."""
import argparse
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time


class MCPProbe:
    def __init__(self, plugin, timeout):
        self.timeout = timeout
        self.buffer = b""
        self.proc = subprocess.Popen(
            ["/bin/sh", str(plugin / "scripts/launch.sh")], cwd=str(plugin),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.proc.stdout, selectors.EVENT_READ, "stdout")
        self.selector.register(self.proc.stderr, selectors.EVENT_READ, "stderr")
        self.stderr_bytes = 0

    def send(self, message):
        self.proc.stdin.write(json.dumps(message).encode("utf-8") + b"\n")
        self.proc.stdin.flush()

    def rpc(self, request_id, method, params=None):
        message = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.send(message)
        deadline = time.monotonic() + self.timeout
        while True:
            while b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                reply = json.loads(line.decode("utf-8"))
                if reply.get("id") == request_id:
                    if "error" in reply:
                        raise RuntimeError(f"{method}: JSON-RPC error {reply['error'].get('code')}")
                    return reply["result"]
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"{method}: response timed out")
            for key, _ in self.selector.select(remaining):
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    self.selector.unregister(key.fileobj)
                    if key.data == "stdout":
                        raise RuntimeError(f"{method}: server closed stdout")
                    continue
                if key.data == "stdout":
                    self.buffer += chunk
                    if len(self.buffer) > 16 * 1024 * 1024:
                        raise RuntimeError("MCP response exceeded 16 MiB probe limit")
                else:
                    self.stderr_bytes += len(chunk)

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=3)
        self.selector.close()
        for pipe in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            pipe.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-apps", action="store_true", help="Call read-only list_apps without printing its contents")
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args()
    if not 0 < args.timeout <= 60:
        parser.error("--timeout must be greater than zero and at most 60 seconds")
    plugin = Path(__file__).resolve().parents[1]
    probe = MCPProbe(plugin, args.timeout)
    try:
        initialized = probe.rpc(1, "initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "computer-use-mcp-smoke-test", "version": "0.1.0"},
        })
        probe.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools = probe.rpc(2, "tools/list", {})["tools"]
        names = sorted(tool["name"] for tool in tools)
        if not {"list_apps", "get_app_state", "click", "type_text"}.issubset(names):
            raise RuntimeError("Expected Computer Use tools were not discovered")
        probe.rpc(3, "ping")
        report = {
            "ok": True, "protocol_version": initialized["protocolVersion"],
            "server": initialized["serverInfo"], "tools": names, "tool_count": len(names),
            "initialize": "passed", "ping": "passed", "app_input_tested": False,
        }
        if args.list_apps:
            result = probe.rpc(4, "tools/call", {"name": "list_apps", "arguments": {}})
            if result.get("isError"):
                known_error = "Computer Use server error -10000: Sender process is not authenticated"
                if any(block.get("text") == known_error for block in result.get("content", [])):
                    raise RuntimeError(known_error + "; verify this plugin from the authenticated desktop host")
                raise RuntimeError("list_apps returned an error; its private response is not printed")
            report["list_apps"] = "passed"
            report["list_apps_content_blocks"] = len(result.get("content", []))
        report["stderr_bytes"] = probe.stderr_bytes
        print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        probe.close()


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, TimeoutError, ValueError, KeyError) as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        sys.exit(1)
