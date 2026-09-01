# Taste ingest blocker fix 01

### Task
Исправлена только подтверждённая несовместимость final transactional proof в GitHub-owned Taste ingestion. Proof теперь допускает ingest key после успешного Taste ingest только как строго доказанную отдельную `resolve_base_support_condition` работу, без изменения Taste semantics, queue ownership или submission results.

### Verified facts
- `scripts/process_taste_inbox.py` теперь считает retained ingest key допустимым только одновременно при трёх условиях: соответствующая Taste projection entry уже имеет `status=cache_hit`; queue row имеет ровно `work_required=["resolve_base_support_condition"]`; canonical family существует, совпадает по `taste_subject_key` и имеет `requires_ai_base_support=true`.
- Любой retained ingest key, не удовлетворяющий этим условиям, остаётся fail-closed через `retained_ingest_keys_are_base_support_only`, а `ai_queue_decrement_exact`, `queue_file_count_exact` и `all_ingested_keys_removed_from_queue` рассчитываются с учётом только доказанных retained base-support rows.
- Regression validation покрывает оба обязательных случая: законный retained base-support key проходит все proof checks; обычный retained Taste-evaluation key проваливает proof.
- Canonical ingestion workflow `33440037739`, rerun attempt 2, job `99800543286` завершён успешно. Он использовал актуальный `main` с proof fix и создал canonical ingestion commit `cfadfd094c7a86ffbd4f43370a1bf42f47a79025`.
- Canonical receipt `data/cache/taste_ingest_receipts/970f899a5219e41aa7d7.json` фиксирует 9 input files, 147 results и все transactional checks = `true`.
- `safe_cache_hit_count` вырос `492 -> 639` (+147), `ai_required_count` уменьшился `181 -> 34` (-147). Все 147 ingest keys доказаны как cache hits; повторная Taste semantic evaluation этих результатов не требуется.
- После canonical rebuild `ai_queue_count=3`. В `data/production/pre_ai/chatgpt_taste_queue.jsonl` остались ровно `App_1017030`, `App_1019930`, `App_1022850`; у всех уже есть `resolved_taste_fit=moderate`, `work_required=["resolve_base_support_condition"]` и `requires_ai_base_support=true` для base appid `332950`.
- Canonical workflow после receipt удалил все 9 обработанных submission-файлов. Они не редактировались и не переоценивались вручную.

### Changes
- `scripts/process_taste_inbox.py` — добавлена bounded retained-base-support proof logic и corrected expected queue accounting без общего ослабления guard.
- `scripts/validate_taste_inbox_transactional_proof.py` — добавлены regression cases для legal retained base-support row и illegal retained Taste-required row.
- `.github/workflows/ingest-taste-batch.yml` — regression validator включён в canonical workflow перед ingestion для следующих запусков.
- `CURRENT_TASK.md` — stale Taste blocker status заменён фактическим завершённым ingest status; отдельно зафиксированы три штатные downstream base-support rows.
- 9 submission files и их Taste results вручную не изменялись; их удаление произошло только canonical ingestion workflow после успешного receipt.

Implementation commits:
- proof fix: `7d3d5ed05be8d3ad73e7f647c76fc4a32219def6`;
- regression validator: `2a0b3b17f16643cd42a441b606ac48b1ea9353e2`;
- workflow validation wiring: `f8d7800253922d9499adfaa0ef2e92de3b51c1de`;
- canonical ingestion persistence: `cfadfd094c7a86ffbd4f43370a1bf42f47a79025`;
- `CURRENT_TASK.md` status update: `ad35e6b2a7e1b6da13617e258a468168380923a8`.

### Validation
- Isolated regression validator executed before canonical rerun: `TASTE_INBOX_TRANSACTIONAL_PROOF_VALIDATION=PASS`; legal retained base-support case passed, while illegal retained Taste-work case failed the intended proof checks.
- Canonical GitHub Actions run `33440037739`, attempt 2, job `99800543286`: `success`.
- Canonical runtime proof emitted `TASTE_INBOX_TRANSACTION=PASS`.
- Receipt batch `970f899a5219e41aa7d7`: `result_count=147`, `safe_hits_increment_exact=true`, `ai_required_decrement_exact=true`, `retained_ingest_keys_are_base_support_only=true`, `ai_queue_decrement_exact=true`, `queue_file_count_exact=true`, `all_ingested_keys_removed_from_queue=true`, `all_ingested_keys_are_cache_hits=true`.
- Persisted post-ingest queue has exactly 3 rows and each row is base-support-only; no Taste-evaluation work remains for the 147 ingested results.
- Current canonical workflow now includes `python scripts/validate_taste_inbox_transactional_proof.py` before `process_taste_inbox.py`. The successful rerun was a re-run of the previously failed workflow attempt, so GitHub used that attempt's original step list while its checkout explicitly read current `main`; the new standalone regression step is therefore wired for subsequent fresh workflow invocations, while the end-to-end rerun itself validated the updated `process_taste_inbox.py` against the real 147-result batch.

### Unresolved
`none` ingestion-wise.

Штатная downstream semantic work остаётся отдельно: три rows (`App_1017030`, `App_1019930`, `App_1022850`) требуют только `resolve_base_support_condition`. Это не Taste re-evaluation и не ingestion blocker.

### Status
`complete`

### Recommended next step
Не запускать semantic worker вручную; позволить существующему GitHub-owned/scheduled canonical path обработать три оставшиеся `resolve_base_support_condition` rows как отдельную downstream работу.