# ЧАТ 4 — аудит первого этапа Research: убрать техническое заполнение из семантической работы

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Task ID: `dossier-shadow-research-stage1-technical-boundary-audit-01`
Destination: **НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 4**.
Mode: **READ-ONLY / ARCHITECTURE RECON + CONTRACT DESIGN**, not implementation, not Research execution.
Report: `reviews/worker_reports/dossier-shadow-research-stage1-technical-boundary-audit-01.md` on a dedicated report-only branch; optional draft report-only PR. No other GitHub writes.

## START gate

First fully read current `CHAT_PROTOCOL.md` from `main` and execute its START gate. Then read `CHAT_CONTEXT.md`, `DIRECTOR_PROTOCOL.md` as needed for task boundaries, this task, `config/execution_ownership_contract.json`, current original Research/Assembly schemas, worker/runtime prompts, strict validators, transport contracts, trial immutable marker/buffer, and original Research QA findings in [PR #233](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/233) at head `d068f57fb983809906da7e7ac1dd805f32042b98`. Inspect the relevant frozen original 18-game contract and Stage B gates. Work exclusively in this repo; if GitHub opens another repo, stop and switch back.

## User's decision and goal

The two-stage design is meant to free the semantic Research worker from **mechanical technical JSON filling** and keep it focused on investigating games, making source-supported findings and stating uncertainty. The actual frozen 18-game Research failed for two structurally invalid payloads (SULFUR source-role ref and Sifu `www.` domain normalization), four never-published Research payloads, twelve transport-ready. The user wants the **first stage corrected before proceeding to Assembly**, then the **same first stage rerun for ALL EXACT ORIGINAL 18 games**, not only the six failures, with immutable provenance and a separately authorized new execution.

**Do not assume** all semantic source-role judgments can be automated without loss of correctness. Distinguish content judgments (what evidence proves, source identity, game facts) from deterministic mechanical transforms (ID generation, URL normalization, schema serialization, key binding, safe defaults). Preserve strict evidence/privacy validation; don't silently fill missing substantive facts. Diagnose why four items were absent without inventing attempt history.

## Deliverables

1. A field-by-field **Research worker vs GitHub-owned deterministic adapter** responsibility matrix grounded in exact existing prompts, schemas, validators and actual failed packages. Identify every machine-generated or derived technical field that should not be authored by the semantic worker. Distinguish truly required source/evidence semantic statements and optional/unknown data.
2. A bounded end-to-end trace from frozen GitHub assignment -> semantic research -> typed evidence -> mechanical canonical JSON adapter -> strict source/schema/physical validation -> create-only Git transport -> Stage B inspect. Locate exactly where the architecture currently delegates formatting to the model or loses partial/failed results.
3. Explain both concrete invalid cases and all four missing paths with proven vs unknown causes; examine the absence of per-item attempt receipts and whether an authorized GitHub-owned receipt/disposition would prevent unexplained missing items without creating an ad hoc ChatGPT queue/retry manager.
4. Design the **smallest safe prospective architecture correction** with contract changes, deterministic normalizers and strict validators, tests and compatibility boundaries. Explicitly decide where technical fields are generated; ensure no semantic fabrications, no source-role laundering, no relaxing evidence checks, and no changes to frozen historical bytes.
5. Propose an **exact same-18 Research rerun plan**, with the exact original six groups, order, AppIDs, baseline and immutable trial provenance; determine whether a new isolated versioned trial/namespace, marker and new one-shot authorization are required, rather than reusing the old single-use marker/transport. Define acceptance: all 18 receive individually verified outcomes (valid Research or explicit auditable failure disposition); do NOT promise all 18 can be declared valid regardless of real evidence.
6. Analyze implications for open [PR #232](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/232) and its independent QA blocker. Identify what should pause/rebase/redesign, without editing that PR. Recommend bounded next IMPLEMENT task and independent QA criteria, then separately authorized Research rerun.

## Hard stops

No actual Research rerun, semantic worker call, original frozen sandbox mutation, source code/contract/schema implementation, PR #232 edits/merge, Assembly, manual publish, production/cache modification, Scheduled Task, or self-authorization of recovery. Report only. Do not silently treat the historical original 18 as eligible for overwrite. No rerun until implementation, tests, independent QA and explicit user/contract authorization.

Publish exact GitHub report commit/PR and evidence. End with `ARCHITECTURE_RECON_COMPLETE` or `BLOCKED`, proven/unknown split and one next implementation recommendation.
