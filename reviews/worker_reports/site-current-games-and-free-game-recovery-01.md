# Worker report — site-current-games-and-free-game-recovery-01

- lifecycle: `final`
- status: `failed_closed_root_cause_proven`
- final verification UTC: `2026-09-10T16:44:00Z`
- task: restore the current published site from canonical state and verify the current free-game route end to end.

## Final outcome

The original visual-build failure was diagnosed and repaired, and a real GitHub Pages deployment completed successfully. The end-to-end task is **not complete**, however, because the deployed publication is explicitly classified by its own freshness contract as `degraded/no_fresh_build`, and the giveaway source snapshot is stale after the `2026-09-10T15:00:00Z` Epic rotation. The current Epic giveaways (`Astral Ascent` and `Luftrausers`) are absent from the deployed Pages artifact.

Therefore the only valid final task status is `failed_closed_root_cause_proven`; neither complete status is justified.

## Proven root cause of the original visual build failure

- root-cause classification: `root_cause_proven`
- original failed run: `34484781975` (`Build daily visual payload`)
- original failing job: `102896254727`
- first real failing step: `Build and refresh canonical visual payload once`
- first real error: `ChatGPT production payload is not complete`
- exact defect: `scripts/build_daily_visual_payload.py::current_production_readiness()` rejected every payload whose `status` was not `complete` **before** reaching the already-intended pending-AI branch `if ai_queue_count != 0: return None, payload`.
- state at failure: the canonical production payload was validly `degraded` while the Taste/AI queue was still non-empty. In that state the pipeline is allowed to preserve existing semantic fields and perform only the bounded deterministic visual/commercial refresh. The unconditional early status check made that safe refresh path unreachable.
- the repair did not permit a degraded payload to become a full semantic publication: once the AI queue is closed, `status=complete` is still required and the path remains fail-closed.

After the primary blocker was removed, three downstream surfaces exposed the same orchestration error and were repaired without weakening their full-semantic gates:
1. `normalize_visual_media_urls.py` had unconditionally invoked the grounded-negative semantic finalizer during a pending-AI deterministic refresh;
2. `validate_card_explanations.py` had reapplied full semantic card validation to the preserved current visual during that refresh;
3. `validate_russian_descriptions.py` had reapplied full semantic Russian-description validation to the preserved current visual during that refresh.

## Repair changes and commits

Permanent recovery changes:

- `4907c3363b6b0c8b60c4cbafaeed45fe738721a0` — `fix: allow safe visual refresh while taste queue is pending`
  - repaired the early readiness gate in `scripts/build_daily_visual_payload.py`;
  - added `scripts/test_visual_degraded_refresh_readiness.py`.
- `3d21e884ab98528fe94ad0ba8cabcf2ba0bc50e9` — `fix: keep semantic finalizer out of pending-AI visual refresh`
  - gated the grounded-negative semantic finalizer in `scripts/normalize_visual_media_urls.py` to completed semantic readiness;
  - added `scripts/test_visual_normalize_pending_ai_gate.py`;
  - removed the temporary one-shot repair workflow used to apply/test this bounded change.
- `2790fd038e223e974f68eb559a12f00bdf6de8f6` — `test: cover pending-AI card validation gate`
  - added `scripts/test_validate_card_explanations_pending_ai.py`.
- `e702c271e59fd27a845a7c65a0f41fe60e7ab040` — `fix: preserve existing card semantics while taste queue is pending`
  - changed `scripts/validate_card_explanations.py` so strict semantic validation remains mandatory for completed semantic builds and arbitrary files, while the current canonical visual can preserve already-existing semantics during the bounded pending-AI refresh.
- `e18e1bc5c9ee6c291c01c4dad835d78ce89a5fac` — `test: cover pending-AI Russian description gate`
  - added `scripts/test_validate_russian_descriptions_pending_ai.py`.
- `8f66df1a0df4f82c63c2f8250ffac6477bda6af2` — `fix: preserve existing Russian descriptions while taste queue is pending`
  - changed `scripts/validate_russian_descriptions.py` with the same bounded preservation rule.
- `cbdd3de5c037be0a1d6aec62d8a817394de1859c` — `Refresh daily visual payload`
  - canonical visual refresh commit produced by the successful production build.

Focused regressions and existing giveaway/UI validation passed on the repaired path. No Taste semantic result, Taste queue/cache/overlay, Scheduled Task, or next Taste semantic batch was intentionally changed or started by this recovery task.

## Final build and deploy runs

- final build: run `34498384650` (`Build daily visual payload`) — **success**.
  - build job `102942642272` — **success**;
  - `Build and refresh canonical visual payload once` — success;
  - generated card validation — success;
  - giveaway visual validation — success;
  - Russian-description gate — success;
  - canonical payload commit and freshness-receipt creation/upload — success.
