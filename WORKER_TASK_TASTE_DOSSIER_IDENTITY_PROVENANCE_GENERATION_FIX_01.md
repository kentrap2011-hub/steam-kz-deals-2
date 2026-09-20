# WORKER TASK — TASTE DOSSIER IDENTITY PROVENANCE GENERATION FIX 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-identity-provenance-generation-fix-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- релевантный trigger в `KNOWN_WORKER_PITFALLS.md`, если он действительно применим;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_persistence_bridge.json`;
- `config/taste_steam_review_dossier_recovery_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `scripts/taste_steam_review_dossier_strict.py`;
- focused buffered/prepublication regression paths needed for this issue;
- current `data/production/pre_ai/taste_steam_review_dossier_validation_status.json`;
- current worker index only as needed to confirm active snapshot/blocker.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Accepted production diagnosis

Treat the following as accepted unless current `main` has already superseded it:

- affected snapshot:
  `533abb9b4328efec3b80a61caddb142ffe0ff7fb9438482d5159b2ed9878378d`;
- current canonical expected sequence remained `1`;
- completed count remained `0`;
- deterministic current-snapshot candidates existed for:
  - `g000001`, group SHA `1bf7b03cbd90fd29ff9da33b04e058671b959b540b8fd303074d6188ed0d3fe0`;
  - `g000002`, group SHA `59f3a5687078c168ac1f963915ad04818d1c37f72aabf396337ef205194bc161`;
- GitHub canonical validation marked both invalid with the same error:
  `game identity requires an identity-role provenance source`;
- the first invalid expected group is `g000001`;
- the strict validator is behaving correctly;
- the observed worker output referenced player-feedback sources in `game_identity.identity_source_ids` while those sources had a non-identity role such as `durable_trait`;
- accepted canonical dossiers demonstrate the intended shape: at least one provenance source used by `game_identity.identity_source_ids` has `evidence_role:"identity"`, normally exact-product official metadata, while player-feedback evidence is represented separately.

Do not reinterpret this as a scheduler, snapshot rollover, buffered transport, or canonical-progress defect.

## Architecture boundary

Preserve the existing ownership model:

- Scheduled ChatGPT remains the semantic/data-plane dossier generator;
- GitHub remains the control plane and authoritative validator/persister/progress/recovery owner;
- no control-plane logic moves into the interactive chat or Scheduled worker;
- no new scheduler, queue, retry loop, checkpoint mechanism, or recurring stage is allowed.

This is a generation-contract alignment fix inside the existing dossier architecture.

## Goal

Make it structurally difficult for the Scheduled dossier worker to emit a dossier where:

- `game_identity.identity_source_ids` resolves only to sources whose `evidence_role` is not `identity`.

The active worker-facing prompt/machine contract must explicitly express the invariant that the strict validator already enforces:

> Every resolved game identity must reference at least one provenance source with `evidence_role:"identity"`.

The fix must preserve exact product identity, title + release year resolution, exact appid corroboration, player-feedback provenance, privacy rules, language binding, temporal rules, recurrence rules, Russian retrieval semantics, buffered transport, and GitHub-owned validation.

## Required generation behavior

For every dossier:

1. Resolve the exact intended product identity using reliable public metadata.
2. Persist at least one source suitable for product identity provenance.
3. That source must:
   - be listed in `game_identity.identity_source_ids`;
   - have `evidence_role:"identity"`;
   - resolve to the exact intended product;
   - support the resolved title/release-year/appid identity under current rules.
4. Preserve the exact descriptor appid corroborator in `game_identity.corroborators`.
5. Player-feedback sources used for observations/conflicts remain evidence sources with the appropriate non-identity evidence role.
6. Do not make an ordinary player-feedback source masquerade as identity provenance merely to satisfy validation.
7. Do not count an identity-only metadata source as a player-feedback mention, Russian feedback item, recurrence record, or source-diversity proof.
8. Preserve dossier-local sequential internal IDs and all current privacy restrictions.

The worker may reuse a physical product page only when the resulting source representation is valid under the existing source/alias/physical-source rules. Do not create fake source diversity or duplicate-source aliases merely to obtain two roles.

## Canonical alignment to fix

The strict validator already contains the effective invariant:

`game_identity.identity_source_ids` must contain at least one source with `evidence_role == "identity"`.

Align the worker-facing canonical layers with that behavior.

Expected primary levers:
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_schema.json` identity invariants / machine-readable rule;
- focused tests/fixtures proving worker-facing contract and strict validator agree;
- content-complete binding/revision metadata where required by existing runtime.

Do NOT weaken or remove the strict validator check.

If `config/taste_steam_review_dossier_web_evidence_contract.json` also needs a small consistency clarification, change it only if required to make the active canonical worker contract unambiguous. Do not broaden evidence semantics.

## Required regressions

### ID-PROV-01 — exact old failure remains rejected
A dossier where `identity_source_ids` resolves only to `durable_trait` / other non-identity sources must fail with the existing strict behavior.

