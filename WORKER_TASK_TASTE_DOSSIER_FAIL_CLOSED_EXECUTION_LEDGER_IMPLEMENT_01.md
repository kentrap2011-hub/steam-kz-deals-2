# WORKER TASK — TASTE DOSSIER FAIL-CLOSED EXECUTION LEDGER IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-fail-closed-execution-ledger-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- релевантный `PITFALL-004` в `KNOWN_WORKER_PITFALLS.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- accepted live diagnostic:
  `reviews/worker_reports/taste-dossier-hellish-quart-russian-retrieval-diagnostic-01.md`;
- accepted retrieval improvement baseline:
  `reviews/worker_reports/taste-dossier-steam-russian-review-retrieval-improvement-01.md`.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Accepted problem

A real production invocation stopped fail-closed on Hellish Quart after establishing Russian-review existence but without publishing `g000001`.

The later bounded diagnostic, using the same active prompt class, successfully found a legal exact-product cross-source Russian feedback shape.

The durable state did **not** prove which retrieval routes the failed production invocation actually executed. Therefore the exact production divergence could not be diagnosed from the final message/state.

The problem to fix is **observability of fail-closed execution**, not the evidence standard.

## Goal

When the Scheduled `Taste Steam Review Dossier` worker stops fail-closed before completing/publishing the current group, its final response must contain a compact structured **execution ledger** sufficient to reconstruct:

- what exact contract/evidence gate blocked progress;
- what required retrieval/action classes were actually attempted;
- the observable result of each material attempt;
- budget consumption;
- the last completed stage;
- the next mandatory step, if any;
- why that next step could not be executed;
- exact visible tool/system error when exposed.

The ledger must contain **observable execution facts only**.

It must NOT contain private chain-of-thought, hidden reasoning, free-form internal deliberation, raw review bodies, author identity, secrets, or unsupported causal guesses.

## Architecture boundary

Preserve current ownership:

- Scheduled ChatGPT owns bounded external/semantic retrieval and can report its own observable actions/results.
- GitHub remains owner of scope, ordering, canonical validation, persistence, progress, retry/recovery interpretation and completeness.
- The interactive chat remains operator/director, not runtime owner.

Do NOT add:
- a new queue;
- a new scheduler;
- a new recurring stage;
- a retry daemon;
- a separate logging service;
- a new GitHub persistence path for runtime ledgers;
- manual canonical progress logic.

For this task, the ledger is part of the Scheduled Task **final user-visible response** on fail-closed termination.

If later durable storage proves necessary, that is a separate architecture decision.

## Primary implementation surface

Expected primary lever:
- `config/taste_steam_review_dossier_worker_prompt.md`.

Expected binding metadata:
- advance `worker_prompt_revision` in the canonical evidence contract as required by the existing content-complete binding.

Use schema/evidence-contract machine metadata only where needed to make the fail-closed response contract explicit and testable. Do not add ledger fields to the persisted dossier schema unless current architecture genuinely requires them; they are not dossier evidence.

## Mandatory fail-closed ledger

On every fail-closed stop before the current group is successfully create-only published, output a section with exact marker:

`FAIL_CLOSED_EXECUTION_LEDGER_V1`

The ledger must identify the current work binding without exposing unnecessary payload:

- `snapshot_id`;
- `sequence`;
- `group_sha256`;
- blocked game `title` and `appid` when the stop is game-specific;
- `last_completed_stage`;
- `stop_gate`;
- `publication_state`:
  - `not_attempted`;
  - `create_attempt_failed`;
  - or another existing observable state if necessary;
- `canonical_progress_claim`: always make clear that fail-closed output does not itself mean canonical completion.

### Material attempt entries

Record one row/object per **material** retrieval/action attempt, not every trivial UI/tool interaction.

Each entry must contain:

- sequential `step`;
- `stage`;
- `action_kind` such as `search`, `open/read`, `github_read`, `github_create`;
- safe `route_class`;
- safe `target_summary`:
  - exact product/appid and domain/surface class when useful;
  - never persist profile URL or author/user identity;
- `started`: true/false;
- `response_received`: true/false;
- `observable_result`.

