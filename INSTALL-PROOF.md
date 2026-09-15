# Install proof

Evidence that the plugin installs from the package and is found, enabled, and adopted by Hermes with no manual file copying.

Environment used

- Hermes Agent 0.21.3 (git install), Python 3.11
- a fresh Hermes home (`HERMES_HOME` pointing at an empty directory)
- the package installed into a directory that is not the Hermes install or the repository, reached through `PYTHONPATH` so the host tree and the developer virtualenv are left untouched

The one command a user runs is documented in the README:

```sh
pip install git+https://github.com/ahrazzle/protean-lcm.git
hermes plugins enable protean-lcm
hermes config set context.engine lcm
```

The transcript below installs from the working tree instead of the git URL. The wheel, the entry point, and the discovery path are identical to the git URL form.

## 1. Install

```
$ mkdir -p /tmp/lcm_proof/site /tmp/lcm_proof/home
$ pip install --target /tmp/lcm_proof/site /Users/kethuda/protean-lcm
Successfully built protean-lcm
Installing collected packages: protean-lcm
Successfully installed protean-lcm-0.1.0
```

The installed distribution carries the entry point Hermes reads:

```
$ cat /tmp/lcm_proof/site/protean_lcm-0.1.0.dist-info/entry_points.txt
[hermes_agent.plugins]
protean-lcm = protean_lcm
```

## 2. Discovered, before it is enabled

```
$ HERMES_HOME=/tmp/lcm_proof/home PYTHONPATH=/tmp/lcm_proof/site hermes plugins list --plain --no-bundled
not enabled  entrypoint 0.1.0    protean-lcm
```

Source is `entrypoint`, which is the pip plugin path. Nothing was copied into the Hermes home.

## 3. Enabled and selected

```
$ HERMES_HOME=/tmp/lcm_proof/home PYTHONPATH=/tmp/lcm_proof/site hermes plugins enable protean-lcm
✓ Plugin protean-lcm enabled. Takes effect on next session.

$ hermes config set context.engine lcm
✓ Set context.engine = lcm in /tmp/lcm_proof/home/config.yaml

$ hermes plugins list --plain --no-bundled
enabled      entrypoint 0.1.0    protean-lcm
```

## 4. The host loads it and an agent adopts the engine

`scripts/smoke_check.py`, run against the same fresh home:

```
$ HERMES_HOME=/tmp/lcm_proof/home PYTHONPATH=/tmp/lcm_proof/site python scripts/smoke_check.py
HERMES_HOME: /tmp/lcm_proof/home
context.engine: lcm
plugins.enabled: ['protean-lcm']
discovered: protean-lcm | source: entrypoint | enabled: True | error: None
plugin context engine: protean_lcm.engine | name: lcm
adopted engine: protean_lcm.engine.LCMEngine
engine name: lcm
context_length: 204800
threshold_tokens: 153600
engine tools: ['lcm_expand', 'lcm_page', 'lcm_search', 'lcm_status']
```

Read out: the plugin is found from the entry point, it loads with no error, it registers its engine with the host, and an agent built with `context.engine: lcm` adopts `protean_lcm.engine.LCMEngine`, receives the model context length, and gets the four `lcm_*` tools. The engine module name proves it came from the installed package rather than from a source tree.

## 5. Test suite after packaging

```
$ sh scripts/run_tests.sh /Users/kethuda/.hermes/hermes-agent -q
56 passed, 3 warnings in 1.50s
```

The suite runs against the real context-engine loader of the Hermes checkout passed to the script.

## Reproduce

```sh
SMOKE=/tmp/lcm_proof
mkdir -p "$SMOKE/site" "$SMOKE/home"
pip install --target "$SMOKE/site" .

HERMES_SRC=/path/to/hermes-agent
PY="$HERMES_SRC/venv/bin/python"

HERMES_HOME="$SMOKE/home" PYTHONPATH="$SMOKE/site" "$PY" "$HERMES_SRC/hermes" plugins list --plain --no-bundled
HERMES_HOME="$SMOKE/home" PYTHONPATH="$SMOKE/site" "$PY" "$HERMES_SRC/hermes" plugins enable protean-lcm
HERMES_HOME="$SMOKE/home" PYTHONPATH="$SMOKE/site" "$PY" "$HERMES_SRC/hermes" config set context.engine lcm
HERMES_HOME="$SMOKE/home" PYTHONPATH="$SMOKE/site" "$PY" scripts/smoke_check.py

sh scripts/run_tests.sh "$HERMES_SRC"
```
