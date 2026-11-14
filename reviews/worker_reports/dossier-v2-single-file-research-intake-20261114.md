# Dossier V2 Research: one-file ChatGPT → GitHub intake (2026-11-14)

## Authority and requested outcome
The user explicitly asked to simplify the full Research mechanism after a six-game
run took about 23 minutes and was derailed by manual JS/handoff corruption.
A mandatory tool-access/source-process audit was **not** requested: Research
should produce useful neutral feedback, and content quality can be audited
separately upon suspicion.

Architecture preflight: existing `config/execution_ownership_contract.json`
assigns frozen scope/issuer, validation and persistence to GitHub; the chat
supplies bounded semantic facts only. The new GitHub sandbox `push` event is
technical intake/receipt generation, not a scheduled semantic stage, retry
daemon, new work queue or canonical writer. Existing batch authorization and
the eventual strict GitHub writer are unchanged.

## Delivered in draft PR #447
- One plain, create-only semantic input per game:
  `data/ai_inbox/dossier_notes_v2_intake/{trial_id}/{appid}.json`;
  only `appid` and `notes` mandatory; optional `unknowns`, `conflicts`,
  `source_urls`; no access-status log, caller-supplied Git metadata or
  SHA/handoff.
- `scripts/dossier_notes_v2_research_intake.py` validates the original
  frozen issuer/manifest against the authenticated first-attempt owner
  authorizer, strict exact source/file/edition, full standard Notes V2 schema
  and privacy rules. GitHub alone derives the assignment; source URLs become
  `access:unknown`, never an attestation that a page was opened.
- Existing unchanged typed candidate and receipt validators are used to
  create two one-add Git commits; one non-force push then verified branch-tip
  readback. No write to V1, Assembly, production, canonical, Deep.
- `.github/workflows/dossier-notes-v2-research-intake.yml` runs only on
  incoming plain Research files on `sandbox/dossier-notes-v2-*`. Multiple fast
  incoming events may be coalesced by GitHub Actions; each job reconciles all
  bounded unprocessed immutable inputs on that branch, so a coalesced event
  cannot silently omit independent games.
- The new short Research prompt and runbook replace the multi-call manual JS
  routine for **new batches frozen after the feature is merged**. Older
  immutable batches, including the submitted fresh6 data, retain their
  previously authorized transport and must not be retrofitted.
- Regression tests cover normal strict receipt equivalence, duplicate/off-
  scope/unsafe inputs, sparse Research, multiple submitted games in one
  coalesced GitHub Action, invalid sibling isolation, and unrelated events.

## Bounded verification
- Initial draft PR V2 CI run `43605225199`: SUCCESS for normal intake and
  unchanged V2 regressions before follow-up coalescing improvements.
- Existing unrelated chain test `test_23_incorrect_original_anchor_cannot_be_substituted`
  failed nondeterministically in run `43605225252`; a later same-workflow
  run `43605818512` passed without changes to that test. This unrelated
  flaky test also failed on implementation SHA 72af in run 43606457649;
  a single manual rerun was requested, not a code change.
- Reconciliation, independent-sibling and issuer-frozen-source regressions PASSED
  in [V2 run 43606457667](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43606457667) at implementation SHA `72af0089c86b52c58aa4483c2b158b615e54a30f`.
  Final documentary PR HEAD CI remains to be checked; do not claim a live GitHub intake trigger.
- No owner Freeze/Authorize replay, no manual Research re-run, no Assembly,
  no sandbox mutation, no production action triggered by this task.

## Remaining acceptance gates
Independent source/security review of PR #447, exact final-HEAD CI, then
merge under the project's source-acceptance procedure. A distinct **future**
owner-approved cohort can measure real end-to-end latency and GitHub push
trigger/receipt behavior. A PR-only unit test cannot guarantee the event will
fire or that runtime permissions allow GitHub Actions to push.
