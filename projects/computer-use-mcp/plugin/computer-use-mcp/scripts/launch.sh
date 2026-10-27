#!/bin/sh
# Delegate stdio unchanged to the installed engine. Never modify host policy.
set -eu

fail() { printf '%s\n' "computer-use-mcp: $*" >&2; exit 1; }
case "${1:-}" in
  ""|--check) ;;
  *) fail "usage: /bin/sh launch.sh [--check]" ;;
esac
[ "$#" -le 1 ] || fail "too many arguments"
[ "$(/usr/bin/uname -s)" = Darwin ] || fail "macOS is required"
runtime_base="${CODEX_HOME:-${HOME:?HOME is required}/.codex}/computer-use"
runtime_app="$runtime_base/Codex Computer Use.app"
runtime_client="$runtime_app/Contents/SharedSupport/SkyComputerUseClient.app/Contents/MacOS/SkyComputerUseClient"
[ -d "$runtime_app" ] || fail "Computer Use is not installed. Install/enable the official Computer Use plugin in the desktop app."
[ -x "$runtime_client" ] || fail "Computer Use client is missing or not executable. Repair the official installation."
if [ "${1:-}" = --check ]; then
  printf '%s\n' "computer-use-mcp: installed client found" "Client: $runtime_client" "Check covers file availability only; MCP and app permissions need separate verification." >&2
  exit 0
fi
cd "$runtime_base"
exec "$runtime_client" mcp
