# ЧАТ 1 — независимая публикация сайта
Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: site-publication-independent-failure-isolation-implement-01
Mode: IMPLEMENT (draft PR only)
Worker slot: НОВЫЙ ЧАТ 1
Report: reviews/worker_reports/site-publication-independent-failure-isolation-implement-01.md

First read CHAT_PROTOCOL.md, CHAT_CONTEXT.md, START gate, routes, architecture preflight and relevant contracts. Work ONLY in this repository. Read full PR #236 report (head 9b815b8ec1055a80e5096a35de71f0338edb5f0c) and current workflow/ownership/resilience contracts.

Implement bounded isolation of unrelated Director task registry, task page generation, synthetic regressions and independent optional site sections from paid-games publication. Preserve mandatory fail-closed verification of prices, source/receipt, canonical material hashes, scope, schema, safety and exact staged bytes. Separate synthetic tests into PR CI while retaining real deploy acceptance. Use verified compatible last-good section or omit it with degraded diagnostic and no broken links; do not mix incompatible commercial snapshots. Correct temp Git cleanup race without weakening mismatch tests. Respect status-only/giveaway-only contract-specific gates. Record source/staged/published hashes and per-section disposition.

Tests: bad tasks registry, missing recent_completion, generator crash, optional section failures, synthetic cleanup; independently valid paid publication succeeds; corrupt prices, scope, canonical inputs, receipt, SHA or run ID fail closed. Verify actual live/canonical freshness read-only or mark unverified with precise evidence gap. No production Deploy, merge, schedules, semantic workers, new queue/retry owner or unrelated changes. Submit draft implementation PR, tests/CI, exact HEAD, independent QA handoff and report at above path. Stop BLOCKED if current Board/registry or contracts deny authority; never bypass START.
