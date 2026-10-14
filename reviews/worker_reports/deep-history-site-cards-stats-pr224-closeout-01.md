# Worker-report — PR #224 Deep history site cards and Statistics closeout

- **Task:** `WORKER_TASK_DEEP_HISTORY_SITE_CARDS_STATS_PR224_CLOSEOUT_01.md`, ЧАТ 1 (existing PR, bounded closeout).
- **Repository:** `kentrap2011-hub/steam-kz-deals-2`; canonical source: `main`.
- **Pull request:** [#224](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/224), `implement/deep-history-site-cards-stats-01`; remains **open; no self-merge or Pages deployment**.
- **Verified application/test-code head:** `8e69b8dacc885e8074421b52478de1886bc688af`. This report is committed *after* verifying that head; its report-only commit advances the PR head. The PR's final exact head and final-head checks must be read from GitHub PR metadata/checks (and are recorded separately in the PR closeout comment after verification).
- **Normal merge base brought in:** `a5c05e875d705d5aa17ff9f07e8d8f88bd710651` from current `main` at the time; two-parent merge commit `026cd081128503b8b77e2d028cedcb9b1983efb9` (parents in order: old PR head `06a9371ec36c80247eaef931dc046b0c73fa30e8`, above main). Strict disjoint changed-path comparison of both sides against common ancestor `10ee3cf3aefe1212cbc7c7d3da214e661f84c7fa`: zero overlaps, 16 PR-owned files, no conflict, no force/rebase/history rewrite. GitHub marked PR mergeable against latest main at verification time; ongoing production commits can advance main afterwards.

## Independent recheck and narrowly fixed defect

1. Verified current `main` Director registry `config/director_task_plan.json` has allowed public effort `низкая` on `dossier-shadow-18-first-real-launch-gate-01` (previous invalid `небольшая` removed), consistent with `scripts/build_site_tasks.py` enumeration. Neither Director Board nor registry was edited in this PR. The site-task check was **rerun and passed**, not inferred from the earlier Director fix.
2. Preserved newer main-only changes including Dossier PR #225, Deep manual-one-shot PR #226, production receipts/state and `data/production/visual/current.json`. The merged tree differs from its captured main parent only by the 16 bounded Deep history PR files, with no production-state mutation.
3. Confirmed producer `scripts/progressive_personalization.py` uses `progressive_deep_history.latest_completed` for the accepted-history *presentation only*, with strict current family/AppID/taste-subject identity; later incomplete attempts do not erase earlier accepted success. Only independent `deep_authoritative` can produce current Deep score/analysis/ranking; stale history never becomes scoring authority. Producer partitions current target into current-compatible / history-only / never, with per-version unique-game dedup rather than summing legacy migration overlaps.
4. Checked `scripts/progressive_profile_content_dates.py`: pinned exact source commit + raw bytes + SHA256 + Git blob identity and Git path-content change provenance, with differing first-parent bytes. Same-content commits do not date-reset; unsupported historical pins and failed attestation become `null`. Neither profile dates nor Deep accepted dates are synthesized from build/deploy time.
5. Verified `web/deep-history-ui.js` renders original saved Deep outcome, accepted UTC or explicit unavailable date, saved positive/negative/evidence findings, historical/current profile version and proven date or `Дата версии профиля неизвестна`; all strings are HTML-escaped. Shows current/outdated/never and warns that outdated conclusion does not affect present rating. `web/progressive-personalization-ui.js` shows disjoint versioned Statistics, last profile date and target/remaining from one published snapshot.
6. **Fixed a confirmed remaining UI-state bug:** `web/app.js` previously suppressed `deep_history` when `DeepTwoStageUI.active(g)` was true (`!twoStage` gate). The two sources are independent read-only presentation panels and may coexist. Removed that suppression; historic Deep now renders alongside two-stage detail when history data is present. Updated `web/progressive-personalization-ui.test.js` to assert both independent rendering paths, without touching scoring/Stage1/Stage2 selection.
7. No favicon/PWA changes, producer authority or semantic workflow changes, reanalysis, queue/retry, Dossier Research/Assembly, ranking/Fast edits, scheduled tasks, or direct canonical data write.

## Exact 8/8 CI on validated application/test-code head `8e69b8d...`

| GitHub PR workflow | Run ID | Result |
| --- | ---: | --- |
| Validate Progressive PASS 2 core | [38612178762](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38612178762) | **success** |
| Validate site publication resilience | [38612178719](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38612178719) | **success** |
| Validate Deep site mirror UI | [38612178522](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38612178522) | **success** |
| Validate browser Deep feed refresh (PR only) | [38612178453](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38612178453) | **success** |
| Validate site Deep count queue diagnosis (PR only) | [38612178700](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38612178700) | **success** |
| Validate package purchase value | [38612178365](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38612178365) | **success** |
| Validate site task registry and page | [38612178534](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38612178534) | **success** |
| Validate backlog dispositions | [38612178827](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38612178827) | **success** |

The PASS 2 successful job explicitly includes Deep versioned history, profile-content-date and `node web/deep-history-ui.test.js`, semantic identity, negative assessment/score evidence, Deep-first ordering, producer personalization and visual freshness regressions. Site publication CI includes profile dates, cards, statistical UI and freshness/quarantine validation. The site-task workflow successfully ran `python scripts/test_site_tasks.py`, `python scripts/build_site_tasks.py --output /tmp/site-tasks.json` and `--validate-current` (same output-behavior check as requested `/tmp/tasks.json`, using workflow's own temporary pathname). These are genuine remote GitHub Actions tests, **not** locally executed Python commands.

## Acceptance and outstanding verification

- **Confirmed:** 8/8 checks green on the source-code verification head; site-task registry defect resolved on actual combined PR source; GitHub `mergeable=true` at that check, with no conflicts; both Deep panels may coexist; historical verdict stays read-only and old revisions remain visible under exact game identities.
- **Limitations:** older unpinned Deep records intentionally show an **unknown** profile-content date, not a guessed date. A live deployed browser/screenshot of unmerged #224 is unavailable and **not claimed**. Re-run/check all PR workflows on the report-bearing **final** head and reconfirm mergeability against latest moving `main`; record those final IDs in the PR closeout comment. Do not claim public-site delivery before Director merges and Pages deploy passes.
- **Director next step (single):** inspect the final PR #224 head/checks and this report, decide whether to merge; only after merge verify Pages publication/UI. Worker must stop without merge.
