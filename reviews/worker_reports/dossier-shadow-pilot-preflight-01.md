# Worker report — Dossier shadow pilot immutable writer preflight (inactive)

- **Physical worker:** НОВЫЙ ЧАТ — ЧАТ 1.
- **Task:** `WORKER_TASK_DOSSIER_SHADOW_PILOT_PREFLIGHT_01.md`.
- **Base:** `main` at `84eee0ae23ace999ae815eccb3646e5d870095d1`.
- **Branch:** `implement/dossier-shadow-pilot-preflight-01`; PR only, not merged.
- **Status:** `offline_preflight_implemented_no_real_pilot`. This is a technical proof interface, **not authorization or actual eligibility of a real cohort**.

## Ownership and architecture preflight

1. GitHub control plane remains owner of original Dossier 3-item scope, snapshot/group progress, strict-V2 acceptance, canonical cache, retry and Deep gates under `config/execution_ownership_contract.json` and `config/taste_steam_review_dossier_contract.json`.
2. The inactive two-stage bridge contract is `config/dossier_two_stage_final_acceptance_bridge_contract.json`: `active=false`, `authorized_for_canonical_ingest=false`, `executable_in_production=false`, `cross_pr_research_original_year_fix_verified=true`. This task adds only isolated read-only QA.
3. No GitHub→ChatGPT ownership transfer, new selector, quota, receipt authority, acceptance writer, recurring stage, waiting loop, scheduler or production workflow. Existing fully async independent Research/Assembly semantics remain unchanged.
4. No Shared/Chat 2 site files, Fast, Deep, cache, production manifests, current scheduler, or `manual-shell-write.yml` were modified.

## Implementation

- `scripts/dossier_shadow_pilot_preflight.py`: caller supplies exact immutable Git HEAD, original Git manifest commit and descriptor/blob, original group sequence, the historical one-stage writer commit and its actual first parent, all three work/AppID/title/original-year identities, three canonical cache writer blobs/content SHA-256, a SHA-256 locator for a writer-appended frozen-invocation acceptance-audit record, and frozen inactive proposal-contract blob bindings. It cannot discover/select groups or launch a trial.
- A **preflight-ready** return requires all of:
  - separately marked disposable Git clone, exact unmodified requested HEAD, first-parent Git ancestry, immutable original manifest/descriptor and exact original ordered three-game group from the existing `validate_manifest`/`validate_group_plan` APIs;
  - historical **pending→accepted** group-progress transition in the declared writer commit without a changed immutable group plan, actual transaction diff for manifest and **all three cache files**;
  - exact append-only `data/audit/taste_steam_review_dossier_frozen_invocations.jsonl` receipt introduced **by that writer commit**, correct receipt schema/outcome/group/snapshot/sequence, valid marker-only commit with actual marker Git parent, matching historical candidate introduction and artifact raw-byte SHA-256;
  - every receipt `persisted_current_group_dossier` AppID + canonical SHA equals exactly the declared unchanged cache blob at both writer commit and frozen target, with the existing `validate_dossier_strict` V2 validator invoked; baseline work year/title checked against explicit original-game identity and canonical `game_identity.release_year/work_title`;
  - unchanged Git blobs of the four inactive Research/Assembly/final-acceptance proposal contracts.
- Invalid Git parent/marker, wrong descriptor/group/order/AppID/year, absent audit receipt, reprinted old audit, unsupported marker, changed HEAD, changed legacy cache bytes or fake schema-valid cache without a real writer transition **raise fail-closed**. No result is ever reported as Dossier or Deep authoritative.
- `scripts/test_dossier_shadow_pilot_preflight.py`: disposable synthetic Git using the existing `drain_buffered_groups` writer and its `_authority_audit_record` record builder; exercises genuine strict-V2 writer transition and adversarial failures. A test-only synthetic writer-audit append emulates the existing frozen-invocation audit in the same Git transaction; this is **not an asserted historical acceptance of any real group**. Existing Research→Assembly original-three-item fixture, strict acceptance bridge and shadow quality tests remain the independent next-stage chain/quality APIs.
- `.github/workflows/validate-dossier-shadow-pilot-preflight.yml`: PR-triggered, read-only, isolated three-suite validation only. No `push`/dispatch trigger, token write permission, live semantic execution or production mutation.

