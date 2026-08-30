# CURRENT TASK

## UI: показывать причины текущей позиции по ranking-факторам

Статус: in_progress
Дата: 2026-08-30

Цель:
- не пересчитывать ranking в UI;
- producer должен записывать в каждую игру готовые диагностические значения canonical ranking-факторов;
- producer должен записывать первый фактор, на котором текущая игра выигрывает у следующей;
- UI только отображает готовые данные человекочитаемо;
- сохранить неизменным canonical `priority_rank` и порядок факторов из `config/final_ranking_policy.json`.

Проверяемые точки:
- `config/final_ranking_policy.json`
- `scripts/priority_ranking.py`
- `scripts/validate_priority_ranking.py`
- `scripts/build_final_visual_payload.py`
- `web/index.html`
- `web/app.js`
- `web/styles.css`
- `BACKLOG.md` после успешной проверки.
