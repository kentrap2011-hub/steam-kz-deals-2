# Worker report — code-architect-system-review-01

Final status: `review_complete_recommendations_ready`

Mode: `READ_ONLY_REVIEW`

Repository: `kentrap2011-hub/steam-kz-deals-2`

## Review snapshots

- Starting `main` reviewed: `f5fb6cc2df5005f351f419139733c4866a2760c1`
- Accepted Steam worker head reviewed separately: `5556ce5c763d886a42b3c89ba69df711ba745adb`
- Steam integration merge in `main` ancestry: `c9980e79d002e84a321d2cff089645f81d91c6b7`
- Final architecture-bearing `main` snapshot reviewed before report publication: `6305421da2a4aecf43fc9051531680f42a81994d`
- `main` advanced by 15 commits during the review. A bounded compare from the starting snapshot to the final snapshot shows no changes under `scripts/` or `.github/workflows/`; the changes were Director state/reporting and production/cache/output data from the real refresh/downstream chain. Therefore the whole review was not restarted.

This task did not change code, workflows, production data, runtime behavior, or start/stop any workflow. The only repository write performed by this task is this required review report.

## Executive conclusion

There is no `blocking_structure_issue` in the current production architecture.

The current Steam system is operationally sound enough to remain in production. The real workflow run `34643249267` completed successfully with the new canonical entry point `scripts/steam_partial_publish_runner.py`; the focused partial-publish regression passed before the collector, the collector completed, ownership guards passed, publication succeeded, and downstream dispatch succeeded.

The real production result is especially useful architectural evidence: Steam reported and yielded 17,299 catalog items, 17,287 items were processed successfully, 12 game-level review-enrichment failures were isolated, catalog-segment failures were 0, system-state failures were 0, source coverage remained complete, and a 676-item shortlist was published. In other words, the new failure-isolation boundary did the job it was introduced to do without turning isolated game failures into a full-run failure.

The main maintainability debt is not that `steam_partial_publish_runner.py` is fundamentally the wrong design. It is that it is a bounded transition sitting on top of a legacy collector that was not originally written as an importable library. The runner avoids copying the low-level Steam parser and selection rules, but it obtains them by reading `steam_production.py`, splitting on a literal source marker and `exec`-ing the prefix. The accelerator similarly relies on global monkey-patching of `requests.Session.get` and `time.sleep`. That is acceptable as a short-term compatibility bridge, but it should not become the permanent API boundary.

Across the wider project, large-file size alone is not the main problem. The highest-value improvements are: remove hidden/dynamic boundaries, make canonical entry points explicit, test the real runner boundary, move deterministic domain decisions out of workflow heredocs, and retire or clearly label legacy parallel paths. Several large coordinator files should remain intact because they already delegate policy to focused modules and benefit more from section anchors than from further fragmentation.

## Evidence and bounded measurements

### 1. Steam module structure

At the accepted implementation/current code state:

| File | Approx. size observed | Primary responsibility |
| --- | ---: | --- |
| `scripts/steam_production.py` | 45.1 KB | Steam HTTP/parsing/review/selection core plus legacy top-level full-publish orchestration |
| `scripts/steam_partial_publish_runner.py` | 21.9 KB | Canonical partial-publish orchestration, failure isolation and output assembly |
| `scripts/steam_partial_publish.py` | 12.0 KB | Failure queue, source-status policy, last-known-good helpers and durable failure state |
| `scripts/steam_production_cached.py` | 8.8 KB | Review HTTP cache/search-delay accelerator plus legacy execution wrapper |
| `scripts/steam_traversal_recovery.py` | <1 KB | Legacy traversal recovery policy |

The runner is roughly 48% of the byte size of the legacy collector. This is not 48% literal line duplication: the runner deliberately reuses parser/rating/selection functions from `steam_production.py`. The duplicated area is mainly orchestration: catalog traversal, review enrichment flow, broad/refined selection, quality guards, shortlist serialization and manifest/index assembly all have an old full-publish form and a new partial-publish form.

Current blob checks at the final reviewed `main` confirm the architecture used in production is still the accepted implementation:

