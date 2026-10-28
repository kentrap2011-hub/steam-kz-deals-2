# WORKER TASK — Steam post-merge Actions failures fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`
Task ID: `steam-postmerge-actions-failures-fix-01`
Worker slot: **НЕ НАЗНАЧЕН — отложенная задача; до нового director assignment / sync Board+registry не запускать**

Work only in `kentrap2011-hub/steam-kz-deals-2`. If another repository opens, stop and switch. Start with `CHAT_PROTOCOL.md` and its START gate, then `CHAT_CONTEXT.md`; use relevant `PROJECT_ROUTES.md`, canonical policies and architecture preflight before any workflow/source edits.

## Authorization and scope

IMPLEMENT + bounded VALIDATE the **confirmed post-merge GitHub Actions failures** after merged PR #311, not a redesign of Steam discovery.

Observed failures on merge commit `59b5aec1310ab356dd0950171dfc8f63620b7f2d`:

1. [Validate mailing policy #40523125907](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125907): `Mailing policy invariant failure: version, projection_compares_exact_profile_blob`. At that commit `config/mailing_policy.json` says `1.22`, whereas `scripts/validate_mailing_policy.py` expects `1.21` plus an exact projection source string. Determine the proper current semantic contract and repair the consistency without weakening profile-binding validation or changing its meaning.
2. [Build offer family resolution #40523125705](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40523125705): `KeyError: 'App_1492680'` at family resolution, after content eligibility included this key but the mailing feed did not. The missing feed row was also present in the same pre-merge state, so do not blame it on PR #311. Identify the actual producer/consumer binding problem and fail closed or reconcile through the authoritative existing source; do not fabricate a price, discard an eligible key silently, or bypass family completeness.

Examine any directly consequential downstream failures from these two problems only (e.g. content eligibility/site status/visual self-check) and separate unrelated or pre-existing failures, without launching broad new diagnostics.

## Work boundaries

- Reuse existing GitHub pipelines/validators, no duplicate collector, scheduler, worker, retry/recovery loop or new validation workflow.
- Do not modify Dossier V1/V2, Deep, ITAD, unrelated production or other repository. Preserve >=50% KZ sale rule, <=4500 KZT, top-100 paid cap, full Deep candidates, and giveaway analysis beyond top-100.
- Do not manually dispatch production, rerun an unresolved existing workflow, or rewrite canonical generated state without the established GitHub-owned path.
- Implement the minimum justified code/contract/fixture changes in **one new PR** from current main. Add only targeted regression checks for the confirmed failures; let existing PR CI run normally.
- Preserve the original accepted PR #311 and #312; no rewriting merged history.

## Acceptance and handoff

- Exact failed invariants now pass under the **actual current contract**, not a hardcoded/disabled assertion workaround.
- Missing eligible/feed key path handled correctly with an explicit test, preserving full-coverage and identity requirements and downstream stability.
- Existing relevant PR checks green on exact final PR HEAD; explain any still-open live production verification separately.
- Record concise result in `reviews/worker_reports/steam-postmerge-actions-failures-fix-01.md` and in the PR description/comment, including cause, exact changes, relevant CI and remaining production limits.
- Leave PR open for Director review/merge; no independent production launch and no extra QA task unless a concrete novel risk demands one.
