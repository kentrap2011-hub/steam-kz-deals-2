# CURRENT TASK

## UI: переключатель «Срочные вперёд»

Статус: in_progress
Дата: 2026-08-30

Цель:
- production `priority_rank` и `FINAL-PRIORITY-RANKING-V2` не менять;
- по умолчанию локальная очередь витрины сортируется без срочности: `total_score DESC → title`;
- по кнопке «⏱ Срочные вперёд» локальная очередь использует production-порядок: `urgency → total_score → title`;
- состояние кнопки хранится локально;
- `manual_end_at` («В конец очереди») остаётся абсолютным локальным override в обоих режимах;
- переключение режима сохраняет текущую открытую игру, если она ещё активна.

Architecture preflight:
1. Каноническим ranking/control-plane владеет GitHub; он не меняется.
2. Разрешённая точка расширения — существующий local UI override layer (`UI-001`).
3. В ChatGPT/UI не переносится semantic scoring: UI сортирует только по готовым producer-owned `total_score`/`priority_rank`.
4. Новых recurring stages, queues, retries или production ownership changes нет.
