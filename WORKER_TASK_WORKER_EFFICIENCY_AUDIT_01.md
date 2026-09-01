# WORKER TASK — NEXT AVAILABLE SLOT

Task ID: `worker-efficiency-audit-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/worker-efficiency-audit-01.md`

## Goal

Audit recent worker execution patterns and identify avoidable repeated work, repeated dead ends, redundant GitHub/file reads, unnecessary workflow reruns, context-heavy navigation, and recurring orchestration mistakes that make bounded tasks take longer than necessary.

The goal is NOT to make workers rush or skip validation. The goal is to reduce repeated mistakes and rediscovery while preserving correctness and canonical ownership.

This is an operational/process audit only. Do not implement product features.

## Read first

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `PROJECT_ROUTES.md`
- `DIRECTOR_TASK_BOARD.md`
- recent compact worker reports under `reviews/worker_reports/`

Use Git history/logs only when a report specifically points to a delay or repeated failure that cannot be understood otherwise. Do not reconstruct the whole project.

## Scope

Review a bounded recent sample of worker tasks, prioritizing tasks from the current development period that had one or more of:
- long elapsed work;
- repeated failed retrieval/tool approaches;
- wrong report path / closeout rework;
- duplicated diagnosis already done in another task;
- stale route/schema assumptions;
- unnecessary broad searches;
- repeated workflow runs caused by the same preventable issue;
- director/worker role confusion;
- user corrections that revealed a reusable process mistake.

A sample of roughly the most recent 10–20 materially different worker tasks is sufficient. Do not audit every historical task.

## Existing controls to evaluate

Current `CHAT_PROTOCOL.md` already includes:
- context-budget discipline;
- route-first navigation;
- decision-before-history navigation;
- stop repeating after two failed approaches to the same data;
- truthful progress updates;
- >1 minute delay explanation plus durable improvement when obvious.

Determine whether these controls are:
- sufficient but inconsistently followed;
- missing a reusable knowledge artifact;
- too vague to prevent repeated mistakes;
- or causing unnecessary overhead themselves.

## Required analysis

For each recurring inefficiency pattern, record:
1. symptom;
2. concrete recent examples/refs;
3. root cause;
4. whether it was avoidable;
5. smallest durable prevention mechanism.

Pay special attention to whether workers repeatedly rediscover facts that should instead live in one of:
- `PROJECT_ROUTES.md` — where/how to find something;
- `PROJECT_DECISIONS.md` — why a non-obvious decision exists;
- a compact new operational lessons/known-failures artifact, only if routes/decisions/protocol are not suitable;
- task templates / report requirements.

## Candidate mechanisms to assess, not assume

Evaluate whether any of these would help:
- a compact `KNOWN_WORKER_PITFALLS.md` / operational lessons file: `symptom -> do not repeat -> correct route -> evidence/ref`;
- mandatory "Known pitfalls checked" task preflight for relevant tasks;
- worker report field for `Efficiency / avoidable detours / reusable lesson`;
- automatic or procedural rule that a repeated problem must update the correct durable route/lesson before closeout;
- stronger stop/escalation rule when a worker repeats the same failed method;
- report-path validation at task closeout;
- task templates that explicitly name expected canonical routes and forbidden rediscovery.

Do not create a heavy PM/telemetry system unless the evidence clearly justifies it.

## Metrics

Do not depend on exact wall-clock time unless reliable timestamps exist.

Prefer observable process metrics such as:
- repeated failed approaches to the same objective;
- redundant broad searches;
- repeated reading of already routed files;
- unnecessary workflow reruns;
- closeout/report-path rework;
- avoidable director intervention;
- reusable route/pitfall updates missed.

If reliable start/end timestamps can be derived cheaply from commits/reports, they may be used as supporting evidence only.

## Hard boundaries

Do NOT:
- modify product code, workflows, ranking, translation, giveaways, duration, UI or production data;
- perform broad code archaeology;
- judge a task inefficient merely because necessary external validation took time;
- recommend skipping acceptance or safety checks for speed;
- create arbitrary production quotas or deadlines;
- turn the director chat into a performance monitor.

## Done when

- recurring avoidable delay patterns are identified from a bounded recent sample;
- existing protocol controls are assessed;
- one minimal durable efficiency mechanism is recommended, with exact files/rules to change;
- optional secondary improvements are ranked by expected value vs overhead;
- no product work is performed.

## Report format

Save:
`reviews/worker_reports/worker-efficiency-audit-01.md`

### Task
Sample and scope.

### Existing controls
What already prevents wasted work.

### Recurring inefficiency patterns
Compact table: pattern | evidence | root cause | avoidable? | prevention.

### Recommended minimal mechanism
One primary durable change.

### Optional secondary improvements
Only high-value low-overhead items.

### What not to optimize away
Necessary validation/external waiting that should remain.

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded next step only.

Final response must include report path and commit ref.