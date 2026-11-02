# НОВЫЙ ЧАТ 1 — непрерывное завершение работ и резервирование при сбоях

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Task ID: director-durable-closeout-recovery-implement-01
Worker slot: НОВЫЙ физический ЧАТ 1; старый завершён.
Mode: scoped RECON and safety-first IMPLEMENT, one draft PR.
Report: reviews/worker_reports/director-durable-closeout-recovery-implement-01.md

Сначала прочитай CHAT_PROTOCOL.md, выполни START gate, затем этот task, CHAT_CONTEXT.md, PROJECT_ROUTES.md и актуальные разделы DIRECTOR_PROTOCOL.md. Работай только в kentrap2011-hub/steam-kz-deals-2; другой репозиторий запрещён, при неверном target STOP.

User explicitly requests a durable end-to-end completion chain: approved task -> worker result -> risk-based QA -> director merge -> any separately authorized release verification or accurate blocker, with a clearly persisted owner/next action and NO forgotten orphan PR. Never mark original task fully closed merely because one worker completed. Implement the minimal safe persistent closeout protocol/registry reconciliation, reusing existing canonical registry/Board and PR/checks instead of creating a rival approval store. No automatic semantic research, production, scheduled actions or unsafe merge. Detect prior user authorization accurately; do not invent it.

Investigate narrowly the tool-registration incident from 2026-11-02: one official registration request was rejected by OpenAI tool safety before GitHub writes (exact cause unknown), whereas GitHub read and issue create succeeded; a separate earlier deterministic prewrite validation rejected forbidden public field 'PR #' with writeCalls:0. Distinguish tool-level rejection from GitHub outage or schema validation. Design and, where safe and limited, implement a fail-closed durable recovery outbox using existing GitHub issue #375 as pinned example. On failed registration, write a precise pending record via permitted channel if available; make canonical registration reconciliation/dedup and proven final acceptance mandatory before closing outbox. If no GitHub write available, use portable/library backed handoff requiring explicit later reconciliation; never claim automatic sync without actual runner.

Avoid a repeated generic audit: reuse existing prior reports about post-QA merge followthrough and registration failures; implement a small, testable change where technical authority is proven. If unsafe to implement automation without new ownership, return bounded contract/implementation handoff with exact blockers rather than speculate. Preserve existing separation of duties, required CI/QA and distinct permission gates for production, semantic one-shots, rights and retries.

Allowed changes: DIRECTOR_PROTOCOL.md, CHAT_PROTOCOL.md, relevant existing director closeout/recovery validation or helper scripts if architecture preflight proves owner; this report. Do not modify Dossier V1/V2, Fast/Deep, runtime, production, canonical candidate states or schedules, and do not modify the source PR #372 concurrently. If overlapping director rules are currently edited in PR #372, coordinate by leaving those exact files untouched and submit report-only actionable implement scope instead of conflicting writes.

Acceptance: demonstrate tests for positive closeout, QA fail, unapproved merge, stale HEAD, pending CI, registration tool rejection with no write, outbox dedup/reconciliation and no forgotten outcome. One draft PR, exact-head CI, explicit risk classification and next actor. No worker self-merge.
