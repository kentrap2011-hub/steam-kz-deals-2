# WORKER TASK — TASTE DOSSIER CONTRACT CONTRADICTION AUDIT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-contract-contradiction-audit-01`
Mode: `READ-ONLY DIAGNOSTIC`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- strict validator / compact provenance / binding compatibility code paths;
- relevant TASTE decisions in `PROJECT_DECISIONS.md`, especially recent evidence/provenance/source decisions;
- recent accepted reports:
  - `reviews/worker_reports/taste-dossier-semantic-consistency-gaps-implement-01.md`;
  - `reviews/worker_reports/taste-dossier-russian-existence-retrieval-gate-implement-01.md`;
  - `reviews/worker_reports/taste-dossier-russian-multi-source-retrieval-implement-01.md`;
  - `reviews/worker_reports/taste-dossier-transient-author-dedupe-fallback-implement-01.md`;
  - `reviews/worker_reports/taste-story-dlc-scope-policy-implement-01.md`;
- current task `WORKER_TASK_TASTE_DOSSIER_STEAM_STORE_REVIEW_CARD_PARENT_FIX_01.md` only to understand the known contradiction being fixed by Chat 1.

Do NOT inspect unrelated repos or unrelated product areas.

## Purpose

Parallel diagnostic only.

Chat 1 is currently implementing the known Steam Store review-card parent fix.

This Chat 2 must search for **other similar internal contradictions** in the active Taste Steam Review Dossier evidence pipeline.

Target pattern:

> A newer narrow rule intentionally permits a valid evidence path, but an older broader schema/contract/prompt/validator/provenance restriction still rejects the same path for a different reason.

The known Crown Trick Steam Store parent contradiction is the example, not the target. Do not duplicate Chat 1's implementation work.

## Scope

Audit only active dossier evidence semantics and their validation/serialization compatibility.

Check the interaction between:
- stable locator records;
- transient-author fallback records;
- parent collection/source surfaces;
- Steam/non-Steam source classification;
- aggregate vs concrete feedback;
- Russian existence/retrieval states;
- exact product/appid binding;
- language binding;
- publication date / recency rules;
- observation/conflict binding;
- mention_count / recurrence strength;
- compact provenance / privacy;
- source↔child physical provenance;
- source↔child temporal coherence;
- fallback local ids/source ids;
- content-complete compatibility/binding;
- buffered create-only candidate validation where evidence schema changes matter.

Do NOT audit:
- ranking;
- pricing;
- package economics;
- giveaway;
- UI;
- story-DLC classification except for direct interaction with dossier evidence identity;
- production scheduling;
- retry/healing architecture;
- unrelated Taste Semantic Producer logic.

## Diagnostic method

Do not perform a repository-wide speculative bug hunt.

Instead build a compact rule-interaction matrix around active evidence modes:

1. normal stable-locator player feedback;
2. transient-author fallback on non-Steam collection parent;
3. transient-author fallback on Steam Store exact-product parent after Chat 1's intended fix;
4. direct profile-scoped item inspected transiently but profile identity not persisted;
5. mixed stable + fallback evidence;
6. Russian found-and-used via fallback;
7. old/recent feedback split;
8. exact product identity when source URL exposes appid;
9. source parent containing multiple concrete child items;
10. duplicate/alias physical feedback encountered through multiple surfaces.

For each mode, trace:
- schema acceptance;
- prompt permission;
- evidence contract;
- strict validator;
- compact provenance;
- recurrence/count derivation;
- language/date binding;
- compatibility revision/binding.

Look specifically for mismatches where one layer permits and another layer rejects or interprets differently.

## What counts as a real contradiction

Report only issues meeting all three:

1. two active canonical rules/components disagree about the same intended case;
2. the case is reachable in normal production/retrieval, not purely hypothetical;
3. the disagreement can cause false rejection, false acceptance, wrong count/strength, privacy leak, or incompatible serialization.

Do NOT report:
- deliberate fail-closed policy;
- known design tradeoff with matching validator behavior;
- style inconsistencies;
- merely duplicated wording;
- unreachable fixture-only cases;
- the known Crown Trick Steam Store parent issue already assigned to Chat 1, except as a reference baseline.

## Required output per finding

For each confirmed finding provide:

- ID: `CONTRA-01`, `CONTRA-02`, ...
- Plain-language description.
- Exact intended valid/invalid case.
- Rule/component A.
- Rule/component B.
- Why they conflict.
- Production consequence.
- Severity:
  - `blocking`
  - `silent_semantic_error`
  - `privacy_risk`
  - `strength_count_error`
  - `compatibility_risk`
- Whether current g000001 can hit it.
- Minimal fix direction (design only, no implementation).
- Whether fixing it would weaken an intentional guard.

Rank by actual production impact, not code cleanliness.

## Negative-result requirement

If no additional real contradictions are found, say so explicitly.

Do not invent findings to justify the audit.

A clean result is valid:
`no_additional_material_contradictions_found`.

## Current live context

Use the current canonical state from main at audit time.

Recent authoritative live result:
- transient-author fallback worked for Hellish Quart and Tetris Effect;
- Crown Trick was blocked because concrete Steam Store review cards could not use the Store app page as parent source;
- Chat 1 is fixing that exact issue now.

Do not assume the snapshot/binding remains unchanged; read current canonical state only as needed.

## No implementation

This task is READ-ONLY diagnostic.

Allowed repository write:
- only the required durable report.

Do NOT:
- edit config/contracts/schema/prompt/scripts/workflows/tests;
- create PR;
- merge code;
- trigger activation;
- run Scheduled Task;
- modify CURRENT_TASK unless CHAT_PROTOCOL explicitly requires a diagnostic handoff and it can be done without interfering with Chat 1. Prefer not to change it.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-contract-contradiction-audit-01.md`

Required sections:
1. Task / repo / mode.
2. Audit boundaries.
3. Current canonical evidence modes reviewed.
4. Known Chat 1 contradiction excluded from duplicate finding list.
5. Rule-interaction matrix summary.
6. Confirmed findings, ordered by production impact.
7. For each finding: exact conflicting rules/components and consequence.
8. Current g000001 exposure.
9. False positives considered and rejected.
10. Areas checked with no contradiction.
11. Status.
12. Exactly one recommended next step.
13. Efficiency / reusable lesson.

Allowed statuses:
- `complete_findings`
- `no_additional_material_contradictions_found`
- `blocked`

## Exactly one next step

If findings exist:
- recommend Director compare this report with Chat 1's completed fix before opening any new implementation task.

If no findings:
- recommend Director proceed with Chat 1 acceptance/live test only.

Do not implement fixes inside this audit.