### ID-PROV-02 — worker contract explicitly requires identity-role source
The active prompt/machine contract must state the same invariant the strict validator enforces.

### ID-PROV-03 — valid identity source passes
A valid exact-product dossier with:
- a reliable identity provenance source marked `evidence_role:"identity"`;
- exact appid corroborator;
- separate legal player-feedback evidence;
must pass focused strict/prepublication/buffered validation.

### ID-PROV-04 — identity source cannot create fake feedback support
Identity-only source must not contribute to:
- `mention_count`;
- `player_feedback_records`;
- Russian `found_and_used`;
- recurrence strength;
- player-feedback source diversity.

### ID-PROV-05 — exact product identity preserved
Title, release year, descriptor appid and identity source must resolve to the same intended product under current exact-product rules.

### ID-PROV-06 — internal ID and privacy rules preserved
No author identity, profile identity, direct hashes, or author-derived IDs may appear; sequential dossier-local IDs remain intact.

### ID-PROV-07 — existing evidence semantics unchanged
Language, temporal status, recurrence, Russian existence/retrieval, Steam parent/child, transient-author fallback and source alias rules remain unchanged.

### ID-PROV-08 — prior focused suites remain green
Run the relevant existing dossier suites, including at minimum:
- contract gaps / contradictions;
- language binding;
- semantic consistency;
- transient-author fallback;
- Steam Store review-card parent;
- package identity;
- story-DLC scope;
- parallel buffered validation;
- execution ownership validation.

### ID-PROV-09 — binding compatibility works normally
If prompt/schema/evidence-contract content binding changes, normal GitHub activation must produce a fresh compatible snapshot/projection. Old incompatible buffered candidates must become stale/inert under existing rules; they must not be rebound.

### ID-PROV-10 — no production Scheduled Task run
Do not press/run Scheduled Task `Run now` and do not change its settings.

## Old invalid artifacts

Do NOT manually:
- edit;
- overwrite;
- delete;
- rename;
- rebind;
- replace with alternate filenames;
- advance canonical progress past;
- or reinterpret as valid

the current invalid `g000001` / `g000002` artifacts.

Do not manually repair canonical cache/progress.

Because the expected fix changes content-complete worker binding, prefer the existing normal activation path that creates a fresh compatible snapshot/projection. The old invalid artifacts should then be handled as stale/inert by existing GitHub-owned compatibility/recovery behavior.

Only use explicit current-snapshot invalid-artifact recovery if, after implementation, the canonical contracts prove it is still required. Do not invent a new recovery mechanism.

## Implementation discipline

Use a bounded branch/PR.

Do not hardcode:
- snapshot id `533abb9b...`;
- g000001/g000002;
- Skul;
- Atelier titles;
- a specific Steam URL;
- any one source domain

into generic runtime logic.

The production diagnosis may appear in tests/report as a regression case, but runtime generation rules must be generic.

## Activation

If implementation and regressions are green:

1. merge through the normal repository path;
2. run/use the existing GitHub-owned activation/rebuild path;
3. confirm the current worker/evidence binding reflects the fix;
4. confirm a fresh compatible snapshot/projection exists if binding changed;
5. confirm the old invalid current-snapshot candidates are no longer active canonical blockers;
6. do not run production Scheduled Task.

No manual progress surgery.

## Validation state to report

After activation report at minimum:

- active snapshot id;
- prepared date;
- worker prompt revision/hash;
- schema/evidence binding revisions/hashes if changed;
- prepared/completed/remaining;
- canonical expected sequence;
- group count / group size;
- exact expected group descriptor;
- whether old snapshot `533abb9b...` is stale/inert;
- whether its old `g000001/g000002` artifacts remain untouched;
- whether any explicit recovery request was necessary, and why;
- confirmation Scheduled Task was not run.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-identity-provenance-generation-fix-01.md`

Keep it compact. Required sections:

1. Task / repo / mode.
2. Architecture preflight.
3. Accepted production diagnosis.
4. Exact worker-generation gap.
5. Canonical prompt/schema/contract alignment change.
6. Validator boundary — confirmation it was not weakened.
7. Before/after identity provenance shape in plain language.
8. ID-PROV-01..10 results.
9. Existing guard suites.
10. PR / CI / merge refs.
11. Activation refs.
12. Active snapshot/binding state.
13. Old invalid artifact compatibility/recovery result.
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

- the worker-facing generation contract now explicitly requires an identity-role provenance source;
- strict validator behavior remains intact;
- focused positive and negative regressions pass;
- relevant prior dossier suites remain green;
- normal activation completes;
- active binding/snapshot is compatible with the fix;
- old invalid artifacts were not manually rewritten/rebound;
- Scheduled Task was not run.

## Exactly one next step

If complete:
- return to Director for one clean production `Run now` acceptance on the newly activated compatible snapshot.

If `needs_fix`:
- identify one exact remaining implementation defect.

If `needs_user_decision`:
- identify one bounded contract/architecture choice only.

If `blocked_external`:
- identify the exact external limitation.

Do not start the next production run inside this task.
