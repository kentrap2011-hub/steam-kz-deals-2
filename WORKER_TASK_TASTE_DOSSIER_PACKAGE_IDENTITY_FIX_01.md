# WORKER TASK — Taste Dossier Package Identity Fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If a tool opens another repository by default, stop and switch back to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-package-identity-fix-01`
Mode: `IMPLEMENT`

## Goal
Fix the concrete live-acceptance blocker where a package/bundle-backed Taste offer enters dossier work with mismatched identity, e.g. offer key `Sub_87601` / title `Resident Evil Deluxe Origins Bundle / Biohazard Deluxe Origins Bundle` combined with appid `304240`.

The fix must preserve bundles/packages as valid discount offers shown to the user. Only the identity passed into the game-review dossier layer should be corrected or fail-closed before semantic research.

## Read first
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- relevant `PROJECT_ROUTES.md`
- relevant `PROJECT_DECISIONS.md`, especially `TASTE-007`
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-01.md`
- `reviews/worker_reports/taste-dossier-web-evidence-redesign-01.md`
- `reviews/worker_reports/taste-dossier-web-evidence-activation-recovery-01.md`
- current Taste queue/work builders and identity contracts
- `config/execution_ownership_contract.json`

Run architecture preflight before changes.

## Required product invariant
Do **not** solve this by removing `Sub_...`, bundle, package, deluxe-edition, collection, or multi-item offers from the discount product surface.

Preserve the distinction:
- store offer / discount entity may be a package or bundle and must remain eligible for display;
- dossier research identity must refer to one unambiguous game/release entity, or the item must be marked ineligible for a single-game dossier before reaching the semantic worker.

The offer itself must not disappear merely because dossier research cannot map it to one game.

## Required investigation within scope
Trace the exact current path that produced the mismatch for `Sub_87601` / appid `304240` and establish which field belongs to the store offer versus which field is being used as the dossier game identity.

Then implement the narrowest durable fix so the dossier work builder never emits a hybrid identity such as package title + unrelated/single contained appid.

Acceptable outcomes by case:
- if one canonical game identity is deterministically and safely associated with the offer, emit that exact game title/appid plus release-year-resolvable identity for dossier research while preserving original offer metadata separately;
- if a package contains multiple independent games and there is no single canonical game identity, do not guess or select the first app; keep the offer in discounts but exclude/fail-closed only from the single-game dossier work layer;
- if mapping is ambiguous, fail before Scheduled ChatGPT, with a machine-readable reason suitable for diagnostics.

Do not broaden this task into full handling of every possible Steam package type; the separate recon task covers analogous cases.

## Tests / acceptance for implementation
Add regression coverage proving at least:
- the concrete `Sub_87601`-style mismatch cannot be emitted again;
- bundle/package offer remains present in the product/discount-side fixture or equivalent tested surface;
- single-game package mapping, if supported, produces consistent title/appid identity;
- multi-game/ambiguous package does not fabricate a single-game identity;
- ordinary app-backed Taste rows remain unchanged;
- V2 title/appid/release-year identity contract remains compatible;
- no invalid dossier progress is advanced.

Run the relevant deterministic suites.

## Production restrictions
- Do not press Scheduled Task `Run now`.
- Do not edit Scheduled Task UI.
- Do not manually dispatch production workflows.
- Do not merge an implementation PR if merge would trigger production side effects; leave it ready for Director activation instead.
- Do not change Taste Semantic Producer.
- Do not filter bundle/package offers out of the user-visible discounts pipeline as a shortcut.

## Deliverable
Prepare the implementation in a branch/PR with tests green, but leave activation/merge to a separate Director-authorized step if production side effects would occur.

Publish durable report to `main`:
`reviews/worker_reports/taste-dossier-package-identity-fix-01.md`

Report must include:
- architecture preflight;
- root cause of the concrete mismatch;
- exact separation between offer identity and dossier game identity;
- files changed;
- proof discount bundles/packages are not lost;
- test results;
- PR/commit refs;
- production side effects not performed;
- exactly one next step.

Allowed final statuses:
- `complete_ready_for_activation`
- `blocked`

Do not change `CURRENT_TASK.md` unless protocol explicitly requires it for this task.
Stop after the durable report.