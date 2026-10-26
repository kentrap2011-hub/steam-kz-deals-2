# Worker report — Steam discount >=50%, rolling top-100

**Task:** `WORKER_TASK_STEAM_DISCOVERY_50_PERCENT_DISCOUNT_TOP100_IMPLEMENT_01.md`  
**Worker:** physical ЧАТ 1  
**Repository:** `kentrap2011-hub/steam-kz-deals-2`  
**Date:** 2026-10-26  
**Base main:** `6709956d5dc1d5b729d48de42ca727d33c149f16`  
**Branch:** `implement/steam-discovery-50-top100-01`  
**PR:** [#311](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/311) (DRAFT, unmerged)

## Status: PARTIAL / NOT ACCEPTED — do not merge or activate

The requested full implementation has **not** been delivered. This report explicitly separates completed code from unverified and unimplemented requirements.

### Completed source changes

1. **Deep operational queue priority** — `config/progressive_pass2_work_order_policy.json` owns the strict ordering of previously never-completed Deep work: descending existing deterministic commercial purchase score, descending current Steam global positive percent, descending current review count, then exact family ID. `scripts/build_progressive_pass2_work.py` consumes it. Existing never-analyzed-first / historical oldest-success ordering remains, scope and exact bindings are preserved, no raw/intermediate top-N, no expiry signal. `config/progressive_pass2_worker_prompt.md` untouched.
2. **Rolling visible cap** — `config/mailing_policy.json#visible_paid_publication` and `scripts/build_final_visual_payload.py` apply hard visible cap 100 only after full canonical family/package processing, refinement and `priority_rank` calculation. Full Deep status is computed **before** slicing. When a canonical full visual build runs again, newly accepted Deep results can reshuffle the visible 100. Canonical source gate remains 50% discount / <=4500 KZT, and published paid rows are checked.
3. **Commercial-only refresh** — applies the same visible cap to production-bound snapshots and preserves last full Deep scope counts; generic helper scoring without a production binding is not prematurely treated as site publication.
4. **Observed funnel / Statistics** — source-manifest rows and parsed/rejected/eligible counts are attached only when the complete manifest's exact timestamp matches the visual's source; partition and rejection counts must reconcile. Independent full internal-ranked / capped-visible / hidden-below-cap counters are exposed in the UI Statistics, without inventing numbers for old snapshots.
5. **Regressions** — `scripts/test_semantic_queue_priority.py` expanded with strict work-order, >100 full-scope and expiry-invariance checks. `scripts/test_visible_paid_offer_limit.py` adds bounded visible cap, strict KZ price/discount, Deep scope, stale-source/funnel reconciliation and giveaway isolation fixtures. Existing `steam-test.yml` PR-only regression runs these tests. No new scheduled job.

### Outstanding task checklist / blockers

- **Stage 1/2:** canonical early paid/source gates and existing review/quality reuse were already present; the requested **new validated obscure-low-signal early rejection with exceptional-value/quality escape** is not implemented. It must not silently discard candidate games merely on unverified search-review counts.
- **Stage 3:** **not implemented**. Existing production discovery still traverses global `category1=21` DLC. Safest verified base→DLC relation and efficient price lookup path must be demonstrated on live KZ rows before replacing full traversal. Owned-library DLC expansion remains a separate follow-up task.
- **Stage 4:** **not implemented**. Existing `Sub_` preservation in games partition and existing fixed-package purchase-option scoring remain, but independent on-sale packages whose qualifying member games are not on sale and the explicit 5-middling-games/cheap-bundle regression are missing. `category1=996` was previously proven broad/untyped, so no speculative standalone crawl was introduced.
- **Stage 5:** operational Deep work order and post-ranking cap implemented, but no actual production acceptance / site deployment. Existing source-side Deep-first positive fit priority is retained.
- **Stage 6:** only preexisting collector funnel + source-bound observation + final cap counters. Missing major counts: obscure rejects, admitted bases, eligible-base DLC identities/accepted/rejected, independent bundle counts/content and final family reductions.
- **Live acceptance:** source-bound live KZ Steam relation/package probes and one ordinary full production run against updated `main` **not performed**. PR-only CI exercises synthetic code and legacy regressions, **not** a normal production `collect` (explicitly disabled for PRs). A previously accepted main manifest records a completed collection, but that is not acceptance evidence for this proposed branch.
- **Cross-chat boundary:** no Dossier V2, giveaways identity provider, Director Board/registry or scheduler edits; no main write or semantic worker run.

### Validation and limitations

- Existing source owner: `scripts/steam_partial_publish_runner.py` and `scripts/steam_production.py`, untouched. Existing ranking owner: `scripts/progressive_personalization.py` and `scripts/priority_ranking.py`, untouched. This worker did not create competing collectors/semantic queues/scheduled automations.
- Evidence from PR workflow: first revision exposed a generic scoring-fixture missing KZ price (package validator); fixed by separating scoring-only use from bound paid publication. A later source-funnel assertion exposed an inconsistent prefixed metric name; corrected. Check **final exact PR HEAD** Actions before treating CI as green.
- Steam storefront appdetails relation and package probing could not be established with trustworthy current live responses in this interactive environment; no inferred live semantics or source-completeness claims were made.
- Next authorized operation should be **bounded live STEAM KZ SOURCE RECON** of the game/appdetails→DLC relationship, on-sale bundle/contents and regional price endpoints, then focused implementation of stages 1,3,4,6 in the existing collector, regression for five middling games, full production acceptance on merged main after review. Do not dispatch a second collector or silently widen/source-cross other worker tasks.

### Operational improvements

The dedicated machine-readable `config/progressive_pass2_work_order_policy.json` removes future changes to Deep worker prompts for sorting; PR-only focused regression tests make visual/Deep scope boundary repeatable. Source-bound funnel guard reports only exact-current complete evidence and avoids debugging stale cross-run numbers. Existing route `PROJECT_ROUTES.md#Steam KZ discovery` identifies owner and check locations; future route extension should add the new policy/test/visual cap references after fully accepted product implementation.
