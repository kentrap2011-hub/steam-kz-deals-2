# Worker report — Dossier original 18-game real sandbox Research feasibility gate

Task: `WORKER_TASK_DOSSIER_SHADOW_18_REAL_RESEARCH_FEASIBILITY_GATE_01.md`  
Worker: **НОВЫЙ ЧАТ 1**; mode **IMPLEMENT / isolated PR; no self-merge**  
Repository: `kentrap2011-hub/steam-kz-deals-2`; base `main`  
Original implementation base commit: `4cfa6ec3d35e49183b8808e3ba308f744b889ace` (not a launch SHA)  
PR: pending CI/link finalization. No semantic Research/Assembly performed.

## Decision and architecture preflight

- Current owner of all GitHub scope, immutable original group bindings, Research buffer, run-start marker, issuance/validation/retries: GitHub control plane, per `config/execution_ownership_contract.json`; interactive developer must not become the semantic worker.
- Original `scripts/dossier_shadow_research_trial_publish.py` and `frozen_trial` retain exact semantics and **MUST return `blocked`** under `standalone_sandbox_semantics_approved=false` and `reviewer_roles_finalized=false`. No change to original strict publisher or the six-group/18-item selection.
- User approval dated 2026-10-14 permits **only a bounded nonproduction feasibility Research evidence run** without first appointing independent quality reviewers A/B/C. Production adoption still requires independent A/B + C quality comparison, explicit later authorization and separate cutover.
- New `config/dossier_shadow_research_feasibility_contract_v1.json` creates no production authority, recurring stage, retry/recovery, semantic queue, browser/Deep/ranking work or Scheduled Task. The separate one-shot feasibility authority is a GitHub-owned direct-child commit, not an amendment to the old publisher marker.

## Implemented two-phase finite usable path

1. **Original freeze (unchanged):** Director, after merge, explicitly dispatches existing `Publish frozen Dossier 18 Research trial (manual, once)` on `main`; `expected_main_sha` must be freshly fetched 40-hex current head and `confirmation=PUBLISH_DOSSIER_SHADOW_18_ONCE`. Output branch `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research` contains exact frozen `research_buffer.json` then a later *single-parent marker-only* `run_starts/<nonce>.json` commit; no one may repeat/repair an unsuccessful attempt through chat. Must verify real Action success, marker/ref and strict marker/buffer relationship.
2. **Separate feasibility authorization:** Director explicitly dispatches new `Authorize Dossier 18 sandbox Research FEASIBILITY (manual, once)` on `main` after real original frozen marker publication. Inputs: fresh `expected_main_sha=<current exact main 40-hex SHA>`, `original_marker_commit=<exact real 40-hex original marker HEAD>`, `confirmation=AUTHORIZE_DOSSIER_SHADOW_18_FEASIBILITY_ONCE`. GitHub Action requires exact main workflow context, first run attempt, unchanged pinned predeclared contract/prompt/verifier Git blobs at original marker parent and exact remote sandbox marker; it executes `frozen_trial` (must remain `blocked`), then appends ONE added fixed `authorizations/research-feasibility-v1.json` path in ONE direct child commit of the exact marker, pushed with exact old-SHA lease. Subsequent dispatch/rerun is rejected. Authorizing commit includes buffer/blob/original contract/legacy prompt/new contract/new prompt/verifier/schema/source-original-marker/nonce/18 exact AppID/quality-inactive hash bindings; neither full A/B/C review nor older source audit required.
3. **Explicit semantic launch only after real GitHub proof:** Director opens a **NEW separate manual Research semantic chat**, not either IMPLEMENT worker, using the exact prompt `config/dossier_shadow_research_feasibility_one_shot_prompt.md` frozen at original marker parent and supplies all **three** concrete GitHub-resolved bindings. Before Research, `authorized_trial` must verify remote first-parent chain and content; it alone returns `sandbox_research_invocation_ready`; original `frozen_trial` still returns `blocked`. Original 18 records, exact six groups, twelve Research dimensions, source/year/identity/privacy, create-only per-item isolated Git output and nonacceptance are unchanged.

### EXACT copyable later manual Research launch (ONLY once both GitHub publications are real)

```text
Ручной одноразовый sandbox Research нового Dossier — 18 исходных игр.
Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: original frozen GitHub marker parent, NOT mutable main.
Это НЕ developer-чат, НЕ Scheduled Task и НЕ production worker.
Полностью прочитай CHAT_PROTOCOL.md, CHAT_CONTEXT.md и
config/dossier_shadow_research_feasibility_one_shot_prompt.md
из исходного marker parent и выполни их без отклонений.
shadow_marker_commit=<ACTUAL_40_HEX_FROM_FIRST_GITHUB_ACTION>
research_buffer_path=reviews/dossier_shadow_offline/trials/dossier-shadow-calibration-20261011-6x3/research_buffer.json
research_feasibility_authorization_commit=<ACTUAL_40_HEX_FROM_SECOND_GITHUB_ACTION>
Сначала независимо проверь оба реальные GitHub коммита, freeze marker,
18 exact frozen assignments и readiness через
scripts/dossier_shadow_research_feasibility.py::authorized_trial;
если подтверждения нет — BLOCKED, 0 Research/0 writes.
Никаких собственных игр, маркеров, очередей, повторов, recovery или выбора источников
из старых кэшей. Исследуй один раз 18 исходных игр в точном порядке и по схеме;
на каждую завершённую валидную игру — только отдельный create-only Git файл
на исходной sandbox ветке, с независимой строгой проверкой и без отметки accepted.
Не меняй production, Deep, Fast, ranking, Assembly, Scheduled Tasks.
По завершении сообщи реальные тайминги, отправленные/неотправленные/непринятые;
остановись.
```

The placeholder strings are **NOT** an authorization. Do not send this to a semantic worker or invent SHA values until both real GitHub Actions have finished successfully and independent GitHub ref/commit proof has been inspected. The entire existing original publisher must remain intact.

## Checks and outcome

- Preflight: isolated nonproduction sandbox authority; separate reviewers A/B/C are **later quality gate**, NEVER implied passing.
- Tests: `scripts/test_dossier_shadow_research_feasibility.py` (synthetic local Git only) plus existing `scripts/test_dossier_shadow_research_trial_publish.py`, `scripts/test_dossier_shadow_research_trial.py` and existing PR-only strict original 6×3 buffer/marker test. Negative: wrong marker/parent, missing authorization, changed original trial contract/prompt/new feasibility contract/prompt/verifier/buffer, extra path, collision, wrong 18 items, dispatch/rerun guards and no remote head authorization. Existing Research strict validator covers unsupported sources/privacy, raw source attribution, identity and twelve dimensions.
- PR-only validation workflow extended; no new recurring CI job or scheduled work.
- Actual live GitHub Actions effective write-token/branch permission not yet exercised and not asserted PASS; original sandbox branch absent at task start.
- PASS/FAIL CI receipts: **to be completed from real PR checks**; no fixture is claimed as real live marker/Research.
- Changed files confined to new isolated feasibility contract/prompt/verifier/action/tests, the preexisting PR-only publisher validation workflow and this worker-report. No change to original publisher, production data/cache/inbox/control, old Dossier flags, Deep, Fast, ranking, site, Assembly-owned files, Director Board or CURRENT_TASK.

Status before CI: **implementation prepared for isolated PR validation**, not real semantic permission. Director next: review/merge PR, then explicitly publish original marker ONCE, separately authorize feasibility ONCE, then launch new Research chat with three verified real GitHub bindings. No automatic transition and no self-merge.
