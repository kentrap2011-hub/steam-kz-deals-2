# ЧАТ 2 — Lean Writer automatic activation: post-merge preclaim event gate correction

## Latest runtime failure and source fix (2026-11-25)

- **Status:** `SOURCE_READY_AWAITING_DIRECTOR_MERGE` for [source PR #487](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/487) (`fix/dossier-lean-auto-main-push-added-files-gate-20261125`); **final HEAD CI and source PR acceptance still pending**. This section supersedes historical pre-merge status below.
- Source activation PR #486 merged to `main` as `cfd29df88311af8749428f580dfa3dff236f9dba`. Its exact final PR HEAD `f2c1ba57e1196913b174203b2cabf91e08fb025d` had **5/5 successful PR checks**.
- Genuine owner `main` activation-file push triggered real [Actions #45591943959](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45591943959), job `139128109794`; conclusion **failure at 10:07:56Z**, before any claim or writer: `LEAN_AUTO_READY_BLOCKED: catch-up only on a genuine separate activation contract change`.
- Exact cause: `verify_source_signal` required the expected activation path in `head_commit.modified` **and globally empty** `head_commit.added`. The owner merge legitimately modified the activation config but also added this worker report. The unrelated added path is not a change to activation authority. The old mock test had `added=[]`, so CI did not cover the real merge shape.
- The bounded source fix changes that check to **require the existing config path in `modified`, reject the same config in `added`, allow unrelated added files**, with list types checked. Repo, actor, ref, event, single run attempt, original failed-run provenance, immutable one-use grant/claim and 6+6 sandbox readback are **unchanged**.
- Targeted tests now cover merged owner event with an added report; reject unrelated-only modified events, new activation files, malformed `added`, spoofed owner actor, forced push/wrong SHA. Config `status` gets one versioned update under already granted historical recovery authority, so an eventual owner merge can fire the existing `push.paths` event; `activation_enabled=true`, isolated-only, separate future opt-in, no automatic retry or Deep/production remain unchanged.
- Read-only check after failure: no `dossier-lean-auto-attempts/` claim branch; frozen sandbox remains `d1b9a9e78dcde879a03370682ade4969763fd9d1`. **0/6 accepted docs and 0/6 receipts; no new auto attempt has yet been spent**. Old first manual run `45540222575` remains forever spent.
- **Next Director action:** accept only final HEAD CI-green scoped fix PR; do not self-merge or rerun failed Actions. After true owner `main` config update verify *new* Actions ID, no more than one claim, postpush immutable 6+6 readback (or exact fail-closed reason). No manual GitHub UI steps requested from user.

---


**Task:** `dossier-lean-writer-auto-activation-01`  
**Repo:** `kentrap2011-hub/steam-kz-deals-2` only; source `main` at worker START `134ca73f89baf9e680ab7c93bc6455f06107c7a4`.  
**Status:** `SOURCE_READY_AWAITING_DIRECTOR_MERGE` (CI exact final HEAD pending as of this report revision).  
**PR:** [#486](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/486), reusing previous report-only draft branch; now scoped activation source plus tests and report. **Do not self-merge.**

## Owner decision / review

After a safety-blocked report the owner explicitly instructed: **«Включай без проверки»**. This waives *independent L3 review only* for narrow isolated sandbox auto-writer activation. It is not retrospective evidence of a security audit. PR #484 already merged `5ec1fd0f0ffbf72948e09366b43b155d361f1950`, exact source HEAD `6f5a8e60e51311079a5c3eeb4d578361b3fde2c8`, CI 6/6 success (`45573278202`, `45573278233`, `45573278194`, `45573278285`, `45573278278`, `45573278220`). No independent PR #484 security review was found.

## Versioned change in PR #486

- `config/dossier_lean_writer_auto_ready_v1.json`: `activation_enabled=true` in PR **branch only**; `requires_independent_L3_final_head_review=false` with new exact structured `owner_L3_waiver`, direct owner decision, date, narrow isolated scope, and explicit `does_not_waive_runtime_gates=true`. There is no silent global QA waiver.
- `scripts/dossier_lean_writer_auto_ready.py::policy`: accept either the original unwaived review contract or **only the exact owner waiver object** accompanying enabled activation. A missing, broadened, different or disabled waiver fails closed. All actual Actions event/actor, previous failed owner Actions run, grant, sandbox HEAD, exact receipts, one-use claim, strict writer and postpush readback paths remain unchanged. `inspect-policy` reports the true enabled state.
- `scripts/test_dossier_lean_writer_auto_ready.py`: positive exact owner waiver, negative absent/broadened waiver, inactive-policy guards; existing event and one-use checks retained. `scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py` preserves isolated-only shared concurrency and asserts explicit scope of now-enabled policy; still rejects canonical/Deep write behavior.
- `PROJECT_DECISIONS.md` records rationale and accepted risk. This report and `CURRENT_TASK.md` retain handoff without discarding other workers.

## Preflight

1. GitHub retains event, queue/grant, single writer, claim/attempt, receipt, persistence and readback ownership under `config/execution_ownership_contract.json`.
2. The separately owner-approved versioned `config/dossier_lean_writer_auto_ready_v1.json` permits **only** historical frozen six (a new one-use recovery, never a rerun of Action #45540222575) and future independent `lean_auto_writer:true` immutable owner opt-ins.
3. No ChatGPT production execution; no second scheduler or polling, no auto semantic Research/Assembly/Deep and no canonical writer/reader/Deep/production, no retry switch.
4. Source PR merge cannot be mistaken for original #484 source merge; the reviewed activation contract change on owner-authenticated `main` is itself the activation event.

## Live evidence / limitations

Prior [Actions #45580621666](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45580621666) = `success`, **activation-disabled/no writer**. Historical failed owner first-attempt [#45540222575](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45540222575) is spent; **never rerun**. Sandbox `sandbox/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4` remained `d1b9a9e78dcde879a03370682ade4969763fd9d1`, no auto-attempt claim branch and no old sample doc/receipt at that ref on last check. **Actual documents: 0/6; accepted receipts: 0/6. No genuine activated GitHub event or immutable 12-file readback exists yet.** Source PR and test green do not prove successful live publication.

## Single next handoff for Director

Obtain exact **final PR #486 HEAD** GitHub CI statuses; in light of the owner's *new, explicit, narrow* independent-L3 waiver, accept/merge the scoped activation PR as the **owner authenticated main push** only if remaining source/authority/scope gates pass. Verify that `Dossier Lean Writer Auto Ready` actually runs on that owner main activation-file change and examine real run ID/actor, claim ref, exact six docs + six accepted receipts and immutable sandbox postpush HEAD. If real event authenticity fails or writer blocks, STOP at the returned status. Do not self-merge, rerun #45540222575, or create a second recovery attempt.

**Risk:** independent L3 was deliberately waived; true GitHub event/actor behavior is not proven offline, so future activation may fail closed; there must be no unapproved manual fallback. No user GitHub UI actions are required.
