# Progressive site stage icons + statistics UI 01 — worker report

## 1. Task
- task: `WORKER_TASK_PROGRESSIVE_SITE_STAGE_ICONS_STATISTICS_UI_01.md`
- task id: `progressive-site-stage-icons-statistics-ui-01`
- mode: `IMPLEMENT / VALIDATE`
- repository / branch: `kentrap2011-hub/steam-kz-deals-2` / `main`

## 2. Verified facts
- Architecture preflight passed before editing:
  1. GitHub remains owner of Fast/Dossier/Deep state projection, aggregate counts, effective-result provenance and publication.
  2. Browser remains `read_only_presentation`.
  3. No scheduler, queue, retry loop, checkpoint, production worker or semantic owner was added or changed.
  4. `config/progressive_personalization_contract.json` remains the source of truth for stage/statistics presentation.
  5. The required stage/statistics fields were already present in the producer and current visual payload, so producer business/projection code did not need a source change.
- `scripts/progressive_personalization.py` already excludes `analyzed_not_fit` from normal visible states and strips personalized semantic fields from unresolved cards.
- Current visual payload inspection proved explicit per-game stage fields and separate Fast/Dossier/Deep aggregate scopes are already published.
- The existing GitHub visual build refreshed `data/production/visual/current.json` after the web changes; no Fast/Dossier/Deep semantic execution was performed by this worker.

## 3. Changes
- Removed the large always-visible top-page statistics / processing blocks.
- Added a compact `Статистика` control in the top bar and a dedicated statistics view with separate Fast, Dossier and Deep sections.
- Replaced the large generic per-card analysis badge with three compact stage indicators:
  - `⚡` Fast / Быстрый разбор;
  - `▤` Dossier / Подготовка досье;
  - `◆` Deep / Глубокий разбор.
- Stage indicator state is mapped only from explicit producer-owned stage fields; generic `analysis_state` is not a fallback for stage truth.
- Unresolved cards no longer show the large generic `Ожидает персонального разбора` decision pill. Trustworthy `analyzed_fit` cards retain producer-owned decision, personalized score, reasons and ranking presentation.
- Added the same compact stage indicators to visible list cards.
- Preserved existing tier sorting, urgency option and manual `В конец очереди` behavior.
- Added focused regression coverage for stage mapping, separate statistics denominators, no Dossier fit reinterpretation, removal of old large status hooks and compact responsive layout contracts.

## 4. Exact producer fields used

### Per-card stage fields
- `fast_stage_state`
- `fast_stage_outcome`
- `dossier_stage_state`
- `deep_stage_state`
- `deep_stage_outcome`
- `deep_recovery_state`

No stage state is inferred from `analysis_state`, `analysis_resolution_pass`, history, attempt flags or legacy generic status fields.

### Statistics — Fast
Denominator: `fast_total_current_scope`
- `fast_attempted_count`
- `fast_completed_fit_count`
- `fast_completed_not_fit_count`
- `fast_incomplete_count`
- `fast_error_count`
- `fast_skipped_due_to_authoritative_deep_count`
- `fast_remaining_count`

### Statistics — Dossier
Denominator: `dossier_total_current_scope`
- `dossier_accepted_count`
- `dossier_pending_count`
- `dossier_failed_or_recovery_count`
- `dossier_normal_first_pass_complete`
- `dossier_all_accepted_or_recovered_complete`

### Statistics — Deep
Denominator: `deep_total_current_coverage_target`
- `deep_first_pass_attempted_count`
- `deep_authoritative_completed_count`
- `deep_completed_fit_count`
- `deep_completed_not_fit_count`
- `deep_incomplete_or_recovery_count`
- `deep_waiting_for_dossier_count`
- `deep_ready_or_pending_count`
- `deep_normal_first_pass_remaining_count`
- `deep_remaining_until_all_authoritative_count`
- `deep_normal_first_pass_complete`
- `deep_all_current_authoritative_complete`