- `steam_partial_publish_runner.py`: blob `1ccae4053c65fcd3a231a602fe24080f756629de`
- `steam_production.py`: blob `bec4e47a2306b374467e46894ebc87f371b06bcb`
- `steam_production_cached.py`: blob `63073a0f152785142ca192e06b816ec8cc1f3ae5`
- `steam_partial_publish.py`: blob `69730df850fe7056062b7d640d4424dd308f83df`
- `test_steam_partial_publish.py`: blob `751764bb8e871ca967f9655ab69a6c3466f6e31e`

No code/workflow change after the initial review snapshot invalidated the earlier structural findings.

### 2. Steam entry points and dependency hops

Canonical production path:

`steam-test.yml` -> focused regression tests -> `steam_partial_publish_runner.py` -> shared legacy Steam core loaded dynamically + `steam_partial_publish.py` + accelerator functions -> owned production outputs -> ownership checks -> publication -> visual refresh dispatch.

The scheduled/workflow entry point is therefore clear: there is one canonical production collector invocation.

However, there are still multiple manually executable ways to collect Steam data:

1. `steam_partial_publish_runner.py` — current canonical production path.
2. `steam_production_cached.py` — legacy wrapper that monkey-patches global HTTP/sleep behavior and executes `steam_production.py`.
3. `steam_production.py` — legacy collector with top-level execution.

These are not three competing scheduled production pipelines today, but they are three apparent execution paths to a worker reading the repository. That is a navigation/maintenance hazard and a future divergence risk.

### 3. Testability measurement

`test_steam_partial_publish.py` contains seven deterministic partial-publish regression tests. They cover:

- one-game failure isolation;
- last-known-good preservation;
- catalog-segment isolation;
- honest partial-source metadata;
- live total-count drift handling;
- durable failure persistence/summary;
- corrupt failure-queue quarantine/recovery.

The test module imports `steam_partial_publish.py`; it does not import `steam_partial_publish_runner.py`. Thus the policy/state module is independently testable, while the highest-coupling production orchestration boundary is not directly unit-tested.

Two generic helpers (`process_individual_items` and `fetch_segments_resilient`) are easy to test but the production runner implements its real loops directly instead of delegating to those helpers. This means the tests prove the intended primitives/policy, but not every integration boundary used by the real runner.

The successful production run reduces immediate operational concern, but it does not remove this maintainability gap: future changes to `load_core()`, dynamic namespace keys, output assembly or accelerator patching could break the runner without those seven tests noticing.

### 4. Real production evidence

Workflow run `34643249267` (`Steam KZ production shortlist`) completed with conclusion `success` on integration head `c9980e79d002e84a321d2cff089645f81d91c6b7`.

Relevant successful steps included:

- Regression test Steam partial publish
- Regression test Steam traversal recovery
- Regression test production output ownership
- Collect Steam KZ catalog with partial publish failure isolation
- Verify Steam collector touched only owned production paths
- Verify production writers touched only owned paths
- Commit production feed, giveaways, failure state and review cache
- Dispatch visual refresh after production update

The production report records:

- Steam reported total: 17,299
- Unique items collected: 17,299
- Successful items: 17,287
- Isolated problematic games: 12
- Problematic catalog segments: 0
- System-state problems: 0
- Shortlist items: 676
- Source coverage ratio: 1.0
- Source status: complete
- Last-known-good preserved items in this run: 0 (the 12 failures had no previous published rows requiring preservation)

This is evidence in favor of keeping the current partial-publish behavior while cleaning its internal boundary later.

### 5. Visual pipeline structure

`build_final_visual_payload.py` is large (about 36 KB) but already delegates substantial policy to focused modules: package purchase options, base/daily builder, card explanation policy, duration enrichment, giveaway visual handoff, play-priority context, canonical priority ranking, ranking refinement, commercial refresh and semantic runtime completion.

Its size is therefore mostly coordinator complexity, not proof that it should be split into many files.

`build-daily-visual-payload.yml` is larger (about 46 KB) and contains real domain/decision logic inside inline Bash/Python blocks: refresh-scope classification, provenance comparison, bounded mutation checks and validation/export logic. These deterministic decisions are much harder to import and test than ordinary Python functions. That is a better extraction target than splitting the entire workflow.

`build_visual_feed.py` and `build_visual_feed_v2.py` contain overlapping implementations for loading, cache normalization, offer construction, currency conversion, Steam enrichment/media lookup and visual item assembly. The active daily builder imports v2. The older v1 file remains present and executable, so there is genuine parallel/legacy surface here that merits a consumer audit.

