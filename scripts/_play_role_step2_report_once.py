import json
import os
from pathlib import Path

impl = os.environ['IMPLEMENTATION_SHA']
run_id = os.environ.get('GITHUB_RUN_ID', 'unknown')
contract = json.loads(Path('config/play_priority_context_contract.json').read_text(encoding='utf-8'))

report = f'''# Play role and start priority implementation 01

## 1. Status

`complete`

This is internal Taste IMPLEMENT step 2. It adds canonical producer-owned play-role / relative-start-priority context without implementing Taste step 3, wishlist-good-deal override, reconsideration commercial bridge, or a second ranker/sorter.

Implementation commit: `{impl}`
Validation workflow run: `{run_id}`

## 2. Exact role / start-priority contract

Canonical contract: `config/play_priority_context_contract.json`
Contract id: `{contract['contract_id']}`

Play roles:
- `main_full` — full/main game candidate;
- `secondary_palate_cleanser` — secondary / lighter parallel role;
- `family_coop` — family/co-op context;
- `unresolved` — insufficient title-specific evidence for a stronger role.

Relative start priority:
- `high`;
- `ordinary`;
- `low`;
- `unresolved`.

Both dimensions persist independent confidence/provenance. The layer is deliberately conservative: uncalibrated titles remain unresolved rather than being inferred from score, genre, wishlist or franchise identity.

## 3. Files changed

Canonical/new:
- `config/play_priority_context_contract.json`;
- `scripts/play_priority_context.py`;
- `scripts/test_play_priority_context.py`.

Existing producer/diagnostics:
- `scripts/build_final_visual_payload.py`;
- `scripts/build_ranking_lookup.py`.

Durable project documentation:
- `PROJECT_RULES.md`;
- `PROJECT_DECISIONS.md` (`TASTE-002`);
- `PROJECT_ROUTES.md`.

Explicitly unchanged by this implementation:
- `.github/workflows/build-daily-visual-payload.yml` and all recurring/scheduled execution;
- `scripts/priority_ranking.py`;
- `config/final_ranking_policy.json`;
- Taste V5 evidence-state semantics/contracts;
- `web/app.js` and the existing urgency/score toggle UI;
- eligibility/commercial bridge logic.

The focused regression is a durable repository test (`scripts/test_play_priority_context.py`) and was executed by the bounded implementation validation. No workflow-permission escalation or new scheduler was introduced merely to wire this test into a recurring job.

## 4. How role differs from fit

`play_role` is not a renamed fit level and is not derived from `total_score` or personal score. The deterministic control `Tails of Iron 2` proves a strong-fit candidate may persist as `secondary_palate_cleanser`; `Trine 4` proves a suitable game may persist as `family_coop` rather than being rewritten to a solo/main role.

When there is no title-specific role evidence, the contract produces `unresolved`. Franchise identity alone is only a weak prior and cannot resolve or cap the role.

Step-1 `confirmed_negative` is a hard guard. It forces role `unresolved` and relative start priority `low`, so a confirmed negative can never become `high` from a title calibration or later commercial signal.

## 5. How start priority differs from sale urgency

`relative_start_priority` answers how soon a suitable game should be started relative to other suitable games. `sale_expiry_urgency` remains the separate commercial question of whether a purchase deadline needs attention.

The resolver does not read wishlist, discount, price, history quality, purchase decision, sale end/urgency, total score or priority rank. `Terminator: Resistance` remains `ordinary` with either today/later sale urgency; `High On Life` remains `ordinary` whether wishlist is true or false.

No sorting formula consumes the new states in this step. Existing `priority_rank` remains purchase-attention order and the existing mobile score/urgency toggle remains unchanged.

## 6. Control / regression results

Workflow `{run_id}` passed the focused play-priority test and the existing Taste/ranking regressions.

Calibrated controls:
- `Sifu` -> `main_full / high`;
- `High On Life` -> `main_full / ordinary`;
- `Amnesia: The Bunker` -> `main_full / ordinary`;
- `Terminator: Resistance` -> `main_full / ordinary`;
- `Tails of Iron 2` -> `secondary_palate_cleanser / ordinary`;
- `Trine 4` -> `family_coop / ordinary`;
- `TMNT: Splintered Fate` -> `unresolved / unresolved` from franchise-prior-only evidence; synthetic title-specific evidence can resolve either main or secondary independently;
- `HighFleet` + exact `confirmed_negative` -> `unresolved / low`, never high.

Focused invariants proven:
- role != fit;
- start priority != commercial urgency;
- wishlist does not imply high;
- strong fit may be secondary;
- family role survives into ranking diagnostics;
- franchise prior is not a hard role cap;
- confirmed negative cannot receive high start priority;
- applying the context does not mutate fit, total/personal/purchase score or priority rank;
- no second sorter/ranker is introduced.

Existing regressions executed in the same workflow:
- `scripts/test_taste_evidence_states.py` — PASS;
- `scripts/validate_taste_v3_contract.py` — PASS;
- `scripts/test_grounded_negative_contract.py` — PASS;
- `scripts/test_card_explanation_policy.py` — PASS;
- `scripts/validate_priority_ranking.py` — PASS;
- `git diff --exit-code -- scripts/priority_ranking.py config/final_ranking_policy.json web/app.js .github/workflows/build-daily-visual-payload.yml` — PASS;
- single-ranker static guard — PASS;
- `git diff --check` — PASS.

## 7. Ranking / UI impact

Ranking math and ordering are unchanged. The final visual producer attaches the new context fields after Taste evidence is available and before/through commercial refresh, but never passes them into `priority_ranking`.

`build_ranking_lookup.py` exposes role/start/confidence/provenance for diagnostics. `web/app.js` is intentionally unchanged in this step, avoiding conflict with parallel score-breakdown UI work and preserving the current truthful score/urgency toggle behavior.

## 8. Proof no wishlist / commercial bridge was implemented

The contract explicitly forbids wishlist, discount, price, purchase decision, history quality, sale urgency, total score and priority rank as resolution inputs. The focused test varies these commercial fields and proves identical role/start output.

No eligibility gate, wishlist rule, deal-quality threshold, reconsideration purchase path, bundle bridge or ranking weight was changed. Step 3 remains unimplemented.

## 9. Can Taste step 3 safely start?

**Yes — as the next bounded internal implementation step.** Step 1 evidence state and step 2 role/start context are now separate explicit layers, and step 2 does not consume commercial value. That gives step 3 a safe boundary for a later reconsideration/wishlist commercial bridge without mutating fit or role/start semantics.

This is not final material Taste acceptance. If steps 1–3 remain one bounded internal sequence, run one independent current Taste Review after step 3 and regenerated controls before final acceptance.

## 10. Exact commits / runs / artifacts

- implementation commit: `{impl}`;
- implementation/validation workflow run: `{run_id}`;
- report: `reviews/worker_reports/play-role-and-start-priority-implement-01.md`;
- no manual production semantic artifact was fabricated;
- one-shot implementation/report machinery is removed by the final report commit.

## 11. One bounded next step

Only: Taste step 3 — reconsideration commercial bridge / wishlist-good-deal override, consuming step-1 evidence state while preserving step-2 role/start context and the existing single ranking authority.
'''

