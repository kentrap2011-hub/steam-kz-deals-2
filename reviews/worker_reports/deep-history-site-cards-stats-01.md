# Worker-report — Deep history site cards and Statistics 01

- **Task**: `WORKER_TASK_DEEP_HISTORY_SITE_CARDS_STATS_01.md`; worker: ЧАТ 1; **IMPLEMENT**.
- **Repository/base**: `kentrap2011-hub/steam-kz-deals-2`, `main` (source of truth).
- **PR**: [#224](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/224), branch `implement/deep-history-site-cards-stats-01`, **open, not merged**. No production deploy or end-user visibility asserted.
- **Implementation status**: bounded code complete; project-specific CI green except the independently failing site-task registry, detailed below. The PR remains subject to Director review.

## Delivered, with authority boundaries

1. **Accepted history and exact identity** — existing `progressive_deep_history.completed_versions/latest_completed` remains the single source for the latest successfully accepted Deep result from V1 `completed_versions`, V2 root or `revision_history`. Producer `progressive_personalization.build_state_index` retains strict family/AppID/taste-subject identity and separate current `deep_authoritative` scoring authority. The `deep_history` presentation has `current/outdated/never_completed` with historical accepted UTC, original `outcome`, accepted positive/not-fit evidence, negative assessment and structured score finding texts; unsuccessful latest attempts cannot hide an older success.
2. **Profile revision dates** — new `scripts/progressive_profile_content_dates.py` verifies the immutable `PROGRESSIVE-PROFILE-PIN-V1` provenance against exact raw `gaming_taste_live.json` bytes, SHA256, Git blob SHA1, path-changing Git revision, and first-parent blob change. Date means **last content change**, not last unrelated commit, build or analysis date. Confirmed example: pinned source `42225fa313c9957f70931206716b5e8c5503b3da` resolves via latest true path change `de5000be91a539157bb1c0d266ff3d99c4ad7198`, Git UTC `2026-10-11T05:11:09Z`. Any unavailable/unproven date is `null`; card and Statistics explicitly say `Дата версии профиля неизвестна`. Legacy unpinned provenance stays unknown.
3. **Read-only cards** — new `web/deep-history-ui.js` + stylesheet, loaded from `web/index.html` and displayed by `web/app.js`; accessible section clearly labels `Актуальный разбор`, `Устаревший разбор` or never analyzed. Stored evidence is escaped; stale verdict is explicitly archival and not current recommendation or score. Existing two-stage display mode is preserved.
4. **Versioned Statistics** — `web/progressive-personalization-ui.js` uses producer counters: `deep_current_version_target`, compatible current completions, historical-only completed, never completed, current remaining, per-profile unique games; explains overlapping migrations/versions must not be summed. The visual snapshot now governs these numbers where the history contract exists, avoiding mixed site-status and card timestamps.
5. **Canonical contract and durable route** — `config/progressive_personalization_contract.json` v12 formalizes true profile-content date attestation and UI/partition invariants. `PROJECT_ROUTES.md` records file-level navigation; `CURRENT_TASK.md` includes only a compact closed worker handoff without replacing parallel task records.
6. **Non-interference** — no edits to `data/cache/progressive_pass2_state.json`, `data/production/visual/current.json`, Deep or Dossier/Fast work/manifests, queues, ranking, semantically computed score, Scheduled Tasks, live profile, favicon/icon/PWA, or cutover logic. No semantic execution.

## Verification

**Confirmed GitHub PR checks on implementation head `1321475a68054446d985d1d46620f733ac21dad6`:**

| CI workflow | Run | Result |
| --- | ---: | --- |
| Validate Progressive PASS 2 core | [38509873194](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38509873194) | **success** |
| Validate site publication resilience | [38509873197](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38509873197) | **success** |
| Validate Deep site mirror UI | [38509873912](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38509873912) | **success** |
| Validate browser Deep feed refresh (PR only) | [38509873173](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38509873173) | **success** |
| Validate site Deep count queue diagnosis (PR only) | [38509873205](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38509873205) | **success** |
| Validate package purchase value | [38509873165](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38509873165) | **success** |
| Validate site task registry and page | [38509873174](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/38509873174) | **failure — unrelated preexisting task-plan validation** |

PASS2 CI log explicitly confirmed `scripts/test_progressive_deep_versioned_history.py` success (incl. three real accepted records, duplicate migration/count and identity cases), `scripts/test_progressive_profile_content_dates.py` success (punctuation revision, commit-only same-content churn, mismatch/unknown), `web/deep-history-ui.test.js` success (current/old/never, evidence, null date, scores unchanged, version counts). Existing Progressive publication/site tests also green. Dedicated browser screenshot of new history card was not available; no visual screenshot/deployed UI evidence is claimed.

**Known red check, deliberately out of scope**: `Validate site task registry and page` fails in `scripts/build_site_tasks.py::validate_plan` with `ValueError: Invalid state, effort or urgency: dossier-shadow-18-first-real-launch-gate-01`. This error is in the independent current task registry, not Deep history files; this PR must not silently repair unrelated task authority/plan. Director must resolve or explicitly account for it before merge. Early CI failures on `web/progressive-personalization-ui.test.js` were fixed by updating its assertion for the intentionally new visual-snapshot statistics fallback; the follow-up site/deep/browser checks then passed.

**Git-attested date gap:** an old Deep revision lacking exact source `content_sha256`, `blob_sha`, `source_commit_sha` cannot receive a profile date; that is rendered as unknown rather than fabricated. GitHub network/API failure also fails closed to unknown. No missing historic Deep revisions were reconstructed from Git commits.

## Director next step (single handoff)

Review **PR #224**, resolve/evaluate the independent red site-task-registry check, verify green Deep/site checks on final head, then decide merge and subsequently verify GitHub Pages publication. **Worker does not merge or execute production.**
