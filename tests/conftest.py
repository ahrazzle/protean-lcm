"""Per-test isolation for the LCM suite.

These tests drive two process-global pieces of Hermes state:

* the plugin manager singleton (registration, and the ``/lcm`` command it
  forwards into ``plugin_manager._plugin_commands``), and
* the Hermes home that the engine resolves its store path from.

Without a reset between tests, a command registered by one test is still
present when the next test calls ``register()``, which changes that test's
outcome. Hermes ships this reset in its own ``tests/conftest.py``. A standalone
checkout has to provide the equivalent, so it is reproduced here in the minimal
form the suite needs.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolated_home_and_plugin_state(tmp_path, monkeypatch):
    # Keep the engine's store path inside the test's tmp dir.
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-home"))
    monkeypatch.setenv("TZ", "UTC")
    # Never let an agent-init path reach pip or the network.
    monkeypatch.setenv("HERMES_DISABLE_LAZY_INSTALLS", "1")

    try:
        import hermes_cli.plugins as plugins_mod
    except Exception:
        yield
        return

    monkeypatch.setattr(plugins_mod, "_plugin_manager", None, raising=False)
    reset = getattr(plugins_mod, "_reset_plugin_managers_for_tests", None)
    if callable(reset):
        try:
            reset()
        except Exception:
            pass

    yield

    # Drop anything the test registered, including the per-home manager cache.
    plugins_mod._plugin_manager = None
    if callable(reset):
        try:
            reset()
        except Exception:
            pass
