# Worker report — site-giveaway-and-freshness-recovery-02

- lifecycle: `final`
- status: `failed_closed_root_cause_proven`
- started UTC: `2026-09-10T17:10:00Z`
- final verification UTC: `2026-09-10T18:38:00Z`
- task: restore canonical giveaway refresh, repair publication freshness binding, rebuild/deploy, and verify the exact published Pages artifact.
- boundary: no Taste queue/cache/overlay/Scheduled Task work was started; no new Taste semantic batch was started.

## Final outcome

The task is **not complete**. The originally observed `visual_source_history_mismatch` classification defect was repaired and regression-tested, but the live end-to-end publication chain did not reach a fresh build/deploy because the canonical production owner still fails during the mutable Steam catalog traversal before it reaches the giveaway producer.

Consequences at final verification:

- canonical giveaway snapshot is still stale;
- current Epic giveaways `Astral Ascent` and `Luftrausers` are absent from canonical state;
- there is no new fresh visual payload build;
- latest freshness receipt is still `degraded/no_fresh_build`, now for `upstream_prerequisite_not_ready` rather than `visual_source_history_mismatch`;
- there is no new Pages deploy after the recovery attempt;
- the exact currently published Pages artifact still contains 115 ordinary games but neither current giveaway.

## Repairs already landed before final verification

### Permanent code repair

Commit:

- `eba9492af7c9e1cf9d8274c2912147877d78348c` — `fix: recover giveaway source and freshness classification`

This commit:

1. added bounded Steam traversal reconciliation support in `scripts/steam_traversal_recovery.py` and its regression test;
2. changed `scripts/steam_production.py` from a two-pass recovery to a maximum three-pass bounded reconciliation while retaining strict fail-closed completeness;
3. changed `scripts/visual_freshness_receipt.py` to capture semantic/Taste queue state and prevent a deterministic refresh that intentionally preserves accepted semantic history from falsely claiming full semantic freshness;
4. added regression coverage for that freshness classification.

Focused helper run `34508513922` completed successfully. The Steam traversal recovery test, visual freshness receipt tests, cross-platform giveaway tests, and giveaway visual handoff tests all passed before the permanent commit was pushed.

### Production-owner CI integration

Commit:

- `113fa2ac51624cba3d43aeb47ece653c48999c5c` — `ci: validate bounded Steam traversal recovery`

This added the new traversal helper/test to `.github/workflows/steam-test.yml` path ownership and regression execution so future collector changes exercise the bounded-recovery regression automatically.

Current `main` immediately before this report-only finalization was:

- `31e6df0cff908797643f1d3a074212c120aa7d9b` — `ci: dispatch visual refresh after production update`

No production code/workflow repair was started during this finalization pass.

## Canonical giveaway snapshot — final state

File:

`data/production/giveaways/v1/current.json`

Final repository state is unchanged from the stale pre-rotation snapshot:

- contract: `CROSS-PLATFORM-GIVEAWAY-V1`
- `generated_at_utc`: `2026-09-08T20:46:17.374139Z`
- `fresh_until_utc`: `2026-09-10T02:46:17.374139Z`
- `snapshot_status`: `complete` for that old observation only
- accepted game: `Alone With You`
- its Epic promotion ended at `2026-09-10T15:00:00Z`
- `Astral Ascent`: absent
- `Luftrausers`: absent

Therefore the canonical snapshot **did not update** after the 2026-09-10 Epic rotation.

Independent current-store verification on 2026-09-10 confirms the new Epic rotation is `Astral Ascent` and `Luftrausers` for Sep 10–17. They are real current giveaways, not a legitimate no-giveaway state.

## Canonical production owner — latest run and proven remaining root cause

Workflow:

`Steam KZ production shortlist`

Latest recovery run:

- run ID: `34508649895`
- head SHA: `113fa2ac51624cba3d43aeb47ece653c48999c5c`
- job ID: `102976972787`
- conclusion: `failure`
- first failing step: `Collect full Steam KZ catalog and build production shortlist`

All regression steps before the live crawl passed, including:

- Steam traversal recovery regression;
- production output ownership regression;
- cross-platform giveaway regression (`23` tests);
- giveaway IGDB identity probe (`8` tests).

The live collector then proved that the remaining problem is not merely a one-item end-of-run race. The Steam search result set was mutating throughout the offset-paginated traversal:

- first `Name_ASC` pass ended non-exact: `17712 / 17730`;
- the `Name_DESC` recovery pass changed the merged union to `17733 / 17730`;
- a third bounded `Name_ASC` reconciliation pass ran;
- source totals continued moving during that pass (`17730`, `17732`, `17733`, etc.);
- final strict check failed with:
  - `Full Steam traversal completeness check failed: unique=17734 reported=17732`

The giveaway build step and giveaway contract validation were therefore skipped, so no new canonical giveaway snapshot could be committed.

### Proven root cause

The collector is trying to prove exact completeness by unioning multiple **live offset-paginated traversals of a changing catalog** and comparing that union to an instantaneous reported total. Those values do not describe one coherent source snapshot. When catalog membership changes between pages/passes, the union can both miss rows and contain rows that are no longer part of the final reported total. Adding one more bounded pass cannot make that proof valid; it only samples another moving state.

The collector correctly fails closed instead of publishing an unproven commercial snapshot, but because canonical giveaway production is sequenced after this long commercial crawl in the same job, current Epic/GOG giveaway refresh is also blocked by an unrelated Steam commercial completeness failure.

### Minimal next step — not executed in this finalization

