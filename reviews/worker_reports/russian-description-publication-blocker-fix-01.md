# Worker Report — russian-description-publication-blocker-fix-01

## Task

Repository: `kentrap2011-hub/steam-kz-deals-2`, canonical branch `main`.

Task: remove the proven Russian-description publication blocker for `game:1213210` / `Command & Conquer™ Remastered Collection` without bypassing the meaningful-Russian gate and without manually processing Dossier, Deep or Fast semantic backlog or changing any ChatGPT Scheduled Task.

## Architecture preflight

- Russian description acquisition, source selection, exact translation scope, validation, cache persistence and downstream rebuild remain GitHub control-plane responsibilities under the existing Russian-description contracts and `config/execution_ownership_contract.json`.
- The target became `needs_translation` in `scripts/russian_description_translation_runtime.py`: the direct Russian Steam candidate was passed through `scripts/russian_description_quality.py`; when rejected, the resolver selected the preserved English `content_metadata.json` text and `build_russian_description_translation_queue.py` emitted `App_1213210`.
- The canonical translation cache was empty; however semantic translation was not the smallest repair for this title because a meaningful direct Russian Steam description already existed.
- The repair stays on the existing direct-Steam -> quality gate -> resolver -> optional exact translation fallback -> visual validation path.
- No scheduler, new semantic stage, second translation queue, retry daemon, browser-side fallback or ChatGPT-owned production authority was introduced.

## Verified blocker

Fresh pre-fix `main` at `c5d2f1762ef2dd3c668ab61d631a3a172f09bd82` had:
- `data/production/pre_ai/chatgpt_ru_description_status.json`: `status=translation_required`, queue `104`, direct-RU `273`, translation-cache `0`, nontranslatable blockers `21`;
- exact queue row `App_1213210` with request `1864950d3049b4da94cbc79554c0319ee80cda70439b7bf38ef986d47753ba52`, source hash `e0de298904442ffff6d34d2e0dc45cb1de07a6787f756fc1c440e70b5df0bb0a`, English source text from `content_metadata.json`;
- canonical translation cache still had no accepted entry for this app.

The previously accepted Deep report had already proved the earlier Deep visual-binding defect fixed and that full visual runs #803 / #804 reached `VISUAL_FINAL_BUILD=BUILT` before failing the later Russian-description gate on this exact game.

## Root cause

The target's direct Russian Steam short description begins with `Переиздание ...` and is meaningful Russian text.

The quality classifier's technical-edition regex contained bare `издани[ея]` without word boundaries. It therefore matched the `издание` substring inside `Переиздание` and incorrectly classified this meaningful remaster description as `placeholder_or_technical`. The resolver then fell back to the English metadata source and emitted `needs_translation`.

Investigation also exposed a shared direct-source gap for unresolved titles: StoreBrowse can be missing/non-good while the repository's already-used exact-app official Steam `/api/appdetails?cc=kz&l=russian` response contains a valid Russian short description. This is still a deterministic GitHub-owned Steam source, not semantic translation.

## Changes

Implementation merged in PR #103:

1. `scripts/russian_description_quality.py`
   - technical-edition matching now requires word boundaries around `издани[ея]` and `комплект`;
   - `Переиздание` is no longer falsely treated as an edition/package boilerplate marker;
   - the existing fail-closed technical example remains rejected.

2. `scripts/russian_description_translation_runtime.py`
   - preserves explicit direct-source provenance;
   - adds exact-app Steam `appdetails(l=russian,cc=kz)` as a deterministic direct-Steam fallback only when StoreBrowse is not `good_ru`;
   - accepts that fallback only after the unchanged `good_ru` quality gate;
   - semantic translation/cache remains the next fallback when no direct Steam source is acceptable.

3. `scripts/build_visual_feed_v2.py`
   - reuses the same localized `appdetails` payload already fetched for practical facts to enrich the description only when StoreBrowse is not `good_ru`;
   - no browser semantics and no hard-coded title-specific description were added.

4. Regression and validation:
   - focused `App_1213210` regression proves English unresolved input + meaningful Russian direct source becomes `ready_ru` and does not enter the translation queue;
   - negative regression proves non-Russian `appdetails` text cannot override the unresolved translation source;
   - quality regression proves the remaster wording is `good_ru` while existing technical-edition text remains rejected;
   - `.github/workflows/validate-execution-ownership.yml` now runs the Russian description compile/runtime regressions on relevant PRs.

5. `PROJECT_ROUTES.md` documents the reusable direct-Steam -> translation fallback -> visual validation publication route.

## Validation

PR #103 was clean/mergeable and green before merge:
- `Validate execution ownership` PR run `36339863010`: success;
- its Russian quality/runtime regression step: success after the initial failing test exposed and drove the word-boundary correction;
- `Validate backlog dispositions` PR run `36339863005`: success.

Merged:
- PR #103 squash merge: `f950944b1e9e7ee4433e0ed90c4d262b6ac24c91`.

