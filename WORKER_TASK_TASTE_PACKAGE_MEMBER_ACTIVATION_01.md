# WORKER TASK — Taste Package Member Activation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If a tool opens another repository by default or the target repo is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-package-member-activation-01`
Mode: `ACTIVATE / VALIDATE`

## Goal
Activate the already accepted package-member dossier/Taste correction from PR `#31`, then create/confirm a fresh canonical pre-AI + dossier snapshot using the existing GitHub-owned production path so the next live web-evidence acceptance can start from identity-safe work.

Do not perform the live Scheduled ChatGPT acceptance run in this task.

## Read first / START gate
Follow `CHAT_PROTOCOL.md` START gate fully, including:
- `DIRECTOR_PROTOCOL.md` where required by protocol context;
- `CHAT_CONTEXT.md`;
- unfinished `CURRENT_TASK.md` if applicable;
- relevant `PROJECT_ROUTES.md` before broad search;
- relevant `PROJECT_DECISIONS.md`;
- relevant architecture pitfall(s);
- `config/execution_ownership_contract.json`.

Then read:
- `WORKER_TASK_TASTE_DOSSIER_PACKAGE_IDENTITY_FIX_01.md`
- `reviews/worker_reports/taste-dossier-package-identity-fix-01.md`
- `WORKER_TASK_TASTE_PACKAGE_MEMBER_DOSSIER_AGGREGATION_01.md`
- `reviews/worker_reports/taste-package-member-dossier-aggregation-01.md`
- `reviews/worker_reports/taste-package-edition-quality-recon-01.md`
- current metadata/status of PR `#31` (do not re-audit implementation diff unless protocol or an activation failure makes that necessary)

Run architecture preflight before any activation action.

## Accepted behavior being activated
The accepted package/member behavior is:

- package/store offer remains the commercial entity;
- authoritative meaningful game members are expanded into exact per-game dossier identities;
- each distinct member appid has one reusable dossier identity;
- package Taste uses `best-qualifying-member-no-average-v1`;
- one strong/moderate qualifying member keeps the package Taste-eligible;
- weak/unresolved members do not average down a known qualifying member;
- package/edition quality is a separate later risk/scoring concern and is NOT implemented here;
- DLC behavior is not broadened or redesigned in this activation.

For `Sub_87601`, the identity-safe member targets must remain `304240 Resident Evil` and `339340 Resident Evil 0`; the package title must never be paired with one contained appid as a fake game dossier identity.

## Activation sequence
Use only the existing canonical GitHub-owned activation/production route documented in the repository. Do not invent a manual side path.

1. Confirm the accepted durable report is `complete_ready_for_activation` and PR `#31` still corresponds to the validated accepted head or an equivalently validated descendant.
2. Confirm required PR checks are green/current enough for merge under repository policy.
3. Merge PR `#31` into `main` using the repository's normal merge path.
4. Confirm the merge landed in `main`.
5. Allow/execute only the repository-defined canonical post-merge activation/preparation path needed to produce a fresh pre-AI/dossier snapshot. If the canonical path is automatic, observe it; if the repository explicitly defines a manual GitHub action as the activation path, that manual dispatch is authorized for this task. Do not improvise a different workflow.
6. Confirm the fresh snapshot is generated from the merged package-member logic rather than preserving the pre-fix same-day snapshot.
7. Validate snapshot-level identity invariants and readiness for the next live acceptance without manually editing production artifacts.

## Fresh snapshot acceptance checks
The durable report must prove at minimum:

- snapshot was prepared after the PR `#31` merge/activation;
- snapshot identity/manifest changed appropriately from the old rejected snapshot when required by canonical semantics;
- package-member mapping is bound into the snapshot/manifest as implemented;
- `Sub_87601` no longer appears as a hybrid worker descriptor;
- exact member games `App_304240` / `App_339340` resolve coherently and are deduped globally if they also occur independently;
- no invalid/stale buffered result was accepted as progress merely because of activation;
- progress/checkpoint state remains canonical and is not manually advanced;
- next expected live group is known and identity-coherent;
- DLC behavior remains unchanged;
- no package/edition-quality penalty implementation was introduced.

If activation reveals an ordinary deterministic defect, fix only if it is a direct activation defect within this accepted scope and validation can be completed safely. If it reveals a new architecture/product decision, STOP and report `blocked` rather than inventing policy.

## Scheduled Task / UI boundary
Do NOT press ChatGPT Scheduled Task `Run now` in this task.
Do NOT edit its prompt, schedule, or settings.
If any UI-only Scheduled Task datum becomes genuinely necessary, stop and ask the user for that exact datum rather than spending time trying to inspect inaccessible UI state.

## Other prohibitions
- Do not modify or implement `offer_edition_quality` / package-edition scoring from the separate RECON.
- Do not modify Taste Semantic Producer behavior except if an already-documented canonical activation step mechanically refreshes data around it without changing its contract.
- Do not add a scheduler, recurring quota, backlog manager, retry owner, or alternate control plane.
- Do not manually rewrite queue/cache/progress/receipt production files to force success.
- Do not use any other repository.

## Durable report
Publish final report to `main`:
`reviews/worker_reports/taste-package-member-activation-01.md`

Report must include:
- architecture preflight result;
- PR `#31` pre-merge head and merge commit;
- merge/check status evidence;
- canonical activation/preparation path used;
- fresh snapshot id/date/counts and previous snapshot id for comparison;
- exact proof for `Sub_87601` and member identities;
- next expected live group summary sufficient for Director review;
- proof no live Scheduled Task run occurred;
- production side effects actually performed;
- any automatic workflow run refs used for activation/validation;
- exactly one next step.

Allowed final statuses:
- `complete_ready_for_live_acceptance`
- `blocked`

Ensure final durable report is in `main` before claiming completion. Stop after report publication.