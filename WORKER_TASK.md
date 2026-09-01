# WORKER TASK

Task ID: `package-double-count-regression-01`
Mode: `IMPLEMENT`
Report: `reviews/worker_reports/package-double-count-regression-01.md`

## Goal

Закрыть один конкретный пробел, найденный при проверке fixed Steam packages: добавить автоматическую проверку, которая доказывает, что один и тот же контент не считается дважды, если он одновременно входит в Season Pass/edition и виден как отдельный вложенный DLC/content.

Это не новая продуктовая логика и не редизайн системы. Текущее правило уже требует не считать один entitlement дважды; задача — доказать это исполняемым тестом и, только если тест реально выявит баг, сделать минимальное исправление внутри этого узкого места.

## Background

Предыдущая проверка сохранена здесь:

`reviews/worker_reports/package-acceptance-01.md`

Она уже доказала, что основная логика fixed-package valuation, production pre-AI, visual payload, deploy и пользовательская карточка работают для BioShock control case. Единственная незакрытая часть — отсутствующий автоматический тест на двойной подсчёт Season Pass/edition + входящего в него content.

Перед работой перечитай актуальный `main`, `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, `CURRENT_TASK.md`, этот report и релевантные package contracts/tests. Не считай background выше источником истины без проверки.

## What to do

1. Найди существующие package tests, прежде всего:
   - `scripts/test_package_complete_content_value.py`
   - `scripts/test_fixed_package_purchase_options.py`

2. Добавь минимальный тестовый пример, где:
   - Season Pass или edition даёт право на определённый DLC/content;
   - тот же DLC/content также присутствует в структуре так, что наивная рекурсивная оценка могла бы посчитать его отдельно;
   - итоговая денежная/comparable value учитывает этот entitlement ровно один раз.

3. Тест должен проверять реальный итог расчёта, а не только наличие флага, текста правила или строки в коде.

4. Если новый тест проходит на текущей реализации:
   - не меняй production code без причины;
   - зафиксируй только test/regression и validation.

5. Если новый тест выявляет реальный double-count bug:
   - разрешён минимальный fix только внутри этого exact scope;
   - не меняй Taste, ranking weights, package eligibility, fixed-vs-dynamic policy, UI или соседние задачи.

## Validation

Запусти минимум:
- `scripts/test_package_complete_content_value.py`
- `scripts/test_fixed_package_purchase_options.py`

Если штатный bounded validator прямо нужен для этого изменения — запусти его тоже.

Не запускай полный production/deploy только ради добавления теста, если project contract этого не требует.

## CURRENT_TASK

Не закрывай основную fixed-package задачу в этой работе. После успешного IMPLEMENT всё равно нужна отдельная повторная проверка готовности.

Не начинай следующую planned-задачу.

## Done when

- есть исполняемый test на Season Pass/edition + recursive constituent content;
- test доказывает отсутствие двойного подсчёта;
- связанные package tests проходят;
- при найденном баге исправление ограничено только этим узким случаем;
- создан компактный report.

## Report format

Сохрани результат в:

`reviews/worker_reports/package-double-count-regression-01.md`

Структура:

### Task
Что было сделано.

### Verified facts
Что доказано тестом.

### Changes
Какие файлы изменены и зачем.

### Validation
Какие проверки прошли, с точными refs.

### Unresolved
Что осталось.

### Status
Ровно одно:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
При успехе: `repeat fixed-package acceptance`.

Укажи commit SHA. Не копируй большие логи или полный diff.

В финальном ответе обязательно назови путь:

`reviews/worker_reports/package-double-count-regression-01.md`