# WORKER TASK — Taste Dossier Review Source Recon 01

Task ID: `taste-dossier-review-source-recon-01`
Mode: `READ-ONLY / RECON`

## Goal
Determine one reliable, repeatable, production-usable way for the live Scheduled Task to obtain actual Steam review bodies for dossier generation.

This is now the first priority before schema/evidence repair implementation. Do not redesign dossier semantics around zero-review/store-only output until this source question is answered.

## Why this task exists
The full defect sweep proved that:
- groups 1 and 2 were published with zero sampled review bodies;
- group 3 stopped because review bodies were not available through the surface the worker used;
- many affected games have thousands of Steam reviews, so source sparsity is not the real issue;
- therefore the current bottleneck is how the live Scheduled Task actually retrieves review text.

We need to know the exact production source path before deciding evidence semantics.

## START gate
Read fully:
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- this task
- relevant `PROJECT_DECISIONS.md`
- `reviews/worker_reports/taste-dossier-full-defect-sweep-01.md`
- `reviews/worker_reports/taste-dossier-live-compact-acceptance-01.md`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/execution_ownership_contract.json`
- current compact worker index and a representative descriptor set.

Run architecture preflight before recommending any new source or control-plane mechanism.

## Core question
What exact source/interface can the Scheduled Task use to reliably retrieve individual Steam review bodies, including Russian reviews when available and non-Russian reviews when useful, for arbitrary appids in the dossier backlog?

The answer must be production-specific, not theoretical.

## Required source investigation
Evaluate and compare all realistically available paths that could work from the Scheduled Task environment, including where applicable:

1. Official/public Steam review endpoints or APIs that return individual review text.
2. Steam store/review pages or review feeds addressable directly by appid.
3. Web search surfaces that expose review snippets/bodies reliably enough for production use.
4. Any existing repository/plugin/connector/runtime capability already available to the Scheduled Task that can fetch review bodies.
5. If the Scheduled Task itself cannot reliably fetch them, whether GitHub can deterministically prepare a small review-evidence artifact for the worker without transferring semantic/control-plane ownership away from GitHub.

Do not assume any option works until demonstrated.

## Required live-like proof
Without using the Scheduled Task `Run now`, perform bounded read-only verification against at least these representative appids from group 3:
- `1158890` White Shadows
- `1164940` Trepang2
- `1169040` Necesse
- `1172380` STAR WARS Jedi: Fallen Order

For each candidate source, determine whether you can retrieve actual individual review bodies, not merely aggregate counts/ratings.

Where possible verify:
- review text body;
- recommendation polarity;
- language or ability to request/filter language;
- review identifier or stable source reference;
- timestamp/date;
- pagination/cursor behavior;
- whether Russian reviews can be requested specifically;
- whether non-Russian fallback is practical;
- whether source output is bounded/repeatable enough for adaptive sampling up to the current contract ceilings;
- whether access requires authentication, cookies, unsupported scraping, or unstable browser state.

Do not collect huge corpora. A few reviews per appid are enough to prove source capability.

## Production suitability criteria
A recommended source must be assessed on:
- works for arbitrary current backlog appids;
- returns actual review text;
- supports RU-first sampling or at least language identification;
- supports pagination/adaptive sampling;
- source identity/provenance can be persisted compactly;
- no user interaction per game;
- no manual browser/UI steps;
- no secrets that the Scheduled Task cannot safely access;
- no dependence on fragile visual scraping if a structured source exists;
- compatible with GitHub-owned scope/order/control plane;
- realistic for hundreds of games over repeated invocations.

## Important architecture distinction
Separate these cases clearly:

A. **Scheduled Task can directly retrieve review bodies reliably.**
Then recommend the exact endpoint/tool call strategy and what prompt/contract changes are needed.

B. **Scheduled Task cannot, but GitHub/runtime can prepare review evidence automatically.**
Then describe an architecture where GitHub remains control plane and prepares bounded review-evidence artifacts that the Scheduled Task reads. Do not implement; only assess viability and ownership.

C. **No reliable automated source is available in the current environment.**
Say so explicitly. Do not paper over this with store-only dossiers.

## Steam/public endpoint specifics
If an official/public Steam endpoint is viable, document precisely:
- endpoint shape;
- required parameters;
- language/filter parameters;
- pagination/cursor semantics;
- practical per-call sample sizes;
- fields returned that can support dossier provenance;
- observed behavior for the representative appids;
- any rate-limit/availability caveats you can actually evidence.

Do not invent undocumented guarantees.

## Russian-review requirement
The dossier contract treats Russian reviews as a required attempt.

Determine exactly how a production source can:
- request Russian reviews directly; or
- reliably identify/filter Russian reviews after retrieval.

Also determine what should happen when a game genuinely has no Russian reviews but does have non-Russian reviews. This task should describe the source behavior, not yet redesign the dossier schema.

## Output decision
The report must end with exactly one of these recommendations:
- `direct_scheduled_worker_source_recommended`
- `github_prepared_review_evidence_recommended`
- `no_reliable_source_available_currently`

If direct source is recommended, provide the exact retrieval recipe that a future IMPLEMENT/prompt task can adopt.

If GitHub-prepared evidence is recommended, define the smallest architecture change needed and why direct Scheduled Task access is insufficient.

## Prohibitions
- READ-ONLY / RECON only.
- No repository runtime/config/code changes.
- No Scheduled Task UI inspection/edit.
- No `Run now`.
- No manual GitHub workflow dispatch.
- No production inbox/cache mutation.
- No Taste Semantic Producer changes.
- No bulk review harvesting.
- No credentials/secrets added or requested from the user unless the recon proves they are strictly necessary; report first instead.

## Durable report
Write to `main`:
`reviews/worker_reports/taste-dossier-review-source-recon-01.md`

Report must include:
- architecture preflight;
- candidate sources investigated;
- exact representative appid tests and what each returned;
- proof whether actual review bodies were obtained;
- RU-review capability;
- pagination/adaptive-sampling capability;
- provenance fields available;
- operational constraints/rate-limit/auth caveats;
- direct-worker vs GitHub-prepared comparison;
- one recommended production source/path;
- exact next IMPLEMENT scope if viable;
- one next step only.

Allowed final statuses:
- `recon_complete_source_selected`
- `blocked`
- `no_reliable_source_available`

Stop after durable report.