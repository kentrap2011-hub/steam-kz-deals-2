# WORKER TASK — Taste Dossier Live Web Evidence Acceptance 03

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-live-web-evidence-acceptance-03`
Mode: `READ / VALIDATE / ACCEPTANCE`

## Authoritative manual Scheduled Task input from user

Treat the following as confirmed authoritative UI/runtime output from exactly one manual Scheduled Task `Run now` invocation. Do not attempt to re-read Scheduled Task UI state.

> Published three immutable transport artifacts for the current snapshot `d4543076…`:
>
> - Group 1 — commit `3d5296bfbbf54115651b163a30a615f56f06f386`
> - Group 2 — commit `dc6112096728c5fafd1241723b5cb4314590d330`
> - Group 3 — commit `67e4090fb4e322f5046ac630613e3fcf967d9323`
>
> Stopped after group 3 because post-publication review found a contract inconsistency in that artifact: the Sniper Elite 5 dossier declares `russian_attempt:"found_and_used"` but its Russian feedback record is not bound to an observation. Under the create-only contract I did not overwrite, rename, delete, or create an alternate artifact.
>
> Canonical state had not yet advanced during the liveness checks and still reported expected sequence 1 with 591 remaining. Therefore the three writes are transport publication only, not canonical acceptance or completion.

This manual text is sufficient UI evidence. Do not press `Run now` and do not inspect/edit the Scheduled Task UI.

## Goal

Determine the actual canonical and semantic acceptance outcome of the first live run under the new evidence-record binding and 3-item canonical group boundary.

Validate all three published transport groups, not only group 3.

The key questions are:

1. Did the new evidence guard actually improve groups 1 and 2 in live use?
2. Did strict GitHub-owned validation correctly reject the known group-3 Sniper Elite 5 inconsistency rather than silently accepting it?
3. What canonical progress was accepted after the asynchronous GitHub ingestion/drain settled?
4. Did evidence quality remain acceptable across groups 1 -> 2 -> 3 within the same Scheduled Task invocation, or is there still a workload-quality problem despite 3-item transport boundaries?

Do not implement any fix in this task.

## Read first / START gate

Follow `CHAT_PROTOCOL.md` START gate fully, then read at minimum:

- `DIRECTOR_PROTOCOL.md` as applicable;
- `CHAT_CONTEXT.md`;
- relevant `CURRENT_TASK.md` state;
- relevant `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md`, especially active Taste dossier/web-evidence decisions;
- `config/execution_ownership_contract.json`;
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-02.md`;
- `reviews/worker_reports/taste-dossier-evidence-guard-batch3-implement-01.md`;
- active V2 web-evidence contract/schema/prompt and strict/buffered validator only as needed for acceptance interpretation.

Run architecture preflight before any action beyond reading.

## Acceptance target

Canonical fresh snapshot:

`d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973`

Known transport commits from the one manual run:

- group 1: `3d5296bfbbf54115651b163a30a615f56f06f386`
- group 2: `dc6112096728c5fafd1241723b5cb4314590d330`
- group 3: `67e4090fb4e322f5046ac630613e3fcf967d9323`

At the start of the manual invocation the canonical expected sequence was `1` and remaining required count was `591`.

The first nine canonical subjects should come from immutable group descriptors. Do not infer or reorder them manually.

## Validate transport and canonical state

Use repository/GitHub evidence to determine:

1. Each of the three commits created exactly the expected deterministic transport artifact for this snapshot and group sequence 1, 2, and 3 respectively.
2. Each artifact matches the corresponding immutable descriptor/hash/order exactly.
3. No overwrite, rename, delete, alternate artifact, or manual canonical-state rewrite was used by the Scheduled Task invocation.
4. Observe the normal GitHub-owned ingestion/reconciliation outcome after the async workflows settled.
5. Record exactly which contiguous groups, if any, were accepted.
6. Record exact canonical completed/remaining/expected-sequence values after settlement.
7. If group 3 was rejected or blocked, record the exact machine-readable validator/drain reason and prove that canonical progress did not cross the invalid group.
8. If groups 1 and/or 2 were accepted before group 3 blocked progress, verify that this is the intended maximal-contiguous-prefix behavior rather than partial/manual recovery.
9. Distinguish transport publication from canonical acceptance throughout the report.

Do not manually trigger ingestion unless the repository contract explicitly requires a normal automatic run that demonstrably failed to fire; observation is preferred. Do not invent retries.

## Validate the new evidence guard semantically

Audit all nine dossier objects with emphasis on the exact failure classes from acceptance-02.

For every observation verify at least:

