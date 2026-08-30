# CURRENT TASK

## Ranking: прозрачный числовой рейтинг 0–100

Статус: in_progress_design
Дата: 2026-08-30

Цель:
- заменить непрозрачный lexicographic final ranking на producer-owned числовую модель, которую пользователь видит в том же виде, в каком она реально сортирует игры;
- ориентир: около 60 баллов за соответствие вкусу и 40 за качество покупки;
- каждый компонент итогового балла должен быть видим на карточке;
- не вводить декоративный score, который не определяет порядок;
- не допускать двойного учёта одного сигнала;
- сохранить eligibility/budget gates, явный manual_end_at override и отдельную обработку срочности, если она логически остаётся вне обычных баллов.

Architecture preflight:
1. Владелец business rules, deterministic scoring, persistence и final ordering — GitHub repository/GitHub Actions по `config/execution_ownership_contract.json`.
2. Текущий canonical final contract — `config/final_ranking_policy.json`; production-изменение потребует новой согласованной версии этого контракта и rationale в `PROJECT_DECISIONS.md` до переключения producer.
3. Control-plane логика не переносится в ChatGPT или UI; scheduled semantic worker может выдавать только явно контрактованные taste evidence/score inputs, если это понадобится.
4. Новая recurring stage/queue/retry не создаётся; задача меняет существующую final ranking model внутри текущего nightly pipeline.

Текущий этап:
- инвентаризация реально доступных upstream taste/deal сигналов;
- проектирование понятной шкалы и весов;
- production не переключать до согласования продуктовых весов с пользователем.
