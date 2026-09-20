# WORKER TASK — TASTE DOSSIER VALIDATOR ↔ GENERATOR PARITY FIX 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-validator-generator-parity-fix-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `scripts/taste_steam_review_dossier_strict.py`;
- only focused prepublication/buffered helpers and tests needed for these three findings;
- accepted audit report:
  `reviews/worker_reports/taste-dossier-validator-generator-parity-audit-01.md`;
- accepted identity-provenance fix report only as a regression/control reference:
  `reviews/worker_reports/taste-dossier-identity-provenance-generation-fix-01.md`.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Accepted audit findings

Treat exactly these three findings as accepted:

### PARITY-01 — source locator serialization
Strict validator already requires:
- every provenance source contains exactly one of `url` or `public_ref`;
- when `url` is used it is public HTTPS;
- `source.domain` equals the normalized URL hostname exactly.

Generator-facing layers do not currently encode the full invariant strongly enough.

### PARITY-02 — multi-source reason nullability
Strict validator already requires:
- if `evidence.source_mix_status == "multi_source"`, then:
  - at least two distinct physical used player-feedback sources exist; and
  - `evidence.single_source_reason is null`.

Generator-facing layers explain the positive single-source case but do not explicitly require the converse `null` in the multi-source case.

### PARITY-03 — Steam Store fallback-parent source type
Strict validator already permits an exact Steam Store `/app/{appid}/` source used as:
- `feedback_surface_mode:"concrete_item_collection"`;
- `player_feedback:true`;

only when `source_type` is one of:
- `steam_reviews`;
- `store_user_reviews`.

Current generator-facing wording says those types are only “normally” used and machine contracts do not make the set exclusive.

No other parity finding is authorized by this task.

## Goal

Align generator-facing prompt/schema/evidence-contract layers to the already-existing strict validator semantics for PARITY-01..03, add focused regressions, activate the content-complete worker binding normally, and leave validator semantics/ownership/control-plane behavior unchanged.

This task is contract alignment, not semantic redesign.

## Hard boundaries

Do NOT:
- weaken, relax or reinterpret strict validator semantics;
- add a new validator rule unrelated to PARITY-01..03;
- add retrieval strategy, new sources or site quotas;
- change scheduler/task settings;
- add queue/retry/checkpoint logic;
- move persistence/recovery/progress ownership away from GitHub;
- edit production candidates or canonical progress manually;
- run Scheduled Task `Taste Steam Review Dossier`;
- reopen the identity-provenance finding;
- expand into unrelated cleanup/refactors.

## Required implementation — PARITY-01

Make the active generator-facing machine contract explicit that every provenance source has exactly one locator:

- either `url`;
- or `public_ref`;
- never both;
- never neither.

When `url` is used:
- require public HTTPS;
- require `domain` to equal the normalized hostname of that URL exactly.

Examples that must be generator-side invalid after the fix:
- both `url` and `public_ref`;
- `http://...`;
- `domain:"steampowered.com"` with URL host `store.steampowered.com`.

Do not invent a new normalization algorithm inconsistent with strict validation. Mirror the existing accepted normalization semantics.

Primary expected surface:
- `config/taste_steam_review_dossier_schema.json`;
- prompt clarification only if needed for human-readable generation clarity;
- focused fixtures/tests.

## Required implementation — PARITY-02

Make the generator-facing contract explicit:

- `source_mix_status:"single_source_only"` requires the existing compact reason behavior;
- `source_mix_status:"multi_source"` requires:
  `single_source_reason:null`.

Do not change how physical used-source diversity is counted.

Primary expected surface:
- `config/taste_steam_review_dossier_schema.json`;
- prompt/evidence-contract clarification only if needed to eliminate ambiguity;
- focused fixture/test.

## Required implementation — PARITY-03

Make the Steam Store fallback-parent exception explicit and exclusive.

For exact Steam Store `/app/{appid}/` parent used as:
- `feedback_surface_mode:"concrete_item_collection"`;
- `player_feedback:true`;

the allowed `source_type` set is exactly:
- `steam_reviews`;
- `store_user_reviews`.

Remove ambiguous “normally” wording from the active worker-facing instruction where it suggests other source types may be legal.

Do not broaden the Store-parent exception to other source types.

Primary expected surface:
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- schema only if needed for machine-level consistency;
- focused regression.

## Required regressions

### PARITY-FIX-01 — locator cardinality
A source with both `url` and `public_ref` is rejected generator-side / parity fixture; a source with exactly one legal locator remains valid.