### 6. Navigation cost

The flat `scripts/` namespace mixes current producers, compatibility wrappers, validators, tests, stateful tools and historical/fix scripts. A representative Steam investigation requires at least these hops:

1. workflow to find the canonical command;
2. runner to find the partial-publish orchestration;
3. `load_core()` into `steam_production.py` for parser/selection behavior;
4. `steam_partial_publish.py` for failure-state policy;
5. `steam_production_cached.py` for cache/sleep behavior.

This is workable, but slower and less obvious than a documented/importable dependency graph.

A repository-wide folder move would not be the efficient first fix because workflows contain exact path filters and direct `python scripts/...` invocations. Documentation plus gradual domain packaging during natural refactors has better benefit/cost.

---

## blocking_structure_issue

### B1 — None found

**Problem:** No current structural defect makes the production system unsafe to operate or requires rollback of the Steam partial-publish integration.

**Evidence/measurement:** The canonical workflow uses one explicit collector entry point; the real workflow completed successfully; ownership guards passed; 12 game-level failures were isolated without catalog failure; source coverage was complete; no catalog-segment or system-state failure occurred.

**Proposed solution:** No blocking change. Keep the current production path.

**Expected gain:** Avoids destabilizing a working reliability improvement for architectural cleanup.

**Implementation cost:** None.

**Urgency:** None / do not block current work.

---

## refactor_recommended

### R1 — Replace `exec`-based Steam core loading with a normal importable core

**Problem:** `steam_partial_publish_runner.py` reads `steam_production.py`, looks for the literal marker `started = datetime.now(timezone.utc)`, splits the source at that marker and executes the prefix into a dictionary namespace. The production API therefore depends on source-file layout rather than a normal module interface.

**Evidence/measurement:** The production runner has at least three hidden dependencies beyond ordinary imports: the source marker, dictionary lookup of dynamically created functions/constants, and global accelerator monkey-patches. A harmless reordering of the legacy file around the marker can break the current runner even if the actual parser functions remain valid.

**Proposed solution:** Extract one cohesive importable Steam core containing HTTP/parsing/review/selection functions and constants. Keep `steam_partial_publish.py` as the failure/publication-policy module. Keep one thin canonical production runner. Expose the review-cache/search-delay behavior as an explicit adapter/client or injected dependency instead of relying on global patching. Temporarily retain old scripts only as thin compatibility wrappers, then retire them after consumer confirmation.

**Expected gain:** Normal imports/static analysis, fewer hidden breakpoints, direct test injection, one canonical orchestration location, safer future changes to Steam parsing/selection.

**Implementation cost:** Medium. Most risk is behavioral equivalence during extraction, not code volume.

**Urgency:** High-value but not urgent. Do after the successful partial-publish path has had a short stabilization period; no need to interrupt operational work.

### R2 — Add deterministic tests at the real Steam runner boundary

**Problem:** Existing seven partial-publish tests cover the helper/policy layer, not the actual runner integration.

**Evidence/measurement:** `test_steam_partial_publish.py` has 7 tests and 0 imports of `steam_partial_publish_runner.py`. Production loops are implemented directly in the runner. The real production success is useful acceptance evidence but is not a substitute for cheap deterministic regression coverage when the runner is refactored.

**Proposed solution:** During R1, make runner operations accept explicit dependencies/roots where practical. Add runner-level tests for: failed segment followed by later success; failed game with last-known-good preservation; blocked traversal; output/manifest source-status consistency; review-cache adapter behavior; and restoration of patched/global resources if the compatibility adapter remains.

**Expected gain:** Tests cover the actual production path rather than a parallel model of it; future structural changes become much safer.

**Implementation cost:** Medium now, lower when paired with R1.

**Urgency:** Medium. Pair closely with R1; can wait while current production is stable.

### R3 — Extract deterministic scope/provenance decisions from `build-daily-visual-payload.yml`

**Problem:** Important refresh decisions are embedded in Bash/Python heredocs inside a large workflow.

**Evidence/measurement:** The workflow is about 46 KB and contains multiple embedded Python blocks for giveaway/commercial/full scope selection, source provenance comparisons, hash/bounded-diff proofs, history readiness and review export. Those blocks are domain logic, not merely CI wiring.

