# Taste Manual Throughput Drain 01 — Worker Report

- task_id: `taste-manual-throughput-drain-01`
- lifecycle: `in_progress`
- started_at_utc: `2026-09-10T08:12:02Z`
- checkpoint_at_utc: `2026-09-10T08:14:03Z`
- starting_queue_count: `566`
- current_verified_queue_count: `566`
- accepted_batches: `0`
- accepted_games_total: `0`
- last_committed_batch: `none`
- stop_reason: `none`
- observed_games_capacity_this_worker_chat: `0`
- next_action: `semantically evaluate, validate, submit, and verify batch 1`

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

## Batch 1 — selected, not yet submitted

- selection_queue_sha: `74be1d45c1b93ab9607971ab9c8cb3f38f6ae4e9`
- selection_order: canonical queue lines `1..10`
- result_contract: `TASTE-SEMANTIC-RESULT-V5`
- producer_generation_required: `2`
- profile_blob_sha: `b487e62b3fec9f413fb001d96b4894f8ac43e5d5`
- taste_model_version: `taste-v3`
- taste_semantics_sha256: `0dbcc4c167a995bf6505b4e1e361e38103c5eacb254a308b4ba6d5ae13eb2828`
- source_mailing_updated_at_utc: `2026-09-08T20:46:16.637935+00:00`

| # | taste_subject_key | appid | title | taste_fingerprint | candidate_context_sha256 |
|---:|---|---:|---|---|---|
| 1 | `App_2336880` | `2336880` | Destiny 2: The Final Shape | `097b3a222b602f3128ecf89a20737c9ac9bd223c41e5110149eede7ff75074af` | `de83aa96a5fb29a1d8df896f006442c708b4afc25533df77b7c49504efe03a2a` |
| 2 | `App_527070` | `527070` | Galactic Civilizations III: Crusade Expansion Pack | `18ac32f48583dfe8f548bb744449c63e45485cb1b98f8955283141ffa74ca830` | `562b863fe6ca932362076a8d1ce1e8eb16d193313e0aee4c1edd346fadaf3e54` |
| 3 | `Sub_4156` | `6800` | Commandos Pack | `f339b834aa9017192bf5fc1a85b88a714e0cfa46aab09ec16677403f2b031c8f` | `eda37d7a4316fdaaee140ef458139eac40107479a4719683d4ad8f00aba35221` |
| 4 | `Sub_44162` | `214340` | Daedalic Adventure Bundle | `db847c1e087b86f675cb53c8e882e5237bc4f987ca23c6f67f1a58faaa715068` | `628900bd6b11edba6767fdf1701c1a1c8c0defa7cb8085685c474143ae432168` |
| 5 | `Sub_55062` | `214340` | The Daedalic Armageddon Bundle | `2c91187c103dde9a228a2ffb263b34483930ddf751b2d98eb8abe122c0aba2f3` | `d5175e738adfe2c22025c12a5f44840b9f8115d6e58b02a4d8669bf1704c5120` |
| 6 | `Sub_87601` | `304240` | Resident Evil Deluxe Origins Bundle / Biohazard Deluxe Origins Bundle | `8c492c88bfd549e881568ca60bd615e746164e158caae58dc2e96d43235df5ee` | `54b46a1879b19917d0a47d5526f273dd2b07ba997aa207df0902d3d181ef142c` |
| 7 | `App_1004240` | `1004240` | Hentai Girl Karen | `aa91889d1666d6c8dcecdbc35ea0eb2b71a814463ed58999e817ef5454a511cb` | `8a5b75f53d3000e8a466ff885702723251296eac61287a74780aa574b2469bb7` |
| 8 | `App_10150` | `10150` | Prototype™ | `ed46bdeca520dcc7dd002fb462eef58689fb423a6ef8be1acd896109622f8a4e` | `b43f8e93ab6bc1aa8d4e213c3a4aa6978e09b434e266e2a3c2669b745e87a3e5` |
| 9 | `App_1015940` | `1015940` | Welcome to Elk | `ec612c812134b6455b80ddc1e12cf5575337005030d83b76ef681fc0fcde2a1c` | `ec0e18a36084e98e0ca5c11c3dd2daa74a6ad9c3bbb7293a1971bb1b4c3b86e3` |
| 10 | `App_1016920` | `1016920` | Unrailed! | `725ef10ec9c94aa0ef83e5543dbeb19c327499f95961726ded2e2568a6c2d311` | `5eddb6f5dd6fec14e9899e136f92536cf3e18bb4c28774201ea884888903f972` |

Batch 1 has been durably selected before semantic execution. No result for this batch has been submitted or counted yet.

This is an authorized one-off production execution and empirical worker-chat capacity probe. Only canonically accepted real games from this chat count toward `observed_games_capacity_this_worker_chat`.
