# Worker efficiency audit 01

### Task

Audit recent worker execution patterns for avoidable repeated work, repeated dead ends, redundant navigation, unnecessary reruns, closeout rework, stale assumptions, and reusable orchestration mistakes. This is process-only; no product/runtime behavior was changed.

Sample: 17 materially different recent worker reports from the current development period, bounded to the areas most likely to expose efficiency problems:

- `reviews/worker_reports/backlog-disposition-validator-01.md`
- `reviews/worker_reports/task-memory-audit-01.md`
- `reviews/worker_reports/detailed-score-ui-01.md`
- `reviews/worker_reports/detailed-score-user-fixes-01.md`
- `reviews/worker_reports/compact-purchase-options-01.md`
- `reviews/worker_reports/image-swipe-01.md`
- `reviews/worker_reports/package-acceptance-01.md`
- `reviews/worker_reports/package-acceptance-02.md`
- `reviews/worker_reports/package-ui-blocker-fix-01.md`
- `reviews/worker_reports/card-explanation-audit-01.md`
- `reviews/worker_reports/duration-data-diagnosis-01.md`
- `reviews/worker_reports/duration-source-recon-01.md`
- `reviews/worker_reports/duration-provider-recon-01.md`
- `reviews/worker_reports/duration-contract-01.md`
- `reviews/worker_reports/duration-igdb-implement-01.md`
- `reviews/worker_reports/ru-translation-runtime-acceptance-01.md`
- `reviews/worker_reports/cross-platform-giveaway-recon-01.md`

No wall-clock efficiency claims are made because reliable per-task start/end timestamps were not needed. The audit uses observable process evidence: rework tasks, failed approaches, reruns, stale assertions, recommendation backtracking, lifecycle recovery, and missed durable lessons.

### Existing controls

`CHAT_PROTOCOL.md` / `CHAT_CONTEXT.md` already contain the right baseline controls:

- context-budget discipline and minimal reads;
- route-first navigation through `PROJECT_ROUTES.md`;
- decision-before-history navigation through `PROJECT_DECISIONS.md`;
- stop repeating after two failed ways to obtain the same data;
- architecture preflight before workflow/runtime/queue/ownership changes;
- truthful progress updates;
- durable route updates when navigation required meaningful rediscovery;
- a >1 minute delay explanation plus durable improvement when obvious;
- full PRE-SEND checks before closeout.

Assessment:

1. **Mostly sufficient, but inconsistently applied at the edges.** The sample does not justify replacing these controls.
2. **One gap is real:** there is no small canonical home for cross-cutting operational failure recipes that are neither a project route nor a design decision. Examples: stale static regression proxies, GitHub Pages artifact-rerun traps, or a recommendation that assumes a canonical source path before proving one exists.
3. **Architecture preflight is slightly too narrow in wording.** It clearly gates implementation, but the duration chain shows that a worker can still recommend an IMPLEMENT that would fail that same preflight when the director acts on it.
4. **The controls themselves are not the main observed overhead.** Re-reading the core protocol/context is repetitive, but the sample gives stronger evidence for downstream rework than for harmful protocol-reading cost. Do not weaken canonical preflight/validation to save time.
5. **Truthful progress and >1 minute explanation cannot be reliably audited from saved reports alone.** No claim is made that they were or were not followed in chat transcripts.

### Recurring inefficiency patterns

