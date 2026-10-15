# ЧАТ 1 — снять тупиковую паузу Deep после исчерпания score-explainability migration

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: deep-score-migration-zero-pending-release-normal-01
Worker slot: НОВЫЙ физический ЧАТ 1 (предыдущий Research/PR #227 завершён)
Mode: narrow IMPLEMENT + focused regression, separate PR, no self-merge
Worker report: reviews/worker_reports/deep-score-migration-zero-pending-release-normal-01.md

## START / verified Director issue
Fully read latest main CHAT_PROTOCOL.md and execute START, then CHAT_CONTEXT.md, this task, relevant PROJECT_ROUTES.md / PROJECT_DECISIONS.md score-evidence route and exact ownership/Deep contracts. Work ONLY in kentrap2011-hub/steam-kz-deals-2; if GitHub opens another repo, switch before inspecting/editing. Only open code/tests specifically needed for this issue.

Director verified current main 2026-10-15: `data/production/pre_ai/progressive_pass2_work.json` has `items=[]`, `projection_status=score_explainability_migration_active` even though recomputed normal `normal_pass2_eligible_count=158`. Its finite score migration shows `total_count=43`, `pending_count=0`, `accepted_count=42` (including already-compliant 1), `stale_or_missing_prior_count=1`, `complete=false`, `deep_normal_work_paused_for_score_explainability_migration=true`. The actual mechanism is `scripts/progressive_pass2.py::score_explainability_work_and_metrics` + `scripts/build_progressive_pass2_work.py` lines ~199-252: the builder pauses ALL normal work whenever migration !complete, even when no migration item remains runnable. Current Deep semantic worker has nothing to do. Do NOT assume the stale target is accepted; determine exact authoritative target disposition and affected current product identity from existing bounded sources/tests first.

## Deliver actual smallest root fix, not another plan
1. Resolve **finite migration exhausted without acceptance of every frozen target** as a distinct, honest terminal/non-runnable accounting condition. Preserve `accepted_count=42`, `stale_or_missing_prior_count=1`, `complete=false` if that is semantically correct: do NOT falsely count stale as accepted/completed or retroactively rewrite the frozen 43-target manifest, migrate/fabricate a result, invent recovery authorization or retry.
2. When score migration has **zero actually runnable pending items** and no in-flight authorized pending result that must be honored, ordinary GitHub-computed Deep eligible work must be resumed in canonical order rather than blocked indefinitely. Model migration completion versus migration exhaustion/disposition separately as needed, preserve visible evidence of unresolved stale target and all old acceptance/history. Respect existing normal-work ordering: never completed first, then oldest last successful. If an exact authoritative contract requires another handling, adjust it narrowly with explicit rationale and isolated tests; do not bypass its substantive score-finding proof for NEW analyzed_fit results.
3. Keep real migration processing priority when **pending > 0**; never interleave/rebind started frozen runs, bypass run-start V2 marker/confirmed receipt, or unlock arbitrary old migration retry. Resume normal Deep only through `scripts/build_progressive_pass2_work.py` existing deterministic GitHub control plane; no manual queue file patching, no direct `data/production/**` or `data/cache/**` state rewrite.
4. Add focused regression for (a) current 43 total / 42 accepted / 1 stale / 0 pending / 158 normal eligible unblocks, (b) nonzero migration pending stays prioritized, (c) fully accepted migration stays complete, (d) submitted-but-not-resolved result and ordinary coverage/recovery/history accounting stay truthful. Execute bounded existing PASS2 producer/core/Deep-history tests and new PR CI. Check `PROJECT_DECISIONS.md` rationale before changing any migration stop rule.
5. Do not edit site UI/Deep history producer unrelated to the pause, Deep Stage1/2 cutover, Dossier, Fast/ranking, Scheduled Tasks/automations, retries, scope, taste/profile pins or any GitHub semantically accepted result. Do not invoke Deep semantic work from this implementation chat.
6. Deliver focused PR and exact worker-report, explain whether next normal producer cycle will expose >0 actual work, and distinguish verified tests from not-yet-run production recomputation. DO NOT merge PR; stop.

## Noninterference
Parallel Chat2 works only on existing Dossier PR #228. This task owns `scripts/progressive_pass2.py` and `scripts/build_progressive_pass2_work.py` + focused tests/contract if strictly needed. Do not edit `CURRENT_TASK.md`, Director Board/registry, `data/production/**` or Chat2 Dossier paths; no duplicate architecture.