## Real `main` diagnostic (read-only; no games assigned)

The current `data/production/pre_ai/taste_steam_review_dossier_work.json` contains the group-plan, exact group descriptors, group-progress acceptance records, and the 2026-10-11 snapshot; the tracked frozen invocation audit has `dossier_candidate_accepted_current_snapshot` entries with `authority`, `dossier_actions`, AppID and hashes. **No specific real group was sampled or independently matched across all historical commit/cache/action bindings.** A present cache, a progress `accepted` entry, or an audit line in isolation does not establish a historically accepted comparable baseline.

**Known strict limitation:** some legitimate accepted one-stage groups were processed without a frozen run-start audit. Their normal group-progress state may be valid, but the current historical evidence is insufficient for this conservative verifier: they remain **not preflight eligible** here. Also a Git-local audit+transaction cannot cryptographically attest the GitHub Actions runner/actor in isolation. Before **any real use**, an independent operator must corroborate the exact writer commit with the existing GitHub Actions writer run and provenance, as well as the safe source evidence. Do not add a self-attested override bool. A future separate, approved minimum fix, if coverage is inadequate, is an **append-only writer-owned historical receipt for future normal group accepts**, inside the existing shared canonical transaction; never backfill/forge old acceptances or turn it on via this PR. Such a production writer change is **out of scope**.

## Exact later pre-run evidence checklist (NOT APPROVED)

- [ ] User/Director separately authorizes a trial ID, **exact frozen Git baseline** and explicit sample group IDs/size/order. The prospective 6 groups/18 games and 30 groups/90 games in the earlier plan are **not quotas or approved selections**.
- [ ] Frozen group frame and stratum/sampling method/seed, group inclusion/exclusion accounting and full denominator flow are independently approved **before** unblinding semantic outputs.
- [ ] Each group has caller-pinned manifest/descriptor/work/game IDs, writer commit + actual Git parent, verified existing writer run and historical receipt, cache Git blobs unchanged at frozen HEAD, and separately verified true original-work years (not storefront release-year substitution). Missing receipt means exclusion with reason, **never silent group replacement**.
- [ ] Four inactive proposal contract Git blobs bind the exact Research/Assembly interface. Each later Research/Assembly result must independently pass the existing `inspect_original_groups` strict three-game Git chain and `evaluate_offline_fixture` shadow harness; its `baseline_acceptance=not_verified_separate_writer_receipt_required` field must never be promoted on its own.
- [ ] Two independent human reviewers, a disinterested adjudicator, review rubric, safe immutable source access, privacy/source-parent policy, exact material-negative preservation criteria and conflict handling are assigned **before** real outputs.
- [ ] User/Director approves numerical stop/failure thresholds in advance; previously proposed `2/90` is a hypothetical criterion, **not a binding threshold**.
- [ ] Read-only real-source evidence verification, trial dates, exact approvals, rollback/no-cutover plan, and independent GitHub Actions writer run corroboration are recorded; no private/player identities, quotes or review bodies appear in reports.
- [ ] Any proposed `preflight_ready` is only technical evidence. **`quality_verified=false`, `pilot_authorized=false`, `canonical_readiness=false`, `deep_readiness=false`** until separate independent audit, authorizations and later purpose-built approval. No semantics may run under this task.

## Checks / disposition

New and existing fixture suites are exercised by the PR-only workflow. Record the actual workflow conclusion/run URL in PR discussion when available; do not confuse submitted code or synthetic success with a real pilot. A proposal for real trial requires a **new** user-approved task after reviewing missing historical writer receipts.

No real Research/Assembly semantic result, real trial selection or freeze, production/cache/Deep write, scheduled task update or site fix was performed.