## 5. Validation — SITE-01..18
| Gate | Result | Evidence |
|---|---|---|
| SITE-01 | PASS | `web/index.html` no longer contains `#stats`, `processingStats` or `processingUpdated`; main header is compact. |
| SITE-02 | PASS | `#statisticsBtn` labeled `Статистика` opens `#statisticsView`; back control returns to feed. |
| SITE-03 | PASS | Dedicated view renders Fast, Dossier and Deep sections separately. |
| SITE-04 | PASS | Regression asserts distinct canonical denominator keys and deliberately different denominator values; no shared denominator exists in UI helper. |
| SITE-05 | PASS | Main game card and visible list cards call `stageIndicatorsHtml(g)`, which always emits Fast/Dossier/Deep indicators. |
| SITE-06 | PASS | Regression proves indicator mapping consumes explicit stage fields and does not fall back from generic `analysis_state` / PASS provenance. |
| SITE-07 | PASS | Old large analysis badge removed; regression checks prohibited generic status labels are absent from normal card implementation. Unresolved generic decision pill is hidden. |
| SITE-08 | PASS | Producer visibility semantics unchanged; `analyzed_not_fit` remains outside normal visible states and no new not-fit list path was added. |
| SITE-09 | PASS | Existing `personalized = analysis_state==='analyzed_fit'` path still renders `why_fit`, risk and priority/score details; ranking helper unchanged. |
| SITE-10 | PASS | Existing unresolved path still hides personalization/priority, clears reason/risk UI, and producer strips unresolved personalized fields; no UI score/reason fallback added. |
| SITE-11 | PASS | Existing `sortItems`, urgency behavior, queue signature and `manual_end_at` handling preserved; regression retained. |
| SITE-12 | PASS | Responsive structural regression + CSS proof: <=430px uses 9px shell padding; three main indicators occupy about 89px including gaps; statistics grid uses `minmax(0,1fr)`; list/title containers use `min-width:0`; no new fixed-width element exceeds the 342px inner width at 360px. Same rules cover 390/412/430px. The former large top statistics/processing blocks are removed, so recommendation content starts materially sooner. |
| SITE-13 | PASS | >=560px statistics metrics expand to three columns; existing 720px app/card layout remains unchanged; final Pages deploy succeeded. |
| SITE-14 | PASS | Deploy run `35909243926`, job `107344602638`: `Run UI regressions` success; log: `progressive personalization stage/statistics UI regression: ok`. |
| SITE-15 | PASS | Producer implementation/contracts were not edited. Existing GitHub visual workflow alone refreshed the payload. |
| SITE-16 | PASS | `Build daily visual payload` run `35909184960`, build job `107344462685`: success, including progressive/ranking validations, fresh visual build and generated-payload validations. |
| SITE-17 | PASS | No Scheduled Task action and no semantic production run was performed by this worker. Only existing push-triggered GitHub workflows ran. |
| SITE-18 | PASS | This durable report is committed to `main` and is reread from fresh `main` before worker completion. |

## 6. Mobile / desktop verification
- Mobile target: structural responsive proof covers 360, 390, 412 and 430 CSS px without introducing a horizontal-overflow requirement. Stage indicators remain one compact row and the statistics view uses shrinking grid tracks.
- Main-page vertical compaction is direct: the former four-cell stats block plus six-cell processing block and update row are gone from the first screen; only the compact top-bar `Статистика` control remains.
- Desktop/tablet: the existing card/navigation layout is preserved and the statistics page uses a three-column metric grid from 560px upward.
- Canonical Pages deploy: run `35909243926` succeeded; Pages artifact `10772283302`, artifact SHA-256 `d377ff89a6b89e1fa70476b0d1b7ec9a1483f1404dc0af7be62e22184571a93a`.

## 7. Unresolved item
- none.

## 8. Status
`complete_ready_for_director_acceptance`

## 9. Recommended next step
Director acceptance, with an optional human visual smoke-check on the deployed Pages site at a typical phone width (~390px). No further source change is indicated by the automated validation.

## 10. Exact commit / run / file refs
Implementation commits:
- task handoff / preflight: `1586dfc30ba2c6ef7dd440978aa162c39d120c9e`
- stage/statistics presentation helpers: `a5b38306ad32ddc681ded2d326ef4cc43d89e726`
- compact Statistics entry/view + stage slots: `06bc4516d9344fcd4dcd614605933164d5ce0990`
- stage/statistics rendering + navigation: `80d28b45e6ec8c5908f7c099627c6b5519b196f0`
- responsive styles: `4c7ea525c78d4cce8b4cf718f8adb6dc33c336d9`
- unresolved generic decision removal: `66717f1c5deb25841864b46bad21056ea4c56025`
- focused UI regression: `e5015d234cecdd431d247dc3b865d5771e6b5ba1`

Validation:
- visual build run: `35909184960`
- visual build job: `107344462685`
- deploy run: `35909243926`
- deploy job: `107344602638`
- Pages artifact: `10772283302`

Fresh-main file blobs before report commit:
- `web/index.html`: `a1c7be4238e105a7539b4c5266be213c2e60ed1c`
- `web/app.js`: `d3ecfa6b41cd6e9046725d151bcfefb74844d755`
- `web/progressive-personalization-ui.js`: `ac1f783ee4be028f6e164fc51bf1cd6cdf1fa4d1`
- `web/progressive-personalization-ui.test.js`: `b79e8f362679e2041e08818ebec41bf4436020b4`
- `web/styles.css`: `b2f41b3758daa7120190dfea5f94f949dbdeaa3c`
- `data/production/visual/current.json`: `84bed23f39b3b720a7afd76c6da56e226cbce7f7`

Concurrency note:
- after the UI deploy, `main` advanced independently to Deep-result commit `38fb6ea34ea6d9585dd6ecb9612797a155a4851c`, whose parent is the final UI regression commit `e5015d...`; report/closeout writes are based on fresh `main` and do not overwrite that parallel work.

## 11. Efficiency / reusable lesson
`none`
