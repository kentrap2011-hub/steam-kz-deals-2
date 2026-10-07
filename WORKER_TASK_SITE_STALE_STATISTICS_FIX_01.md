# WORKER TASK — Site stale statistics fix 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

## Repository scope guard

Работай только в репозитории `kentrap2011-hub/steam-kz-deals-2`.
Если GitHub/tool открыл другой repo или target неоднозначен — остановись и сначала переключись на этот repo.

## Task ID

`SITE-STALE-STATISTICS-FIX-01`

## Mode

`IMPLEMENT / VALIDATE`

## Background

Продолжение:
`WORKER_TASK_SITE_STALE_STATISTICS_DIAGNOSTIC_01.md`

Durable diagnostic report:
`reviews/worker_reports/site-stale-statistics-diagnostic-01.md`

Диагностика доказала первый причинный stale stage:

current Deep truth доходит до full visual candidate generation, но свежий visual payload отклоняется на gate `Validate generated card explanations` до canonical persistence.

Доказанный текущий пример:
`Tetris® Effect: Connected` — positive player-facing `why_fit` получает commercial/ranking-only wording из accepted Deep finding и валидатор отклоняет такие токены.

Translation block не имеет текущего отдельного stale defect; его наблюдаемые значения совпадают с canonical translation status.

## Goal

Исправить только bounded producer/validator parity так, чтобы свежий Deep-derived visual payload мог канонически сохраниться и затем опубликоваться на Pages, не ослабляя player-facing explanation policy.

## Required implementation

Предпочтительное минимальное направление из diagnostic report:

- accepted Deep score finding, score/provenance и canonical Deep semantics не менять;
- не переносить commercial/ranking-only Deep finding text verbatim в player-facing positive `why_fit`;
- если positive finding непригоден для player-facing explanation, fail closed на уровне presentation: не включать его как positive explanation, а не ослаблять validator;
- добавить regression, воспроизводящий текущий Tetris case;
- сохранить строгий validator, если только exact existing contract не требует иного.

Primary expected implementation surface:
- `scripts/card_explanation_policy.py`;
- focused regression in `scripts/test_card_explanation_policy.py` и/или exact validator regression.

Не расширяй fix на общий rewrite визуальной системы.

## Architecture boundary

Не менять:
- Deep/Dossier semantic results;
- Deep Stage 1 / Stage 2 logic or frozen contracts;
- ranking formula;
- queue ordering;
- translation semantics/state;
- browser fetch authority;
- scheduler/Scheduled Tasks;
- unrelated visual/UI behavior.

GitHub remains the existing control-plane and publication owner.

## Validation

Минимально докажи:

1. regression for current commercial/ranking-only positive finding passes;
2. valid ordinary positive explanations are not accidentally removed;
3. `Validate generated card explanations` passes;
4. exact material binding/freshness validation passes;
5. a current-state full visual cycle can persist a fresh `data/production/visual/current.json`;
6. downstream deploy publishes the same fresh visual state;
7. Statistics Deep counters reflect the same current accounting snapshot used by the build;
8. translation block remains bound to current canonical Russian-description status;
9. result is fresh full-visual success, not `degraded/no_fresh_build`.

Do not run semantic workers just to create test data.

## Deliverables

- bounded implementation branch;
- PR;
- green relevant checks;
- compact report:
  `reviews/worker_reports/site-stale-statistics-fix-01.md`.

Report must state:
- exact code change;
- regression used;
- final relevant workflow/run results;
- persisted visual commit/blob;
- published Pages artifact/run;
- before/after Deep statistics;
- translation regression check;
- any remaining publication lag risk.

## CURRENT_TASK.md

Update only minimal closeout state if required by current protocol. Do not overwrite concurrent sections.

## Completion criteria

Complete only when the original stale Deep publication path is fixed and validated through one fresh current-state visual persistence + deploy path.

## Expected next step

Return to Director for acceptance. Do not start the queued Current Tasks page or any other project task.
