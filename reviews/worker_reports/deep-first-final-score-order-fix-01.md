# Deep-first final-score order fix 01 — worker report

## 1. Summary
Task: `WORKER_TASK_DEEP_FIRST_FINAL_SCORE_ORDER_FIX_01.md`.

Implemented a contract-first correction so the canonical automatic visible-card order is:
`deep_fit → fast_fit → analysis_incomplete → not_analyzed`.

Inside completed Deep and Fast stages, ordering is `total_score DESC` with deterministic title/ID fallback. Score composition itself is unchanged.

## 2. Startup / context package used
Read and obeyed from current `main`:
- `CHAT_PROTOCOL.md` and START gate;
- `CHAT_CONTEXT.md`;
- `WORKER_TASK_DEEP_FIRST_FINAL_SCORE_ORDER_FIX_01.md`;
- `CURRENT_TASK.md`;
- relevant `PROJECT_ROUTES.md`, `PROJECT_RULES.md`, `PROJECT_DECISIONS.md`;
- `config/final_ranking_policy.json`;
- `config/progressive_personalization_contract.json`;
- `config/execution_ownership_contract.json`;
- `reviews/worker_reports/kof-xv-high-priority-without-deep-diagnostic-01.md`.

No unrelated task was started.

## 3. Architecture preflight
Ownership remains unchanged:
- GitHub owns ranking policy, deterministic ranking transform, persistence, queue/order publication and validation.
- Fast/PASS 1, Dossier and Deep/PASS 2 semantic workers keep their existing bounded ownership.
- Browser is presentation/local-view state only.
- No scheduler, retry, backlog-manager or Scheduled Task ownership was moved.
- No semantic worker was invoked and no semantic result was rewritten.

## 4. Confirmed prior conflict / root cause
The pinned KOF diagnostic showed:
- Severed Steel — current Deep, score 71.8;
- THE KING OF FIGHTERS XV — current Fast, score 68.0;
- MY HERO ONE'S JUSTICE 2 — current Deep, score 67.1.

Old Progressive ranking collapsed current Deep-fit and Fast-fit into the same `analyzed_fit` ranking tier, so score could place KOF Fast 68.0 above MY HERO Deep 67.1. The older RANK-002/RANK-010 urgency clauses could also move cards before score without respecting Deep/Fast authority.

## 5. Canonical ranking decision
Added canonical `RANK-013 — Deep-first: этап анализа раньше итогового балла, срочность только внутри этапа`.

It supersedes only the conflicting cross-stage urgency/order parts of RANK-002/RANK-010. It does not change score weights or semantic eligibility.

## 6. Contract changes
`config/final_ranking_policy.json` now defines:
- default automatic order: `ranking_stage_asc → stage_score_desc → title_asc`;
- completed-fit stage order: `total_score_desc → title_asc`;
- explicit urgency view: `ranking_stage_asc → sale_expiry_urgency_asc → stage_score_desc → title_asc`;
- producer-owned stage precedence: `deep_fit, fast_fit, analysis_incomplete, not_analyzed`.

`config/progressive_personalization_contract.json` now publishes the same stage model and makes `ranking_stage` / `ranking_stage_rank` producer-owned.

## 7. Producer implementation
`scripts/progressive_personalization.py` now:
- derives canonical ranking stage only from current producer-owned state;
- scores Deep and provisional/Fast groups independently with the unchanged V2 scorer;
- computes unresolved purchase-only score as before;
- applies the cross-stage order only after stage-local score calculation;
- emits one canonical global `priority_rank` for the default feed;
- emits ranking diagnostics that explain stage first, then score, then deterministic fallback.

No score is compared across Deep/Fast stage boundaries.

## 8. Reusable-cache edge case
Existing exact-compatible reusable Taste cache is an established Fast-path that can resolve `analyzed_fit` without rerunning PASS 1.

To preserve current behavior without inventing a fifth stage, such a current compatible-cache fit is placed in provisional `fast_fit`:
- below authoritative current Deep;
- above unresolved/not-analyzed;
- never treated as Deep.

This compatibility rule was added to the canonical decision/contracts before runtime implementation.

## 9. Current Deep, stale Deep, and PPD-012
Deep stage is granted only when current effective authority is Deep.

Therefore:
- missing Deep + valid Fast => `fast_fit`;
- Deep waiting/incomplete/error + valid Fast => `fast_fit`;
- stale/historical Deep fields do not grant Deep stage;
- PPD-012 semantically reconciled current authoritative Deep uses the existing `effective_analysis_source=deep` path and therefore receives `deep_fit`.

## 10. Score calculation preservation
`scripts/priority_ranking.py` still owns and calculates the same V2 score model.

The only ranking change inside that helper is that its ordering role is now explicitly stage-local:
`total_score DESC → title`.

No personal, purchase, risk, wishlist, achievement, history, savings, package or duration weights were changed.

## 11. Urgency behavior
Default automatic feed no longer has urgency as a global upper layer.

Default:
`stage → stage score → title/ID`.

Explicit user-selected «Срочные» view:
`stage → urgency → stage score → title/ID`.

Urgency cannot move Fast above Deep, or unresolved/not-analyzed above completed Deep/Fast.