**Proposed solution:** Leave permissions, concurrency, job dependencies, conditions, checkout, artifacts, commits/rebase/push and secret/environment wiring in YAML. Move only deterministic reusable decisions into a small tested Python module/CLI.

**Expected gain:** Easier independent tests, fewer quoting/heredoc errors, clearer ownership, less need to edit a large workflow for policy changes.

**Implementation cost:** Low-to-medium if done incrementally.

**Urgency:** Medium-low. Useful later; current workflow is functioning.

### R4 — Resolve `build_visual_feed.py` vs `build_visual_feed_v2.py` after a bounded usage audit

**Problem:** Two files implement overlapping visual-feed responsibilities, while v2 is the path imported by the active daily builder.

**Evidence/measurement:** Both versions independently implement loader/cache/price/offer and Steam enrichment/visual assembly behavior. This creates multiple places a worker could modify when asked to change visual feed behavior.

**Proposed solution:** First audit references/consumers. If v1 has no required consumer, mark it deprecated and remove/archive it in a dedicated cleanup task. If both are still required temporarily, factor only genuinely shared low-level utilities; do not build a version/inheritance framework.

**Expected gain:** Less duplicate maintenance, clearer canonical visual path, fewer wrong-file edits.

**Implementation cost:** Low if v1 is dead; medium if active consumers remain.

**Urgency:** Low. Safe to postpone until a visual-pipeline change naturally touches this area.

### R5 — Audit/label legacy workflow and manual execution paths

**Problem:** Files such as `.github/workflows/build-feed.yml`, `steam_production.py`, `steam_production_cached.py`, and old visual builders look like viable production entry points even where the canonical chain has moved elsewhere.

**Evidence/measurement:** The current Steam workflow is named `Steam KZ production shortlist` and explicitly dispatches `build-daily-visual-payload.yml`. `build-feed.yml` still references an older workflow name (`Update Steam KZ deals`) and a different compact-feed data path. Steam itself has three executable collector-style scripts although only the partial runner is the canonical workflow command.

**Proposed solution:** Confirm remaining consumers. Retire dead paths; otherwise label them explicitly as compatibility/manual/legacy in file headers and the architecture index.

**Expected gain:** Fewer accidental manual runs/edits to the wrong path; faster worker orientation.

**Implementation cost:** Low after consumer confirmation.

**Urgency:** Medium-low. Documentation can happen early; deletion should wait for usage confirmation.

---

## navigation_improvement

### N1 — Add a canonical architecture / entry-point index

**Problem:** Canonical status is not obvious from filenames. Workers must infer current paths by following workflow calls and imports.

**Evidence/measurement:** Steam alone takes roughly five navigation hops to understand end-to-end behavior. The flat script namespace contains `build_*`, `test_*`, `validate_*`, old/new versions, wrappers and fix scripts together.

**Proposed solution:** Add a short maintained `ARCHITECTURE.md` or `scripts/README.md` with, for each pipeline: canonical workflow, canonical entry point, internal modules, owned outputs, tests, and legacy/manual alternatives. Explicitly document the Steam path as:

`steam-test.yml -> steam_partial_publish_runner.py -> Steam core + steam_partial_publish + cache adapter -> owned production outputs`.

**Expected gain:** Very high navigation value with essentially no runtime risk; likely the fastest improvement for future worker speed.

**Implementation cost:** Low.

**Urgency:** High relative to its cost, but still non-blocking. This should be the first cleanup action when architecture work is authorized.

### N2 — Add section anchors to large cohesive coordinators

**Problem:** Large files such as `build_final_visual_payload.py` and `director_orchestration_controller.py` are slower to navigate, but their responsibilities are internally cohesive.

**Evidence/measurement:** `build_final_visual_payload.py` already imports many focused policy modules; the Director controller shares one state/contract invariant model. Splitting either would add cross-file hops without a proven independent boundary.

**Proposed solution:** Add module-level maps and clear internal section headings. For the visual coordinator: common helpers, giveaway-only, commercial-only, deterministic refresh, full semantic build, publication. For the Director controller: contract validation, state validation, repository bindings, eligibility/selection, leases/transitions, CLI/pilot handling.

