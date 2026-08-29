# CURRENT_TASK

status: in_progress
started_at: 2026-08-30 Europe/Berlin
current_task: Исправить отсутствие исторического минимума у большинства игр в новой рассылке.
last_progress: Установлена причина: pre-AI history snapshot классифицирует 659 текущих семейств, но SteamDB cache classification/lookup pipeline всё ещё привязан к legacy store_state.validation + offer_family.validation на 93 primary. Persistent history cache содержит только 147 записей, поэтому 534 из 659 текущих primary имеют cache_status=missing.
next_step: Перевести SteamDB miss classification/checkpoint на текущие pre-AI family_graph + store_snapshot (или добавить совместимый current-primary вход), затем обеспечить автоматический lookup/persist новых misses до построения history_snapshot и проверить покрытие свежего снимка.
