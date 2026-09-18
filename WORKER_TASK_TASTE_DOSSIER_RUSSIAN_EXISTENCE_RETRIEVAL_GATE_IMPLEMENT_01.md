# WORKER TASK — TASTE DOSSIER RUSSIAN EXISTENCE RETRIEVAL GATE IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-russian-existence-retrieval-gate-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START gate

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main` и зафиксируй checklist.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный Taste dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- canonical strict/buffered validator paths только в объёме этой задачи;
- `PROJECT_DECISIONS.md` для фиксации нового non-obvious business/evidence rule.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Required prior durable reports

Прочитай полностью:
1. `reviews/worker_reports/taste-dossier-post-scg-live-acceptance-01.md`
2. `reviews/worker_reports/taste-dossier-russian-discovery-audit-01.md`

Используй их как доказанную исходную проблему:
- live worker ошибочно считал отсутствие Russian records самостоятельным blocker-ом;
- независимый audit затем доказал, что discovery тоже не идеален: Tetris имел легко discoverable exact-product Russian item, а BG3 DLC / Hellish Quart имели exact-product evidence существования Russian review activity, но usable item-level provenance в bounds не был найден.

## User-approved canonical policy change

Новая политика должна различать **отсутствие доказательств существования Russian player feedback** и **неудачу retrieval при доказанном существовании**.

### Core rule

Russian-language player-feedback search остаётся обязательным.

Но теперь:

1. Если bounded search **не нашёл даже надёжного exact-product сигнала, что Russian player feedback существует**, то после добросовестного поиска допустим terminal outcome, эквивалентный `searched_not_found_or_insufficient`. Он сам по себе не блокирует otherwise-sufficient dossier.

2. Если существует надёжный **exact-product existence signal**, что Russian player feedback реально есть, worker обязан получить хотя бы один **contract-usable attributable item-level Russian/mixed feedback record**.

3. Если existence signal подтверждён, но в пределах canonical hard bounds worker не смог получить ни одного contract-usable item-level record, это **retrieval/discovery failure**, а не обычное `searched_not_found_or_insufficient`.
   - dossier/game не считать complete;
   - 3-game candidate group не публиковать;
   - не подменять это состоянием “русских отзывов нет”;
   - не создавать retry/healing архитектуру;
   - exact reason должен быть machine-readable / deterministically testable.

4. Если доступ к нужной evidence surface недоступен и это мешает разрешить уже подтверждённый existence signal, это тоже retrieval/access failure, а не доказательство отсутствия Russian feedback.

### What may count as an existence signal

Сигнал должен относиться к **exact product/appid** и быть достаточно надёжным, например:
- exact-product Steam surface показывает ненулевую Russian-language review population;
- exact-product community/discussion surface явно содержит Russian-language player activity;
- другой reliable exact-product player-feedback index/aggregate подтверждает Russian player activity.

Existence signal сам по себе **не является usable feedback record** и не может поддерживать observation/mention_count/recurrence.

Russian-rendered UI без player-activity evidence не является existence proof.

Professional/journalistic Russian content:
- может быть context/relevance evidence;
- не заменяет player feedback;
- не удовлетворяет retrieval gate;
- не создаёт mention_count.

### Exact identity

Не смешивать base game, DLC, edition, sequel, remaster или другой appid.

Для `Baldur's Gate 3 - Digital Deluxe Edition DLC`:
- base-game Russian discussion/review не становится DLC player feedback автоматически;
- exact DLC existence signal может использоваться только как existence signal;
- usable item должен соответствовать active exact-product identity rules;
- если current contract действительно не позволяет использовать обсуждение Deluxe внутри base-game surface, не ослабляй identity ради прохождения gate.

## Discovery method requirement

Не вводить fixed website quota или обязательный Steam-only путь.

