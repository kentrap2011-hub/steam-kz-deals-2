# CURRENT_TASK

status: in_progress
started_at: 2026-08-30 Europe/Berlin
current_task: Исправить production-контур SteamDB так, чтобы все актуальные true lookup miss обрабатывались ChatGPT в рамках одного ночного цикла, без суточной квоты.
last_progress: Подтверждено 534 актуальных true_lookup_miss из 659 primary; старый lookup validation покрывает только прежние 51. Найден дополнительный дефект: workflow-цепочка сейчас потенциально циклическая — Build SteamDB cache classification → Export SteamDB miss manifest → runtime validation → Checkpoint SteamDB history → снова Build SteamDB cache classification по workflow_run. Также Build daily visual payload ссылается на workflow name «Build pre-AI deterministic payload», но соответствующий workflow-файл пока не найден в текущем дереве.
next_step: Определить фактический ночной orchestrator/pre-AI workflow и зависимости history_snapshot; затем убрать циклический workflow_run и сделать однократную post-checkpoint перестройку history/downstream artifacts в том же production cycle.