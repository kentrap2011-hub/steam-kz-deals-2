# WORKER TASK — TASTE DOSSIER WORKER PROMPT V2 ALIGNMENT FIX 01

## Assignment
- Worker slot: **NEW physical ЧАТ 2**
- Mode: **IMPLEMENT / ACTIVATE / VALIDATE**
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Branch/source of truth: `main`
- Durable report: `reviews/worker_reports/taste-dossier-worker-prompt-v2-alignment-fix-01.md`

Do not search, read, modify, or use any other repository.

## START
1. Read current `CHAT_PROTOCOL.md` from `main` and execute its START gate.
2. Read this task fully.
3. Read current canonical Dossier prompt/runtime/contract/projection files needed for this bounded fix.
4. Read the accepted non-blocking progress report:
   `reviews/worker_reports/taste-dossier-nonblocking-group-progress-implement-01.md`.

## Accepted diagnosis
Current production has a canonical prompt/projection contradiction:

- `config/taste_steam_review_dossier_worker_prompt.md` still requires `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V1` and `canonical_expected_sequence`.
- Current GitHub-generated worker index is `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2`.
- Current runtime prompt already requires V2 and uses `next_pending_sequence` + `pending_group_sequences`.
- Current index has `next_pending_sequence=1`, but the Scheduled worker correctly stopped fail-closed because the primary canonical prompt still required the superseded V1 traversal contract.

No dossier candidate was created by the blocked invocation.

## Required implementation

### FIX-01 — align primary worker prompt to V2 traversal
Update only the stale start/traversal/progress semantics in
`config/taste_steam_review_dossier_worker_prompt.md`
so they match the accepted current non-blocking V2 architecture.

At minimum:
- require worker index schema `TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2`;
- use `normal_first_pass_complete`, `next_pending_sequence`, and `pending_group_sequences`;
- start from the exact GitHub-projected `next_pending_sequence`;
- preserve exact descriptor identity/binding checks;
- preserve same-invocation strictly ordered traversal only through the current immutable plan;
- preserve fail-closed behavior for missing/inconsistent projection;
- do not restore `canonical_expected_sequence` as the current owner;
- preserve separate GitHub-owned failed-group recovery semantics.

Do not weaken any evidence, privacy, exact-app, source, validation, create-only, or ownership rules elsewhere in the prompt.

### FIX-02 — prevent prompt/projection drift
Add focused regression coverage that fails if the canonical worker prompt regresses to V1/`canonical_expected_sequence` while the live runtime/projection architecture is V2.

The regression must be tied to the current production validation surface and must verify the live files, not a disconnected fixture only.

### FIX-03 — refresh binding/projection
If the canonical prompt content hash participates in the current worker binding/projection, rebuild the current GitHub-owned Dossier projection through the existing canonical path after the prompt change.

Do not hand-edit snapshot/index hashes or work/progress state.

### FIX-04 — validate fresh main
Prove on fresh `main`:
- primary worker prompt and runtime prompt both require V2;
- current index is V2 and exposes a legal `next_pending_sequence` or a legitimate complete state;
- all binding hashes are current and mutually compatible;
- current descriptor for the next pending group is readable and consistent;
- no dossier candidate was fabricated;
- no current progress/group status was manually advanced;
- no Scheduled Task setting changed and no Scheduled Task `Run now` occurred.

## Hard prohibitions
Do not:
- change Dossier evidence semantics beyond the stale traversal/progress text;
- change Fast/PASS 1 or Deep/PASS 2 behavior;
- recreate old V1 contiguous-prefix ownership;
- manually choose/skip/reorder a group outside GitHub V2 projection;
- manually edit Dossier canonical progress/state/counts;
- create a new scheduler/retry owner;
- run the Dossier Scheduled Task;
- modify external ChatGPT Scheduled Task settings.

## Acceptance gates
- FIX-01 primary canonical worker prompt aligned to current V2 traversal.
- FIX-02 focused anti-drift regression passes and is in the live validation surface.
- FIX-03 binding/projection refreshed canonically if required.
- FIX-04 fresh-main index/descriptor/binding consistency proven.
- FIX-05 no semantic/history/progress rewrite outside expected derived projection refresh.
- FIX-06 durable report committed to `main` and reread exactly from `main`.

## Report
Create:
`reviews/worker_reports/taste-dossier-worker-prompt-v2-alignment-fix-01.md`

Final status:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `blocked`

Keep the report compact and include exact commits/runs/bindings sufficient for Director verification.
