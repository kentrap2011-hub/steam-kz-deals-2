# CURRENT TASK

## Ranking: прозрачный числовой рейтинг 0–100

Статус: in_progress_implementation
Дата: 2026-08-30

Цель:
- заменить непрозрачный lexicographic final ranking на producer-owned числовую модель, которую пользователь видит в том же виде, в каком она реально сортирует игры;
- базовая шкала: 60 баллов за персональную ценность / 40 за качество покупки;
- каждый компонент итогового балла должен быть видим на карточке;
- не вводить декоративный score, который не определяет порядок;
- не допускать двойного учёта одного сигнала;
- сохранить eligibility/budget gates, явный manual_end_at override и срочность скидки как отдельный верхний слой вне 100 баллов.

Подтверждено пользователем:
- пробуем модель 60/40;
- серьёзный персональный риск: ориентир −10, подтверждённая серьёзная Windows-проблема: −12;
- purchase: реальная экономия в рублях до 20, текущая цена до 12, история цены до 8;
- процент скидки не даёт баллов сам по себе: score использует `max(0, original_price_rub - current_price_rub)`; процент остаётся только для отображения/контекста;
- веса и пороги должны быть легко и удобно корректируемыми позже.

Architecture preflight:
1. Владелец business rules, deterministic scoring, persistence и final ordering — GitHub repository/GitHub Actions по `config/execution_ownership_contract.json`.
2. Текущий canonical final contract — `config/final_ranking_policy.json`; переход требует V2 этого контракта и rationale в `PROJECT_DECISIONS.md`.
3. Control-plane логика не переносится в ChatGPT или UI. Semantic worker выдаёт только price-blind нормализованные taste-факторы; GitHub применяет веса.
4. Новая recurring stage/queue/retry не создаётся; используется существующий taste pipeline и существующий final producer.

Ключевое решение для удобной настройки:
- все веса, штрафы, пороги и таблицы начисления хранятся в одном `config/final_ranking_policy.json`;
- код не содержит независимых копий числовых весов;
- semantic taste layer при дальнейшем enrichment хранит нормализованные оценки факторов, не зависящие от текущих весов;
- изменение весов в final policy не должно требовать повторной AI-оценки уже имеющего нормализованные taste-факторы кандидата;
- старые taste-cache записи без factor vector временно получают явно помеченный `legacy_coarse_fit` fallback из того же конфига, чтобы V2 мог заработать сразу без фальшивой точности.

Текущий этап:
- канонизировать V2 policy и rationale;
- реализовать config-driven scoring в producer;
- добавить score breakdown/precision в production и UI;
- расширить taste ingest для будущих нормализованных factor vectors без разрушения существующего cache;
- обновить regression validation, rebuild и проверить bounded примеры.