Use compact observable results such as, when applicable:
- `exact_product_confirmed`;
- `aggregate_only`;
- `concrete_russian_card_visible`;
- `concrete_non_russian_cards_only`;
- `stable_locator_available`;
- `transient_fallback_available`;
- `profile_scoped_discovery_only`;
- `exact_product_mismatch`;
- `no_results`;
- `inaccessible_or_dynamic`;
- `tool_error`;
- `binding_changed`;
- `candidate_create_failed`;
- other equally concrete current-contract result if needed.

Do not invent a result enum if the observable result does not fit; use short factual text rather than guessing.

### Budget/state summary

For evidence/retrieval stops include:
- `search_queries_used` and `search_query_limit`;
- `opened_pages_used` and `opened_page_limit`;
- whether required source-diversification / Russian / temporal / identity routes were exhausted or still pending.

For non-web fail-closed stops include only applicable counters.

### Mandatory next-step accounting

The ledger must include:

- `next_required_step`;
- `next_required_step_status`:
  - `none_all_required_routes_exhausted`;
  - `not_executed`;
  - `blocked`;
- `why_not_executed`.

Allowed factual reasons include:
- search budget exhausted;
- page/open budget exhausted;
- exact visible tool error;
- current snapshot/plan/binding changed;
- current runtime ended before step could execute;
- required route unavailable/inaccessible in current tool result;
- create-only write failed;
- other directly observed blocker.

If no factual reason is known, write:
`why_not_executed: unknown — no system/tool cause exposed`.

Do NOT substitute:
- “probably timeout”;
- “likely context limit”;
- “Steam blocked it”;
- or any other unobserved cause.

## Required-route completion guard

For a fail-closed **evidence/retrieval** stop:

If the active prompt requires another material recovery route and:
- budget remains;
- no snapshot/binding liveness change occurred;
- no exposed tool/runtime blocker prevents it;

then the worker must not declare that evidence route exhausted.

It must either:
1. execute the required next route; or
2. explicitly stop for a separately observed runtime/tool blocker and ledger that blocker.

This does not add a new retrieval strategy. It only makes the current required strategy execution auditable.

In particular, for the current Russian gate:
- aggregate existence is not terminal;
- if the active prompt requires cross-source pivot and budget remains, the ledger must show whether that pivot was executed;
- a fail-closed final response may not merely say “concrete Russian review unavailable” without accounting for the required recovery route.

## Privacy / safety

The ledger must never contain:
- raw review/post bodies;
- quotes/excerpts from player content;
- usernames/display names;
- SteamID/account identifiers;
- author-derived hashes/pseudonyms;
- profile URLs;
- secrets/tokens;
- hidden chain-of-thought or internal reasoning text.

A route may be identified as:
`Steam Store exact-app`,
`Steam Community exact-app`,
`cross-source exact-product player feedback`,
`steamstat.io exact-app`,
etc., only when actually attempted.

Profile-scoped results must be summarized as `profile_scoped_discovery_only` without reproducing the profile locator.

## Success-path behavior

Do not burden normal successful runs with a verbose ledger.

On success:
- preserve current concise publication/progress reporting;
- no full execution ledger is required.

A minimal invocation summary may remain if already present.

The detailed ledger is mandatory only when the invocation stops fail-closed before completing the current local target.

## Hellish Quart control scenario

Use the accepted Hellish Quart incident as a control case, without hardcoding it into runtime behavior.

A compliant hypothetical fail-closed ledger for that scenario must make it possible to distinguish at least:

A. production attempted only Steam aggregate/non-Russian routes and did not execute required cross-source pivot;
B. production executed cross-source pivot but it returned no legal item;
C. production was prevented from executing the pivot by an exposed runtime/tool blocker.

The ledger must not collapse A/B/C into the same sentence.

## Required regressions

### LEDGER-01 — marker and binding
Fail-closed response contract requires `FAIL_CLOSED_EXECUTION_LEDGER_V1` and current work binding fields.

### LEDGER-02 — observable attempts
Material attempt entries include stage/action/route/start/response/result without reasoning text.

