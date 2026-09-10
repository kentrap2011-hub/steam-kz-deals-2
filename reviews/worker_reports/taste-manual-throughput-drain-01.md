# Taste Manual Throughput Drain 01 — Worker Report

- task_id: `taste-manual-throughput-drain-01`
- lifecycle: `in_progress`
- started_at_utc: `2026-09-10T08:12:02Z`
- checkpoint_at_utc: `2026-09-10T08:12:02Z`
- starting_queue_count: `566`
- current_verified_queue_count: `566`
- accepted_batches: `0`
- accepted_games_total: `0`
- last_committed_batch: `none`
- stop_reason: `none`
- observed_games_capacity_this_worker_chat: `0`
- next_action: `validate and process batch 1`

## Start-state verification

- canonical_queue: `data/production/pre_ai/chatgpt_taste_queue.jsonl`
- canonical_manifest: `data/production/pre_ai/chatgpt_payload.json`
- manifest_ai_queue_count: `566`
- queue_line_566_present: `true`
- queue_sha: `74be1d45c1b93ab9607971ab9c8cb3f38f6ae4e9`
- manifest_sha: `702a0bea68e7933446706d35a3500711ae8ce74f`
- projection_status: `complete`
- projection_complete_coverage: `true`
- projection_index_integrity_ok: `true`
- profile_blob_sha: `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`
- taste_model_version: `taste-v3`
- taste_semantics_sha256: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- source_mailing_updated_at_utc: `2026-09-08T20:46:16.637935+00:00`
- canonical_ingest_workflow: `.github/workflows/ingest-taste-batch.yml`
- scheduled_task_touched: `false`

This is an authorized one-off production execution and empirical worker-chat capacity probe. Only canonically accepted real games from this chat count toward `observed_games_capacity_this_worker_chat`.
