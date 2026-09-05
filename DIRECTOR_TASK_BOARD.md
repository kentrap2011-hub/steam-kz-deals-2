# DIRECTOR TASK BOARD

Компактная директорская карта задач проекта `kentrap2011-hub/steam-kz-deals-2`.

`CURRENT_TASK.md` остаётся техническим источником истины, но эта board новее и выигрывает при расхождении статусов.

## Ключевые правила

1. По умолчанию держать два worker-чата занятыми параллельно, если задачи независимы и не конфликтуют.
2. Неясная проблема сначала `READ-ONLY / RECON`, затем отдельный `IMPLEMENT`.
3. Worker-чат удалять только после durable report + Director decision + ближайших user checks.
4. В каждой копируемой worker-команде первая строка явно начинается с `=== ЧАТ N ===`.
5. Номер принадлежит worker-слоту.
6. Не запускать параллельно конфликтующие Taste/ranking IMPLEMENT.
7. Taste Reviewer recommendations имеют VERY HIGH USER PRIORITY.
8. Automation migration идёт по отдельным gated phases; live Codex dispatch остаётся выключен до независимого Phase 2A audit acceptance и последующего explicit Phase 2B enablement.

## Review checkpoint

`system_audit_due: true`.
Audit target: Phase 2A orchestration security/state boundary.
Audit task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2A_SYSTEM_AUDIT_01.md`.
Expected report:
`reviews/system_audits/director-orchestration-phase2a-audit-01.md`.

## Latest completed

### Taste step 2

Report:
`reviews/worker_reports/play-role-and-start-priority-implement-01.md`
Status: `complete`.
Implementation commit: `19ff08128b09b9acb6cbe81f1789e0a5bba294ec`.
Validation run: `33964033846`.

Implemented explicit producer-owned context:
- play role: `main_full`, `secondary_palate_cleanser`, `family_coop`, `unresolved`;
- relative start priority: `high`, `ordinary`, `low`, `unresolved`;
- both remain separate from fit and sale urgency;
- ranking math unchanged;
- no wishlist/commercial bridge yet.

### Automation Phase 2A

Report:
`reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`
Status: `complete`.
Validated head: `bd0b8ad88f8c1f6b8ba4f8ac7da628df2e51be6c`.
Validation run: `33964008655`.
Validation job: `101300745779`.
Artifact: `9968832310`.

Implemented:
- single future state writer/controller;
- immutable intake/revision/attempt/lease semantics;
- exact task/blob/base/report binding;
- READ-ONLY RECON/AUDIT worker request/result schemas;
- trusted report publisher boundary;
- future pinned `openai/codex-action` template with LLM read-only permissions;
- real dispatch disabled;
- no OpenAI/API key used.

Independent audit required before Phase 2B or user secret provisioning.

## Active next pair

### ЧАТ 1 — Taste step 3: reconsideration + wishlist good-deal bridge

Task:
`WORKER_TASK_RECONSIDERATION_COMMERCIAL_BRIDGE_AND_WISHLIST_IMPLEMENT_01.md`
Task ID: `reconsideration-commercial-bridge-and-wishlist-implement-01`
Mode: `IMPLEMENT`
Expected report:
`reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md`
Priority: `VERY_HIGH_USER_PRIORITY`.
Status: `ready_continue_existing_chat_1`.

Goal:
- wishlist + canonical genuinely good deal may bypass only ordinary non-negative/insufficient Taste eligibility;
- `reconsiderable` may become purchase-worthy through credible commercial/package value;
- `confirmed_negative` and direct confirmed conflict remain non-overridable;
- preserve Taste evidence state, role/start priority, risks and provenance;
- reuse existing good-deal authority, no new discount threshold;
- giveaways and final ranking weights unchanged unless mechanically necessary.

After step 3, one independent current Taste Review is mandatory before final material acceptance of the combined three-step sequence.

### ЧАТ 2 — independent Phase 2A System Audit

Task:
`WORKER_TASK_DIRECTOR_ORCHESTRATION_PHASE2A_SYSTEM_AUDIT_01.md`
Task ID: `director-orchestration-phase2a-system-audit-01`
Mode: `READ-ONLY / AUDIT`
Expected report:
`reviews/system_audits/director-orchestration-phase2a-audit-01.md`
Status: `ready_new_chat_2_independent_auditor`.

Goal:
- independently verify single-writer, lease/revision/stale-result protections;
- verify worker cannot write GitHub/state/product files;
- verify trusted publisher path confinement;
- verify exact immutable Codex Action pin/provenance and read-only worker permissions;
- verify dispatch still disabled;
- decide whether user may provision `OPENAI_API_KEY` and whether one bounded Phase 2B READ-ONLY pilot is safe.

The Phase 2A implementation Chat 2 must not self-audit; delete it and use a fresh independent Chat 2.

## Taste sequence

1. evidence state/confidence/reconsideration — complete internally;
2. play role + relative start priority — complete internally;
3. reconsideration commercial bridge + wishlist-good-deal override — active next;
4. independent current Taste Review — mandatory after step 3 before final acceptance.

## Automation sequence

- Phase 1 shadow observer — implemented + audited accepted.
- Phase 2A security/state boundary — implemented, audit pending.
- Phase 2B live READ-ONLY worker pilot — not authorized yet.
- `OPENAI_API_KEY` — do not provision until Phase 2A audit acceptance.
- Autonomous IMPLEMENT remains out of scope.

## Steam access policy

User approved:
- Steam Web API key for read-only `GetOwnedGames`: yes;
- authenticated Steam Store session for personalized Complete The Set payable price: no for now.

DLC ownership eligibility remains queued. Personalized Complete The Set actual payable price remains fail-closed/unknown.

## Other queued

- `WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md`.
- DLC ownership eligibility IMPLEMENT.
- `WORKER_TASK_TOP_SUMMARY_FILTER_BUTTONS_01.md`.
- `WORKER_TASK_MOBILE_FEED_REGRESSION_GATE_01.md`.
- `WORKER_TASK_GIVEAWAY_ITAD_IDENTITY_IMPLEMENT_01.md`.
- Russian-language availability ranking factor.
- YouTube review selection.
- modern Windows compatibility evidence.
- semantic/Russian-description completion remains blocked on existing scheduled semantic runtime evidence; do not create another scheduler.

## Next decision

1. Continue existing Chat 1 with Taste step 3.
2. Delete Phase 2A implementation Chat 2 and create fresh independent audit Chat 2.
3. After Chat 1 report, launch independent Taste Review before final Taste acceptance.
4. After Chat 2 audit acceptance, instruct user to provision `OPENAI_API_KEY` directly in GitHub Actions Secrets and then prepare one bounded Phase 2B live READ-ONLY pilot.
