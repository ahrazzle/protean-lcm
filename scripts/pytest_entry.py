"""pytest entry point used by ``scripts/run_tests.sh``.

Drops editable-install meta-path finders before pytest starts, so the overlay
directory on ``PYTHONPATH`` wins for the top-level ``plugins`` package. An
editable install of Hermes maps ``plugins`` to its own checkout, which does not
carry this repository's engine, and meta-path finders run ahead of the path
finder.
"""

from __future__ import annotations

import sys

sys.meta_path[:] = [
    finder for finder in sys.meta_path if "editable" not in type(finder).__module__.lower()
]

import pytest  # noqa: E402

raise SystemExit(pytest.main(sys.argv[1:]))