**Expected gain:** Faster code location with near-zero architectural churn.

**Implementation cost:** Low.

**Urgency:** Low-to-medium; do opportunistically.

### N3 — Do not mass-reorganize the flat `scripts/` tree

**Problem:** The directory is crowded, but a mass move would touch imports, workflow path filters, exact command invocations and documentation.

**Evidence/measurement:** GitHub workflows enumerate many exact script paths and use direct `python scripts/...` commands. Moving files produces a large mechanical blast radius while providing little immediate runtime benefit.

**Proposed solution:** Use the architecture index first. Introduce domain packages/folders only when an already-authorized refactor such as R1 or R4 naturally changes that domain.

**Expected gain:** Gradual navigation improvement without repository-wide churn.

**Implementation cost:** Low for documentation; high for a mass move, which is not recommended.

**Urgency:** No mass move. Incremental only.

---

## no_change_recommended

### C1 — Keep `steam_partial_publish.py` separate

**Problem considered:** Whether the helper/state file is an unnecessary intermediate layer.

**Evidence/measurement:** It has a coherent responsibility (failure queue schema/state, last-known-good preservation, source coverage metadata and deterministic helpers) and seven focused regression tests. Real production demonstrated that its failure policy can coexist with a successful complete-source publish containing isolated game failures.

**Recommendation:** Keep it separate. The undesirable indirection is the dynamic legacy-core loading/global patching, not this module.

**Expected gain:** Preserves a testable failure-policy boundary.

**Implementation cost:** None.

**Urgency:** No change.

### C2 — Do not split `build_final_visual_payload.py` just because it is large

**Problem considered:** About 36 KB and multiple refresh/build modes.

**Evidence/measurement:** The file already delegates major policy to roughly ten focused helper/policy modules. Its remaining code coordinates cross-stage invariants and bounded modes.

**Recommendation:** Keep it as the top-level visual coordinator. Add anchors; extract only a responsibility that later proves independently reusable/testable.

**Expected gain:** Avoids unnecessary module hopping and preserves one place for final cross-stage invariants.

**Implementation cost:** None beyond optional navigation headings.

**Urgency:** No split now.

### C3 — Do not split `director_orchestration_controller.py` solely by size

**Problem considered:** Large control-plane script with many functions.

**Evidence/measurement:** Its logic revolves around one deterministic state model: contract validation, task/state validation, repository bindings, eligibility, slots/leases and transitions. Those functions share invariants heavily.

**Recommendation:** Keep the controller cohesive unless a future phase creates a stable independent subsystem. Improve internal sectioning/formatting first.

**Expected gain:** Keeps single-writer/state invariants locally visible.

**Implementation cost:** None for the architecture choice.

**Urgency:** No split now.

### C4 — Keep GitHub Actions orchestration in YAML

**Problem considered:** Whether the large daily workflow should be replaced by one Python orchestrator.

**Evidence/measurement:** Permissions, concurrency, job dependencies, conditions, checkout, artifact handling, commit/rebase/push behavior and secret/env wiring are genuine CI concerns that remain clearest in YAML.

**Recommendation:** Keep those concerns in YAML. Extract only deterministic domain decisions that benefit from importable tests (R3).

**Expected gain:** Retains transparent CI behavior without embedding too much policy in YAML.

**Implementation cost:** None for this boundary choice.

**Urgency:** No broad replacement.

### C5 — Keep the new canonical Steam partial-publish path

**Problem considered:** Whether the new runner should be removed because it overlaps the legacy collector.

**Evidence/measurement:** The production run succeeded and isolated 12 individual failures while completing the full source and publishing 676 shortlist entries. The runner reuses low-level parser/selection logic rather than maintaining an entirely separate copy.

**Recommendation:** Keep `steam_partial_publish_runner.py` as the canonical entry point. Refactor its dependency boundary later; do not merge it back into the legacy top-level monolith.

**Expected gain:** Retains proven failure isolation and keeps the future architecture direction clear.

**Implementation cost:** None now.

**Urgency:** No change to current production entry point.

---

## Explicit answers requested

### Is the current Steam system arranged normally?

