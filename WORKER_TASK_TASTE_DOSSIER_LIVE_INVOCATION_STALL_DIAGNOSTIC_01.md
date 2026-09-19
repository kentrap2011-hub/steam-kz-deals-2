# WORKER TASK — TASTE DOSSIER LIVE INVOCATION STALL DIAGNOSTIC 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repository target неоднозначен — остановись и сначала переключись на kentrap2011-hub/steam-kz-deals-2.

## Task ID

TASTE_DOSSIER_LIVE_INVOCATION_STALL_DIAGNOSTIC_01

## Mode

READ-ONLY / RECON

## Goal

Проверить текущий долгий live-запуск существующей Scheduled Task `Taste Steam Review Dossier` и установить, продолжает ли он фактически выполнять полезную работу или остановился/завис на текущей группе.

Это диагностическая задача. Не исправлять pipeline и не вмешиваться в работающую инвокацию.

На момент постановки задачи Director наблюдал:
- active snapshot: `bbb40469f96be618ec10fa7fc6b9edca8ccd56e8f2e73442529a47de76164902`;
- canonical progress: 48 / 734;
- canonical expected sequence: `g000017`;
- последняя durable публикация: `g000016`, commit `2aed22859bd2a9cd81716019f2fbf859bd234b89`;
- сразу после неё GitHub drain/validation commit `471dc0f821c5c9412643dc9c605206b23da7896b`;
- `g000017` на тот момент: Skul: The Hero Slayer / Atelier Ayesha: The Alchemist of Dusk DX / Atelier Escha & Logy: Alchemists of the Dusk Sky DX.

Эти данные только стартовая точка. Сначала перечитай свежий `main`: запуск мог успеть продвинуться после постановки task.

## Mandatory start

1. Открой актуальный `CHAT_PROTOCOL.md` в `main` и выполни START gate.
2. Прочитай `CHAT_CONTEXT.md`.
3. Прочитай `CURRENT_TASK.md`.
4. Проверь релевантный route в `PROJECT_ROUTES.md` до широкого поиска.
5. Затем выполни только bounded диагностику ниже.

## Diagnostic questions

Нужно дать фактический ответ на четыре вопроса:

1. Есть ли после Director-check новые candidate-group публикации и/или новые canonical drain/validation commits?
2. Каков свежий `canonical_expected_sequence`, completed/remaining и snapshot binding?
3. Если expected group всё ещё не продвинулась, можно ли по доступным данным установить:
   - что текущая Scheduled invocation всё ещё явно running/active;
   - либо что она завершилась/оборвалась;
   - либо что execution status недоступен и живость нельзя доказать напрямую?
4. Если durable progress остановился на одной группе, какой первый конкретный объект/эvidence-path является подтверждённым blocker-ом? Если это нельзя доказать без внутреннего execution trace — прямо написать `причина неизвестна`, не угадывать по сложности игр.

## Bounded checks

Разрешено:
- прочитать свежий worker index / validation status / descriptor текущей expected group;
- посмотреть последние релевантные commits в этом repo;
- проверить наличие candidate artifact для текущей/следующей группы;
- проверить доступный task/automation execution state, если инструмент действительно предоставляет его этому чату;
- сделать небольшой targeted web/retrieval check только если он нужен, чтобы подтвердить уже локализованный конкретный blocker текущей expected group.

Не делать repository-wide audit.

Если текущая группа уже продвинулась, следуй за свежим expected sequence только настолько, насколько нужно понять, продолжает ли live invocation двигаться. Не исследуй весь backlog.

## Classification

В отчёте выбрать ровно один итоговый status:

- `active_progress_confirmed` — после постановки задачи есть новый durable progress и/или доступный execution state прямо подтверждает продолжающуюся работу;
- `active_but_no_new_durable_output_confirmed` — execution state прямо подтверждает active/running, но новых candidate/canonical commits пока нет;
- `stopped_with_confirmed_blocker` — invocation больше не active или durable progress остановлен, и конкретный blocker доказан;
- `stopped_or_stalled_cause_unknown` — новых durable следов нет, execution не подтверждает активность/недоступен, а конкретную причину доказать нельзя;
- `completed_or_advanced_past_observed_point` — исходная проблема уже исчезла: invocation завершилась или значительно ушла дальше `g000017`.

Не использовать вероятностные формулировки как факт. Отдельно раздели:
- подтверждённое состояние GitHub;
- подтверждённый execution/task status, если доступен;
- выводы, которые нельзя доказать.

## Strict prohibitions

Запрещено:
- нажимать `Run now`;
- запускать вторую Scheduled invocation;
- останавливать/перезапускать текущую;
- менять Scheduled Task settings;
- менять prompt/schema/contract/validator/runtime/workflow;
- публиковать dossier candidates вручную;
- менять canonical progress/checkpoint;
- делать repair/retry;
- открывать PR;
- делать implementation;
- менять `CURRENT_TASK.md`.

Единственная разрешённая запись — итоговый worker report.

## Report

Сохрани результат только в:

`reviews/worker_reports/taste-dossier-live-invocation-stall-diagnostic-01.md`

Report должен быть компактным и содержать:
1. Task
2. Verified facts
3. Latest observed durable progress
4. Execution-state visibility
5. Current expected group
6. Confirmed blocker, либо буквально `причина неизвестна`
7. Changes: none
8. Status — ровно одно значение из Classification
9. Recommended next step — ровно один bounded следующий шаг
10. Exact refs: snapshot, sequence, relevant commit/artifact refs
11. Efficiency / reusable lesson — `none`, если нет реального переносимого route/pitfall candidate

## Completion rule

Не считать отсутствие новых commits само по себе доказательством зависания.
Не считать сложность конкретной игры доказательством blocker-а.
Если runtime/task status недоступен, так и зафиксировать.

После сохранения report остановись. Следующую проектную работу не начинай.
