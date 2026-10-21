# ЧАТ 3 — Research Notes V2 / autonomous Assembly implementation report

**Task:** `research-assembly-notes-v2-autonomous-assembly-implement-01`  
**Status:** `INACTIVE_IMPLEMENTATION_PR_READY_FOR_INDEPENDENT_QA` (not QA-approved)  
**Repository:** `kentrap2011-hub/steam-kz-deals-2`; source `main` at merged PR #237 SHA `a2f734d15dddfe870927c7bd484050b73594ec10`.  
**Branch:** `implement/research-notes-v2-autonomous-assembly-01`, [draft PR #239](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/239). No merge or production activation.

## START and architecture preflight

Full CHAT_PROTOCOL, CHAT_CONTEXT, current explicit task and Board/registry checked; Director Board says AUTHORIZED_READY_FOR_WORKER and registry status is authorized_ready_for_worker. Reference full PR #235 design, PR #234 and independent PR #232 CHANGES_REQUIRED. GitHub owns original scope, Git marker, immutability, privacy, typed item dispositions and eventual strict acceptance; semantic workers remain bounded independent data plane, and interactive developer never runs them. Additive inactive versioned schemas are the concrete authorized contract amendment. No recurring worker, new queue/retry, quota or transfer of control-plane authority.

## Implemented in branch

1. New inactive `config/dossier_research_notes_v2_contract.json` and minimal `config/dossier_research_notes_v2.schema.json`. UTF-8 JSON notes permit empty notes, no sources, unknown original year, absent dimensions; includes honest worker-claimed source access and optional conflicts/unknowns. No semantic completeness gate. SULFUR source-role confusion and Sifu `www`/2022–2023 contradiction are Assembly questions, not Stage1 transport failures.
2. `scripts/dossier_research_notes_v2.py` checks 18 exact old AppIDs in the original group order 3/8/13/15/18/20, original baseline/marker/authorization pins, new exact marker parent and frozen manifest Git bytes. Prepared Notes include marker/manifest blob, per-item AppID/index/title/assignment; original Research introduction must be one-parent one-add with verified SHA/blob/raw and uninterrupted first-parent ancestry. Unsafe locators, personal identifiers, raw content, bad Git proof and wrong assignment fail item-locally. Submission without bytes is explicitly missing/unknown, never a fictitious semantic failure.
3. Versioned `scripts/dossier_two_stage_versioned.py` provides explicit V1 unchanged versus new V2 dispatch; future Notes V2 Research/Assembly instructions are in dedicated **INACTIVE** prompt siblings. The old strict V1 schema, parent/child checks and buffer/worker entrypoints are **not loosened**; no automatic V1 → V2 migration.
4. V2 Assembly accepts original unaccepted **safe** Notes transport as leads and permits independent discovery, source revisits, contradictions, no named gap ID or mandatory first-source rule; returns strict V2 dossier only if independently justified, otherwise separate terminal statuses. Max two prepublication in-invocation mechanical corrections. The existing `validate_dossier_strict` runs before an item can be proposed for create-only submission and is repeated at GitHub-style item inspection; original 3-item group readiness is reported but **not** canonically accepted. No new writer.
5. Typed `DOSSIER-NOTES-V2-ITEM-RECEIPT` schema + offline GitHub-bound blueprint records local dispositions with unknown semantic attempt state and no acceptance claim. Actual GitHub receipt attestation/persistence is **not** invented in this offline PR.
6. Stable original authorized typed-publish order helper demonstrates two sequential publishes when first target becomes `candidate_already_submitted`; fails duplicates/wrong order/nonready target. Requires independent verified GitHub reviewer A/B/C account IDs and Director approval callbacks; username regexp alone is explicitly insufficient. **PR #232 itself remains unmodified and blocked by its separate QA verdict.**

## Synthetic tests / evidence

- [V2 PR Actions run 39645191028](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39645191028), code HEAD `0e2b2a7adee39fa59f192aa410f9a8132e6c8549`: **21 tests PASS**; marker, manifest, wrong binding, 18-order, sparse notes, SULFUR/Sifu, unsafe/public locators, too many self-corrections, interruption vs semantic insufficiency, immutable Git first-parent, two sequential publishes, strict invalid Dossier and reviewer identity gates.
- [Existing Dossier chain Actions run 39645191025](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39645191025): check result against final PR HEAD; avoid claiming a semantic run.
- PR-only workflow `.github/workflows/validate-dossier-research-notes-v2.yml` uses read-only checkout, synthetic disposable local Git histories and `jsonschema`; no workflow_dispatch and no external access. All other installed production activation flags stay false.

## Important compatibility limits and risks

- This is **offline developer implementation**, not an activated V2 GitHub Actions issuer or actual new frozen 18-game semantic launch. No actual marker, Research notes for a real game, Assembly dossier, receipt persistence or canonical Dossier/Deep group acceptance was written. The pure future manifest proposal must be separately issued under owner-controlled GitHub authorization before any real invocation.
- No claim that a human has independently verified source truth or reviewer appointments. `verify_independent_reviewers` is fail-closed unless a future caller provides authenticated GitHub identity lookups and truly verified Director appointments. Independent QA should insist this is not silently skipped in a future live workflow.
- V2 immutable-publish order logic is scoped to this new version; original PR #232 must be fixed/independently re-reviewed separately before it can merge. It is unsafe to interpret V2 tests as retroactive PR232 correctness.
- Real-world source reliability, RU search coverage, 12 final dimensions and three-member same-group true equivalence remain future semantic/QA acceptance work. Old V1 original 12-ready/2-invalid/4-missing evidence has not been overwritten, cleaned or rebased into new V2.

## Independent QA requested

1. Check START authorization, inactive flags, no production/workflow dispatch/schedules, unique namespace and old frozen marker/baseline unchanged.
2. Reproduce 21 synthetic V2 tests at exact latest PR HEAD; inspect the Git fixture first-parent ancestry, marker+manifest immutability and duplicate/wrong binding refusal.
3. Verify safe zero-source/no-year Notes reaches the Assembly frontier without V1 Research acceptance, and that SULFUR role and Sifu hostname/year are not silently normalized into facts.
4. Reject unsafe personal/profile/localhost and raw review payloads. Probe Unicode, unknown dates, invalid URL ports, marker changes after Git introduction and current HEAD races.
5. Review independent Assembly source operations (not named-gap-bound), two correction cap, honest terminals, exact final strict validator, and no canonical acceptance from a single item.
6. Trace typed prefix across publish A then B after A is no longer ready; inspect PR232 compatibility note, never merge PR232 because of this helper alone.
7. Demand authenticated independent real reviewer identity and owner appointment checks in any future live launcher; this offline interface is not itself an appointment.
8. Recheck existing V1/two-stage and one-stage tests and all same-HEAD PR CI, then post PASS_FOR_DIRECTOR_REVIEW or CHANGES_REQUIRED. No real Research/Assembly/publish run during QA.

**No scheduled tasks, semantic runs, production changes, original trial artifact edits, Deep/Fast/ranking/site changes or merges performed.**