Yes for current production operation, with one important caveat. The canonical workflow path is clear and has now succeeded in real production. Failure isolation, durable failure state, ownership checks and downstream dispatch are all sensible boundaries. The caveat is the compatibility technique used to reuse the legacy core (`exec` of a source prefix plus global monkey-patching), which is suitable as transitional glue but not as the desired permanent module API.

### How much does `steam_partial_publish_runner.py` duplicate the old Steam files?

It duplicates a meaningful share of **orchestration**, not the underlying parser/selection rules. Its size is about 21.9 KB versus about 45.1 KB for `steam_production.py`, but that ratio must not be read as literal 48% duplicate code. The runner reuses the old core dynamically and then reimplements the failure-tolerant traversal/review/selection/output flow required by partial publish. The future fix is to consolidate orchestration around one canonical runner and expose the reused core as a normal module — not to copy more code and not to collapse everything back into the legacy monolith.

### Are there now several ways to do the same thing?

There is one canonical scheduled Steam path, but several executable-looking manual paths remain. `steam_partial_publish_runner.py`, `steam_production_cached.py` and `steam_production.py` can all look like ways to run Steam collection. Similarly, the visual area has v1/v2 builders and an older compact-feed workflow surface. This is currently a navigation/maintenance problem rather than evidence of multiple workflows racing to own the same production output.

### Which large files really should be divided?

`steam_production.py` should be divided once, along a stable boundary: reusable Steam core versus orchestration. `build-daily-visual-payload.yml` should not be split into many workflows, but deterministic decision/heredoc logic should be extracted into tested Python helpers. The v1/v2 visual builders should first be resolved as a legacy/consumer question before further module splitting.

### Which large files should stay whole?

`build_final_visual_payload.py` should remain the final coordinator for now. `director_orchestration_controller.py` should remain one control-plane module while it enforces a single shared state model. The GitHub Actions workflow should retain CI-specific orchestration in YAML.

### Where are sections/anchors enough?

They are the preferred change for `build_final_visual_payload.py` and `director_orchestration_controller.py`, plus useful headers in legacy/compatibility wrappers. Clear sections deliver most of the navigation benefit without creating new cross-file dependencies.

### Where are there unnecessary levels/dependencies?

The clearest unnecessary/brittle dependency chain is runner -> source-file text marker -> dynamic `exec` namespace -> legacy functions, plus accelerator-wide monkey-patching. The old/new visual execution surfaces also add unnecessary conceptual levels if v1/legacy consumers are dead. By contrast, `steam_partial_publish.py` is not an unnecessary level because it owns coherent, independently tested state/policy.

### What will actually speed future development?

Highest benefit/cost order:

1. Document canonical entry points and legacy paths.
2. Refactor the Steam core into a normal importable module and retain one canonical runner.
3. Add deterministic runner-boundary tests as part of that refactor.
4. Extract testable decision logic from workflow heredocs.
5. Audit/retire dead legacy workflow and visual-builder paths.
6. Add section anchors to large cohesive coordinators.
7. Reorganize folders only gradually when natural refactors already touch those domains.

### What can safely be postponed?

All structural code refactors can be postponed while operational speed is the priority. The real Steam path is working. R3/R4/R5 and folder organization are clearly deferrable. R1/R2 are the most valuable engineering cleanup, but even they are not urgent production fixes. The architecture index is the only recommendation with such low risk/cost that it is worth doing early once a separate implementation task is authorized.

---

## Priority by benefit vs implementation cost

| Priority | Recommendation | Benefit | Cost | Urgency |
| --- | --- | --- | --- | --- |
| 1 | N1 canonical architecture/entry-point index | High | Low | First cleanup; non-blocking |
| 2 | R1 importable Steam core + one canonical runner | Very high | Medium | After stabilization |
| 3 | R2 real runner-boundary deterministic tests | High | Medium | Pair with R1 |
| 4 | R3 extract workflow decision logic | High | Low-Medium | Later bounded refactor |
| 5 | R5 audit/label legacy execution/workflow paths | Medium-High | Low | After consumer check |
| 6 | R4 resolve visual v1/v2 duplication | Medium | Low-Medium | Can wait |
| 7 | N2 section anchors | Medium | Low | Opportunistic |
| 8 | N3 gradual domain packaging only | Medium | Low incrementally / high as mass move | Do not mass-move |

## Final status

`review_complete_recommendations_ready`
