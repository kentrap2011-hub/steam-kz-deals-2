# WORKER TASK — TASTE DOSSIER CONTRACT CONTRADICTIONS FIX 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-contract-contradictions-fix-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `scripts/taste_steam_review_dossier_strict.py`;
- `scripts/taste_steam_review_dossier_compact_provenance.py`;
- relevant buffered/prepublication compatibility paths only as needed;
- `PROJECT_DECISIONS.md`, especially recent dossier evidence/privacy/language decisions;
- `reviews/worker_reports/taste-dossier-contract-contradiction-audit-01.md`;
- `reviews/worker_reports/taste-dossier-steam-store-review-card-parent-fix-01.md`;
- `reviews/worker_reports/taste-dossier-transient-author-dedupe-fallback-implement-01.md`;
- prior language-binding and semantic-consistency reports only where directly relevant.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Current accepted baseline

The following is already accepted and must remain intact:
- Steam Store exact-app page may be a parent collection surface for concrete review-card fallback;
- Store page itself and aggregate counts/ratings/language totals are not mentions;
- transient-author fallback privacy model;
- stable locator remains preferred;
- fallback recurrence cap remains limited;
- exact-product identity remains fail-closed;
- Story-DLC policy remains story-only;
- current compatible first group remains:
  1. Crown Trick — 1000010
  2. Hellish Quart — 1000360
  3. Tetris® Effect: Connected — 1003590
unless normal canonical source recomputation independently changes scope during activation.

Do not regress the accepted Steam Store review-card parent fix.

## Source diagnostic

The read-only audit:
`reviews/worker_reports/taste-dossier-contract-contradiction-audit-01.md`

confirmed exactly three additional material contradictions:

- CONTRA-01 — stable Steam child evidence not fully bound to exact product/physical parent;
- CONTRA-02 — author identity can leak through stable `source_id` / `feedback_id`;
- CONTRA-03 — strict validator does not enforce exact bound-record language projection.

Fix these three and only these three unless implementation exposes a directly coupled regression necessary to preserve consistency.

---

# CONTRA-01 — exact Steam child/product/parent binding

## Intended rule

If a stable Steam feedback child exposes a Steam appid or a deterministically resolvable Steam container/thread identity, it must belong to:
- the exact dossier appid;
- the physical parent source/container represented by its parent source record.

Host match alone is insufficient.

## Required behavior

For normal `stable_locator` Steam child records:
- parse child appid when deterministically exposed by URL/ref;
- require child appid == exact dossier appid;
- where both parent and child expose a deterministically resolvable Steam container/thread/discussion identity, require physical containment/identity consistency;
- do not allow a child from another Steam app just because parent host/source type is Steam;
- preserve existing accepted Reddit containment semantics and alias normalization;
- do not invent fuzzy title-based matching.

If a Steam URL form does not expose a reliable product/container identity, keep existing safe behavior; do not invent one.

## Do not over-tighten fallback

`transient_author_deduped` records have no child item URL/ref by design.
Their exact-product binding remains parent-surface based under the accepted fallback contract.

Do not force stable-child URL requirements onto fallback records.

---

# CONTRA-02 — stable internal IDs must be author-independent

## Problem

Privacy contract forbids persisted usernames/SteamIDs/profile identity, but ordinary stable `source_id` and `feedback_id` currently accept arbitrary strings.

That allows author identity to leak through an internal join key.

## Intended rule

All persisted internal join IDs must be dossier-local / author-independent.

The stable physical identity belongs in already-validated safe item URL / `public_ref`, not in `source_id` / `feedback_id`.

## Required behavior

Choose the smallest deterministic local-ID model compatible with current artifacts.

Preferred shape:
- source IDs follow a neutral dossier-local pattern such as `source-NNN`;
- feedback IDs follow a neutral dossier-local pattern such as `feedback-NNN` for stable records and existing `fallback-NNN` for fallback records;
- IDs must not encode username, SteamID, profile id, vanity id, author name, profile URL, or direct hash/predictable pseudonym derived from them.

Do not create:
- cross-run reviewer registry;
- persistent identity map;
- secret/salted author hashing system;
- author-derived deterministic IDs.

If changing stable internal ID format affects aliases/bindings/fixtures, migrate schema/prompt/validator/tests coherently within this task.

## Compatibility

Do not break canonical reopenability/auditability:
- stable physical item identity still comes from safe URL/public_ref;
- source/feedback internal IDs remain local join keys only.

---

# CONTRA-03 — exact language projection enforcement

## Intended rule

Observation `evidence_languages` is a deterministic derived field from final bound `player_feedback_ids`.

It must equal the exact ordered distinct projection of the bound records' languages.

Canonical output order:
1. `russian`
2. `non_russian`
3. `unknown`

Input record language `mixed` expands to:
- `russian`
- `non_russian`

`mixed` must NOT appear as an observation-summary output token.

## Required behavior

In canonical strict validation:
- derive expected language projection from final bound records;
- require exact list equality with serialized observation `evidence_languages`;
- reject missing required token;
- reject extra unsupported token;
- reject wrong order;
- reject `mixed` as observation-summary output;
- preserve feedback-record-level `mixed` input where already allowed.

Apply the same deterministic language binding wherever conflicts/other canonical structures have an equivalent derived language summary, but only if the active contract already defines such a field. Do not invent new summary fields.

---

# Required regressions

## CONTRA-FIX-01 — wrong Steam appid child rejected
Correct exact-app parent with stable child URL exposing a different Steam appid must fail.

## CONTRA-FIX-02 — matching Steam stable child accepted
Exact dossier appid + matching parent + matching stable child remains valid.