### PARITY-FIX-02 — HTTPS requirement
An HTTP source URL is invalid; HTTPS remains valid.

### PARITY-FIX-03 — exact normalized host equality
Mismatch between `domain` and URL hostname is invalid; exact normalized host match is valid.

### PARITY-FIX-04 — multi-source reason null
`multi_source + non-null single_source_reason` is invalid; `multi_source + null` with >=2 legal physical used player-feedback sources remains valid.

### PARITY-FIX-05 — single-source semantics preserved
Existing valid `single_source_only` reason behavior remains unchanged.

### PARITY-FIX-06 — Steam Store allowed types
Exact-app Store fallback parent with `steam_reviews` and `store_user_reviews` remains valid.

### PARITY-FIX-07 — Steam Store disallowed type
Same Store-parent shape with `other_player_feedback` is generator-side invalid and remains strict-validator invalid.

### PARITY-FIX-08 — validator unchanged
Focused test must prove the existing strict validator behavior did not change.

### PARITY-FIX-09 — identity provenance remains aligned
Recent identity-provenance generation fix remains green.

### PARITY-FIX-10 — prior focused dossier suites remain green
Run relevant existing guards including at minimum:
- contract gaps / contradictions;
- language binding;
- semantic consistency;
- transient-author fallback;
- Steam Store review-card parent;
- identity provenance generation;
- package identity;
- story-DLC scope;
- parallel buffered validation;
- execution ownership validation.

### PARITY-FIX-11 — binding activation
If prompt/schema/evidence-contract content-complete binding changes, normal GitHub-owned activation must create/publish a compatible fresh worker projection/snapshot as required by current contracts. Old incompatible candidates must not be rebound.

### PARITY-FIX-12 — no production run
Scheduled Task is not run and its settings remain unchanged.

## Validator boundary

The strict validator is the existing semantic acceptance authority and should remain unchanged.

If implementation appears to require changing strict semantics to make generator-facing contracts easier, stop and report `needs_user_decision` instead of altering validator behavior.

If a true contradiction not present in the accepted audit is discovered, do not expand scope automatically.

## Activation

If implementation and regressions pass:

1. bounded branch/PR;
2. focused CI and existing relevant dossier suites;
3. merge only green;
4. normal GitHub-owned activation/rebuild;
5. confirm current worker binding/snapshot is compatible with the aligned contracts;
6. confirm any previous snapshot becomes stale/inert through existing compatibility rules if binding changed;
7. do not manually edit/quarantine/rebind production artifacts unless the existing canonical activation path does so automatically;
8. do not run production Scheduled Task.

## Active-state report requirements

After activation report:
- active snapshot id;
- prepared date;
- canonical expected sequence;
- completed/remaining;
- group count / normal group size;
- exact current expected group descriptor;
- prompt revision/hash;
- schema revision/hash;
- evidence contract revision/hash;
- whether activation created a fresh snapshot;
- compatibility effect on the pre-fix snapshot;
- confirmation no manual progress/recovery surgery;
- confirmation Scheduled Task was not run.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-validator-generator-parity-fix-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight.
3. Accepted PARITY-01..03 findings.
4. Exact changes for PARITY-01.
5. Exact changes for PARITY-02.
6. Exact changes for PARITY-03.
7. Validator boundary confirmation.
8. PARITY-FIX-01..12 results.
9. Existing guard suites.
10. PR / CI / merge refs.
11. Activation refs.
12. Active snapshot/binding state.
13. Compatibility effect on prior snapshot/candidates.
14. Scheduled Task confirmation.
15. Unresolved.
16. Status.
17. Exactly one recommended next step.
18. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `needs_user_decision`
- `blocked_external`

## Status rule

`complete_ready_for_live_acceptance` is allowed ONLY if:
- PARITY-01..03 are explicitly aligned generator-side;
- strict validator semantics are unchanged;
- PARITY-FIX-01..12 pass;
- relevant prior dossier guard suites remain green;
- normal activation completes;
- active binding/snapshot is compatible with the fix;
- no manual production progress/recovery surgery occurred;
- Scheduled Task was not run.

## Exactly one next step

If complete:
- return to Director for one clean production `Run now` acceptance.

If `needs_fix`:
- identify one exact remaining implementation defect.

If `needs_user_decision`:
- identify one bounded contract/architecture choice.

If `blocked_external`:
- identify the exact external blocker.

Do not start production inside this task.