| pattern | evidence | root cause | avoidable? | prevention |
|---|---|---|---|---|
| **Validation checks the proxy/code shape instead of the actual contract/outcome** | `detailed-score-ui-01` had a green regression that checked `panel.hidden`, but `detailed-score-user-fixes-01` proved CSS `display:flex` still made the panel visible on the real browser. `package-ui-blocker-fix-01` shows a Python static regression still requiring obsolete `window.renderPackageDeal=function(g)`, obsolete copy, and an old asset token after the compact UI had already been accepted; run `33516400092` was blocked until commit `c243dfe498abec27923bc7f229f34fc82b5c26f0`. `package-acceptance-01` then found a Definition-of-Done regression scenario (Season Pass/constituent overlap) had never been implemented, requiring another IMPLEMENT + second acceptance (`package-acceptance-02`). | Tests/acceptance were not consistently traced from each required semantic/user-visible outcome to an executed check. Some guards were coupled to implementation text/shape rather than behavior. | **Yes, mostly.** Real-device judgment still cannot be automated away, but the CSS-visible state, stale source-shape assertion, and missing explicit DoD regression were preventable. | Prefer behavioral/output assertions over source-shape markers; when refactoring implementation/copy/asset wiring, update dependent static guards atomically; before closeout map each explicit DoD item to an executed check or mark it unproven. Keep real-device checks separate rather than pretending DOM/property tests replace them. |
| **Architecture/source preflight happens after a next-step recommendation instead of before it** | `duration-data-diagnosis-01` recommended a bounded IMPLEMENT to add/connect normalized duration enrichment from an “already allowed canonical source path”. The immediately following `duration-source-recon-01` proved that no canonical structured duration source/path, cache, contract, workflow, or allowed external runtime existed and that IMPLEMENT would violate the architecture gate. This forced provider recon -> contract -> implementation before the original recommendation became valid. | PRE-SEND did not require architecture preflight for a worker's `Recommended next step`; the rule is phrased primarily around making changes. | **Yes.** The diagnosis itself was useful; the avoidable part was recommending an implementation before proving the required canonical route/authority existed. | Apply architecture preflight to any recommended next step that would add/change a source, workflow, runtime, schedule, queue, retry/checkpoint, or ownership boundary. If no authorizing contract/route exists, recommend RECON/CONTRACT, not IMPLEMENT. |
| **Known GitHub Pages concurrency/rerun failure modes are rediscovered** | `detailed-score-ui-01` and `compact-purchase-options-01` both had deploy attempts cancelled by existing `concurrency: pages` and then rerun. `detailed-score-user-fixes-01` hit a more specific dead end: rerunning a run that had already uploaded the `github-pages` artifact produced a duplicate-artifact failure; the worker then had to use a run that had stopped before artifact upload (`job 99817807119`). | The generic “stop repeating after two failed approaches” rule is too abstract to encode the exact safe recovery for this recurring CI failure mode. | **Partly.** Concurrency cancellation itself is expected and should not be optimized away. Choosing a known-bad rerun target is avoidable. | Durable pitfall recipe: after Pages concurrency cancellation, inspect the stopping step first; do not rerun a run that already uploaded the Pages artifact; use a safe pre-upload cancelled run, a fresh supported trigger, or a newer successful run that demonstrably contains the target change. |
| **Task closeout/lifecycle facts were historically removed before durable disposition/acceptance** | `task-memory-audit-01` documents repeated unsafe backlog deletion/non-atomic transfer: `5573f6...`, `7bcff5c...`, `b383938...`, and `6088c1...`; user/device acceptance could also remain only in live chat. This caused later recovery/reconciliation work. | Textual lifecycle rules did not originally require an atomic durable destination for every deletion/verification state. | **Yes historically; now largely addressed.** | Do **not** add another mechanism. `backlog-disposition-validator-01` now provides the correct lightweight fail-closed guard, with main validation run `33534211167` green after its integration-scope fix. Keep this as an example of when a recurring process failure should become a machine guard. |
| **Route/schema drift can remain trapped inside a RECON report** | `card-explanation-audit-01` found that a referenced standalone `config/visual_payload.schema.json` was absent and that current behavior had to be bound from the canonical artifact plus embedded producer contract; it explicitly calls stale schema/audit documentation route drift. `duration-source-recon-01` had to inspect a full recursive tree to prove no duration-specific path existed—appropriate for first discovery, but a future worker should not need to repeat that discovery. | `PROJECT_ROUTES.md` is the right home for proven navigation facts, but strict report-only/read-only task boundaries can prevent a worker from updating it, so the discovery may survive only in a long report. | **Partly.** First discovery is necessary; repeated rediscovery is avoidable. | When read-only scope forbids operational-doc edits, the worker report should flag a **route/pitfall candidate** for one bounded follow-up rather than silently leaving the fact buried. When edits are allowed, update `PROJECT_ROUTES.md` in the same task. |
| **Large RECON reports can defeat the director's compact-context goal** | Several bounded audits are necessarily detailed: `card-explanation-audit-01` and `cross-platform-giveaway-recon-01` are large; `duration-provider-recon-01` also carries extensive provider evidence. Their research is useful, but `DIRECTOR_PROTOCOL.md` expects compact worker handoff. | The same file is serving both as compact director handoff and as detailed audit evidence. | **Partly, lower confidence as a delay source.** | Secondary only: keep the decision/status/refs at the top and move large sample matrices/evidence appendices to a separate review artifact only when the task genuinely needs them. Do not impose arbitrary word quotas. |

Additional observations:

- **No strong recent evidence of wrong report-path closeout errors** was found in this bounded sample. Do not add report-path automation solely because it was a candidate in the task prompt.
- **No evidence supports a heavy telemetry/time-tracking system.** Process mistakes are visible from reports/runs without creating worker performance monitoring.
- The initial integration false-positive in `backlog-disposition-validator-01` (its parser matched its own Python docstring example before the scope was restricted to durable Markdown evidence) is a useful one-off validator lesson, but not enough by itself to justify another standalone control.

### Recommended minimal mechanism