Separate canonical giveaway production from the full Steam commercial crawl so `scripts/giveaway_production.py` can refresh and commit the strict `CROSS-PLATFORM-GIVEAWAY-V1` artifact independently before/without waiting for commercial Steam traversal completeness. Keep the Steam commercial collector fail-closed. Then replace the commercial traversal's multi-pass live-union completeness proof with a coherent-snapshot criterion (stable source cursor/snapshot if available, otherwise acceptance only after repeat end-to-end observations prove the same exact ID set/total).

No such new repair was started because this pass was explicitly restricted to final verification/report finalization.

## Latest visual build / freshness result

Latest downstream workflow:

- workflow: `Build daily visual payload`
- run ID: `34514010056`
- head SHA: `31e6df0cff908797643f1d3a074212c120aa7d9b`
- workflow conclusion: `success`

This **was not a successful fresh visual build**. The workflow succeeded only in recording a fail-closed no-build receipt:

- `scope`: success
- `giveaway_refresh`: skipped
- `build`: skipped
- `commercial_refresh`: skipped
- `no_build_receipt`: success

Its upstream prerequisite was:

- `Build pre-AI deterministic payload`
- run ID: `34514004016`
- conclusion: `skipped`

Freshness receipt:

- artifact ID: `10166930106`
- artifact name: `visual-freshness-receipt`
- digest: `sha256:e0612d688ddfa3941585eb9852a1dd6f9c3f62604a0796cb197efa1a8a6adb02`
- receipt result: `fresh_build=false`
- freshness scope: `full_visual`
- publication outcome: `degraded/no_fresh_build`
- reason: `upstream_prerequisite_not_ready`

### `visual_source_history_mismatch` status

The exact old reason `visual_source_history_mismatch` is **not present in the latest receipt**. The classification defect that produced it was repaired in `eba9492af7c9e1cf9d8274c2912147877d78348c` and its regression tests pass.

However, this cannot be counted as a successful live freshness acceptance: the latest chain never executed a fresh visual build because the upstream production prerequisite failed. Therefore `degraded/no_fresh_build` has **not disappeared overall**; only its current reason changed from the old history mismatch to `upstream_prerequisite_not_ready`.

## Deploy status

No new `Deploy visual mailing` run occurred after the latest recovery chain. Therefore there is no new successful publication to certify.

The last successful deploy remains the pre-recovery deployment:

- deploy run ID: `34498439445`
- workflow: `Deploy visual mailing`
- conclusion: `success`
- head SHA: `cbdd3de5c037be0a1d6aec62d8a817394de1859c`
- deployment artifact: `github-pages`
- Pages artifact ID: `10160783850`
- artifact size: `172003` bytes
- artifact digest: `sha256:8cb65395d6b03fcd6bac3ef799f8c36b94d021a4e7784e9a52f7562c1753b215`

## Exact currently published GitHub Pages artifact verification

The exact `github-pages` ZIP from deploy run `34498439445`, artifact `10160783850`, was downloaded again during final verification. Its `artifact.tar` contains `./data/current.json`.

Exact deployed payload state:

- payload status: `degraded`
- `generated_at_utc`: `2026-08-31T18:09:11.137550+00:00`
- ordinary `items`: `115`
- giveaway state: `unavailable`
- giveaway `accepted_offer_count_at_build`: `0`
- giveaway `games`: `[]`
- `Astral Ascent`: absent
- `Luftrausers`: absent

Ordinary games are still present. Representative entries in the exact artifact include:

- `The Forgotten City`
- `The Dungeon Of Naheulbeuk: The Amulet Of Chaos`
- `Jusant`
- `Mindcop`
- `Röki`
- `Hellslave`
- `Gravity Circuit`
- `Tails of Iron`
- `Nobody Saves the World`
- `Nocturnal`
- `Car For Sale Simulator`
- `Celeste`
- `Saviorless`
- `TowerFall Ascension`
- `Somber Echoes`

Its commercial-only freshness block is still published, with `store_observed_at_utc=2026-09-10T12:26:13.173020+00:00`; the failure is specifically that current giveaway/publication freshness did not advance.

## Required final checklist

| Requirement | Final result |
|---|---|
| Canonical giveaway snapshot updated | **No** — still generated 2026-09-08 |
| `Astral Ascent` current externally | **Yes** |
| `Luftrausers` current externally | **Yes** |
| `Astral Ascent` in canonical snapshot | **No** |
| `Luftrausers` in canonical snapshot | **No** |
| New fresh visual build succeeded | **No** — run `34514010056` emitted only a no-build receipt |
| New deploy succeeded | **No new deploy occurred** |
| `visual_source_history_mismatch` still latest reason | **No** — old reason absent; code path repaired/tested |
| `degraded/no_fresh_build` gone | **No** — remains with `upstream_prerequisite_not_ready` |
| Both giveaways in exact published Pages artifact | **No** |
| Ordinary games preserved in exact artifact | **Yes — 115 items** |
| Taste semantics/queue/cache/Scheduled Task changed in finalization | **No** |
| New Taste batch started | **No** |

## Terminal disposition

`failed_closed_root_cause_proven`

The site is still serving the prior 115-game publication without the current Epic giveaways. The remaining blocking root cause is proven: the strict Steam commercial collector has no coherent snapshot boundary while traversing a mutable offset-paginated catalog, and canonical giveaway production is currently coupled behind that failing crawl. The smallest next engineering action is recorded above; it was intentionally not started in this report-only finalization pass.