- `mention_count` equals the number of distinct bound `player_feedback_ids`;
- those feedback records are attributable player-feedback records, not aggregate storefront counts;
- recurrence is consistent with the bound evidence count;
- each bound feedback record resolves to an allowed `player_feedback:true` source used by that observation;
- aggregate Steam/store counts are not being used as topic-level evidence counts;
- raw review bodies, quotes/excerpts, usernames/profiles are absent;
- plain HTTPS/public-reference rules are respected;
- current-state technical claims have recent current-state support;
- historical/fixed claims have the required temporal support;
- durable claims are not mislabeled as current merely because a recent aggregate/store page exists.

## Russian-feedback acceptance

For every dossier check:

- `russian_attempt:"found_and_used"` is present only when at least one attributable Russian/mixed player-feedback record is actually bound to an observation;
- a Steam Store `?l=russian` page or Russian UI/aggregate counts alone do not satisfy the Russian attempt;
- such pages do not inflate player-feedback `source_mix_status`;
- if no usable attributable Russian feedback was found, the dossier uses `searched_not_found_or_insufficient`;
- Russian-specific localization/translation/voice/font/regional claims are actually supported by Russian player feedback where required.

For the user-reported Sniper Elite 5 inconsistency specifically, determine whether the artifact really has `found_and_used` with an unbound Russian feedback record, and whether the active strict validator catches this exact inconsistency.

## Group-by-group workload-quality audit

The transport boundary is now 3 games, but one Scheduled Task invocation published three groups before stopping. This task must therefore evaluate whether smaller groups solved the quality problem in practice or merely created smaller artifacts while the same chat continued researching more games.

Compare group 1 vs group 2 vs group 3 for:

- evidence completeness;
- recurrence/count discipline;
- Russian-attempt discipline;
- temporal/current-state discipline;
- source/claim binding quality;
- any increase in shortcuts, malformed evidence, unsupported generalization, or omissions later in the invocation.

Do **not** turn this into a subjective score or broad ranking. Report concrete defects/passes and whether there is evidence of degradation across the three groups.

If group 3 contains one known structural rejection but groups 1 and 2 are materially sound, say so clearly. If additional semantic defects exist in groups 1 or 2 despite structural validity, do not rubber-stamp them.

## Interpretation rules

- Transport publication alone is NOT canonical acceptance.
- A canonical strict validator rejection is a successful safety behavior, but it does not make the live semantic run accepted overall.
- If groups 1 and 2 are valid and accepted while group 3 is correctly rejected, distinguish `guard worked` from `live run fully accepted`.
- Do not delete or repair the invalid immutable group-3 artifact in this task.
- Do not manually author a replacement artifact.
- Do not run Scheduled Task again.
- Do not change code, contracts, prompts, schemas, group size, workflows, queue, cache, progress or receipts.
- If the live run reveals a new implementation defect, report it and propose exactly one bounded next step; do not fix it here.

## Acceptance decision

Use one of these final statuses:

- `accepted_live_web_evidence_groups1_3`
- `partially_accepted_guard_worked_group3_rejected`
- `rejected_live_web_evidence_groups1_3`
- `blocked`

Guidance:

- `accepted_live_web_evidence_groups1_3` only if all three groups are semantically and structurally acceptable and canonically accepted.
- `partially_accepted_guard_worked_group3_rejected` if groups 1 and 2 are acceptable/canonically accepted, group 3 is rejected for the known/new guard violation, and there is no material semantic quality failure in groups 1/2.
- `rejected_live_web_evidence_groups1_3` if evidence quality still materially fails in accepted groups or the new guard does not enforce its intended semantics.
- `blocked` only when authoritative repository evidence cannot establish the canonical outcome.

## Durable report

Publish to `main`:

`reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-03.md`

The report must include:

- architecture preflight;
- exact transport artifact path/hash/commit for groups 1, 2, 3;
- exact nine canonical subjects and per-group structural outcome;
- per-group semantic evidence-quality audit;
- Russian-feedback audit, including the Sniper Elite 5 inconsistency;
- exact GitHub ingestion/drain workflow outcome and canonical progress after settlement;
- whether the validator rejected group 3 for the intended reason;
- whether groups 1/2 were accepted as maximal valid contiguous prefix;
- workload-quality comparison across groups 1 -> 2 -> 3;
- exact final status from the allowed list;
- production side effects (observation only; should be no worker-caused production mutation except durable report);
- exactly one next step.

On successful partial acceptance, the one next step should be a bounded IMPLEMENT/RECOVERY task that preserves immutable create-only semantics and defines the correct recovery path for the invalid canonical group 3 without weakening the evidence guard. If the report finds a broader workload-quality failure, the next step should instead target that exact demonstrated defect.

Ensure the durable report is in `main` before completion. Stop after report publication.