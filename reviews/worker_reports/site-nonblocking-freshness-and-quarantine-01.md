# Site nonblocking freshness and quarantine 01

## Task

- Task: `WORKER_TASK_SITE_NONBLOCKING_FRESHNESS_AND_QUARANTINE_01.md`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Branch: `fix/site-nonblocking-freshness-quarantine-01`
- Mode: IMPLEMENT / ARCHITECTURE AUDIT / VALIDATE
- This task supersedes the earlier narrow Tetris-only fix. No semantic worker, ranking formula, queue order, Stage 1/2 score semantics, profile, or Scheduled Task is changed.

## Architecture preflight

- Current owner: GitHub repository + GitHub Actions.
- Canonical authority: `config/execution_ownership_contract.json`, `config/progressive_personalization_contract.json`, and new `config/site_publication_resilience_contract.json`.
- Browser remains read-only presentation.
- No control-plane responsibility is transferred to ChatGPT/current chat.
- No recurring semantic stage, semantic queue, retry daemon, quota, or backlog manager is added.
- Global source/schema/material authority remains fail-closed.

## Publication blocker inventory

| Surface / gate | Classification | Before | Implemented behavior |
| --- | --- | --- | --- |
| Progressive source/scope/accounting invariants | GLOBAL | fail closed | unchanged, fail closed |
| complete history/source readiness for full visual replacement | GLOBAL | may hold visual build | unchanged for visual; independent status may still refresh |
| exact full-visual material binding + repeated material drift | GLOBAL | fail closed | unchanged, fail closed |
| canonical ranking / ownership / schema contract regressions | GLOBAL | fail closed | unchanged, fail closed |
| missing stable paid-card identity | GLOBAL | unsafe to isolate | remains fail closed |
| card `why_fit`/risk/caution presentation validation | LOCAL | one card failed whole full-visual persistence | hide only invalid presentation fields, quarantine exact card/field, continue |
| current personalized binding/verdict mismatch found in grounded-negative finalization | LOCAL exact family | one row could raise and abort all cards | quarantine/hide only exact card, continue unrelated rows |
| missing grounded negative presentation candidate | LOCAL exact family | one row could raise and abort all cards | hide risk presentation only, quarantine, keep card/scoring |
| invalid personalized Russian description presentation | LOCAL exact family | invalid `ready_ru` could abort publication | hide summary, mark `publication_quarantined`, quarantine; never promote invalid text |
| invalid giveaway offer under a globally trusted giveaway snapshot | LOCAL exact game | one malformed offer degraded the whole giveaway sibling to unavailable | omit invalid offer/game contribution, quarantine diagnostic, publish valid siblings |
| untrusted/incomplete/wrong-contract giveaway snapshot | GLOBAL to giveaway sibling | unavailable | unchanged global trust rule; never reinterpret as local valid data |
| Pages exact visual receipt/material identity | GLOBAL | fail closed for claimed fresh visual | unchanged |
| current site-status exact source bindings | GLOBAL to status artifact | new | fail closed if status cannot prove exact current canonical sources |

## Implementation

### Canonical resilience contract and ownership

Added `config/site_publication_resilience_contract.json` and bound it from execution ownership / Progressive publication contracts.

Core rule:
- exact identifiable local presentation defect → quarantine + deterministic omission/isolation + continue;
- global authority/integrity defect → fail closed.

Last-known-good reuse is permitted only with exact compatible proof. Otherwise the implementation omits only the unsafe field/item. It does not silently reuse arbitrary old content.

### GitHub-owned quarantine

Added:
- `scripts/site_publication_resilience.py`
- `data/production/site/publication_quarantine.json`

Stable identity:
`category + object_type + object_id + field` → deterministic SHA-256 `defect_id`.

Entries carry:
- category/object/field;
- reason codes;
- first/last seen;
- source binding;
- pending/resolved/superseded state.

Repeated observation coalesces into one entry. A pending defect missing from the complete next observation becomes resolved rather than accumulating duplicate rows.

### Local per-item isolation

Added `scripts/isolate_site_publication_defects.py`.

After visual candidate generation and grounded-negative finalization, but before strict validators/persistence:
- invalid card explanation/risk/caution presentation is removed from that card only;
- invalid Russian description presentation is removed from that card only;
- invalid giveaway offers under trusted snapshot are omitted individually;
- all such defects are reconciled into canonical quarantine.

Existing validators remain strict for unquarantined content. Quarantine is accepted only when the corresponding visible fields are actually hidden.

### Independent current Statistics artifact

Added:
- `scripts/build_site_status.py`
- `.github/workflows/build-site-current-status.yml`

Artifact:
`data/production/site/current_status.json`.

It derives Fast/Dossier/Deep/translation counts from current canonical GitHub state independently of rendered cards, cross-checks Fast and Deep against their current work-scope accounting, requires Dossier/translation observability, and binds exact source blobs.

It also publishes quarantine:
- pending count;
- category counts;
- last quarantine change;
- current status generation timestamp.

The dedicated workflow is GitHub-owned and deterministic. It does not execute semantic work.

### Full visual publication

`.github/workflows/build-daily-visual-payload.yml` now follows:

fresh candidate → local isolation/quarantine → independent current status → strict post-isolation validators → exact material binding → canonical persistence.

Quarantine and current status are staged atomically with a successful full visual persistence. The material-drift rebuild path runs the same isolation/validation sequence.

### Pages / browser

`.github/workflows/deploy-visual.yml` stages both:
- `web/data/current.json`
- `web/data/status.json` when the canonical status artifact exists.

A status-only canonical commit can deploy current Statistics while preserving the existing visual payload. Exact status source bindings are validated before deploy. Local visual validators are not used to veto a status-only publication.

`web/app.js` fetches status independently with `cache:'no-store'`. Statistics prefers the independent status; if absent, it falls back to legacy `visual.processing_status`.

`web/progressive-personalization-ui.js` adds `Диагностика публикации`, showing pending count, brief category counts, and producer-owned current status timestamp.

## Tetris regression

Focused regression uses `Tetris® Effect: Connected` with accepted Deep score/provenance and commercial/ranking language in `why_fit`.

Expected/implemented:
- accepted Deep `total_score`, score breakdown and semantic generation remain unchanged;
- invalid player-facing positive text is removed;
- exact defect enters quarantine;
- strict card validator passes the sanitized card;
- unrelated current content remains publishable.

## Tests / validation

Added:
- `scripts/test_site_publication_resilience.py`
- `.github/workflows/validate-site-publication-resilience.yml`
- updated giveaway and Progressive UI regressions.

Covered:
- Tetris local failure isolation without semantic mutation;
- quarantine dedupe and automatic resolved transition;
- invalid description isolation;
- missing stable identity remains global fail-closed;
- malformed giveaway offer does not hide valid sibling;
- missing giveaway game identity remains fail-closed;
- Statistics quarantine section / independent status fetch;
- current canonical status build + exact source-binding validation.

## Durable project documentation

Added:
- `PROJECT_DECISIONS.md#VISUAL-002`
- `PROJECT_ROUTES.md#Site-publication-resilience-current-Statistics-local-quarantine`

## Runtime acceptance

Pending at this report revision:
- PR checks;
- merge to current `main`;
- one fresh production-relevant status/visual/deploy cycle;
- exact Pages artifact confirmation that current status matches the same current canonical accounting snapshot;
- confirmation that global guards still fail closed in CI regressions.

This section must be updated before final completion is claimed.

## Status

`implementation_complete_runtime_acceptance_pending`
