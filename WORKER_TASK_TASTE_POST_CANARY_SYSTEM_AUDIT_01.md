# WORKER TASK — TASTE POST-CANARY SYSTEM AUDIT 01

## Task ID
`taste-post-canary-system-audit-01`

## Mode
`ACCEPTANCE / READ-ONLY SYSTEM AUDIT`

## Expected report
`reviews/worker_reports/taste-post-canary-system-audit-01.md`

## Goal
Independently verify that Taste is safe and ready for normal daily operation after the accepted real Chernobylite test.

This task must NOT run another real semantic game analysis.

## Required predecessor
Read first:
- `reviews/worker_reports/taste-current-live-profile-binding-fix-01.md`
- `reviews/worker_reports/taste-chernobylite-real-canary-acceptance-02.md`

The Chernobylite acceptance report must show final status:
`complete_canary_accepted_ready_for_system_audit`

If not, stop `blocked`.

## Required reading
- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `WORKER_REPORT_DURABILITY_PROTOCOL.md`
- `WORKER_ANTI_STALL_PROTOCOL.md`
- `DIRECTOR_USER_COMMUNICATION_PROTOCOL.md`
- `DIRECTOR_TASK_BOARD.md`
- the two predecessor reports above
- only the current canonical Taste policy, ownership, producer, queue, cache, ingest, receipt, and profile-binding files needed for the audit.

Do not perform broad history/log archaeology.

## Audit questions
Prove the current production state answers YES to all of these:

1. The accepted Chernobylite result is present exactly once in canonical Taste state.
2. `App_1016800` is no longer pending in the Taste queue.
3. The accepted result uses the required producer generation 2 and exact model/profile/semantics/fingerprint/context bindings.
4. The canonical ingest receipt exists and matches the accepted one-result transaction.
5. The active inbox no longer contains the consumed Chernobylite result.
6. The Taste cache/overlay contains the accepted result and is internally consistent.
7. The existing Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9` still exists, remains enabled, and is restored to DAILY 01:00 Europe/Samara.
8. No second Scheduled Task exists for the same semantic role.
9. No second semantic result or fallback game was produced by the acceptance run.
10. The current one-game preparation route still freezes one exact current-live profile version and does not depend on the user pausing profile updates.
11. If the profile changes before a new tuple is frozen, the newer version is selected; if it changes after freeze, versions cannot be mixed.
12. The daily path cannot silently reuse the old stale profile binding that caused the earlier failure.
13. Producer fence, binding checks, V5, evidence and price-blind rules remain enabled and unchanged.
14. No manual queue/cache/receipt/inbox repair is required for normal next-run operation.
15. No paid OpenAI API, Copilot, paid external service, or external scheduler is required.
16. There is no unresolved blocker that would make daily operation unsafe or repeatedly stall on profile updates.

## Allowed validation
- read-only inspection of current `main` and canonical Taste state;
- focused existing tests;
- read-only/non-semantic preparation if needed to prove current behavior;
- inspection of the exact accepted GitHub Actions run/job/receipt referenced by the predecessor report;
- inspection of the existing Scheduled Task state.

Do NOT generate or ingest another semantic result.

## Hard boundaries
Do NOT:
- modify production code/config/data;
- modify or trigger the Scheduled Task;
- create another Scheduled Task;
- generate any semantic Taste result;
- ingest any new semantic result;
- edit queue/cache/receipt/inbox manually;
- process a second game;
- widen daily production;
- start unrelated Giveaway/ITAD work;
- use paid OpenAI API, Copilot, paid external service, or external scheduler.

If a real defect is found, report it and stop. Do not fix it in this audit.

## Decision
Final report must give exactly one recommendation:
- `PASS_READY_FOR_DAILY_OPERATION`
- `FAIL_NOT_READY_FOR_DAILY_OPERATION`

If PASS, state exactly what may be enabled next and what must remain unchanged.
If FAIL, state the smallest concrete blocker and recommended next bounded task.

## Required report
Save:
`reviews/worker_reports/taste-post-canary-system-audit-01.md`

Include:
1. Task
2. Predecessor verification
3. Current production state
4. Chernobylite persistence/queue/receipt/inbox proof
5. Scheduled Task state
6. Live-profile update safety proof
7. Guardrail proof
8. Any unresolved issue
9. Decision
10. Recommended next step
11. Exact file/run/job/receipt refs used
12. Efficiency / reusable lesson

Final lifecycle status exactly one:
- `complete_system_audit_pass`
- `complete_system_audit_fail`
- `blocked`

Do not widen production in this task.