Добавь минимальную adaptive guidance:
- exact title + release year/appid;
- Russian-language query variants;
- если обычный search не разрешил Russian attempt и budget остаётся — relevant site-specific player-feedback/community search;
- exact-product Steam Community/discussion/review surfaces являются естественным вариантом, когда существуют;
- если existence signal уже найден, оставшийся bounded search должен быть направлен на получение item-level attributable record, а не повторять aggregate/list lookups.

Сохрани hard bounds:
- <=8 web-search queries per game;
- <=16 opened/read source pages per game.

Bounds остаются safety ceilings, не targets и не quota.

## Required machine semantics

Не оставляй новое правило только в prose, если тогда GitHub не сможет отличить:
- genuine “no existence signal found”;
- “existence proven but retrieval failed”.

Выбери минимальное совместимое machine-readable представление в active schema/evidence contract, достаточное для deterministic generation + validation.

Не создавать второй validator truth source.

После реализации должно быть детерминированно возможно различить минимум:
- Russian usable feedback found and used;
- no Russian existence signal established after bounded search;
- Russian existence established but usable item unresolved;
- access failure preventing resolution, если применимо.

Существующие `russian_attempt` states можно сохранить/уточнить или минимально расширить — выбери наименьшее изменение, но не оставляй ambiguous state, в котором proven existence + failed retrieval выглядит как ordinary absence.

## Strict validation requirement

Canonical GitHub strict validator должен оставаться fail-closed и единственным authority.

Минимально:
- candidate с internally contradictory Russian discovery state должен reject-иться;
- если persisted machine state говорит, что exact-product Russian feedback existence подтверждено, complete dossier не может утверждать ordinary “not found/insufficient” без usable Russian/mixed bound record;
- `found_and_used` по-прежнему требует реально bound Russian/mixed record;
- existence aggregate/list signal сам не превращается в feedback record, observation support, mention_count или recurrence;
- no-existence-signal terminal state должен оставаться валидным для otherwise sufficient dossier;
- не ослаблять identity, language binding, source-item provenance, temporal coherence, summary, duplicate conflict и все прежние SCG guards.

## Required regressions

Нужен focused deterministic regression suite минимум для следующих shapes.

### RUS-GATE-01 — Tetris discoverable usable item
Exact product: `Tetris® Effect: Connected`, appid `1003590`.

Regression/sample должен доказывать generation/discovery guidance:
- existence/readily discoverable Russian exact-product Steam Community item;
- minimal pattern exact title/appid + Russian term + relevant Steam Community/discussion surface;
- worker contract не должен завершать Russian attempt как ordinary no-evidence before this reasonable bounded path is attempted when budget remains.

Не нужно превращать live web content в flaky CI dependency: используй deterministic fixture/contract assertions representing audited shape.

### RUS-GATE-02 — existence proven, item unresolved
Shapes derived from audited BG3 DLC / Hellish Quart:
- exact-product signal says Russian player reviews exist;
- no usable item-level Russian record is obtained within bounded fixture;
- must classify as retrieval/discovery unresolved/failure;
- complete dossier/candidate publication must not be allowed under ordinary `searched_not_found_or_insufficient`.

### RUS-GATE-03 — genuine no-existence-signal case
Synthetic/fixture game:
- bounded Russian search completed;
- no reliable exact-product Russian player-feedback existence signal;
- enough general non-Russian player evidence exists;
- Russian absence state is valid and **does not block** otherwise complete dossier.

### RUS-GATE-04 — existence signal is not player feedback
- Russian review aggregate/index or count proves existence only;
- it must not create player_feedback_record, mention_count, recurrence, observation support or `found_and_used`.

### RUS-GATE-05 — identity preserved
- base-game Russian feedback cannot satisfy exact DLC item retrieval gate when active product identity contract forbids it.

### RUS-GATE-06 — access failure
- if proven existence cannot be resolved because required player-feedback surface is inaccessible, outcome is access/retrieval unresolved according to the new machine semantics, not ordinary “no Russian feedback exists”.

## Architecture constraints — MUST NOT CHANGE