- final deploy: run `34498439445` (`Deploy visual mailing`) — **success**.
  - deploy job `102942783747` — **success**;
  - Pages artifact upload — success;
  - `Deploy to GitHub Pages` — success;
  - GitHub Pages action reported `Reported success!` at `2026-09-10T15:52:23Z`;
  - evaluated environment URL: `https://kentrap2011-hub.github.io/steam-kz-deals-2/`.

Critical qualification: during that successful deploy, binding the staged site payload to the triggering build freshness receipt produced:

`VISUAL_FRESHNESS=degraded/no_fresh_build scope=full_visual reason=visual_source_history_mismatch run_id=34498384650`

and then:

`VISUAL_PUBLICATION_OUTCOME=degraded/no_fresh_build`

So the deployment succeeded operationally, but its own freshness invariant does **not** certify the published payload as a current fresh-cycle success.

## Real published Pages result

This verification did not rely only on repository files. The exact `github-pages` artifact uploaded by deploy run `34498439445` was retrieved and inspected after the Pages deployment reported success:

- Pages artifact ID: `10160783850`
- artifact digest: `sha256:8cb65395d6b03fcd6bac3ef799f8c36b94d021a4e7784e9a52f7562c1753b215`
- deployment head SHA: `cbdd3de5c037be0a1d6aec62d8a817394de1859c`
- deployed site payload: `data/current.json`
- deployed paid/other item count: `115`
- deployed giveaway state: `unavailable`
- deployed giveaway games: `[]`
- deployed giveaway accepted-offer count at build: `0`

Representative paid/other entries present in the exact deployed Pages payload include `The Forgotten City`, `The Dungeon Of Naheulbeuk: The Amulet Of Chaos`, `Jusant`, `Mindcop`, `Röki`, `Hellslave`, `Gravity Circuit`, `Tails of Iron`, `Nobody Saves the World`, and others.

Therefore:

- was a real Pages site deployed? **Yes.** GitHub Pages created the deployment for `cbdd3de5c037be0a1d6aec62d8a817394de1859c` and reported success.
- did the non-giveaway game list make it into the deployed site package? **Yes: 115 entries are in the exact deployed Pages payload.**
- can those 115 entries be certified as the fully current publication required by the task? **No.** The deployment's own freshness binding classified the publication as `degraded/no_fresh_build` because of `visual_source_history_mismatch`.

A second independent anonymous HTTP/DOM fetch of the public Pages URL could not be completed from this execution environment because the available public-URL access path would not open this unindexed Pages host and the container has no external DNS/network route. The proof above is therefore the actual GitHub Pages deployment service result plus the exact artifact that service deployed, not a separate browser-origin fetch.

## Current free-game truth and published result

The repository's canonical giveaway snapshot is stale:

- file: `data/production/giveaways/v1/current.json`
- generated: `2026-09-08T20:46:17.374139Z`
- `fresh_until_utc`: `2026-09-10T02:46:17.374139Z`
- it still records `Alone With You` with promotion end `2026-09-10T15:00:00Z`.

At final verification time (`2026-09-10T16:44Z`), `Alone With You` was no longer the current giveaway. Current external Epic giveaway state was cross-checked after the rotation: there are **two** current free games for the new `2026-09-10` → `2026-09-17` window:

1. `Astral Ascent`
2. `Luftrausers`

The current public sources report both as the new Epic weekly giveaways beginning September 10, and current community deal verification reports no regional restriction for either. Under the project's giveaway business rules they are the current entries that should be represented once the canonical giveaway source is refreshed and validates them for KZ.

Published result:

- `Alone With You`: correctly absent after its `15:00Z` expiry.
- `Astral Ascent`: **absent** from the deployed giveaway block.
- `Luftrausers`: **absent** from the deployed giveaway block.
- exact deployed giveaway block: `state=unavailable`, `games=[]`.

Thus the current free-game requirement of the original task is **not satisfied**.

## Remaining unresolved items

1. **Giveaway source freshness is unresolved.** The canonical `CROSS-PLATFORM-GIVEAWAY-V1` snapshot was already stale before the September 10 rotation and did not refresh to the new `Astral Ascent` + `Luftrausers` window. The exact producer/scheduling cause of that stale snapshot was not changed or investigated further during this report-only finalization.
2. **Publication freshness binding is unresolved.** Deploy run `34498439445` successfully published Pages, but the exact staged payload failed fresh-build binding with `visual_source_history_mismatch`; the published result is explicitly degraded by the project's own contract.
3. **Independent public HTTP/DOM re-fetch is unavailable from this worker environment.** Pages deployment success and the exact deployed artifact are verified, but a second origin fetch could not be performed here.

Because items 1 and 2 are production correctness failures, Taste backlog work should **not** be treated as resumed by this report. No new Taste work was started.

## Final lifecycle/status

- lifecycle: `final`
- status: `failed_closed_root_cause_proven`
- complete-site status intentionally not used: current giveaways are active but missing, and publication freshness is degraded.
