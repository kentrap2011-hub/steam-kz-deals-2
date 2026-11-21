# Independent execution preflight — frozen original 18-game shadow Assembly

**Task ID:** `dossier-shadow-18-independent-execution-preflight-01`  
**Role:** ЧАТ 2, independent read-only pre-execution QA, not semantic operator/developer  
**Checked:** 2026-10-20 UTC; `main` snapshot `93c354ef0dadf1bb48d52451090a796666aae366`  
**Result:** **PREFLIGHT_READY_FOR_PR_QA**; **NO-GO FOR REAL ASSEMBLY NOW**. This is readiness to inspect the future developer PR, NOT permission to start a semantic worker, approval of a developer PR, or approval to publish any AppID.

## START / provenance / tested evidence

- Read `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, this exact worker task and bounded sections of `PROJECT_ROUTES.md` (`#Frozen 18-game shadow Assembly`) and `CURRENT_TASK.md`. Read canonical ownership, original Research-trial contract, original Director decision, actual marker-era Assembly prompt and Stage B, pins, current handoff Python, workflow, strict schema/semantic instructions, inactive interfaces/staging/async/final-acceptance contracts, and named tests. No workflow dispatch, Research retry, semantic work, or synthetic result write performed.
- Exact repository: [kentrap2011-hub/steam-kz-deals-2](https://github.com/kentrap2011-hub/steam-kz-deals-2); default/source-of-truth `main`. Main SHA at start/just before report: `93c354ef0dadf1bb48d52451090a796666aae366`.
- Original user freeze: [Director decision](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/reviews/dossier_shadow_offline/dossier_shadow_calibration_20261011_6x3_director_decision_v1.json) with source `95a4bf4990a60082ecb3302da5bc7f23b618d93e`, fixed group SHA-256 and original group membership. This historical user request does **not** override negative execution authority.
- Original marker `2c2649fb98322507cd3758ff0ff7992128f94de0` has a **single parent** `9782ab8492aadc744c23ec0425abf8d2d877590e`; marker commit adds **only** `reviews/dossier_shadow_offline/trials/dossier-shadow-calibration-20261011-6x3/assembly_run_starts/7e92dc8a122c7ebefc9c2a242fb8664c.json`. Parent adds **only** `reviews/dossier_shadow_offline/trials/dossier-shadow-calibration-20261011-6x3/assembly_buffer.json`; its actual Git blob SHA is `5c7e66db7d3880098c0cd85f0690661c9655cd09`. [Marker commit](https://github.com/kentrap2011-hub/steam-kz-deals-2/commit/2c2649fb98322507cd3758ff0ff7992128f94de0), [buffer commit](https://github.com/kentrap2011-hub/steam-kz-deals-2/commit/9782ab8492aadc744c23ec0425abf8d2d877590e).
- GitHub API branch check: `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research` **HEAD equals the unchanged original marker** `2c2649fb98322507cd3758ff0ff7992128f94de0`. No current Assembly candidate commits or real semantics in the original sandbox. Exact typed input branch `handoff/dossier-shadow-18-assembly-typed` returned **404/not created** at preflight; no existing typed input files/commits can be claimed.
- [Issuer run #39054131983](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39054131983): `workflow_dispatch`, `run_attempt=1`, `actor=kentrap2011-hub`, exact original sandbox branch, successful; the original marker's `issuer_run_id` and frozen `buffer_blob_sha` match. Never reissue this run.
- [Merged PR #230](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230): `state=closed`, `merged=true`, merged `2026-10-20T11:07:22Z`. [Real read-only inspect run #39413937596](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596) on `main` completed successfully: **read-only-inspect SUCCESS**, **manually-gated-candidate SKIPPED**; uploaded `frozen-shadow-18-python-inspect` artifact (ID `12260293764`). Job log independently displays the Python assertions and result: `{'ready': 12, 'research_not_submitted': 4, 'research_transport_invalid': 2}`, `len(rows)==18`, `semantic_attempts==0`, no canonical acceptance/Deep readiness. This is strong real GitHub CI evidence, **not** this auditor independently running local Python.
- Exact handoff pins: [V1 pins](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_shadow_18_github_python_handoff_pins_v1.json). Issuer, Research marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`, direct-child feasibility authorization `2a726cf6731c0fc1e7bc809474627383c107ef9b`, original Research introduction commits, original buffer and marker are fixed. Inspect CI validates all 14 pinned introduction commits as ancestors of the marker. Status `research_transport_invalid` carries generic `invalid_origin_or_binding`; do **not** assert a specific causal defect based on this generic code alone.

## Original frozen order and item statuses

Original Assembly buffer contains exactly these 18 unique rows in this order, not a new/filtered queue:

| Original group | Pos | AppID | Actual inspect | Original Research introducing commit (if submitted) |
|---|---:|---|---|---|
| 3 | 1 | 1508750 | research_not_submitted | — |
| 3 | 2 | 1517180 | **ready** | `33faf93e578d32dd5e694f72f119041eb102021d` |
| 3 | 3 | 1533420 | **ready** | `4be027d8a26da46ccb3b4887f2cfc89a6517f85d` |
| 8 | 1 | 1590230 | **ready** | `7cb2eed3038a99d8b6af8ad3b36813415979b8dd` |
| 8 | 2 | 1599600 | **ready** | `334251771cbd0c858e7437dbdbae8c9bbb5c39dc` |
| 8 | 3 | 1607130 | research_not_submitted | — |
| 13 | 1 | 1849000 | research_not_submitted | — |
| 13 | 2 | 1857090 | research_not_submitted | — |
| 13 | 3 | 1868140 | **ready** | `162eea9dd2caeefe0e8dae02b82127bf07e9c563` |
| 15 | 1 | 1999170 | **ready** | `abf88e5318422e55915a437ad9b6798c5d22a077` |
| 15 | 2 | 1999360 | **ready** | `37f950419bde189c766eba8a174847b53284cb60` |
| 15 | 3 | 2009010 | **ready** | `90b57935ed598b8d458c839c9a80bee22adbbf04` |
| 18 | 1 | 206420 | **ready** | `73f88b35f7658e9373365489068ae927a75e95b0` |
| 18 | 2 | 2067050 | **ready** | `24dd6b56c50d97e81d7fe1cbb3619a63af71a47c` |
| 18 | 3 | 2076140 | **ready** | `1b5cd015a3a00425f20ca01ae6da4dd43ea40012` |
| 20 | 1 | 2124120 (SULFUR) | research_transport_invalid | `cef43773d710b2d87c4c75c648d690b36def386f` |
| 20 | 2 | 213610 | **ready** | `9049a4df4766e25a4ae8053200465096323b6b99` |
| 20 | 3 | 2138710 (Sifu) | research_transport_invalid | `af470aad964c1f20afebca2d25dd2347b2ddc668` |

**Counts:** 12 technically ready, 2 transport-invalid, 4 not submitted. The two invalid entries are not equivalent to missing and do not authorize re-Research. Ready means structural strict Research transport eligibility, not high-quality validated evidence and not approval for semantic work. Original group order is `3,8,13,15,18,20`; never compress the frozen 18 to a new 12-item manifest.

## Authority: current NO-GO and prospective gate

**Negative existing authority:** `config/dossier_shadow_research_trial_contract_v1.json` expressly says `no_assembly_activation=true`, `standalone_sandbox_semantics_approved=false`, `reviewer_roles_finalized=false`, `no_authorization_from_decision_json=true`. The original Director decision has `actual_semantic_execution_permitted_now=false` and `github_prepared_snapshot_marker_and_transport=false` as historic original state. The Research feasibility direct-child authorization covers **Research feasibility**, not prospective Assembly semantics. Marker-era `config/dossier_shadow_18_assembly_semantic_prompt.md` is explicitly `NOT active today`, not a role grant. These historical bytes must **never** be amended, reinterpreted as newly true, or used as a positive approval source.
 
**Ownership gap:** current [`config/execution_ownership_contract.json`](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/execution_ownership_contract.json) lists only `russian_description_one_shot` and `progressive_deep_one_shot` under `explicit_manual_semantic_worker_chats`, **not** a frozen-shadow Assembly one-shot role. Ordinary interactive developer chat is not a semantic backlog executor. A newly **additive**, explicit nonproduction one-shot entry under `explicit_manual_semantic_worker_chats`, plus a narrowly scoped prospective launcher/contract, can authorize the future actor without altering original frozen negatives, if independently reviewed and merged. The positive contract must bind the exact existing marker, issuer, Research SHAs, frozen row order, typed branch and one-file transport, and require a **fresh explicit user launch** for each run. The developer task/PR by itself is not activation.

**Live gates remain inactive:** current `config/dossier_two_stage_interfaces_contract.json` (`active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`); staging, async-buffer and final-acceptance bridge all have `active=false`. The one-stage production Dossier, canonical writer, accepted cache, Deep, Fast, ranking and UI remain unaffected. No Scheduled Task or new recurring process.

**Reviewer requirement:** the separate independent **reviewer ROLE appointment** (independent A/B side and C side, with privacy/source constraints) must be evidenced before real execution if the prospective gate preserves the Director decision requirement. It is distinct from, and does **not** mean, up-front A/B/C qualitative review/scores for the 18 games: source-quality comparison and pass/fail judgments are **deferred** until after isolated semantic candidate production. Never fabricate appointment, reviewer score or quality approval.

### Go/no-go checklist for developer PR / future invocation

1. **GO prerequisite**: separate current positive exact-scope shadow-only authority in canonical ownership/launch contract, approved via the developer PR, no rewrites of original Research/Director marker-era negative flags. Otherwise **STOP_AUTHORITY**.
2. **GO prerequisite**: original marker `2c2649fb...`, original sandbox, issuer run #39054131983, buffer Git blob `5c7e66db...`, exact research marker/feasibility child, all 14 original submitted Research SHA locators (and four missing) are reverified. Any mutable substitutions, new marker/branch from user-supplied historical authority or mismatch: **STOP_INVOCATION**.
3. **GO prerequisite**: independently evidenced reviewer roles, fresh explicit user invocation, exact 18 immutable manifest, initial semantic file branch state known, no production activation. Otherwise **STOP**.
4. **GO for each ready row only**: source-first bounded Assembly semantics from original submitted Research bytes; exact source revisit for named gaps then at most narrow one-product one-gap lookup if justified; 12 dimensions, work-year/source provenance, privacy and typed diagnosis on uncertainty. No Research repeat, no automatic retry, no made-up source facts. Unready rows are zero-attempt skips; preserve original row order and continue unrelated siblings.
5. **GO for transport only**: validated `outcome,payload,supplemental_operations` exact typed object to `reviews/dossier_shadow_offline/handoff/dossier-shadow-calibration-20261011-6x3/<appid>.json` on `handoff/dossier-shadow-18-assembly-typed`. One Git create-only file per commit; immutable introducing commit/blob, verify new HEAD, success receipt per game. Do not imply canonical acceptance/Assembly sandbox publication from a typed transport receipt.
6. **STOP on drift/collision/failed write**: fresh branch remote tip before each creation, no force, overwrite, rename, rebase, invented retry or silent continuation after uncertain persistence. If a chat context limit/interruption occurs, preserve completed Git receipts and accurately report remaining frozen rows; **never** mark missing work complete.
7. **Manual publish remains separate**: only distinct [`workflow_dispatch(operation=publish)`](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/.github/workflows/validate-dossier-shadow-18-github-python-handoff.yml), human GitHub PR Conversation approval **per AppID**, exact introducing `semantic_commit` plus `expected-semantic-tip`, actor/main/event/attempt checks, immutable expected original sandbox tip and one add-only Assembly candidate to original sandbox. An exposed constant `DIRECTOR_AUTHORIZED_SHADOW_ASSEMBLY_TYPED_HANDOFF` is only a technical phrase, **not human authentication**. No blanket approval, automatic dispatch, canonical ingest or Deep readiness.

## GitHub connector feasibility and exact safety limitations

**Available capabilities proven from the connected GitHub action interfaces (schema + repository push permission):**
- `create_branch(repository_full_name,branch_name,sha|base_ref)` creates an exact ref; `create_file(...,branch)` performs a GitHub Contents create-only UTF-8 write and returns commit SHA. `fetch_file`, `fetch_commit`, `fetch` (branch/tree/commits), combined read-only APIs can confirm branch, path, Git blob and introducing commit. The account has `push=true` in the exact repository; these are **connector capabilities**, not proof that a real Assembly artifact write was attempted.
- The designated typed branch is **currently absent**. A compliant future initialization needs a separately authorized **GitHub control-plane/operator** branch creation at an explicitly fixed existing commit/ref, with recorded initial branch-tip SHA, no mixed semantic/source/control-plane file modifications. The semantic worker must **not** opportunistically create an arbitrary branch as a recovery shortcut. After initialization, each exact typed JSON file can be create-only committed separately. No test branch/result/sample semantic file was created in this QA.
- The actual `scripts/dossier_shadow_18_github_python_handoff.py` validates remote tip, frozen sandbox descent, exact marker-era Python checkout, original `inspect`, typed schema/size (`<=2,000,000` raw bytes), a create-only result-introducing commit and unchanged blob at fetched handoff branch tip. Workflow `publish` additionally ensures original sandbox commit extends exact expected remote tip and refuses non-fast-forward pushes. Synthetic tests `scripts/test_dossier_shadow_18_github_python_handoff.py` test paths, invalid A vs valid B/C, tampering and races.
- **Not yet a guaranteed GitHub-enforced global traversal order:** `original_order_gate(state, appid)` checks `status == ready`, not proof of submission of preceding ready AppIDs. `semantic_submission` validates one selected introducing commit but does not audit the complete typed branch as an append-only 18-row ledger with globally monotonic item order. The currently observed workflow technically allows selecting a later ready AppID for publish ahead of an earlier one if separately approved. Future worker prompt **must** require original 18-row traversal, and prospective PR QA must evaluate whether added proof/checkpoints make that order auditable rather than merely a chat promise. Original sandbox per-file integrity **is** checked, but same does not equal global transport traversal enforcement.
- **Per-game Git receipt is technically feasible, not infinite-context guaranteed**: a single expressly authorized chat can work through the 18 frozen rows (12 ready semantics, six zero-attempt skips) without sibling Research receipt waits; **12 semantic games may exceed a finite context/window or tool budget**. The safe contract is explicit verified checkpoint after every game, no hidden fallback, and accurate partial completion on interruption. One physical chat is a feasible target, not an unconditional success guarantee.
- Publish is **not** semantic upload: typed branch only buffers candidate input; `publish` generates/verifies one original Stage-B result in the original sandbox; `submitted_unaccepted_shadow_only` is still nonproduction and no canonical acceptance.

## Allow / deny / safe-fail matrix

| Situation | Decision | Required behavior |
|---|---|---|
| Current preflight, real issuer and frozen inspect | **ALLOW READ-ONLY** | Read only; no dispatch |
| Future PR changes additive explicit nonprod manual role/prompt | **REVIEW BEFORE GO** | Verify positive authority, no historic reinterpretation |
| Same new chat traverses exactly 18 original rows | **CONDITIONALLY ALLOW** | 12 ready semantics in order, independent sibling liveness and per-game receipts |
| Missing Research: `1508750,1607130,1849000,1857090` | **DENY SEMANTICS** | Skip with zero attempts; no Research retry |
| Invalid Research: `2124120,2138710` | **DENY SEMANTICS** | Skip with zero attempts, isolate from siblings |
| New typed handoff branch is absent or branch tip is unproven | **STOP BEFORE WRITE** | Require approved initialized branch; don't fabricate transport |
| One strict typed create-only file on correct ref and exact SHA | **ALLOW AFTER GATES** | Verify commit, byte/path identity and durable Git receipt |
| Duplicate/stale/extra file, unexpected appid, wrong repo, source, year, privacy, semantic format | **DENY / FAIL CLOSED** | No overwrite, no fake success, no retry |
| Chat interrupted or GitHub response uncertain | **SAFE PARTIAL STOP** | Keep prior exact Git receipts, explain remaining work; don't assume submission |
| Publish without separate per-AppID human PR Conversation approval | **DENY** | Do not dispatch even if technical confirmation string is known |
| Production Dossier/Deep/Cache/fast/ranking writes, cron/scheduled task or canonical ingest | **DENY** | Remain isolated, inactive; no production activation |
| Independent reviewer role absent / A/B/C scores forged | **DENY** | Require real appointment, defer qualitative A/B/C scoring |

## Recommended developer CI/security negative tests (PR QA acceptance)

- Positive role narrowly scoped to exact marker/issuer/ready rows, with explicit launch and reviewer role prerequisite; no authority derived from original negative Research/Director docs, no production flags changed.
- Wrong owner/repository, branch, marker parent, issuer identity, non-direct-child feasibility auth, buffer/plan blob or source SHA; fail before semantics/write.
- Foreign or reordered AppIDs, worker-built 12-row alternative manifest, missing/invalid treated as ready, implicit research retry, sibling receipt barrier, second marker, hidden retry.
- Typed handoff branch absent, unexpected initializer, stale remote tip, two writers racing, non-fast-forward, deletion/rename/overwrite, unchanged name but modified blob, duplicate AppID; one semantic Git commit adds anything but its sole approved typed path.
- Entire typed handoff branch has unexpected intermediate commits, non-additive mutations or out-of-order submissions; distinguish strict original order from readiness-only AppID lookup.
- Overlength/untyped payload, bad schema/outcome, invented source, wrong title/year, privacy or raw text, invented A/B/C quality verdict; diagnostic safe fail.
- Main/manual publish on wrong event/actor/attempt, missing separately evidenced AppID consent, wrong `semantic_commit`, expected-tip mismatch, original sandbox drift; no default auto dispatch. Exercise immutable original Stage B builder/verifier and no production artifacts.
- Loss/interruption after game N: first N receipts still durable; remaining rows unsubmitted rather than silently complete; no hidden retry or new semantic work without authorization.

## Other observations / bounded follow-up

- `PROJECT_ROUTES.md` line 532 and `CURRENT_TASK.md` opening still describe PR #230 as draft/in review, while GitHub API confirms **merged**. Updating those navigation/handoff descriptions is a bounded route/current-task hygiene candidate for the responsible developer/operator; this read-only QA did not edit either.
- Additional quality A/B/C and canonical final group acceptance remain separate, inactive processes; no claim is made that the 12 Research packages are source-accurate merely because strict transport is structurally ready.
- The report was saved on a **report-only** branch. The only repository change by Chat 2 is this Markdown report; original sandbox, Research, code/contracts, production, workflow execution and developer branch remain unmodified.

### Final determination

**PREFLIGHT_READY_FOR_PR_QA.** The technical lineage/12-of-18 status and current nonproduction transport isolation are confirmed. **Real semantic Assembly is currently NO-GO**: canonical prospective manual Assembly authorization, verified reviewer-role appointment, approved typed branch initialization, and a fresh explicit user launch are not present. The developer ЧАТ 1 must deliver its own PR; this existing independent ЧАТ 2 will inspect that PR at its exact final head and CI and issue a separate GitHub PR Conversation verdict (no premature approval). The report-only PR must not be mistaken for developer PR approval.

### GitHub evidence index

- [Task](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/WORKER_TASK_DOSSIER_SHADOW_18_INDEPENDENT_EXECUTION_PREFLIGHT_01.md); [trial contract](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_shadow_research_trial_contract_v1.json); [Director decision](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/reviews/dossier_shadow_offline/dossier_shadow_calibration_20261011_6x3_director_decision_v1.json).
- [Original marker-era Assembly prompt](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/2c2649fb98322507cd3758ff0ff7992128f94de0/config/dossier_shadow_18_assembly_semantic_prompt.md); [original Stage B inspect/build/verify](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/2c2649fb98322507cd3758ff0ff7992128f94de0/scripts/dossier_shadow_18_assembly_stage_b.py); [actual Assembly buffer](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/9782ab8492aadc744c23ec0425abf8d2d877590e/reviews/dossier_shadow_offline/trials/dossier-shadow-calibration-20261011-6x3/assembly_buffer.json).
- [Original issuer #39054131983](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39054131983); [merged PR #230](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230); [real inspect #39413937596](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596); [report’s input pins](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_shadow_18_github_python_handoff_pins_v1.json).
- [handoff Python](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/scripts/dossier_shadow_18_github_python_handoff.py); [workflow inspect/publish](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/.github/workflows/validate-dossier-shadow-18-github-python-handoff.yml); [transport tests](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/scripts/test_dossier_shadow_18_github_python_handoff.py); [inactive canonical interfaces](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_two_stage_interfaces_contract.json).
