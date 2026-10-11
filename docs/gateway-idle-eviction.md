# Gateway idle-only memory recovery

ExO gateway MOD-143 uses `POST /admin/api/models/evict-idle` with JSON `exclude_model_id`. It accepts existing admin-session or bearer authentication. Model aliases resolve through the pool before exclusion. Each candidate uses `unload_if_idle_unpinned`, which locks activity checks and unload together; this endpoint never requests abort or queues unload of a busy model.

Response: `status: ok`, `evicted` and `skipped` model IDs. The caller must remeasure memory and enforce its own admission guard; a successful endpoint response alone does not establish enough headroom. One finite candidate pass runs per request. Existing manual-unload semantics remain unchanged.

Tests: `python tests/test_gateway_idle_eviction.py` (AST-isolated endpoint and real pool activity-protection branches; not a concurrency stress test). Live authenticated endpoint, eviction receipt and subsequent generation verified2026-10-11 in `/home/director/Work/outputs/gateway-idle-eviction-2026-10-11`, local evidence81e1802.