## 12. Browser / queue behavior
`web/progressive-personalization-ui.js`:
- consumes producer `priority_rank` for default order;
- consumes producer `ranking_stage_rank` for urgency view;
- does not infer semantic authority from stage-indicator decoration.

`web/app.js`:
- bumps local queue schema to v6;
- includes stage/rank/urgency fields in ranking signature;
- changes the cursor header from `Приоритет: N из M` to `Позиция в ленте: N из M`;
- no longer labels the local cursor as an independent “priority/rating”.

## 13. Manual end-of-queue override
Existing explicit `manual_end_at` behavior is unchanged and remains absolute:
automatic/view-mode ordering is calculated first, then manual-end cards are appended.

## 14. analyzed_not_fit / semantic ownership
`analyzed_not_fit` visibility/exclusion behavior is unchanged.

No Fast result, Deep result, Dossier artifact, semantic worker prompt, scheduler setting, queue manifest, retry rule or recovery authority was changed.

## 15. Focused regression coverage
Added `scripts/test_deep_first_final_score_order.py` covering:
1. Deep score 60 above Fast score 99;
2. Deep 70 above Deep 60;
3. Fast 90 above Fast 80;
4. deterministic title/ID tie-break;
5. Fast without Deep;
6. Fast with Deep waiting;
7. Fast with Deep incomplete/recovery;
8. stale-looking Deep does not grant Deep authority;
9. PPD-012 current Deep;
10. unresolved cannot outrank Fast/Deep;
11. not-analyzed cannot outrank Fast/Deep;
12. purchase-only score orders inside unresolved;
13. default ignores urgency inside stage;
14. urgency contract is nested after stage;
15. score bytes unchanged through stage wrapper;
16. UI uses producer canonical rank and feed-position wording;
17. manual end remains absolute;
18. concrete MY HERO Deep 67.1 above KOF XV Fast 68.0.

The JS regression additionally verifies explicit urgency reorder only inside one stage.

## 16. Commercial/package and freshness preservation
`ranking_stage` and `ranking_stage_rank` were added to semantic-preservation/protected fields for deterministic commercial refresh and deploy freshness checks.

Package purchase scoring still uses the unchanged stage-local V2 score helper; package-value regression expectation was updated only for the removal of default urgency from that stage-local order.

## 17. Validation results
PR #117 validation completed successfully on head `42444aad7f4b3d8b3fc155dfc646cc4fbbcfe6e6`:
- `Validate backlog dispositions` — run `36458847048` — success;
- `Validate package purchase value` — run `36458847059` — success;
- `Validate Progressive PASS 2 core` — run `36458847057` — success.

The PASS 2 job explicitly passed:
- PPD-012 Progressive profile semantic identity stability;
- PASS 2 core and Dossier integration;
- Deep legacy/recovery regressions;
- PASS 1 regressions;
- Progressive personalization;
- `Deep-first final-score ordering regression`;
- unresolved-row preservation;
- visual activation routing;
- UI provenance regression.

## 18. Fresh-main reconcile / merge / publication evidence
Initial working branch: `fix/deep-first-final-score-order-01`.

Before PR, `main` advanced by 6 commits containing only Dossier/Deep data/work progress. None overlapped implementation files. The branch was rebuilt exactly on fresh `main` `85f55df8ee542ebfc47f82d9f7c15dbef2b46141`, preserving that progress.

Integration refs:
- PR: `#117`;
- validated PR head: `42444aad7f4b3d8b3fc155dfc646cc4fbbcfe6e6`;
- merge commit on `main`: `9cb123765884440d37632740d51695a371338483`.

Active CHAT 2 / Dossier progress was not modified or reverted.

Post-merge normal GitHub publication path:
- `Build daily visual payload` push run `36458961848` entered the full `build` job;
- ranking contract validation, focused Deep-first regression, Progressive tests, package-value tests, card-explanation validation and `Build and refresh canonical visual payload once` all succeeded in that runner;
- publication then stopped at the independent gate `Require meaningful Russian descriptions before canonical commit`;
- therefore the ranking review/lookup/persist commit steps did not run and no fresh canonical visual commit was created.

This blocker predates this task: pre-merge main build run `36457892914` had already failed at the exact same `Require meaningful Russian descriptions before canonical commit` gate.

A subsequent automatically triggered `Build daily visual payload` run `36459026993` reports overall success only because its full `build` job was skipped after an ineligible/failed pre-AI upstream; it produced only the `no_build_receipt`. It is not publication evidence.

Pages/deploy evidence:
- push deploy run `36458961533` — cancelled;
- workflow-run deploy `36459045495` — skipped;
- no fresh Pages deployment exists for the new ranking;
- no fresh persisted `data/production/visual/current.json` exists from this task, so final first-position/KOF-vs-MY-HERO verification against persisted production output cannot truthfully be claimed.

The unrelated Russian-description quality gate was not bypassed or modified, because doing so would be a different task.

## 19. Final status
`blocked`

Implementation, contracts, regressions, PR validation and merge are complete. The remaining blocker is only the pre-existing Russian-description publication gate, which prevents the task-required fresh canonical visual commit and Pages proof.