## CONTRA-FIX-03 — wrong Steam physical container rejected
When parent and child expose distinct deterministic Steam thread/container identity, mismatch must fail.

## CONTRA-FIX-04 — fallback not over-tightened
Valid transient-author fallback under exact-product parent remains valid without child item URL/ref.

## CONTRA-FIX-05 — author-derived feedback_id rejected
Otherwise-valid stable record with `feedback_id` containing a SteamID/profile-derived token must fail under the chosen local-ID model.

## CONTRA-FIX-06 — author-derived source_id rejected
Otherwise-valid source with author-derived/internal non-local source id must fail.

## CONTRA-FIX-07 — neutral stable local IDs accepted
Stable evidence with safe local source/feedback IDs + valid neutral item URL/public_ref passes.

## CONTRA-FIX-08 — mixed record language projection
Bound feedback language `mixed` must serialize summary exactly as `["russian","non_russian"]`.

## CONTRA-FIX-09 — unknown preserved
Bound unknown-language support must include `unknown` in canonical ordered output.

## CONTRA-FIX-10 — incomplete language summary rejected
Russian + non-Russian bound set serialized as only `["russian"]` must fail.

## CONTRA-FIX-11 — mixed summary token rejected
Observation summary containing `mixed` must fail even though record-level `mixed` remains legal.

## CONTRA-FIX-12 — wrong language order rejected
Correct tokens in non-canonical order must fail.

## CONTRA-FIX-13 — current g000001 complete candidate fixture
A deterministic complete three-game candidate for:
- Crown Trick using accepted Steam Store concrete-card fallback;
- Hellish Quart using an accepted stable/fallback path;
- Tetris Effect using an accepted stable/fallback path;
must validate under all three fixes.

## CONTRA-FIX-14 — prior guards remain green
Run existing suites covering:
- Steam Store review-card parent;
- transient-author fallback;
- language binding;
- semantic consistency;
- Russian existence/retrieval;
- multi-source retrieval;
- package identity;
- Story-DLC;
- buffered/maximal-contiguous-prefix;
- content-complete binding/compatibility.

---

# Canonical contract / prompt / validator alignment

For each of CONTRA-01..03:
- identify the actual canonical owner;
- update schema/contract/prompt/validator only where needed;
- ensure no layer still contradicts the intended behavior;
- do not duplicate the same rule into unnecessary new config surfaces.

If schema revision / evidence contract revision / worker prompt revision must change, update content-complete binding through normal canonical mechanism.

Do not preserve stale compatibility by hand.

---

# PROJECT_DECISIONS

Update the existing relevant TASTE decision(s) or add one compact new decision covering the three enforcement closeouts.

Record:
- exact-product/physical-parent Steam child binding is validator-enforced;
- internal join IDs are author-independent local keys;
- stable item identity remains in safe URL/public_ref;
- observation language summary is exact deterministic projection, not free-form;
- no privacy or recurrence guard is weakened.

Do not rewrite unrelated history.

---

# Architecture constraints

Do not change:
- GitHub control-plane ownership;
- Scheduled ChatGPT role;
- group size = 3;
- atomic full-group publication;
- maximal contiguous prefix;
- retry/healing architecture;
- transient-author fallback model;
- Steam Store review-card parent exception;
- source-agnostic Russian discovery;
- Story-DLC scope policy;
- package/pricing/ranking/giveaway/UI.

Do not create:
- new recurring worker;
- new queue;
- new reviewer identity database;
- cross-run author mapping;
- new retry loop.

---

# Compatibility / activation

Normal bounded flow:
- branch/PR;
- focused CONTRA-FIX regressions;
- existing dossier suites;
- execution ownership validation;
- merge only green;
- normal GitHub-owned activation/rebuild;
- fresh compatible binding/snapshot if required;
- no manual rebind/progress repair.

If canonical source/current-offer scope changes during activation, report the exact before/after counts. If the count changes materially and the reason is not already explicit from canonical source recomputation, do not hand-wave it: close the delta in the report with exact removed/added items or a machine-derived grouped explanation.

---

# Scheduled Task

Do NOT run Scheduled Task `Run now`.
Do not change Scheduled Task settings.

---

# Durable report

Required path:
`reviews/worker_reports/taste-dossier-contract-contradictions-fix-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture preflight.
3. Baseline accepted behavior preserved.
4. CONTRA-01 exact fix.
5. CONTRA-02 exact fix.
6. CONTRA-03 exact fix.
7. Schema/contract/prompt/validator alignment.
8. Privacy implications.
9. Exact-product/physical-parent implications.
10. Exact language projection semantics.
11. CONTRA-FIX-01..14 results.
12. Current g000001 fixture result.
13. Confirmation prior Steam Store/transient-author/Russian/story-DLC guards remain green.
14. PR / CI / merge refs.
15. Activation/binding/snapshot:
   - snapshot id;
   - prepared/completed/remaining;
   - expected sequence;
   - group count;
   - group size;
   - exact g000001;
   - scope delta vs pre-task baseline and exact reason if changed.
16. PROJECT_DECISIONS ref.
17. Confirmation Run now/settings unchanged.
18. Unresolved.
19. Status.
20. Exactly one recommended next step.
21. Efficiency / reusable lesson.

Allowed statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

---

# CURRENT_TASK.md

Update only according to `CHAT_PROTOCOL.md`; preserve unrelated concurrent work.

---

# Exactly one next step after success

Return to Director.

Do not run Scheduled Task inside this task.

Director decides whether to perform one clean live acceptance of the existing Taste Steam Review Dossier worker against the resulting current compatible g000001.
