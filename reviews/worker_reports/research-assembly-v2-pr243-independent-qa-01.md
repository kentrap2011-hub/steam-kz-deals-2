# ЧАТ 2 — independent exact-HEAD QA: inactive Notes V2 PR #243

**Task ID:** `research-assembly-v2-pr243-independent-qa-01`  
**Target:** [PR #243](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/243). Historical original QA HEAD `7765083edfff0802026f1f16b663cef3518c7ed7`; **latest independently re-reviewed HEAD `5e956f35e2aa63f9d56a9006cd186913c8cba2e1`**. Original base `e9d9fd64986ada2e26a5ea1dea95298f98b1ae3e`.  
**LATEST VERDICT (re-review 2026-10-23): `PASS_FOR_DIRECTOR_MERGE_REVIEW` for exact HEAD `5e956f35e2aa63f9d56a9006cd186913c8cba2e1`.** The earlier `CHANGES_REQUIRED` below is retained as **historical QA of prior HEAD only**, not a current blocker. Real-trial authorization is **NOT GRANTED**.  
**Mode:** independent static code review + exact-HEAD GitHub CI readback. No edits to PR #243, original V1/trial, runtime, production, or workflows; no real Research or Assembly.

## Historical first review — superseded after correction

The findings, original CI and `CHANGES_REQUIRED` in the sections below apply only to the earlier `7765083edfff0802026f1f16b663cef3518c7ed7` HEAD. New exact-HEAD re-review and current verdict appear at the end of this file.

## Authority / START / architecture gate

Read current main `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task `WORKER_TASK_RESEARCH_ASSEMBLY_V2_PR243_INDEPENDENT_QA_01.md`, `DIRECTOR_PROTOCOL.md`, applicable Board/registry/route and `config/execution_ownership_contract.json`. Task ID, worker slot **ЧАТ 2**, named task file and planned assignment match main registry/Board. Registration [PR #246](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/246) was merged as `cfd3ade43e9945cc26d422480ed8f2dcebdaa732`; its exact head `11bfb35b5f075e2048c851041f287d14e61d7168` has successful [site-task CI #39974014198](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39974014198) and [backlog CI #39974014167](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39974014167). Source scope: only this repository.

Architecture preflight: GitHub owns original identity/scope, manifest/marker/committed transport, persistence, validation, group acceptance and all control-plane gates; separate semantic workers, if ever authorized, own only bounded semantics. This QA introduces no new actor, recurring schedule, queue, retry, checkpoint or ownership change. Review applies to inactive offline helpers, **not** to a proven runtime writer.

## Exact changes, CI and positive checks

Only three changed paths: `scripts/dossier_research_notes_v2.py`, `scripts/test_dossier_research_notes_v2.py` and the developer's `reviews/worker_reports/research-assembly-v2-safe-use-readiness-01.md`. No source workflow/config/schema flags, original trial, V1, PR #232, deploy or production files changed. `config/dossier_research_notes_v2_contract.json` retains four explicit gates `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false`; separate two-stage interfaces also inactive.

**CI on exact target HEAD** (all `completed/success`): [inactive V2 #39973011419](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39973011419), [site-task #39973011388](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39973011388), [backlog #39973011355](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39973011355). Inspected V2 job `120480325521` logs: **35 tests, 9.663 seconds, OK**, followed by successful syntax/activation checks. Historical red 34/35 is not the final HEAD.

Independently inspected new code and tests (rather than accepting developer's report):
- `_assert_unchanged_since()` at lines 186–197 verifies first-parent ancestry and rejects post-introduction path edits, including byte-identical restore; tests cover manifest, marker, Notes transport and Assembly transport mutate/restore. Marker/manifest and Research/Assembly introduction still require exact one-add commit and original raw/blob lineage. No obvious accepted-path ancestry bypass established by static review.
- `prepare_assembly_transport()` at lines 455–470 rederives canonical frozen Assembly work from `assembly_work()`, blocks stale Research or forged work dictionary (as far as the provenance snapshot is concerned); focused tests cover both.
- `checked_typed_publish_prefix()` at lines 540–564 checks stable typed prefix and earlier `candidate_already_submitted` states across two sequential fixture submissions; it does **not** independently establish GitHub-verified source for `frozen_authorized_order`, `typed_git_history` or inspect states, nor fix the old PR #232 path.
- `submitted_research()` distinguishes missing transport (unknown attempt, explicit nonacceptance) from invalid transport; traversal keeps the original 18 items in six fixed groups (3,8,13,15,18,20), independently classifies four historical missing slots `1508750`, `1607130`, `1849000`, `1857090` and 14 synthetic safe sparse/zero-source Notes. This does not invent prior attempts or authenticate historical evidence.
- `item_receipt_blueprint()` enforces phase restrictions and privacy check and keeps attempt unknown/noncanonical; `verify_independent_reviewers()` requires distinct integer account IDs, distinct appointment references and strict boolean approval. **Actual authenticated lookup and owner-appointed A/B/C receipts are absent**, as explicitly conceded by code/docs. Mock callbacks prove shape only.
- SULFUR source-role conflict and Sifu `www` host / original-work-year disagreement remain unresolved semantic issues, correctly not promoted to established facts by Notes. Strict final Dossier V2 remains mandatory in `inspect_assembly`; `original_group_readiness` reports three-item readiness but is not the actual atomic canonical writer. No true final per-item/group persistence or real runtime path exists yet.

## Blocking source-level finding — pre-submission transport accepts invalid document

**Severity: merge-blocking for promised inactive safe-use helper; no demonstrated live-production exposure.** `prepare_assembly_transport(repo, work, document)`, lines **471–478**, calls `candidate_assembly(work, outcome=..., final_dossier=..., operations=..., mechanical_corrections=..., diagnostic=...)`, which builds and validates an entirely **new** object with hardcoded `staged_only=True`, `canonical_acceptance=False`, schema/version and a filtered set of keys (lines 360–382). It does not validate the original supplied `document`. Lines **493–496** then serialize the **unvalidated original document** and return `status="ready_for_create_only_submission"`.

**Constructive adversarial counterexample (code-path proof, not claimed as executed in CI):**
```python
sha, work = fixture.work()  # existing test fixture with verified Notes
doc = v2.candidate_assembly(work, outcome="assembly_missing_evidence",
                            diagnostic="fixture")
doc["canonical_acceptance"] = True  # schema explicitly requires false
doc["staged_only"] = False           # schema explicitly requires true
doc["raw_reviews"] = "unapproved raw player material"  # forbidden extra/private field
preview = v2.prepare_assembly_transport(fixture.repo, work, doc)
# Current source returns ready_for_create_only_submission and serializes doc.
```
The [Assembly schema](../../config/dossier_autonomous_assembly_result_v2.schema.json) sets `additionalProperties:false` and explicit consts; `_privacy` forbids `raw_reviews`. But these constraints are evaluated only on the reconstructed object, not `document`. The existing positive/negative `test_prepare_assembly_transport_checks_strict_before_publishing` tests only correctly generated input and an incomplete final Dossier; it lacks this adversarial mutation. `inspect_assembly()` **would reject** the malformed persisted file later due to its actual raw-document schema check; therefore this is **not** a proven canonical-acceptance bypass. It is a real **false-positive create-only transport readiness** and avoidable unsafe bytes staged before late rejection, potentially poisoning an immutable result path. It violates the explicit pre-submission safety goal, so green CI does not justify a merge PASS.

**Required bounded fix by ЧАТ 1 (NOT this QA worker):** validate the exact entire supplied `document` before emitting `bytes` / `ready_for_create_only_submission`, including schema, privacy, phase rules, strict-final checks, and exact work binding; add an adversarial negative regression on `canonical_acceptance:true`, `staged_only:false` and forbidden extra/raw fields. Maintain inactive flags and existing authoritative boundaries. Then rerun exact-head CI and independent ЧАТ 2 review.

## Other limits / no-live gate

There is no actual authenticated GitHub reviewer appointment verifier, trusted new marker issuer, per-item durable receipt writer, cross-invocation typed source attestation, real V2 semantic launcher, or canonical shared atomic three-game writer integration. These are **separate bounded contract/architecture blockers to live trials**, not evidence that those operations happened. `prepared` helper objects do not establish authority. Original frozen assignments/title/edition/source digest are bound to original pinned bytes; no mutations observed in this PR.

**Independent execution limit:** an actual isolated checkout/test rerun was unavailable locally because the environment could not resolve the repository's GitHub host. The exploit above is supported by exact source/schema control flow, but was **not executed**; authoritative observed execution is GitHub's exact-head CI. Do not claim an independent test run. No real semantic research, Assembly, workflow dispatch, publication, live site modification, scheduled task, reviewer appointment or merge was performed.

**Recommended ONE next step:** return PR #243 to developer ЧАТ 1 for a narrowly scoped pre-submission document-validation correction and adversarial tests; require fresh exact-HEAD CI and independent QA before Director merge review. Even if corrected and later merged, V2 must remain inactive pending separately authorized GitHub issuer, authenticated appointments, persistence/atomic writer and user-approved live-trial contract.

**Final:** `CHANGES_REQUIRED`; reviewed exact `7765083edfff0802026f1f16b663cef3518c7ed7`; verdict invalid if target HEAD changes.

---

## Independent bounded re-review — 2026-10-23 (current verdict)

**Current target:** [PR #243](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/243), verified OPEN/DRAFT/NOT MERGED, exact final source HEAD `5e956f35e2aa63f9d56a9006cd186913c8cba2e1`. **New verdict: `PASS_FOR_DIRECTOR_MERGE_REVIEW`**, **only for inactive code**; it supersedes the old-head `CHANGES_REQUIRED`. The target was rechecked for exact HEAD after review before reporting.

**Registration / procedure:** Existing registered `WORKER_TASK_RESEARCH_ASSEMBLY_V2_PR243_INDEPENDENT_QA_01.md`, `main` Board + registry and merged director registration PR #246 remain the authority; original registration required site/backlog CI both success. Re-read current `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, bounded Notes V2 route, Director protocol, ownership contract and relevant task. GitHub remains control-plane owner. No authority to change source, stage, pipeline, queue, or runtime; only this report-only QA amendment and target PR Conversation response.

### Delta to prior rejected head

Git compare `7765083edfff0802026f1f16b663cef3518c7ed7..5e956f35e2aa63f9d56a9006cd186913c8cba2e1`: three commits ahead, zero behind; **exactly three modified files**: `scripts/dossier_research_notes_v2.py` (+18/-7), `scripts/test_dossier_research_notes_v2.py` (+45/-0), developer's `reviews/worker_reports/research-assembly-v2-safe-use-readiness-01.md` (+16/-0). No activation contract/schema/workflow edits, no V1, PR #232, original trial, production, publishing, or runtime edits.

**Verified source correction** (`scripts/dossier_research_notes_v2.py::prepare_assembly_transport`, lines around 476–500):
1. Re-verifies immutable marker, original Research-introduction Git parent/blob/raw and current `assembly_work`; supplied `work` must match regenerated full frozen envelope, blocking stale or forged work before examining Assembly output.
2. Calls `_schema("dossier_autonomous_assembly_result_v2.schema.json", document)` on the **actual caller-supplied whole document**. Schema's `additionalProperties:false`, required keys, outcome enum, `canonical_acceptance:false` and `staged_only:true` reject the previously admitted mutations.
3. Calls `_privacy(document)` on the same original payload and applies existing bounded text/size checks; tests confirm forbidden raw/private fields are rejected. Requires exact assignment and Research transport binding. Reconstructed `candidate_assembly` is now compared `checked != document` to reject any drift from semantically validated shape, including terminal/final consistency and operation checks.
4. Strict final dossier validator still runs on a ready outcome, and only **after** these checks and create-only output-path/lineage checks is the exact `_canonical(document)` returned. This closes the previous false-positive `ready_for_create_only_submission` on mutated source document. No operator transport writer is created.

**New adversarial tests** (`scripts/test_dossier_research_notes_v2.py`):
- `test_pre_submission_rejects_original_document_forbidden_flags_and_fields`: checks prohibited true acceptance, false staging, `raw_reviews`, unknown extra field, wrong schema, invalid outcome, and missing terminal diagnostic. Each must raise `NotesV2Error`; test confirms no published output path.
- `test_pre_submission_validates_exact_original_payload_and_status`: validates a legitimate terminal document and byte-serialized payload round-trip; rejects ready outcome with no final dossier, terminal with unexpected final dossier, invalid operation access, schema version 1 and string-valued `canonical_acceptance`.
- Old tests for immutable original 18 items/six fixed groups, four missing transports (attempt unknown; no fabricated attempts), sparse/yearless/zero-source Notes, SULFUR substantive source-role conflict, Sifu hostname/original-work-year tension, first-parent rewrite/byte-perfect restoration, stale/forged Research, two sequential original-order candidate targets, reviewer A/B/C shape and receipt phases still execute on the exact HEAD. No test or code claims real authenticated appointments.

**Exact HEAD CI readback** (queried specifically for `5e956f35e2aa63f9d56a9006cd186913c8cba2e1`):
- [Validate inactive Research Notes V2 and autonomous Assembly — run 39982459578](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39982459578): `completed/success`. Inspected job `120512983315` log: **37 tests in 11.700s, OK**, including both new test methods; syntax/disabled-activation guard SUCCESS.
- [Validate site task registry and page — run 39982459638](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39982459638): `completed/success`.
- [Validate backlog dispositions — run 39982459698](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39982459698): `completed/success`.

**Inactive boundary / original scope:** `config/dossier_research_notes_v2_contract.json` at this HEAD still says `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false`. `config/dossier_two_stage_interfaces_contract.json` also remains inactive. Original frozen group sequences 3/8/13/15/18/20 and their 18 AppIDs remain unchanged. The stable typed-prefix and reviewer helpers are offline-only; they are **not** integrated authenticated GitHub authorization or a live V2 writer. `original_group_readiness` is a proposal/reporting helper, **not** proof of actual atomic three-item canonical ingest.

**Limits/unknown (not blockers for this inactive PR):** This QA independently read source/schema/test code and CI logs, but did **not** execute an independent local disposable checkout or real semantic acceptance. No live authenticated GitHub reviewer appointment mechanism, new-run issuer/nonce, durable item receipt persistence, V2 transport writer, actual autonomous Research/Assembly launcher or strict atomic canonical writer integration is provided. Git HEAD can move between offline validation and a future GitHub writer; any live integration must attest and revalidate the same immutable authority at its actual write boundary with race protection. No real-trial authorization, Research/Assembly, semantic attempt, Deploy, scheduled-task change or production write is inferred from green tests.

**Next step:** Director may review and decide whether to merge **inactive-only** implementation PR #243 **provided it is still exactly HEAD `5e956f35e2aa63f9d56a9006cd186913c8cba2e1` with the three cited checks green**. If target HEAD changes, re-review is required. Activation/live execution remains a separate GitHub-owned `CONTRACT`/issuer/writer/independent-appointments/QA authorization; **do not start a real trial now**.

**CURRENT VERDICT: `PASS_FOR_DIRECTOR_MERGE_REVIEW`** for HEAD `5e956f35e2aa63f9d56a9006cd186913c8cba2e1`; earlier `CHANGES_REQUIRED` is superseded.