out = Path('reviews/worker_reports/play-role-and-start-priority-implement-01.md')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(report, encoding='utf-8')

current = Path('CURRENT_TASK.md')
text = current.read_text(encoding='utf-8')
active = '''### A2. Play role and start priority implementation 01
Статус: `in_progress`.
- worker task: `WORKER_TASK_PLAY_ROLE_AND_START_PRIORITY_IMPLEMENT_01.md`;
- цель: добавить producer-owned `play_role` и `relative_start_priority` отдельно от fit и commercial urgency;
- role states: `main_full / secondary_palate_cleanser / family_coop / unresolved`;
- start priority: `high / ordinary / low / unresolved`;
- existing `priority_ranking.py` остаётся единственным ranker; новая семантика не меняет `total_score` / `priority_rank`;
- wishlist-good-deal override и reconsideration commercial bridge вне scope;
- A1 / F и другие параллельные работы сохраняются без изменений.

'''
if active not in text:
    raise SystemExit('CURRENT_TASK active A2 block missing')
text = text.replace(active, '', 1)
completed = f'''### Play role and start priority implementation 01
Статус: `complete` (internal Taste step 2; combined final Taste Review remains pending after step 3).
- implementation: `{impl}`;
- report: `reviews/worker_reports/play-role-and-start-priority-implement-01.md`;
- roles: `main_full / secondary_palate_cleanser / family_coop / unresolved`;
- start priority: `high / ordinary / low / unresolved`;
- role/start remain separate from fit, wishlist and commercial sale urgency;
- `confirmed_negative` cannot receive high start priority;
- `priority_ranking.py` / final ranking policy unchanged; no second sorter/scheduler;
- wishlist-good-deal and reconsideration commercial bridge remain intentionally unimplemented.

'''
anchor = '## Завершённые package-инварианты, которые сохраняются\n'
if anchor not in text:
    raise SystemExit('CURRENT_TASK completion anchor missing')
text = text.replace(anchor, completed + anchor, 1)
old = 'Taste evidence state and confidence implementation завершён как internal step 1; A2 / play role and start priority implementation сейчас выполняется как bounded internal step 2 без изменения ranker/commercial eligibility.'
new = 'Taste steps 1–2 завершены как bounded internal implementations; step 3 может начинаться отдельно, а material Taste acceptance остаётся за combined independent review после него.'
if old in text:
    text = text.replace(old, new, 1)
current.write_text(text, encoding='utf-8')
