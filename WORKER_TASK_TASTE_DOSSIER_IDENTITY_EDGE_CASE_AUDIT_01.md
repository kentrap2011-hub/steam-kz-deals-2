# WORKER TASK — Taste Dossier Identity Edge-Case Audit 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If a tool opens another repository by default, stop and switch back to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-identity-edge-case-audit-01`
Mode: `READ-ONLY / RECON`

## Goal
Search systematically for other identity-shape problems similar to the live `Sub_87601` bundle/app mismatch before they block future V2 dossier groups.

This task must not implement fixes. It should identify classes of problematic rows, quantify them where practical, and recommend bounded follow-up categories.

## Read first
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- relevant `PROJECT_ROUTES.md`
- relevant `PROJECT_DECISIONS.md`, especially `TASTE-007`
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-01.md`
- current Taste queue/work builder contracts and identity fields
- current snapshot/index/descriptors needed for bounded audit
- `config/execution_ownership_contract.json`

Run architecture preflight.

## Audit scope
Inspect the current prepared Taste/dossier population and the upstream identity mapping sufficient to find analogous cases such as:
- `Sub_...` / packages;
- bundles/collections/franchise packs;
- deluxe/gold/complete/GOTY editions where store-offer title may not equal base-game identity;
- remasters/remakes/re-releases with same or similar titles;
- DLC/season passes/soundtracks/tools accidentally mapped to a base-game appid;
- package title + contained appid hybrids;
- one offer containing multiple independent games;
- duplicated appids under materially different offer titles;
- same title mapped to multiple appids/years where V2 could confuse releases;
- appid/title pairs that cannot plausibly resolve to one release year;
- other entity-type mismatches that can cause V2 fail-closed identity rejection.

Use a bounded but broad-enough audit. Prefer checking the entire current prepared identity set if cheap; otherwise state exact sample/coverage and why it is sufficient.

## Product invariant
Do not classify package/bundle offers themselves as erroneous merely because they are not single games.

The question is whether the **dossier identity layer** receives a coherent single-game identity. User-visible discount offers, including bundles/packages, must remain valid product entities.

Distinguish clearly:
1. valid store offer that can map safely to one game dossier;
2. valid store offer that represents multiple games and should not be forced into one dossier;
3. malformed/hybrid identity mapping;
4. non-game content accidentally entering the game-dossier layer;
5. ambiguous release/version identity needing explicit handling.

## Required output
Produce a compact taxonomy with, for each discovered class:
- example keys/titles/appids;
- count or bounded prevalence estimate;
- whether it can block V2 Scheduled Task before group publication;
- whether it risks wrong-review attribution rather than fail-closed stopping;
- likely owner/layer of the correction;
- whether the current package-identity fix task is expected to cover it or a separate fix is needed.

Pay special attention to rows appearing early in upcoming groups, because one invalid item blocks the whole group artifact.

## Restrictions
- READ-ONLY except durable report publication.
- Do not edit queue builders, validators, prompts, schemas, data, recovery state, or production artifacts.
- Do not press Scheduled Task `Run now`.
- Do not dispatch workflows.
- Do not change Taste Semantic Producer.
- Do not create fixes or PRs.
- Do not inspect or use any other repository.

## Durable report
Publish to `main`:
`reviews/worker_reports/taste-dossier-identity-edge-case-audit-01.md`

Report must include:
- architecture preflight;
- audit coverage;
- taxonomy of discovered identity edge cases;
- representative examples/counts;
- which are immediate blockers vs correctness risks;
- which are covered by the separate package-identity fix and which are not;
- prioritized bounded follow-up tasks, without implementing them;
- exactly one recommended next step for Director.

Allowed final statuses:
- `complete`
- `blocked`

Do not change `CURRENT_TASK.md`.
Stop after durable report.