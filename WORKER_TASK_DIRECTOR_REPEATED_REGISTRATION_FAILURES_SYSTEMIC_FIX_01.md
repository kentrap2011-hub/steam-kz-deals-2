# ЧАТ 3 — системный разбор повторных ошибок регистрации и директорского управления

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: director-repeated-registration-failures-systemic-fix-01
Worker: НОВЫЙ физический ЧАТ 3, независимый от текущего директора и параллельных QA-ЧАТОВ 1/2.
Mode: independent READ-ONLY RECON / SYSTEM DESIGN; one report-only DRAFT PR.
Worker report: reviews/worker_reports/director-repeated-registration-failures-systemic-fix-01.md

## Start / evidence discipline

Fully read current `CHAT_PROTOCOL.md` and pass START, then this task file, current `DIRECTOR_PROTOCOL.md`, relevant `CHAT_CONTEXT.md` and `PROJECT_ROUTES.md`. Work **only** in the specified repository and canonical `main`; historical reports may be in exact PR branches, not in main. Use bounded targeted fetches, not a repository-wide archaeology or the full Board history. If a required previous audit is already comprehensive, cite/reuse its verified findings instead of repeating its entire research. Distinguish confirmed GitHub facts, supplied user chronology and hypotheses; never claim access to hidden other ChatGPT chats or their time measurements.

## User question and new confirmed incident

User reports another ~5-minute wait to receive two very short launch prompts for new QA Chats 1/2 (2026-10-28). Director was registering two existing-PR independent QA tasks in [registration PR #338](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/338), although source PRs #322/#323 already existed and task goals were known. Two **avoidable** GitHub CI failures occurred:

1. Site task validation run [40683651731](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40683651731) failed because Director wrote `effort: "малая"` rather than allowed `низкая` from `scripts/build_site_tasks.py`.
2. After fixing that, site task validation run [40683768208](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40683768208) failed because public registry text contained forbidden `PR #` despite the site-task regression test.
3. Final runs [40683872119](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40683872119) and [40683872112](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40683872112) passed; #338 merged. Those failures caused unnecessary amendments, new CI runs, waiting and repeated reads. The ~5 minutes are **user-observed**, not an exact GitHub measurement.

**Critical recurrence:** an existing independent report in **draft PR #319**, path `reviews/worker_reports/director-recurrent-long-prompts-slow-registration-audit-01.md` on branch `audit/director-recurrent-long-prompts-slow-registration-01`, already diagnosed registration PR #317 on 2026-10-27 with the *same* public `PR #` defect, unnecessary unrelated registry edits and two red CI cycles. #319 recommended a bounded structured/atomic registration operation, but is still an open report-only PR. Determine what was merely reported, what was implemented, and why this repeat occurred **after** that diagnosis. Do not simply restate the #319 report.

## Required cross-check of past findings (targeted, no blanket audit)

Read exact relevant report/changes for #319 first; cross-check with older report-only audits **#248, #251, #287, #305, #306, #325** and actual merged governance changes **#241, #299, #308, #333, #334, #337** only to the extent necessary for the causal chain. Use named `WORKER_TASK_DIRECTOR_*.md` or exact GitHub PR refs to locate reports in draft branches. The user wants to know why *several audits* did not produce durable operational improvement; audit-count itself is not a desired output. If findings duplicate, consolidate them; explicitly mark accepted/merged vs only draft recommendations and note their remaining owner.

## Questions to answer, concretely

1. Reconstruct minimal timeline/commit history of #338 and its CI failure paths; compare #317 and #338. Distinguish needed REGISTER work (task-file + registry + current Board + existing CI), unnecessary reads/edits, avoidable validation failures, serial tool/CI latency, and unobservable UI elapsed time. Prove precise root mechanisms, not vague “director was slow” or “read more carefully.”
2. Explain exactly **why the model/director repeated known failures despite protocols and prior audits**, including human-readable instructions vs executable guardrails, duplicated state (Board/JSON/task files), free-form mutation, public field format/enum discovery, preflight/test feasibility when using GitHub connector only, and report-only recommendations not making it into an owner-approved implementation. Verify each item; do not assume.
3. Build a concise matrix: old finding/recommendation → actually implemented or not → effect expected → failure repeated on #338 → remaining structural gap/owner. Identify whether the active/old #319 task should be accepted, superseded, or remain separate rather than launching repeated audits indefinitely.
4. Compare **materially different solutions**, not only another sentence in `DIRECTOR_PROTOCOL.md`: a minimal bounded fix; a deterministic pre-commit registration generator/editor validating allowed enums and public fields with a write-set of only the new task ID; a single source of truth with generated Board/launcher; and a more radical change to director/worker handoff or administrative overhead if justified. You may find better options. For each: precise files/components, compatibility with currently available tools, real improvement vs illusion, implementation effort, risks and rollback/migration, and whether it **actually prevents BOTH #338 errors before GitHub CI**, rather than just detecting them afterward.
5. Recommend **one prioritized actionable implementation plan** (or a small staged plan if technically inseparable): named owner(s), exact files and interfaces, data invariants, minimal behavior, bounded change set, acceptance criteria including a replay of #317 and #338 without extra failed CI cycles, and a practical future ordinary registration dry run. Explain how it avoids increasing token/context load, prompts, mandatory audits, PR count and CI time. Preserve exact-head safety, risk-based QA, user authorization and GitHub control plane. Do not introduce a new scheduler, automation, giant governance document or registration helper that the available tools cannot actually execute.
6. Answer directly if a deeper architecture change is worth doing now. Do not treat every idea as mandatory; say what to **stop doing** and which prior audit findings should be retired/closed to avoid another loop.

## Output and limits

One compact actionable report at `reviews/worker_reports/director-repeated-registration-failures-systemic-fix-01.md`, published in **exactly one report-only DRAFT PR**, with status `AUDIT_COMPLETE` or `BLOCKED_EVIDENCE`. Open with a plain-Russian verdict for the user and **one proposed next IMPLEMENT task**, not an invitation to another audit. Include exact evidence links, short trade-off comparison and executable acceptance scenarios. If source is inaccessible, say what is missing, do not invent details.

**No implementation yet**: do not edit `DIRECTOR_PROTOCOL.md`, `CHAT_PROTOCOL.md`, `scripts/`, `config/`, Board, worker tasks, main, source PRs, CI/workflows, GitHub branch settings, production, Deep/Dossier, automations, scheduled tasks or any registry item. Do not merge PRs or dispatch workflows. Do not change physical chat slots or disturb ongoing independent QA Chats 1/2. Director owns any future decision/registration/acceptance.
