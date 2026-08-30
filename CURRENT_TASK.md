# CURRENT_TASK

status: in_progress
started_at: 2026-08-30 Europe/Berlin
current_task: Проверить и исправить текущую логику итоговой сортировки/приоритета игр в витрине Steam KZ.
last_progress: Найдено основное расхождение: production сортируется дважды (`build_daily_visual_payload.py`, затем `refine_visual_ranking.py`), причём финальный refiner использует порядок `priority_bucket -> direct user evidence -> personal risk -> achievement quality -> wishlist -> history quality -> discount -> price -> duration`. Это не совпадает с `config/mailing_policy.json`; особенно achievement quality сейчас может влиять сильнее wishlist и коммерческой выгодности, хотя PROJECT_RULES фиксирует достижения как фактор только при близких кандидатах. Базовая матрица priority_bucket соответствует подтверждённому правилу 60/40 и остаётся пригодной. Полный быстрый маршрут этого участка сохранён в `PROJECT_ROUTES.md` → «Финальная сортировка / priority rank витрины», включая workflow, обе точки сортировки, output/review-файлы и текущее расхождение policy ↔ implementation.
next_step: Не повторять исследование структуры. Начать с маршрута `PROJECT_ROUTES.md`, согласовать/восстановить канонический порядок факторов внутри одного priority_bucket, затем оставить единственный source of sorting truth и добавить regression-проверку, не позволяющую policy и production снова разойтись.
