# WORKER TASK — Taste Dossier Buffered Activation State Align 01

Task ID: `taste-dossier-buffered-activation-state-align-01`
Mode: `IMPLEMENT — CONTRACT/STATE ALIGNMENT ONLY`

## Goal
Resolve the canonical activation-state contradiction found by live acceptance after buffered runtime was already implemented and landed.

Current problem: the repository worker prompt/runtime are buffered, but canonical contract/persistence bridge still contain transition declarations such as `authorized_not_activated`, `authorized_not_implemented`, and legacy active transport. The live Scheduled Task correctly failed closed.

This task must align canonical contract/state declarations with the already-landed buffered runtime. It must NOT redesign or reimplement runtime behavior.

## START gate
Read fully before any change:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-buffered-contract-01.md`
- `reviews/worker_reports/taste-dossier-buffered-submission-implement-01.md`
- `reviews/worker_reports/taste-dossier-live-buffered-prompt-prep-01.md`
- `reviews/worker_reports/taste-dossier-live-buffered-acceptance-01.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current canonical dossier work manifest.

Perform architecture preflight explicitly.

## Required conclusion before edit
First prove from durable `main` that buffered runtime is actually implemented/landed and that the only blocker observed by live acceptance is stale canonical activation/transition wording.

If you discover a real runtime/contract mismatch beyond stale status declarations, STOP and report `blocked` instead of broadening scope.

## Allowed changes
Prefer the smallest canonical alignment necessary, expected primarily in:
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_persistence_bridge.json`
- `PROJECT_DECISIONS.md` only if a durable activation decision/update is actually required.

Do NOT modify runtime scripts/workflows unless a concrete contradiction proves activation cannot be represented correctly without such a change. If runtime change would be required, STOP and report `blocked` for a separate task.

## Alignment requirements
After this task, canonical repository declarations must unambiguously state the already-landed real mode:

- buffered group create-only transport is ACTIVE, not merely authorized for the future;
- state-based maximal-contiguous-prefix buffered drain is implemented/active;
- active transport mode is buffered group create-only V1 (or the exact canonical identifier already implemented);
- legacy current-checkpoint create-only behavior may remain only as an explicitly transitional compatibility fallback if runtime truly still supports it, but it must not be declared the authoritative active transport for the live worker;
- no field may still say buffered mode/drain is `authorized_not_activated`, `authorized_not_implemented`, or otherwise future-only if it is already the landed runtime path;
- repository worker prompt, contract and persistence bridge must agree;
- GitHub remains control-plane owner;
- checkpoint/group size 10 remains durability boundary only;
- Taste Semantic Producer remains unchanged.

Do not invent a new architecture version unless the existing contract's transition/versioning model genuinely requires it. Prefer minimal status/transition alignment over gratuitous version churn.

## Production / trigger safety
The previous contract task proved config changes can trigger production workflows through `push.paths`.

Before the first write:
- inspect relevant workflow triggers;
- use a branch/PR if that is safer;
- do not falsely claim no production activity if merge triggers automatic workflows;
- no manual workflow dispatch;
- no Scheduled Task `Run now` in this task.

If automatic pre-AI refresh occurs after landing, verify read-only that current snapshot/progress/fresh dossier cache remain safe and report the actual effect.

## Validation
Before completion:
- read back aligned canonical files from landed `main`;
- verify no contradictory buffered activation statuses remain in the relevant contract/bridge sections;
- verify worker prompt now agrees with contract/bridge;
- verify execution ownership contract remains unchanged unless a genuine inconsistency was discovered;
- verify no Taste Semantic Producer files/behavior changed;
- verify current dossier canonical state was not reset/lost/duplicated by landing side effects;
- run existing relevant contract/runtime validation if available and proportionate.

Do NOT perform the live acceptance run here.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-buffered-activation-state-align-01.md`

Report must include:
- architecture preflight;
- exact stale declarations found;
- exact canonical alignment made;
- files changed;
- branch/PR/merge refs if used;
- trigger/automatic workflow effects;
- read-back proof that prompt/contract/bridge now agree;
- proof current production state remained safe;
- explicit confirmation no Scheduled Task run and no Taste Semantic Producer change occurred;
- one next step only: repeat separate live buffered ACCEPTANCE.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `alignment_incomplete`

Stop after durable report. Do not start live acceptance.