- GitHub remains control plane.
- Scheduled ChatGPT remains bounded semantic/data worker + immutable create-only candidate publisher.
- Interactive chat is not production executor/backlog manager.
- Canonical group size remains **3**.
- Do not split groups into per-game acceptance/retry.
- Do not add automatic retry/healing manager.
- Do not create a new recurring stage, search service, queue or backlog manager.
- Do not weaken strict validation.
- Keep one canonical strict validator truth source.
- Do not change parallel buffer / maximal contiguous prefix.
- Do not change scope/order/progress/completeness ownership.
- Do not manually repair queue/cache/progress/receipts/candidates.
- Do not change Taste Semantic Producer, ranking, pricing, package economics, giveaway, duration, translation or UI.
- Do not alter DLC/package architecture except to preserve exact identity in this evidence rule.

## Canonical rationale / PROJECT_DECISIONS

Это новый non-obvious product/evidence rule, подтверждённый пользователем.

Добавь или обнови один компактный Taste dossier decision в `PROJECT_DECISIONS.md`, фиксируя rationale:
- Russian search is mandatory because Russian-user relevance matters;
- existence proof and usable feedback are distinct;
- proven existence + failed item retrieval is a discovery defect and must fail closed;
- absence remains acceptable only when bounded search does not establish existence;
- professional Russian content does not substitute for player feedback;
- no fixed-source quota / no retry architecture.

Не переписывай unrelated decisions.

## Compatibility / activation

Изменение machine contract/prompt/schema/validator semantics, вероятно, меняет content-complete compatibility binding.

Используй только normal GitHub-owned migration:
- implementation через bounded branch/PR;
- required focused CI/regressions + ownership checks;
- merge только после green;
- canonical post-merge activation/rebuild;
- если binding incompatible — fresh snapshot;
- old snapshot/candidates становятся stale/inert только штатным GitHub-owned path;
- никакого manual rebinding/progress repair.

Если actual binding rules не требуют fresh snapshot, докажи это в report; не форсируй вручную.

## Scheduled Task

**Scheduled Task `Run now` в этой IMPLEMENT-задаче не запускать.**
Settings Scheduled Task не менять.

После merge/activation live behavior проверяется отдельным acceptance run с manual UI result пользователя.

## Durable report

Required path:

`reviews/worker_reports/taste-dossier-russian-existence-retrieval-gate-implement-01.md`

Report должен быть committed to `main` до complete.

Обязательные разделы:
1. Task / repo / mode.
2. Architecture preflight.
3. Prior live/audit evidence reconciled.
4. Exact new canonical Russian existence/retrieval rule.
5. Machine-readable state model chosen and why it is minimal.
6. Discovery guidance change.
7. Strict validator behavior and confirmation it was not weakened.
8. RUS-GATE-01..06 regression results.
9. Confirmation journalists/context do not substitute player feedback.
10. Confirmation exact product/DLC identity remains strict.
11. PR / CI / merge refs.
12. Post-merge activation/binding/snapshot state:
    - snapshot id;
    - prepared/completed/remaining;
    - expected sequence;
    - group count;
    - group size=3;
    - treatment of old snapshot/artifacts.
13. PROJECT_DECISIONS update ref.
14. Confirmation Scheduled Task Run now/settings unchanged.
15. Unresolved.
16. Status.
17. Exactly one recommended next step.
18. Efficiency / reusable lesson per DIRECTOR_PROTOCOL.md.

Allowed final statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

`complete_ready_for_live_acceptance` только если новое rule детерминированно закрыто, CI/merge/activation завершены и Run now не использовался как proof.

## CURRENT_TASK.md

Можно обновлять только по правилам `CHAT_PROTOCOL.md` для реально выполняемой задачи. Unrelated concurrent work не удалять и не переписывать.

## Exactly one next step after success

One separate live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against the fresh/current compatible snapshot. User supplies the Scheduled Task UI result manually. No proactive auditor before clean live acceptance.
