# WORKER TASK — PROGRESSIVE PINNED LIVE PROFILE HANDOFF FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- implementation scope is this repository only;
- the only external repository that may be read is the already-canonical Taste profile authority `kentrap2011-hub/stopgame-ratings-data`, and only the exact immutable `gaming_taste_live.json` object selected by the GitHub-owned pin/freeze route;
- do not read/change any other repository.

Task ID: `progressive-pinned-live-profile-handoff-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

## User authorization

The user explicitly authorized this implementation after recon proved that Progressive Fast and Deep execute but do not receive the canonical personalized taste content required for reproducible fit/not-fit decisions.

The user also reiterated an already-canonical operating requirement: `gaming_taste_live.json` may be updated at any time while analysis is running. The fix MUST NOT require a quiet window, profile pause, or “latest profile must stay unchanged until ingest”.

This is not a new architecture design. Reuse the previously accepted current-live-profile immutable freeze/pin model and the current ownership invariant already present in `config/execution_ownership_contract.json`.

## START

First open current `CHAT_PROTOCOL.md` from `main` and complete START gate.

Then read this task fully.

Before implementation, read only the minimum current authority needed:
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_ROUTES.md`
- `config/execution_ownership_contract.json`
- `config/mailing_policy.json`
- `config/progressive_personalization_contract.json`
- `config/progressive_pass1_contract.json`
- `config/progressive_pass2_contract.json`
- `config/progressive_pass1_worker_prompt.md`
- `config/progressive_pass2_worker_prompt.md`
- current PASS 1 / PASS 2 builders, validators, ingest/state projection code directly referenced by those contracts
- `WORKER_TASK_TASTE_CURRENT_LIVE_PROFILE_BINDING_FIX_01.md`
- `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
- `reviews/worker_reports/progressive-fast-deep-zero-completion-diagnostic-01.md`

Do not redesign unrelated Dossier, ranking, UI, scheduler or Taste business semantics.

## Architecture preflight — mandatory

Record explicit answers before edits:

1. GitHub remains the control-plane owner of scope, ordering, profile pin creation/retirement, work identity, validation, retry/recovery, persistence and completeness.
2. Scheduled ChatGPT remains semantic data-plane only.
3. Canonical live profile authority remains:
   - repository: `kentrap2011-hub/stopgame-ratings-data`
   - path: `gaming_taste_live.json`
4. The worker must never choose “whatever profile is latest” by itself.
5. GitHub must durably pin one exact immutable profile identity/content source before semantic execution.
6. An already pinned/in-flight work unit must remain valid under the current canonical ownership rule even if the live profile advances later.
7. The next newly prepared work must use the then-current live profile.
8. Arbitrary historical/unpinned/stale results remain forbidden.
9. GitHub must not perform semantic interpretation of the user profile. It may fetch/freeze/hash/copy/select exact deterministic bytes/fields only.
10. No new recurring stage, queue, scheduler, retry daemon, cache authority or semantic producer may be introduced.

If the current Progressive global-generation semantics conflict with #6, reconcile that implementation/contract drift explicitly rather than reverting to the old “profile changed -> in-flight result can never land” behavior.

## Proven defect to fix

The accepted diagnostic proved:

- current Fast/Deep work binds the profile/semantics using hashes and exact work identity;
- Fast and Deep do NOT receive/read the canonical personalized profile content;
- therefore they can prove WHICH profile is intended but cannot know WHAT the user likes/dislikes;
- Fast consequently produces almost only `analysis_incomplete / insufficient_evidence`;
- Deep has the same personalized-context gap and additionally may have thin Dossier evidence.

The primary fix is the profile semantic-content handoff. Do not “fix” zero counts by weakening outcome thresholds or validators.

## Required behavior

### A. Reuse canonical immutable live-profile freeze/pin

Implement the Progressive equivalent of the already accepted Taste rule:

`live profile -> immutable GitHub-owned pin -> exact Fast/Deep work -> semantic worker reads exact pinned profile -> result binds to same pin`

Requirements:

1. Resolve/fetch the canonical live profile deterministically.
2. Freeze exact immutable identity sufficient to reproduce the bytes used, including at minimum:
   - canonical repository;
   - canonical path;
   - immutable commit or equivalent immutable Git object identity;
   - Git blob SHA;
   - content SHA256 if used by the existing canonical freeze route.
3. The exact profile bytes/reference used by semantic execution must be auditable.
4. Do not substitute only a SHA for semantic content.
5. Prefer reusing/refactoring the existing accepted freeze/pin implementation or shared helper instead of creating a second profile-freeze architecture.
6. Do not require GitHub to “understand” or summarize the profile semantically.

### B. Profile may change at any time

Preserve the current ownership invariant:

- if profile changes before pin/freeze completes, preparation may restart from the newer exact version under the existing bounded freeze rule;
- once the Progressive work unit/profile pin is durably established, later live-profile updates MUST NOT silently mutate/mix that work unit;
- an in-flight pinned work unit remains ingest/validation-authorized according to current canonical ownership even if live profile advances later;
- the next newly created Progressive work uses the newest profile then current;
- no user quiet window;
- no unbounded profile chase/retry loop.

Add deterministic regression coverage for:
1. update before pin;
2. update after pin but before semantic result;
3. repeated churn at the freeze boundary;
4. result bound to wrong/unpinned profile;
5. next work after live-profile advance uses the new profile.

### C. Give Fast exact personalized content

Update GitHub-prepared PASS 1 work and canonical worker contract so Fast can read the exact pinned canonical profile content.

The worker must:
- read only the exact GitHub-pinned profile reference/content for that work;
- verify exact pin identity before semantic judgment;
- use that profile plus candidate semantic input and allowed lightweight evidence;
- never switch to a newer live profile mid-item;
- never infer profile content from hashes;
- never use remembered chat/user context as a substitute for the pinned profile.

Keep existing fit/not-fit/incomplete thresholds and five-factor semantics unless a separate proven contract defect requires change. This task does not authorize threshold loosening.

### D. Give Deep the same exact personalized content

Update PASS 2 work and worker contract so Deep receives/reads the same class of exact pinned personalized profile content plus its exact accepted Dossier.

Deep must:
- verify/read only the GitHub-pinned profile for its work identity;
- read only its exact prepared Dossier under existing Dossier liveness rules;
- combine personalized profile content + candidate semantic input + Dossier evidence;
- never switch profile versions mid-work;
- never choose scope/recovery itself.

Do not change Dossier evidence semantics in this task.

### E. Work identity / validation / persistence

The profile pin must be part of exact semantic work identity and validation strongly enough that:
- a result produced from different profile bytes cannot be accepted under another pin;
- a live profile update after pin does not make the already pinned work unverifiable merely because `main` advanced;
- arbitrary old results without a valid pre-semantic GitHub pin are still rejected;
- newly prepared work after profile update binds to the new profile;
- existing Fast/Deep attempt/recovery accounting cannot be bypassed by manually relabeling old results.

If implementing this requires a new pin-authority field/object or separating “live profile currentness” from “pinned work validity”, make the smallest canonical contract change and document why.

### F. Existing consumed incomplete attempts

Do NOT manually reset/rewrite the current 91+ Fast attempts or current Deep attempts.

The implementation must define the canonical transition:
- if the corrected profile handoff changes semantic identity, GitHub may create new exact work identities under normal generation logic;
- if existing identities remain consumed, recovery/re-evaluation must follow the canonical ownership model;
- no blind manual retry and no direct state deletion.

The report must state exactly what will happen to existing incomplete/error results after the fix.

## Explicit prohibitions

Do not:
- require the user to stop updating `gaming_taste_live.json`;
- make Scheduled ChatGPT read arbitrary latest `main` profile by choice;
- make GitHub semantically interpret/summarize the taste profile;
- use interactive-chat memory as production taste evidence;
- create a new profile summary AI stage;
- weaken fit/not-fit, evidence, exact-binding, Dossier or recovery validators to force completion;
- rewrite historical Fast/Deep state by hand;
- manually authorize Deep recovery;
- create/edit/enable/disable/pause/reschedule/rename/recreate any Scheduled Task;
- manually trigger Fast, Dossier or Deep production workers;
- create another queue, retry loop, scheduler or semantic producer;
- change ranking/site semantics except downstream fields strictly required by the corrected identity.

Normal existing schedules may continue independently. Do not manipulate them.

## Validation

Prove at minimum:

- PIN-01: canonical profile authority remains `stopgame-ratings-data/gaming_taste_live.json`.
- PIN-02: GitHub deterministically freezes/pins exact immutable profile identity/content before Progressive semantic execution.
- PIN-03: Fast work exposes an exact auditable pinned-profile reference/content, not only hashes.
- PIN-04: Deep work exposes the same exact pinned-profile class plus exact Dossier binding.
- PIN-05: Fast worker is contractually required to read the exact pinned profile.
- PIN-06: Deep worker is contractually required to read the exact pinned profile.
- PIN-07: update-before-pin selects/retries toward the newer profile under bounded rules.
- PIN-08: update-after-pin does not mutate/invalidate the in-flight pinned work merely because live profile advanced.
- PIN-09: no mixed-profile result can pass validation.
- PIN-10: next newly prepared work after live-profile advance uses the newer profile.
- PIN-11: arbitrary historical/unpinned result remains rejected.
- PIN-12: no user quiet window is required.
- PIN-13: no GitHub semantic taste summarization/AI stage was introduced.
- PIN-14: no Fast/Deep business threshold weakening occurred.
- PIN-15: Dossier evidence semantics are unchanged.
- PIN-16: existing attempt/recovery ownership is preserved; no manual reset/retry was introduced.
- PIN-17: relevant focused and canonical validation suites pass.
- PIN-18: PASS 1 / PASS 2 work generation and ingest/state projection remain coherent under the new pin semantics.
- PIN-19: no Scheduled Task action or manual semantic production run occurred.
- PIN-20: durable report committed and reread from fresh `main`.

### Bounded semantic-readiness proof

Without running production workers, include a deterministic fixture/test proving that a Fast/Deep worker input now has enough canonical personalized content to read at semantic time. Do not claim actual fit/not-fit quality until a later live result exists.

If natural scheduled production happens concurrently, record it as external observation only; do not depend on it for this task's acceptance unless the task can prove exact corrected pin identity.

## Durable report

Create and commit:

`reviews/worker_reports/progressive-pinned-live-profile-handoff-fix-01.md`

Include:
1. Task and architecture preflight.
2. Reused prior canonical decision and exact files/mechanism reused.
3. Root defect.
4. Exact profile pin representation.
5. Fast handoff.
6. Deep handoff.
7. Profile concurrency behavior before/after pin.
8. Work identity / validation behavior.
9. Existing attempt-state transition.
10. Exact files changed.
11. PIN-01..20.
12. Exact test/workflow/commit refs.
13. Any natural concurrent production observations clearly separated.
14. Unresolved items.
15. Final status.
16. Exactly one recommended next Director step.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `needs_user_decision`
- `blocked`

Before completion, reread the committed report from fresh `main`.