### LEDGER-03 — exact stop gate
Fail-closed response names the exact contract/evidence gate that prevented publication.

### LEDGER-04 — budget
Evidence retrieval stop records used/limit counters.

### LEDGER-05 — required next step
Ledger records the next mandatory route/action and whether it was executed or why it could not be.

### LEDGER-06 — no silent early stop
If a mandatory recovery route remains and budget/liveness/tool availability allow it, prompt forbids declaring retrieval exhausted before executing it.

### LEDGER-07 — unknown cause remains unknown
Prompt explicitly forbids inferred timeout/context/platform blame and uses `unknown — no system/tool cause exposed` when necessary.

### LEDGER-08 — privacy
Ledger forbids raw feedback, author/profile identity, profile URLs and secrets.

### LEDGER-09 — no chain-of-thought requirement
Ledger explicitly requests only observable execution facts and contract-gate state, not hidden reasoning/deliberation.

### LEDGER-10 — success remains compact
Successful publication path does not require verbose execution ledger.

### LEDGER-11 — current retrieval semantics unchanged
Russian gate, multi-source, temporal, identity, privacy, source-role, Store-card and transient-fallback semantics remain unchanged.

### LEDGER-12 — current ownership unchanged
No queue/retry/progress/log-service responsibility moves out of GitHub control plane.

### LEDGER-13 — prior dossier suites green
Run relevant existing focused dossier suites, including:
- validator-generator parity;
- identity provenance;
- Russian retrieval;
- temporal pre-stop;
- semantic consistency;
- language binding;
- transient-author fallback;
- Steam Store parent;
- contract contradictions;
- buffered validation;
- execution ownership.

### LEDGER-14 — binding activation
Normal GitHub-owned activation produces a compatible fresh binding/snapshot when the prompt revision changes.

### LEDGER-15 — no production run
Do not run Scheduled Task during implementation/validation.

## Validation proof

A prompt edit alone is not enough.

Perform a bounded non-production proof using the Hellish Quart incident/control shape or a synthetic equivalent that demonstrates the final fail-closed ledger can distinguish:

- required cross-source route not executed;
- route executed but no legal item returned;
- route blocked by exposed tool/runtime error.

Do not publish a production candidate during this proof.

The proof is about ledger structure and stop accounting, not about re-solving Hellish Quart evidence.

## Activation

If implementation succeeds:

1. bounded branch/PR;
2. focused regressions;
3. existing relevant dossier suites;
4. merge only green;
5. normal GitHub-owned activation/rebuild for the prompt-binding change;
6. confirm active snapshot/binding;
7. do not run production Scheduled Task.

Do not manually repair or advance canonical progress.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-fail-closed-execution-ledger-implement-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight.
3. Accepted Hellish Quart observability problem.
4. Exact implementation.
5. Ledger field contract.
6. Required-route completion guard.
7. Privacy / no-chain-of-thought boundary.
8. Hellish/synthetic proof for A/B/C distinction.
9. LEDGER-01..15 results.
10. Existing guard suites.
11. PR / CI / merge refs.
12. Activation refs.
13. Active snapshot/binding state.
14. Confirmation no new durable logging/queue/retry service.
15. Scheduled Task confirmation.
16. Unresolved.
17. Status.
18. Exactly one recommended next step.
19. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `needs_user_decision`
- `blocked_external`

## Status rule

`complete_ready_for_live_acceptance` is allowed ONLY if:
- fail-closed response ledger is mandatory and structured;
- required-route accounting prevents silent early evidence exhaustion;
- privacy and no-chain-of-thought boundaries are explicit;
- current evidence/validator semantics are unchanged;
- LEDGER-01..15 pass;
- normal activation completes;
- no new logging service/queue/retry architecture is introduced;
- Scheduled Task was not run.

## Exactly one next step

If complete:
- return to Director for one production `Run now` acceptance where any new fail-closed stop must provide the structured ledger.

If `needs_fix`:
- identify one exact implementation defect.

If `needs_user_decision`:
- identify one bounded architecture/contract choice.

If `blocked_external`:
- identify the exact platform limitation.

Do not run production inside this task.