Create one compact canonical operational lessons file: **`KNOWN_WORKER_PITFALLS.md`**, and hook it into the existing protocol rather than creating a new management system.

Exact proposed changes:

1. **New `KNOWN_WORKER_PITFALLS.md`**
   - Purpose: only reusable cross-cutting worker failure recipes that do not belong in `PROJECT_ROUTES.md` (where/how) or `PROJECT_DECISIONS.md` (why product/architecture chose something).
   - Compact entry shape:
     - `Trigger / symptom`
     - `Do not repeat`
     - `Correct move`
     - `Evidence refs`
   - Seed only the three high-value patterns proven above:
     1. behavioral contract vs source-shape/static-proxy validation;
     2. Pages concurrency + already-uploaded artifact rerun trap;
     3. architecture preflight before recommending IMPLEMENT for new source/runtime/workflow ownership.
   - Do not use it as a generic troubleshooting diary; one-off bugs stay in their reports.

2. **`CHAT_PROTOCOL.md` — two small hooks, no new gate system**
   - `START`: after checking `PROJECT_ROUTES.md`, check relevant `KNOWN_WORKER_PITFALLS.md` entries when the task matches a known trigger; do not perform a broad historical search first.
   - `PRE-SEND`: if the task encountered a reusable avoidable detour or a user/CI correction exposed one, persist it in the correct durable home (`PROJECT_ROUTES.md`, `PROJECT_DECISIONS.md`, or `KNOWN_WORKER_PITFALLS.md`). If current read-only boundaries prohibit that edit, name the exact candidate in the report for a bounded follow-up.
   - Extend the existing architecture preflight wording so it also applies to a worker's **Recommended next step**, not only to immediate implementation.

Why this is the smallest durable mechanism:

- it preserves the existing protocol instead of replacing it;
- it gives recurring operational failures a canonical home without polluting routes/decisions;
- it directly prevents the three repeated high-value detours in this sample;
- it requires no scheduler, telemetry, quotas, dashboard, or director performance monitoring;
- it can stay tiny because entries are added only when evidence shows reuse value.

### Optional secondary improvements

Ranked by expected value vs overhead:

1. **High value / very low overhead:** add one conditional worker-report line in `DIRECTOR_PROTOCOL.md`: `Efficiency / reusable lesson: none | <short candidate/ref>`. It should remain `none` for normal tasks and should not become a narrative section. This makes read-only workers able to surface a durable lesson without forcing them to violate scope.
2. **Medium value / low overhead:** task templates for IMPLEMENT/ACCEPTANCE should explicitly name any critical user-visible/semantic DoD checks and require an `evidence -> executed check` mapping before closeout. This targets the validation-proxy/missing-regression pattern without adding more tests than the task already requires.
3. **Medium value / low overhead:** for tasks that depend on a pre-existing external runtime/operator object (for example an existing scheduled ChatGPT task), the task file should include its exact addressable identity/control route when available. If it is not addressable, scope the task as occurrence-blocked verification instead of implying an immediate run is possible. `ru-translation-runtime-acceptance-01` correctly refused to invent a second scheduler; the inefficiency risk is in task preparation, not in that refusal.
4. **Low value now:** automatic report-path validation. The bounded sample does not show enough report-path failures to justify a new guard.
5. **Do not add:** worker time telemetry, arbitrary duration targets, per-worker quotas, or a director performance dashboard.

### What not to optimize away

- Real-device/user checks when the acceptance criterion is subjective or browser/device-specific. The detailed-score and image-swipe tasks correctly kept this separate from automated regressions.
- External provider/legal validation in source recon (`duration-provider-recon-01`, `cross-platform-giveaway-recon-01`). Those tasks were long because the decision genuinely required current external evidence; skipping that work would trade time for incorrect architecture.
- Fail-closed architecture stops. `ru-translation-runtime-acceptance-01` was correct to remain blocked rather than create a second scheduler, guess an automation ID, manually translate a production request, or fabricate an inbox result.
- Credential/provisioning blockers. `duration-igdb-implement-01` correctly stopped at missing `IGDB_CLIENT_ID` / `IGDB_CLIENT_SECRET` after repo-side implementation and tests were complete.
- The second fixed-package acceptance itself after `package-acceptance-01` found a genuinely missing required regression. The avoidable error was failing to map the DoD scenario earlier; once found, re-validation was necessary.
- First-time route discovery where no route exists yet. The optimization target is failure to persist the discovery, not the discovery work itself.

### Status

complete

### Recommended next step

One bounded operational-doc IMPLEMENT only: create `KNOWN_WORKER_PITFALLS.md` with the three seeded entries above and add the two minimal `CHAT_PROTOCOL.md` hooks, including architecture preflight for `Recommended next step`. Do not change product code, workflows, ranking, translation, giveaways, duration, UI, or production data.