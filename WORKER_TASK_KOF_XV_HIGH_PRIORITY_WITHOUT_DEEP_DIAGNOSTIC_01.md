# WORKER TASK — KOF XV HIGH PRIORITY WITHOUT DEEP DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `kof-xv-high-priority-without-deep-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/kof-xv-high-priority-without-deep-diagnostic-01.md`

## User-observed symptom

On the current published site, the card:

`THE KING OF FIGHTERS XV`

shows:
- global visible priority: **2 из 391**;
- card appearance counter: **Показ №13**;
- short description unavailable;
- personal reason not prepared;
- no confirmed personal risks shown;
- visually appears not to have completed detailed Deep analysis.

User asks:

> Почему игра без детального анализа на втором месте?

## Goal

Explain exactly why this card is currently priority #2 despite lacking completed detailed Deep analysis.

Do not speculate. Trace the exact current ranking inputs and source precedence for this one game.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. current ranking/priority routes in `PROJECT_ROUTES.md`;
4. current ranking-related canonical decisions/contracts;
5. current production card/visual data for THE KING OF FIGHTERS XV;
6. current Fast/Dossier/Deep state for the same exact AppID/work identity;
7. only the smallest scoring/ranking projection files needed to explain its current priority.

## Required diagnostic

### A. Identify exact product

Resolve the exact current AppID/work identity for `THE KING OF FIGHTERS XV` from canonical production data.

### B. Current semantic state

For that exact identity, report:
- Dossier state;
- Fast/PASS 1 state;
- Deep/PASS 2 state;
- effective semantic source used by the card/ranking: Deep, Fast, fallback/cache, commercial-only, none, or another canonical source;
- whether a prior historical analysis exists but is non-current;
- whether any semantic result is currently contributing to rank.

### C. Exact priority calculation

Trace the exact current inputs that produce priority #2.

Separate at minimum:
- personal/semantic score;
- commercial/deal score;
- discount/price/history signals;
- deadline/urgency;
- resurfacing/show-count behavior;
- any exploration/diversity/randomization or unresolved-item boost;
- any penalty for missing Deep/Fast/Dossier;
- any fallback score.

Give the actual current values for this game where available.

### D. Why incomplete analysis does not block high priority

Determine whether current ranking intentionally allows a not-yet-analyzed game to rank highly.

If yes, prove the canonical rule and explain why.
If no, identify the defect.

Specifically determine whether:
- priority ranking is a queue for what should be analyzed/shown next rather than a confidence ranking;
- unresolved items intentionally receive exposure;
- strong commercial signals can outweigh missing personalization;
- this card is accidentally inheriting stale score/state;
- another exact mechanism is responsible.

### E. Compare with nearby cards

Compare KOF XV with:
- current priority #1;
- current priority #3 if available;
- at least one current completed-Deep card.

Do not create a broad ranking audit. Use only enough comparison to explain why #2 is plausible or defective.

### F. "Показ №13"

Explain exactly what `Показ №13` means and whether it affects priority #2.

### G. User-facing interpretation

State plainly whether:
1. this is expected behavior;
2. the ranking is misleading but mechanically correct;
3. there is a ranking/projection defect.

If there is a defect, recommend exactly one bounded next fix task.
If behavior is intentional, recommend no implementation task unless the label/UI itself is misleading.

## Scope limits

READ-ONLY diagnosis only.

Do NOT:
- change ranking;
- change scores;
- run Fast/Dossier/Deep;
- modify cards;
- change Scheduled Tasks;
- trigger rebuild/deploy;
- edit production state.

## Report

Write:
`reviews/worker_reports/kof-xv-high-priority-without-deep-diagnostic-01.md`

Required sections:
1. `Task`
2. `Pinned current truth`
3. `Exact product identity`
4. `Current semantic state`
5. `Exact priority calculation`
6. `Why missing Deep does or does not block rank`
7. `Nearby-card comparison`
8. `Meaning of Показ №13`
9. `User-facing explanation`
10. `Changes` — report only
11. `Unresolved`
12. `Status`
13. `Recommended next step` — exactly one bounded next step or explicitly `none`
14. exact commit/artifact refs
15. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Do not start another task after this one.
