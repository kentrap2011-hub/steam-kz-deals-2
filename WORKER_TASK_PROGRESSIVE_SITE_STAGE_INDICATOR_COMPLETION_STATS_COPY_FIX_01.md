# WORKER TASK — PROGRESSIVE SITE STAGE INDICATOR COMPLETION + STATS COPY FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard: do not search, read, change, or use any other repository. If GitHub/tool opens another repository by default or the repository target is ambiguous, stop and switch to `kentrap2011-hub/steam-kz-deals-2`.

Task ID: `progressive-site-stage-indicator-completion-stats-copy-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

## User authorization

The user explicitly approved the follow-up UI correction after visually inspecting the deployed Statistics page.

Keep exactly three stage indicators on cards. Do not add extra visible state symbols or badges. A stage indicator should visually “light up” only when that stage is actually complete.

The user also approved replacing confusing technical/statistical wording with clear Russian wording and clarifying how processed/incomplete/error counts relate.

## START

First open the current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read this task fully.

Use the current accepted site implementation and canonical stage/statistics fields. Read only the minimum files needed, expected mainly:
- `web/progressive-personalization-ui.js`
- `web/app.js`
- `web/styles.css`
- `web/index.html`
- relevant web/UI regression tests
- `config/progressive_personalization_contract.json` for semantics only

Do not change producer/business semantics unless the current UI cannot express the already published canonical truth without a minimal presentation-only projection change. No such producer change is expected.

## Architecture preflight

Before editing, record:
1. GitHub remains owner of Fast/Dossier/Deep stage truth and aggregate counts.
2. Browser remains presentation-only.
3. This task changes only visual activation semantics and user-facing copy.
4. No queue, retry, scheduler, worker, semantic outcome, denominator, ranking, attempt accounting or recovery ownership changes are authorized.

## Required UI correction

### 1. Keep exactly three card indicators

Every visible card keeps exactly the existing three stage indicators:
- Fast / Быстрый разбор
- Dossier / Подготовка досье
- Deep / Глубокий разбор

Do not add visible `✓`, `!`, `×`, ellipsis, counters, text badges or a fourth indicator.

Tooltips/titles may continue to explain the detailed state, but visible card chrome must remain three compact icons only.

### 2. “Lit” means completed stage only

The visual “lit/active/bright” treatment must mean stage completion, not merely attempted/pending/incomplete/error.

Exact completion mapping:

- Fast indicator is lit **only** when:
  - `fast_stage_state === "completed"`, and
  - `fast_stage_outcome` is `fit` or `not_fit`.

- Dossier indicator is lit **only** when:
  - `dossier_stage_state === "accepted"`.

- Deep indicator is lit **only** when:
  - `deep_stage_state === "completed"`, and
  - `deep_stage_outcome` is `fit` or `not_fit`.

All other states are visually unlit/dim, including:
- not started;
- waiting;
- eligible/pending;
- incomplete;
- error;
- failed/recovery;
- recovery-owned / recovery-eligible / recovery-pending;
- unknown/unpublished.

The detailed tooltip may distinguish those states, but the icon itself must not look completed.

Do not infer completion from `analysis_state`, attempt counts, history or legacy generic fields.

### 3. Statistics wording: remove technical jargon

Remove user-facing English/internal wording such as:
- `authoritative`
- `Fast-scope`
- `Dossier-scope`
- `Deep-покрытие`

Keep the concepts, but use plain Russian.

Preferred meaning:

Fast section:
- scope label: `Всего игр для быстрого разбора`
- `Попытки` -> `Обработано`
- keep `Завершено: подходит`
- keep `Завершено: не подходит`
- `Не завершено` -> `Не удалось сделать вывод`
- `Ошибки` remains `Ошибки`
- `Пропущено после authoritative Deep` -> `Не требовался: есть готовый глубокий разбор`
- `Осталось` remains `Осталось`

Dossier section:
- scope label: `Всего игр для подготовки досье`
- use plain Russian labels; no English scope jargon.
- preserve the distinction between accepted, pending and failed/recovery.
- do not describe Dossier as fit/not-fit.

Deep section:
- scope label: `Всего игр для глубокого разбора`
- `Попытка первого прохода` -> `Обработано в первом проходе`
- `Authoritative завершено` -> `Окончательно разобрано`
- keep fit/not-fit completed breakdown
- `Не завершено / восстановление` -> clear Russian equivalent such as `Не удалось завершить / требуется восстановление`
- `Готово / ожидает выполнения` -> `Готово к разбору / ожидает`
- `Осталось до полного authoritative покрытия` -> `Осталось до окончательного разбора`
- `Все текущие игры authoritative завершены` -> `Все текущие игры окончательно разобраны`

The exact copy may be refined for layout, but it must preserve these meanings and contain no `authoritative` jargon.

### 4. Explain “Обработано” vs outcomes

Add a short, compact explanatory note in the Statistics view, especially for Fast, so the arithmetic is obvious:

- `Обработано` means the stage has run for that many current-scope games.
- It is the sum of completed fit + completed not-fit + incomplete/no-conclusion + errors.
- `Не удалось сделать вывод` means the Fast worker ran but did not have enough trustworthy evidence for a fit/not-fit conclusion.
- `Ошибка` means a technical/invalid-result class failure, not merely insufficient evidence.

Do not expose raw internal issue-code names unless needed in a tooltip/debug-only surface.

For Deep, make clear that `Окончательно разобрано` is the final authoritative-equivalent concept without using the word `authoritative`.

### 5. Statistics page intro

Replace technical intro text like:
`Fast, Dossier и Deep показаны отдельно — каждый со своим текущим scope.`

Use normal Russian, e.g.:
`Быстрый разбор, подготовка досье и глубокий разбор считаются отдельно — у каждого свой объём работы.`

## Explicit prohibitions

Do not:
- add more card icons/badges;
- change Fast/PASS 1 attempt or outcome semantics;
- change Dossier acceptance/recovery semantics;
- change Deep/PASS 2 completion/recovery semantics;
- change ranking or visibility semantics;
- change producer denominators/count formulas;
- create/edit/run any Scheduled Task;
- perform semantic production work;
- invent frontend semantic fallback from generic `analysis_state`.

## Validation

Prove at minimum:

- FIX-01: exactly three visible stage icons remain on cards.
- FIX-02: Fast icon is lit only for completed fit/not-fit.
- FIX-03: Dossier icon is lit only for accepted.
- FIX-04: Deep icon is lit only for completed fit/not-fit.
- FIX-05: pending/incomplete/error/recovery/unknown states are visibly dim/unlit, not “completed-looking”.
- FIX-06: tooltips may distinguish states without adding visible state glyphs.
- FIX-07: Statistics contains no user-facing `authoritative`, `Fast-scope`, `Dossier-scope` or `Deep-покрытие`.
- FIX-08: Fast `Обработано` is clearly explained as a total of its outcome buckets.
- FIX-09: incomplete/no-conclusion is clearly distinguished from technical error.
- FIX-10: Deep final-completion wording is understandable Russian and semantically identical to canonical authoritative completion.
- FIX-11: Dossier remains neutral evidence-preparation status, not fit/not-fit.
- FIX-12: mobile 360–430px remains compact with no new overflow.
- FIX-13: existing score/explanation/tier/ranking/manual-end semantics remain unchanged.
- FIX-14: relevant UI regressions pass.
- FIX-15: normal visual build/deploy validation succeeds, or any unrelated pre-existing blocker is isolated.
- FIX-16: no Scheduled Task action or semantic production run occurred.
- FIX-17: durable report committed and reread from fresh `main`.

## Durable report

Create and commit:

`reviews/worker_reports/progressive-site-stage-indicator-completion-stats-copy-fix-01.md`

Include:
- verified facts;
- exact files changed;
- exact lit/unlit mapping;
- final user-facing Statistics labels;
- FIX-01..17;
- mobile validation;
- exact run/commit refs;
- unresolved items;
- final status;
- exactly one recommended next step.

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `needs_user_decision`
- `blocked`

Before completion, reread the committed report from fresh `main`.
