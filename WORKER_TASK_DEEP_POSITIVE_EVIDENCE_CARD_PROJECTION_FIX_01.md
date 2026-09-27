# WORKER TASK — DEEP POSITIVE EVIDENCE CARD PROJECTION FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or the target is ambiguous, stop and switch first;
- do not use another repository.

Task ID: `deep-positive-evidence-card-projection-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/deep-positive-evidence-card-projection-fix-01.md`

## User-observed defect

For `game:1172380` / `STAR WARS Jedi: Fallen Order™` the current canonical Deep/PASS 2 state is authoritative and contains concrete positive evidence, but the published card says:

- `Персональная причина пока не подготовлена.`
- `why_fit: []`
- `why_fit_status.has_described_fit = false`.

Current canonical Deep state for this game has:
- `outcome=analyzed_fit`;
- `authoritative_completed=true`;
- `fit_level=strong`;
- `confidence=high`;
- three non-empty `positive_evidence` records;
- normalized `taste_factors`:
  - gameplay_mastery 88
  - development_variety 81
  - structure_pacing_direction 71
  - identity_hooks 87
  - breadth_of_match 86.

The published visual already uses this Deep result for fit/ranking, but its positive explanation is lost before card presentation.

## Goal

Repair the canonical Deep -> visual positive-explanation path so trustworthy current authoritative Deep positive evidence is projected into `Почему может зайти` with proper provenance instead of becoming an empty explanation.

Do not hard-code Jedi-specific text.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current `CHAT_CONTEXT.md`;
3. current top of `DIRECTOR_TASK_BOARD.md`;
4. relevant Progressive / explanation routes in `PROJECT_ROUTES.md`;
5. `config/progressive_personalization_contract.json`;
6. any current explanation/grounding contract referenced by the producer;
7. `config/execution_ownership_contract.json`;
8. exact current Deep state/result for `game:1172380`;
9. exact current visual item for `game:1172380`;
10. only the smallest producer/mapper/test files needed to prove and repair the broken boundary.

Do not re-run Deep or Dossier.

## Architecture preflight

Before writes, prove:
- Deep/PASS 2 accepted state remains GitHub-owned semantic truth;
- visual producer remains GitHub-owned;
- browser remains read-only;
- explanation projection does not become a second semantic analysis stage;
- no scheduler, queue, retry loop, recovery policy or Scheduled Task changes are required;
- positive explanations must remain grounded in accepted semantic evidence and must not be invented from title/genre/score alone.

## Required diagnosis before implementation

Prove the exact boundary where authoritative Deep `positive_evidence` is lost.

Determine whether the defect is:
- Deep ingest/state persistence dropping required positive fields;
- producer mapping ignoring PASS 2 positive evidence;
- explanation grounding/provenance gate recognizing older/Fast sources but not Deep;
- language/localization transformation dropping the evidence;
- another exact proven cause.

Do not assume the fix from the observed symptom.

## Required implementation

Implement the smallest shared fix that makes current trustworthy authoritative Deep positive evidence available to the existing `Почему может зайти` card path.

Requirements:
- use accepted current Deep evidence only;
- preserve exact provenance back to the accepted Deep result/state;
- preserve fail-closed behavior for stale/unbound/non-authoritative/incomplete Deep;
- preserve current behavior when no positive evidence exists;
- do not manufacture positive reasons from scores alone;
- do not expose raw internal/debug text if the existing UI contract requires user-facing Russian text;
- if a canonical translation/rendering layer is required for user-facing Russian explanations, use the existing owned path rather than adding ad-hoc browser translation.

## Regression requirements

At minimum prove:
1. `game:1172380`-equivalent authoritative `analyzed_fit` + non-empty Deep `positive_evidence` => non-empty grounded `why_fit`;
2. provenance is bound to current Deep evidence;
3. stale/non-current/unbound Deep evidence cannot populate `why_fit`;
4. no-positive-evidence remains safely empty rather than invented;
5. existing Fast/cache explanation behavior remains unchanged;
6. fit/ranking scores are unchanged by this explanation-only repair.

## End-to-end validation

After implementation:
- run relevant Progressive/explanation/UI validation;
- refresh against fresh `main` before merge because ЧАТ 2 is operating in parallel;
- merge only if clean/green;
- verify a successful normal full visual build and following Pages deploy;
- inspect deployed `game:1172380` and prove `Почему может зайти` is non-empty and grounded while its Deep fit/ranking result remains unchanged.

## Parallel-work constraint

НОВЫЙ ЧАТ 2 concurrently performs a READ-ONLY diagnostic of missing negative/risk evidence.

Before merge:
- re-read fresh `main`;
- preserve any report/Board commits from ЧАТ 2;
- do not overwrite its findings;
- if it discovers a broader semantic-contract issue that materially contradicts this implementation, stop and report the contradiction instead of merging blindly.

## Scope exclusions

Do not:
- change Dossier worker execution/evidence collection/recovery;
- change Deep semantic conclusions or rerun Deep;
- manually process Fast/Dossier/Deep backlog;
- change Scheduled Tasks;
- fix missing negative/risk evidence in this task;
- alter final ranking weights.

## Report

Write:
`reviews/worker_reports/deep-positive-evidence-card-projection-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Verified root cause`
4. `Changes`
5. `Parallel reconciliation`
6. `Validation`
7. `Published result`
8. `Unresolved`
9. `Status`
10. `Recommended next step` — exactly one bounded next step
11. exact PR/commit/run/artifact refs
12. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_fix`
- `needs_user_decision`

Do not start another task after this one.
