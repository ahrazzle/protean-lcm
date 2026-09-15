#!/bin/sh
# Run the LCM test suite against a Hermes Agent checkout.
#
#   sh scripts/run_tests.sh <hermes-agent-checkout> [pytest args...]
#
# The suite drives the real Hermes context-engine loader, so it needs a Hermes
# source tree. The loader is symlinked into a temporary overlay together with
# this repository's engine, and pytest runs from the repository root with the
# overlay first on the path, which keeps the repository's own engine under test
# without modifying the checkout.
#
#   HERMES_SRC  checkout to test against (same as the first argument)
#   PYTHON      interpreter to use (default: the checkout's venv)

set -eu

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)

if [ -z "${HERMES_SRC:-}" ] && [ "$#" -gt 0 ]; then
  HERMES_SRC=$1
  shift
fi
if [ -z "${HERMES_SRC:-}" ]; then
  printf 'usage: sh scripts/run_tests.sh <hermes-agent-checkout>\n' >&2
  exit 2
fi
HERMES_SRC=$(cd "$HERMES_SRC" && pwd)
if [ ! -f "$HERMES_SRC/plugins/context_engine/__init__.py" ]; then
  printf 'error: %s is not a Hermes Agent checkout\n' "$HERMES_SRC" >&2
  exit 2
fi

OVERLAY=$(mktemp -d "${TMPDIR:-/tmp}/lcm-overlay.XXXXXX")
trap 'rm -rf "$OVERLAY"' EXIT
mkdir -p "$OVERLAY/plugins/context_engine"

# Take every plugin directory from the checkout, then swap in this repository's
# engine. Symlinks keep the overlay tied to the checkout, so the loader and its
# siblings are always the real ones.
for path in "$HERMES_SRC"/plugins/*; do
  name=${path##*/}
  [ "$name" = "context_engine" ] && continue
  ln -s "$path" "$OVERLAY/plugins/$name"
done
for path in "$HERMES_SRC"/plugins/context_engine/*; do
  name=${path##*/}
  [ "$name" = "lcm" ] && continue
  ln -s "$path" "$OVERLAY/plugins/context_engine/$name"
done
ln -s "$REPO_ROOT/plugins/context_engine/lcm" "$OVERLAY/plugins/context_engine/lcm"

if [ -z "${PYTHON:-}" ]; then
  for candidate in "$HERMES_SRC/venv/bin/python" "$HERMES_SRC/.venv/bin/python"; do
    if [ -x "$candidate" ]; then PYTHON=$candidate; break; fi
  done
fi
if [ -z "${PYTHON:-}" ]; then
  PYTHON=$(command -v python3)
fi

printf 'Hermes checkout: %s\n' "$HERMES_SRC"
printf 'Interpreter:     %s\n' "$PYTHON"

cd "$REPO_ROOT"
PYTHONPATH="$OVERLAY:$HERMES_SRC${PYTHONPATH:+:$PYTHONPATH}" \
  exec "$PYTHON" "$REPO_ROOT/scripts/pytest_entry.py" \
    --confcutdir="$REPO_ROOT" \
    tests/plugins/context_engine "$@"
