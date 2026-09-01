### Task
Implemented the deterministic producer-owned portion of the Russian-description contract in the canonical visual pipeline. Scope: preserve source metadata, classify language/quality deterministically, reject placeholders and technical/edition blurbs, expose unresolved source status, add targeted regression, and fail closed before canonical publish/deploy. Canonical ownership/routes were checked for an existing automatic description-translation path; none exists, so no ad-hoc translator, semantic queue, retry loop, or manual per-game translation was invented.

### Verified facts
- `data/production/pre_ai/content_metadata.json` already persists a non-Russian/English StoreBrowse `short_description`; the visual producer separately queries StoreBrowse with `language=russian`.
- Current ownership/routes define no canonical description-translation runtime/provider, immutable translation input/output artifact contract, queue, or GitHub ingest/persistence interface.
- The old visual producer accepted a description when it contained any Cyrillic character and otherwise published the literal fallback `Русское краткое описание для этой игры пока не подготовлено.`.
- Under the new full-payload validator, the legacy current payload contains 442 visible cards: `good_ru` 310, `placeholder_or_technical` 131, `weak_ru` 1; **132/442 invalid**.
- The new deterministic quality gate no longer treats one Cyrillic fragment as sufficient Russian.
- The producer no longer emits the literal placeholder as a normal final `summary`.
- Edition/package technical text is not accepted as a meaningful game description; the CONTROL Ultimate-style case is covered by regression.
- For unresolved descriptions the producer preserves explicit source/status metadata (`description_status`, source locale/quality/appid/path/text) rather than silently presenting bad text as final Russian.
- No ranking, Taste, package economics, duration scoring, or UI behavior was changed.

### Changes
- Added `scripts/russian_description_quality.py`: deterministic normalization/classification and description resolver.
- Added `scripts/test_russian_description_quality.py`: focused cases for good RU, non-RU with a Cyrillic fragment, literal placeholder, technical/edition blurb, empty source, and resolver outcomes.
- Added `scripts/validate_russian_descriptions.py`: full visible-payload fail-closed validator requiring meaningful Russian final descriptions.
- Updated `scripts/build_visual_feed_v2.py` to preserve raw source, use the deterministic quality gate, combine live RU StoreBrowse with persisted source metadata, remove the normal placeholder fallback, and emit explicit unresolved status/source metadata.
- Updated `scripts/build_final_visual_payload.py` to refresh description resolution deterministically with the same producer-owned logic.
- Updated `.github/workflows/build-daily-visual-payload.yml` to run the targeted regression and require the full Russian-description gate before the canonical visual commit.
- Updated `.github/workflows/deploy-visual.yml` to require the same full Russian-description gate before deployment.
- Added a one-shot migration helper/workflow used to apply and validate the deterministic implementation. It does not add a recurring semantic translation stage.
- No production payload was manually translated or hand-edited to make the validator pass.

### Validation
- One-shot migration run `33505457495`, successful deterministic attempt job `99849609519`:
  - `RUSSIAN_DESCRIPTION_PIPELINE_PATCH=PASS`;
  - `RUSSIAN_DESCRIPTION_QUALITY_TEST=PASS`;
  - Python compile checks passed for the changed description producer/validator modules;
  - the legacy current payload was deliberately rejected by the new validator: **132/442 invalid** (`131 placeholder_or_technical`, `1 weak_ru`), proving fail-closed behavior rather than placeholder publication.
- Deterministic implementation commit: `5261fe5b9f9d7c5d9e911bf41749594155f9d1d4` (`Enforce Russian description source quality`).
- Current `main` at final report preparation was `5733d722e3592301bb76481959b0f94a95112b8c`; comparison confirms it is two commits ahead of the implementation commit and those intervening changes touch only `DIRECTOR_TASK_BOARD.md` and `WORKER_TASK_DURATION_PROVIDER_RECON_01.md`, so the Russian-description implementation remains intact.
- Execution-ownership workflow run `33506058686` for the implementation commit passed.
- Canonical daily visual run `33506058710` was triggered, but failed at the pre-existing fixed-package validation step before reaching the new Russian-description steps; therefore this run is not claimed as a Russian gate failure/success. The downstream workflow-run deploy `33506075178` was consequently skipped; the direct push deploy run `33506058712` was cancelled.
- The new Russian-description gate itself was independently exercised in the one-shot validation above against the full 442-card canonical payload and failed exactly as intended on legacy bad descriptions.

### Production handling
- Existing `data/production/visual/current.json` was not manually rewritten or manually translated.
- The canonical producer now carries enough metadata to distinguish meaningful RU from non-RU/weak/technical/missing source and does not normalize an unresolved case into a fake successful Russian summary.
- Build/deploy workflows are wired to fail closed when final visible descriptions are not meaningful Russian.
- No new recurring semantic stage, translation queue, retry loop, secret, or unmanaged external runtime was introduced.
- Until a canonical translation owner/interface exists, unresolved descriptions remain explicit and cannot pass the new final validator as acceptable production output.

### Unresolved
- Exact contract gap: the repository does not define who performs semantic description translation, what immutable request artifact/hash is authoritative, what result schema proves correspondence to that request, or how GitHub validates/persists/ingests translated descriptions before rebuilding the visual payload.
- Therefore `needs_translation` / `needs_ru_rewrite` cannot be turned into `ready_ru` automatically without inventing a new semantic architecture that this task explicitly forbids.
- A canonical rebuild reaching 100% meaningful Russian visible descriptions is blocked on that ownership/interface decision. This is distinct from the deterministic classifier/source/gate work, which is implemented.

### Status
needs_user_decision

### Recommended next step
Approve one bounded canonical description-translation contract attached to the existing GitHub-owned visual producer: GitHub exports unresolved description records keyed by stable game/source hash; one designated semantic runtime returns Russian text keyed to the same immutable key/hash; GitHub validates, persists, ingests, and rebuilds; the validator added here remains the final production gate. Do not introduce manual catalog translations or an unmanaged queue.