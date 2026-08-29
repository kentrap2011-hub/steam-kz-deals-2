# CURRENT_TASK

status: in_progress
started_at: 2026-08-30 Europe/Berlin
current_task: Исправить отсутствие исторического минимума у большинства игр в новой рассылке.
last_progress: SteamDB cache classification переведена на текущие pre-AI families: актуальный miss manifest содержит 534 ключа. Исправлены разрывы GitHub Actions из-за GITHUB_TOKEN: manifest export теперь цепляется через workflow_run после Build SteamDB cache classification, а checkpoint — через workflow_run после Validate SteamDB true-miss runtime resolutions. Добавлен resumable ledger data/cache/steamdb_runtime_progress.json. Создан внешний runtime v2 (04:00 Asia/Almaty ежедневно, до 10 новых unresolved за запуск) с накоплением результатов и публикацией data/cache/steamdb_web_resolutions.json только при полном покрытии manifest. Вручную проверены первые две пачки: 20/534 resolved, все 20 confirmed_min по прямой строке Kazakhstani Tenge / Lowest Recorded Price SteamDB, transient_failures=0.
next_step: Проверить следующий автоматический runtime v2 checkpoint: он должен прочитать resolved_count=20 и обработать следующие максимум 10 ключей без повторов. Далее накапливать до 534/534; после финальной публикации steamdb_web_resolutions.json убедиться, что CI validation проходит, checkpoint расширяет steamdb_history.json и свежий history_snapshot существенно уменьшает missing.
