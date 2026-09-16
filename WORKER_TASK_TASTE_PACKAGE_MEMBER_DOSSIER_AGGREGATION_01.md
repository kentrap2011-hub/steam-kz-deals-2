# WORKER TASK — Taste Package Member Dossier Aggregation 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If a tool opens another repository by default, stop and switch back to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-package-member-dossier-aggregation-01`
Mode: `IMPLEMENT`

## Context
This is a direct continuation/correction of PR `#31` from `taste-dossier-package-identity-fix-01`.

The previous package fix correctly proved that a hybrid identity such as `package title + one contained appid` is invalid. However, the product rule has now been clarified:

- multi-game packages/collections must not be discarded merely because they contain several games;
- package Taste should be driven by the member games, not by averaging the package into one fake game identity;
- if at least one member game is a sufficiently good Taste match, the package remains eligible at the Taste stage;
- weak member games must not mathematically drag down a strong member game by simple averaging;
- quality problems of the specific package/remaster/edition are a separate signal and must NOT hard-exclude the package at this stage; that signal is handled by a separate RECON task;
- bundle/package offers remain valid discount products and must not disappear from the commercial/UI surface.

DLC rule for this task: do not change DLC behavior. DLC is currently evaluated as its own product/dossier. Final-list handling of DLC is outside this task.

## Read first
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- relevant `PROJECT_ROUTES.md`
- relevant `PROJECT_DECISIONS.md`, including `TASTE-007`
- `WORKER_TASK_TASTE_DOSSIER_PACKAGE_IDENTITY_FIX_01.md`
- `reviews/worker_reports/taste-dossier-package-identity-fix-01.md`
- `reviews/worker_reports/taste-dossier-identity-edge-case-audit-01.md`
- current PR `#31` state/branch
- current Taste/package/dossier contracts and canonical package-member fields
- `config/execution_ownership_contract.json`

Run architecture preflight before implementation.

## Required product behavior
For a multi-game package or collection with authoritative member identities:

1. Preserve the package/offer as the commercial entity.
2. Expand the package into its authoritative member-game identities for dossier/Taste purposes.
3. Create or reuse one dossier per distinct member game appid; do not fabricate a package-level single-game dossier.
4. Reuse/dedupe an existing dossier for the same member appid instead of researching it again.
5. Preserve a durable mapping from the package offer to the member game identities used for Taste.
6. Package Taste eligibility must follow the best qualifying member signal rather than a simple average across all members: one strong qualifying member is sufficient to keep the package in consideration at the Taste stage.
7. Weak/nonmatching member games must remain visible in the package composition but must not cancel a strong qualifying member merely because the package contains them.
8. Do not yet introduce a hard exclusion based on package/remaster/edition quality. That is a separate signal under RECON.

Example intent:
A package equivalent to `GTA: The Trilogy – Definitive Edition` must not be rejected just because one member such as GTA III is a weak fit or because the package itself has a poor reputation. If Vice City or San Andreas is a strong fit, the package survives Taste-stage eligibility. Quality problems of the Definitive Edition must later be represented as a strong negative score/warning, not as a Taste hard-exclude.

## Package identity invariants
- Never emit `package title + one contained appid` as though it were one game.
- Never choose the first package member as the package's game identity.
- Use only authoritative package/member mappings already owned by GitHub; no fuzzy title guessing.
- If authoritative member composition is unavailable or ambiguous, fail closed for member expansion with a machine-readable reason, while preserving the offer itself.
- A package member that is also independently present elsewhere in the Taste/dossier scope must resolve to the same canonical dossier identity.

## PR #31 correction
Revise PR `#31` in place if practical rather than creating a competing package-fix PR.

The prior behavior that places a multi-game package into `identity_blocked_items` solely because it has multiple base games is no longer the desired final behavior when authoritative member identities are available. Replace that bounded behavior with member expansion/reuse while retaining all protection against hybrid identities.

If current architecture makes full Taste aggregation inappropriate inside PR #31, stop and report the exact ownership conflict instead of inventing a second control plane.

## Tests / acceptance
Add deterministic regression coverage proving at minimum:
- `Sub_87601` can no longer shadow `App_304240` or emit a hybrid descriptor;
- a multi-game package with two authoritative members produces/reuses the correct two member dossier identities;
- duplicate member appids are researched once and reused;
- a package with one strong member and one weak member remains Taste-eligible based on the strong member rather than an average;
- weak members remain represented in package composition/explanation;
- no member identity is fabricated when authoritative mapping is missing;
- the package offer remains present on the discount/commercial side;
- ordinary single-game App rows remain unchanged;
- DLC behavior is unchanged;
- no invalid dossier progress/checkpoint advancement occurs.

Run relevant deterministic suites and PR validation.

## Production restrictions
- Do not merge PR #31.
- Do not press Scheduled Task `Run now`.
- Do not edit Scheduled Task UI.
- Do not manually dispatch production workflows.
- Do not modify Taste Semantic Producer.
- Do not rebuild or mutate production queue/cache/receipts manually.
- Do not implement package/edition-quality penalties in this task.

## Durable decision
Record the clarified package-Taste rule in the appropriate durable project decision/rule surface if protocol permits: package member games are evaluated independently; at least one qualifying member keeps the package alive at Taste stage; member weaknesses are not averaged into hard exclusion; package/edition quality is a separate later scoring/warning signal.

## Deliverable
Update implementation/PR and publish durable report to `main`:
`reviews/worker_reports/taste-package-member-dossier-aggregation-01.md`

Report must include:
- architecture preflight;
- how PR #31 changed from the previous blocked-multi-game behavior;
- exact package → member dossier mapping model;
- exact Taste aggregation rule used;
- proof commercial package offers are preserved;
- proof DLC behavior is unchanged;
- tests and CI refs;
- PR/head refs;
- production side effects not performed;
- exactly one next step.

Allowed final statuses:
- `complete_ready_for_activation`
- `blocked`

Stop after durable report.