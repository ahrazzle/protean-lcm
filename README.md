# protean-lcm

Opt-in LCM DAG context engine plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent), maintained as a standalone repo in the Protean System. Installs into `~/.hermes/plugins/` or via a pip entry point. No core files touched.

Inspired by [stephenschoettler/hermes-lcm](https://github.com/stephenschoettler/hermes-lcm) (MIT), reimplemented as a bounded-recall, opt-in context engine with migration, backup, rollback, and lifecycle tests.

## Layout

- `plugins/context_engine/lcm/` — engine, storage, recall, compaction, config, skill
- `tests/plugins/context_engine/` — registration, lifecycle, migration/backup, recall, rollback, compaction, storage

## Status

In review. Not yet bundled into the Proteus project.

## License

MIT. See LICENSE. Upstream inspiration attributed above.
