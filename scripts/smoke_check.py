"""Fresh-profile smoke check for the installed plugin.

Run it with the Hermes interpreter, the installed package on the path, and a
throwaway Hermes home:

    HERMES_HOME=/tmp/lcm-home PYTHONPATH=/tmp/lcm-site \\
      /path/to/hermes/venv/bin/python scripts/smoke_check.py

It asserts nothing. It prints what the host discovered and which engine an
agent adopted, so the output can be read as evidence.
"""

from __future__ import annotations

from unittest.mock import patch

import hermes_cli.plugins as plugins_mod
import hermes_constants
from hermes_cli.config import load_config

print("HERMES_HOME:", hermes_constants.get_hermes_home())

cfg = load_config()
print("context.engine:", (cfg.get("context") or {}).get("engine"))
print("plugins.enabled:", (cfg.get("plugins") or {}).get("enabled"))

plugins_mod.discover_plugins()
manager = plugins_mod.get_plugin_manager()

for key, loaded in sorted(manager._plugins.items()):
    if "protean" in key or "lcm" in key:
        print(
            "discovered:",
            key,
            "| source:", loaded.manifest.source,
            "| enabled:", loaded.enabled,
            "| error:", loaded.error,
        )

candidate = plugins_mod.get_plugin_context_engine()
print(
    "plugin context engine:",
    type(candidate).__module__,
    "| name:",
    getattr(candidate, "name", None),
)

# Ask for the engine through the same config path a real session uses.
selection_cfg = {"context": {"engine": "lcm"}, "agent": {}}
with (
    patch("hermes_cli.config.load_config", return_value=selection_cfg),
    patch("hermes_cli.config.load_config_readonly", return_value=selection_cfg),
    patch("agent.model_metadata.get_model_context_length", return_value=204_800),
    patch("model_tools.get_tool_definitions", return_value=[]),
    patch("model_tools.check_toolset_requirements", return_value={}),
    patch("agent.process_bootstrap.OpenAI"),
):
    from run_agent import AIAgent

    agent = AIAgent(
        api_key="test-key-1234567890",
        base_url="https://openrouter.ai/api/v1",
        enabled_toolsets=["context_engine"],
        quiet_mode=True,
        skip_context_files=True,
        skip_memory=True,
    )

engine = agent.context_compressor
print("adopted engine:", type(engine).__module__ + "." + type(engine).__name__)
print("engine name:", engine.name)
print("context_length:", engine.context_length)
print("threshold_tokens:", engine.threshold_tokens)
tool_names = sorted(
    tool.get("function", {}).get("name") for tool in getattr(agent, "tools", [])
)
print("engine tools:", [name for name in tool_names if name and name.startswith("lcm_")])
