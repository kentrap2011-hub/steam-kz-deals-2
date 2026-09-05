import json
import os
from pathlib import Path

impl = os.environ['IMPLEMENTATION_SHA']
run_id = os.environ.get('GITHUB_RUN_ID')
summary = json.loads(Path('/tmp/taste_validation_summary.json').read_text(encoding='utf-8'))
report = f'''# Taste evidence state and confidence implementation 01

## 1. Status

`complete`

This is internal Taste IMPLEMENT step 1 of the ordered three-step sequence. It is technically validated, but it is **not** final product acceptance of the full Taste Reviewer handoff. No wishlist-good-deal override, play-role/start-priority logic, giveaway change, final-ranking weight change, or new scheduler was introduced.

Implementation commit: `{impl}`  
Validation workflow run: `{run_id}`

## 2. Exact semantic changes

A canonical price-blind evidence layer now distinguishes four states independently of the compatibility fit verdict:

- `sufficient` — enough candidate-specific evidence exists to interpret an INCLUDE strong/moderate fit;
- `insufficient` — evidence is too weak to conclude personal dislike; compatibility eligibility may still remain EXCLUDE/below_moderate;
- `reconsiderable` — old brief/partial non-engagement or mixed history has been legitimately reopened by later non-commercial evidence; it is not a fit promotion;
- `confirmed_negative` — high-confidence strong personal/title-specific evidence supports a real negative fit and remains non-overridable by paid commercial signals.

Evidence confidence is `low | medium | high` and the V5 result carries explicit basis, optional historical-negative context, candidate-quality findings, and personal-negative provenance/strength.

Historical semantics distinguish exposure depth, recency, reaction and later reopening evidence. A brief old `didn't hook me` signal cannot alone become `confirmed_negative`; a historical-only confirmed negative requires substantial/complete exposure plus explicit dislike.

Recurring/public complaints are represented as `candidate_quality_findings` with `personal_relevance=unresolved`. They may establish a real implementation-quality question, but they do not change fit/verdict/factors and cannot by themselves produce a personal dislike.

V5 personal-negative findings now carry `evidence_origin`, `evidence_strength`, and `personal_relevance`. Generic feature hypotheses and recurring-player-complaint origin are not admissible personal-negative origins. Score-4 personal risk only remains score 4 with `strong` personal evidence. A dedicated `felt_technical_burden` strong-risk code represents the HighFleet control without generalizing into anti-complexity/strategy/management rules.

## 3. Exact files/contracts

Changed canonical contracts/policy:
- `config/mailing_policy.json` — new top-level `taste_evidence_state`; existing fit-semantic policy fields unchanged;
- `config/taste_result_contract.json` — `TASTE-SEMANTIC-RESULT-V5`;
- `config/taste_cache_entry_contract.json` — `TASTE-CACHE-ENTRY-BINDING-V5`;
- `config/taste_ledger_contract.json` — V1 binary fit ledger retained as compatibility/eligibility only, version 1.1 evidence semantics added.

Changed/new implementation:
- `scripts/taste_evidence_contract.py` (new);
- `scripts/taste_negative_contract.py`;
- `scripts/taste_cache_common.py`;
- `scripts/ingest_taste_results.py`;
- `scripts/build_taste_cache_index.py`;
- `scripts/build_pre_ai_chatgpt_payload.py`;
- `scripts/refine_visual_ranking.py`;
- `scripts/build_final_visual_payload.py`;
- `scripts/build_ranking_lookup.py`;
- `scripts/validate_taste_v3_contract.py` (filename retained for compatibility, now validates V5);
- `scripts/test_taste_evidence_states.py` (new).

Durable navigation/rationale updated:
- `PROJECT_ROUTES.md`;
- `PROJECT_DECISIONS.md` (`TASTE-001`).

## 4. Cache / ledger migration and invalidation behavior

**Existing fit cache is not invalidated.** The pre/post implementation fit semantic digest remained exactly:

`{summary['fit_semantics_sha256']}`

The V5 evidence layer has its own exact `evidence_contract_sha` binding to the Git blob of `config/taste_result_contract.json`. GitHub stamps that binding on ingest; the semantic worker cannot invent it.

Legacy V2/V3/V4 entries remain valid fit cache hits. Migration is bounded and fail-safe:
- legacy INCLUDE with no legacy negative evidence -> compatibility evidence state `sufficient`;
- legacy `exclude_insufficient` -> compatibility evidence state `insufficient`;
- legacy risk-bearing INCLUDE -> V5 evidence backfill required;
- legacy `exclude_audited_below` -> V5 evidence backfill required;
- legacy `exclude_direct_conflict` -> V5 evidence backfill required rather than being assumed permanently confirmed negative.

Backfill reuses the existing `resolve_grounded_negative_analysis` work code and existing GitHub-owned Taste queue/ingest. No new scheduler, queue authority or recurring stage exists. Evidence-only backfill preserves verdict, fit, reason, factors, profile/model/semantic/fingerprint/context bindings and original evaluation timestamp.

The legacy `FINAL-TASTE-LEDGER-V1` mapping still provides complete binary eligibility accounting, but its contract now explicitly forbids interpreting `EXCLUDE/below_moderate` or `exclude_direct_conflict` reason code alone as evidence confidence/dislike. Exact V5 evidence state is the authority for that distinction.

Until an ambiguous legacy row receives exact V5 backfill, legacy personal-risk scoring remains as a migration fallback so an informed negative cannot disappear silently. After V5 binding, ranking/card explanations consume only structured V5 personal negatives; `insufficient` / `reconsiderable` therefore cannot inherit a strong keyword penalty from old free text.

## 5. Regression / control results

All focused and existing regressions passed in workflow run `{run_id}`:

- `scripts/test_taste_evidence_states.py` — PASS;
- `scripts/validate_taste_v3_contract.py` / V5 contract validation — PASS;
- `scripts/test_grounded_negative_contract.py` — PASS;
- `scripts/test_card_explanation_policy.py` — PASS;
- `scripts/build_taste_cache_index.py` against the current mixed legacy cache — PASS;
- bounded `scripts/build_pre_ai_chatgpt_payload.py` regeneration — PASS with complete family partition; generated artifacts were used only for validation and restored before commit.

Calibrated controls proven deterministically:
- **Haven Moon:** `insufficient` can carry recurring opaque-navigation/backtracking quality findings while producing no confirmed personal negative;
- **BioShock:** old brief non-engagement + later quality/reputation evidence validates as `reconsiderable`; a legacy 3/5-style rating does not become a permanent fit cap once the state is reconsiderable;
- **HighFleet:** direct/title-specific dry/technical/tedious evidence validates as `confirmed_negative`; `felt_technical_burden` remains score 4 / high personal risk;
- generic feature presence cannot be a V5 strong personal-negative origin;
- old shallow historical evidence alone cannot be `confirmed_negative`, while substantial/recent explicit historical dislike can;
- candidate-quality recurring complaints survive separately without becoming personal risk;
- price/discount/wishlist language is rejected from evidence-state quality input;
- legacy ambiguous direct-conflict/risk-bearing rows require V5 backfill rather than being silently reclassified.

Bounded current producer validation summary:
```json
{json.dumps(summary, ensure_ascii=False, indent=2)}
```

## 6. Production / runtime dependency

Repository-side implementation is complete. The **existing** scheduled Taste semantic worker must gradually resolve exact V5 evidence backfill rows through the existing GitHub-prepared `resolve_grounded_negative_analysis` queue. This task intentionally did not manually process semantic rows and did not create a scheduler.

That backfill is not a blocker for starting internal step 2 implementation: legacy fit remains usable and migration is fail-safe. It **is** required before relying on a particular legacy ambiguous candidate's new evidence state in production decisions.

Confirmed negative remains non-overridable. This step does not contain the later commercial bridge that could make a `reconsiderable` candidate purchase-eligible, and it does not implement wishlist override.

## 7. Can step 2 safely start?

**Yes — as the next internal bounded implementation step.** The semantic foundation is now explicit and technically validated, fit-cache compatibility is preserved, and no new scheduler/authority was introduced.

Do not treat this as final material Taste acceptance/deployment on its own. Per the task/recon, an independent current Taste Review is required before accepting a material semantic boundary; if steps 1–3 remain internal precursors, one combined Taste Review after all three bounded implementations is acceptable.

## 8. Exact commits / runs / artifacts

- implementation commit: `{impl}`;
- implementation/validation workflow run: `{run_id}`;
- fit semantic digest unchanged: `{summary['fit_semantics_sha256']}`;
- deterministic generated pre-AI/cache artifacts were restored after validation and were **not** persisted as a manual semantic production run.

## 9. One bounded next step

Only: `play-role-and-start-priority-implement-01` (Taste step 2), consuming the new evidence-state layer without implementing wishlist-good-deal or commercial reconsideration bridge yet.
'''
out = Path('reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(report, encoding='utf-8')

current = Path('CURRENT_TASK.md')
text = current.read_text(encoding='utf-8')
block = '''### A2. Taste evidence state and confidence implementation 01
Статус: `in_progress`.
- worker task: `WORKER_TASK_TASTE_EVIDENCE_STATE_AND_CONFIDENCE_IMPLEMENT_01.md`;
- цель: развести `insufficient`, `reconsiderable`, `confirmed_negative` без нарушения price-blind Taste;
- сохранить HighFleet strong-negative control, Haven Moon insufficient control, BioShock reconsiderable control;
- wishlist override, play-role/start-priority, giveaway и новые schedulers вне scope;
- existing GitHub-owned Taste semantic queue/cache/ingest остаются единственным control plane.

'''
if block not in text:
    raise SystemExit('CURRENT_TASK A2 active block missing')
text = text.replace(block, '', 1)
completed = f'''### Taste evidence state and confidence implementation 01
Статус: `complete` (internal Taste step 1; final Taste acceptance pending combined review).
- implementation: `{impl}`;
- report: `reviews/worker_reports/taste-evidence-state-and-confidence-implement-01.md`;
- semantic states: `sufficient / insufficient / reconsiderable / confirmed_negative`;
- existing fit-cache semantic digest preserved; V5 evidence has separate exact contract binding;
- legacy ambiguous evidence backfills through existing `resolve_grounded_negative_analysis`; no new scheduler;
- HighFleet/Haven Moon/BioShock deterministic controls passed;
- wishlist override and play-role/start-priority remain intentionally unimplemented.

'''
anchor = '## Завершённые package-инварианты, которые сохраняются\n'
if anchor not in text:
    raise SystemExit('CURRENT_TASK completion anchor missing')
text = text.replace(anchor, completed + anchor, 1)
old_status = 'F / redesign detailed score breakdown UI и A1 / card explanation implementation сохраняются как отдельные параллельные работы. A2 / Taste evidence state and confidence implementation начат как bounded internal semantic step 1.'
new_status = 'F / redesign detailed score breakdown UI и A1 / card explanation implementation сохраняются как отдельные параллельные работы. Taste evidence state and confidence implementation завершён как internal step 1; следующий Taste implementation step может начинаться, но material Taste acceptance остаётся за combined independent review.'
if old_status in text:
    text = text.replace(old_status, new_status, 1)
current.write_text(text, encoding='utf-8')
