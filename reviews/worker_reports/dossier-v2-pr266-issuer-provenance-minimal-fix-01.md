# Dossier V2 PR #266 — issuer freeze provenance minimal fix

Task: `dossier-v2-pr266-issuer-provenance-minimal-fix-01`  
Status: **FIX_READY_FOR_INDEPENDENT_QA** (code and offline-only guard; **V2 issuance remains intentionally blocked**, not approved to run).  
Target: existing draft PR [#266](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/266), branch `implement/dossier-v2-existing-issuer-adapt-01`. No competing PR, merge, force-push, workflow dispatch, marker/grant or semantic launch.

## Confirmed QA-266-01 correction

- `scripts/dossier_shadow_research_feasibility.py::v2_freeze_chain` independently requires the frozen manifest parent to have exactly **one real Git parent** and to add **only the exact manifest**; its child marker also must have exactly one parent and add only the exact nonce marker. It checks the complete canonical original 18, their original groups, title/edition/assignment pins and payloads.
- During prospective authorization, the source commit is required to be on the first-parent history of the **approved current main** and to descend from the immutable scoped **human grant**. The later authorizer's direct-child check and the GitHub sandbox-ref lease do not substitute for this original-source ancestry. Structural verification of a completed authorization also rechecks the manifest/marker and source on the local actual `main` first-parent lineage.
- **Authentic GitHub Actions freeze-run provenance is NOT provable from these unsigned Git commits** (their author label is spoofable). A later genuine authorization dispatch does not attest the earlier freeze. The issuing path therefore fails closed before creating any authorization unless a genuinely independently authenticated first-attempt original freeze workflow/run-to-marker proof is established in a separately authorized follow-up. There is **no fake verification flag, guessed run ID or trust in the later authorizer**. This correction is deliberately not a working live V2 issuer; its missing real external attestation remains an explicit future gate, not a claim of completion.
- No new CI, workflow, credentials/permissions, grant, stage, scheduler or semantic path. V1 existing dispatch mode/default and source code unchanged; V2/production flags remain false. PRs #270/#274 untouched.

## Offline adversarial regressions

Four additional disposable-Git tests in existing `scripts/test_dossier_research_notes_v2.py`:
1. Correct-looking manifest-parent **plus an unapproved added file** must fail.
2. Correct manifest tree introduced by **two-parent merge** must fail.
3. Structurally correct marker + direct-child authorization on a **forged remote branch** sourced from a different first-parent history must fail.
4. Even a structurally genuine original frozen chain with an otherwise acceptable grant/main/remote must **not issue a new authorization** when there is no independently authenticated original GitHub freeze-run-to-marker proof.

CI code revision before this report: `5c3e7e7f67af4447166bb5ea891c46c1533cf609`.
- [Notes V2 / Assembly run 40288614711](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40288614711): **50/50 synthetic tests PASS**, including all four new attack cases.
- [Original V1 publisher run 40288614575](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40288614575): SUCCESS — 12 feasibility + 7 publisher + 8 original Research trial = **27/27 V1-oriented tests PASS**, plus real disposable original six-group strict proposal/freeze step.
- [Eventual chain 40288614470](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40288614470), [backlog 40288614541](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40288614541), [site task registry 40288614448](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40288614448): SUCCESS.
- Tests run on GitHub Actions PR synthetic merge checkout, **not a detached direct HEAD**; connector runtime has no network-capable local GitHub clone. A first test run failed only because two test assertions expected RuntimeError while the existing `require` raises ValueError; corrected assertions and subsequent 50/50 PASS are verified in the later run.
- Creating this report changes PR HEAD without changing implementation; recheck exact final HEAD and its CI before independent acceptance.

## Gate

Request independent QA of exact updated PR #266 code and offline checks. Do **not** merge based on this worker's claim alone. Do **not** authorize any real V2 freeze or post-freeze operation: true first-attempt original GH workflow-run attribution remains independently unproven; immutable source/tree checks alone are deliberately insufficient. Real Research, Assembly, canonical writer and production authorization are strictly out of scope. `CURRENT_TASK.md` on shared main was left untouched to avoid overwriting concurrent worker handoffs; task outcome is durable in this scoped report.
