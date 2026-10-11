# ExO oMLX fork workflow

Director instruction, 2026-10-11: use `development` for ongoing work in this fork. Do not create per-task or version-specific working branches unless the Director explicitly requests one.

- `fork` is the ExO repository (`emberDesire/omlx`); `origin` is upstream (`jundot/omlx`). Publish our work to `fork`, using explicit branch names.
- Preserve shared working-tree edits and existing fixes. Coordinate edits with other agents; stage only the intended files.
- The development branch was initialized from `6624aec`, preserving the v0.7.0 tool-choice enforcement, thinking-budget fix, and authenticated idle-eviction endpoint.
- Historical branch names are retained as history, not active work locations. A source branch change does not deploy or restart the Mac mini.