Post-merge normal GitHub validation:
- `Validate execution ownership` run `36339890160`: success;
- normal `Build pre-AI deterministic payload` run `36339890275` (#211): success;
- pre-AI persistence commit: `472bbddc360590be3878b4dce864089fecb6ed1a`.

The post-fix canonical Russian scope at that commit proves:
- `App_1213210` is absent from the translation queue;
- `App_1213210` is present in `resolved_direct_ru_source_keys`;
- queue `104`, direct-RU `289`, translation-cache `0`, nontranslatable blockers `5`;
- compared with the pre-fix scope, direct-RU increased `273 -> 289` and nontranslatable blockers decreased `21 -> 5` while the quality gate remained fail-closed.

Normal full visual build:
- `Build daily visual payload` run `36339890167` (#808): success;
- log: `VISUAL_FINAL_BUILD=BUILT`, `items=393`;
- final Russian validation: personalized `good_ru=25`, `invalid_count=0`;
- canonical visual commit: `23cf719353d29d09d9df84bc90f9ec4daa6ce3d3`.

Following Pages deployment:
- `Deploy visual mailing` run `36339924386` (#847), triggered from that visual build: success;
- exact Pages artifact: `10938334090` (`github-pages`);
- deploy passed the Russian-description gate, UI regressions, staging/freshness binding, Pages artifact upload and GitHub Pages deployment.

No ChatGPT Scheduled Task was created, edited, enabled/disabled or manually triggered. No Deep/Fast/Dossier semantic backlog item was manually processed for validation.

## Published result

The exact deployed Pages artifact `10938334090` was downloaded and inspected from `data/current.json`.

For `game:1213210` it contains:
- `description_status=ready_ru`;
- `description_source_locale=russian`;
- `description_source_quality=good_ru`;
- `description_source_appid=1213210`;
- `description_source_path=IStoreBrowseService/GetItems(language=russian)`;
- meaningful Russian summary beginning `Переиздание Command & Conquer и Red Alert ...`;
- `analysis_state=analyzed_fit`;
- `analysis_semantic_source=progressive_pass2`;
- `pass2_attempted=true`;
- `analysis_resolution_pass=pass2`;
- `deep_stage_state=completed`;
- `deep_stage_outcome=fit`;
- `effective_analysis_source=deep`.

The same deployed artifact has current nonzero Deep accounting:
- target `397`;
- first-pass attempted `29`;
- authoritative completed `29`;
- completed fit `25`;
- completed not-fit `4`;
- incomplete/recovery `0`;
- waiting for Dossier `365`;
- ready/pending `3`;
- remaining until all authoritative `368`;
- effective result counts: Deep `29`, Fast `0`, none `368`.

This proves both the Russian-description blocker and the stale zero-Deep publication chain are repaired in the deployed artifact.

## Unresolved

The broader canonical translation scope is intentionally not drained by this task:
- post-fix translation queue remains `104`;
- accepted translation-cache count remains `0`;
- nontranslatable blockers remain `5`.

Those records are outside this bounded publication-blocker repair. Their existence does not invalidate the accepted target result, and this worker did not manually translate or process them.

No Dossier/Deep/Fast semantic issue was investigated or changed.

## Status

`complete_ready_for_director_acceptance`

## Recommended next step

Director should perform one bounded acceptance/closure review of this task using PR #103, full visual run #808, deploy #847 and Pages artifact `10938334090`; do not reopen Deep/Dossier or translation backlog work inside this worker task.

## Exact PR / commit / run / artifact refs

- implementation PR: `#103`
- PR head at final validation: `c5a3467d1b2f686bcc970529165a9656c701316c`
- PR Russian/runtime validation: `36339863010`
- PR backlog validation: `36339863005`
- merge commit: `f950944b1e9e7ee4433e0ed90c4d262b6ac24c91`
- post-merge ownership validation: `36339890160`
- pre-AI run: `36339890275` (#211)
- pre-AI commit: `472bbddc360590be3878b4dce864089fecb6ed1a`
- full visual run: `36339890167` (#808)
- canonical visual commit: `23cf719353d29d09d9df84bc90f9ec4daa6ce3d3`
- following Pages deploy: `36339924386` (#847)
- deployed Pages artifact: `10938334090` (`github-pages`)

## Efficiency / reusable lesson

The useful diagnostic split is: **source absent vs valid direct source rejected by quality classification vs genuine semantic translation required**. For this blocker, reading the exact queue row alone suggested translation, but a focused production-like regression exposed the deeper false-positive quality rule.

Reusable practice:
- bind the regression to the exact blocked app/title but test the shared classifier/resolver rule;
- keep meaningful-Russian validation fail-closed and make the pattern more precise rather than bypassing it;
- reuse an already-owned official exact-app source before semantic translation;
- ensure the focused regression actually runs on PRs, so a test cannot exist without enforcement.

This task took multiple validation cycles because the first focused regression correctly failed on the over-broad quality regex. That extra cycle improved the final repair by identifying the actual target root cause before merge rather than merely adding a source fallback.
