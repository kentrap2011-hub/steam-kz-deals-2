# WORKER TASK — TASTE DOSSIER PRAGMATIC EVIDENCE MODEL FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

Task ID: `taste-dossier-pragmatic-evidence-model-fix-01`
Mode: `IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/taste-dossier-pragmatic-evidence-model-fix-01.md`

## User-approved decision

The current Dossier evidence model is too audit-oriented and may reject useful player evidence only because a concrete review lacks a stable item-level locator or an author-based dedupe fallback.

The new principle is:

> Dossier exists to build a trustworthy, sufficiently complete neutral picture of the exact game for downstream Deep analysis. Evidence usability is determined primarily by whether the worker directly observed useful player-feedback content and can bind that content confidently to the exact target product. A permanent direct URL/locator for every individual review is useful when available, but is not required merely to make the observed information usable.

The user explicitly approved these consequences:

1. Useful information visible directly in web/search results may be used when the result itself exposes enough evidence to establish that it is player feedback about the exact target product.
2. Exact-product/AppID binding remains strict because remasters, DLC, editions, sequels and same/similar titles can genuinely be confused.
3. Exact per-review counting/deduplication is not a primary objective. Dossier should not discard useful evidence merely because it cannot assign a permanent unique identity to every review.
4. Provenance exists for debugging/source traceability and hallucination resistance, not to create a court-like proof chain for every observation.
5. Raw review text, usernames, profile identifiers and author identity still must not be persisted. Persist only safe source-level provenance and neutral paraphrased observations.
6. The existing coverage-sufficiency fix remains fully active: richer usable evidence should improve downstream completeness, not weaken the requirement for a balanced decision-ready picture.

## Triggering production case

A real post-fix Dossier invocation failed closed on:
- game: `Tiny Snow`
- appid: `1002560`

The worker observed:
- exact-product Russian-feedback existence;
- a concrete Russian review text visible in a search result on `stmstat`;
- exact-product context;
- no contract-usable stable item locator;
- no permitted transient-author fallback;
- direct open/read then failed with HTTP/tool error `436 Unknown Status Code`.

The current contract therefore forced:
`existence_established_retrieval_unresolved`
and blocked the entire three-game group despite directly observed useful Russian player-feedback content.

This task must make that class of failure unnecessary without weakening exact-product identity.

## START gate

First read current `CHAT_PROTOCOL.md` and complete its START gate.

Then read this task fully.

Read current, minimally:
- `CHAT_CONTEXT.md`
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/taste_steam_review_dossier_schema.json`
- `scripts/taste_steam_review_dossier_strict.py`
- current provenance helper(s), fixtures and focused Dossier tests
- `reviews/worker_reports/taste-dossier-purpose-and-coverage-sufficiency-fix-01.md`
- relevant TASTE-008 / TASTE-010 / TASTE-012 / TASTE-014 / TASTE-015 decisions.

Do not perform broad archaeology.

## Architecture preflight — fixed decisions

Before implementation verify and preserve:

1. GitHub remains control plane for scope/order/binding/validation/persistence/recovery/completeness.
2. Scheduled ChatGPT remains the neutral semantic/web evidence producer with create-only transport.
3. Dossier remains profile-agnostic; Deep remains personalized.
4. Exact target identity remains strict at product/AppID/release/DLC/edition level where relevant.
5. No raw review/post bodies, verbatim quotes, usernames, Steam IDs, profile IDs, author identities or reversible author hashes are persisted.
6. No new scheduler, retry daemon, queue, crawler, persistent author registry or external evidence store is introduced.
7. No fixed minimum review/source/search/page quota is introduced.
8. TASTE-014 semantic/adaptive bounded retrieval remains active.
9. TASTE-015 purpose/coverage sufficiency remains active.
10. No Scheduled Task action is authorized.
11. No Dossier/Deep recovery or manual backlog replay is authorized by this task.

This task IS authorized to supersede the item-level locator / transient-author / mention-count portions of TASTE-008 and TASTE-010 when they conflict with the user-approved pragmatic evidence model.

## IMPLEMENT

### EVID-01 — evidence may come from an inspected search-result representation

Allow a search/discovery result itself to support neutral Dossier evidence when ALL are true:

- the worker actually received/inspected the result representation;
- the representation exposes concrete player-authored/player-feedback content, not only aggregate rating/count or editorial/publisher copy;
- the result can be bound confidently to the exact target product through result metadata/URL/title/appid/release context;
- the content is useful to one or more neutral Dossier observations;
- persisted output contains only a neutral paraphrase/summary, never the raw snippet/quote;
- persisted provenance contains only safe source-level metadata and an acquisition/evidence mode indicating the content was observed from a search/discovery representation.

The downstream validator must not require the target page to have been successfully opened if the search-result representation itself already exposed usable evidence.

A search query string alone is never evidence.
A domain hit alone is never evidence.
An aggregate rating/count alone is never concrete player feedback.

### EVID-02 — collection/page-level inspected feedback is usable without per-item locator

If the worker directly sees one or more concrete player-feedback cards/items on an exact-product page/collection, the evidence may be used even when the individual item has no stable public URL/ref and no author identity is retained.

Require:
- safe exact-product parent/source provenance;
- direct observation by the worker;
- neutral paraphrase;
- no claim of independently reopenable per-item identity unless such identity actually exists.

Do not require transient-author identity merely to make a visible review usable.

### EVID-03 — item-level stable locators become optional quality metadata

When a stable non-identifying per-item locator exists, preserve it because it improves auditability.

But:
- absence of such a locator must not make otherwise usable exact-product observed feedback invalid;
- absence must not force a Russian gate failure by itself;
- absence must not cap the whole Dossier to failure if semantic coverage is otherwise sufficient.

Represent auditability honestly through evidence/acquisition mode rather than pretending all evidence has stable item identity.

### EVID-04 — simplify dedupe/counting semantics

Review the current `feedback_id`, `mention_count`, recurrence and stable/fallback counting rules.

Required target behavior:

- Dossier does NOT need a globally stable identity for every individual review.
- Do not use exact per-review identity/count as a prerequisite for evidence usability or Dossier completion.
- Avoid obvious duplicate inflation within the same invocation/result set: identical or clearly same surfaced content must not be counted twice merely because it appears through equivalent routes.
- Corroboration/recurrence should be qualitative and evidence-grounded:
  - one observed player-feedback item = anecdotal support;
  - multiple materially independent observations/sources may justify stronger recurrence;
  - do not claim exact review population counts unless the source genuinely provides them and the contract explicitly allows that aggregate claim.
- No semantic threshold should require N stable item locators.
- If backward-compatible numeric fields must remain temporarily, they must not reintroduce the old stable-locator gate; document their reduced/non-authoritative role.

Prefer removing obsolete counting complexity where safe rather than retaining it as hidden policy.

### EVID-05 — Russian attempt semantics

Simplify the Russian gate around actual usable information.

A Russian attempt may resolve as `found_and_used` when usable exact-product Russian/mixed player-feedback content was directly observed and used through any allowed evidence mode, including:
- stable item-level locator;
- exact-product collection/card observation;
- exact-product search/discovery result representation.

Do NOT require item-level stable locator or transient-author identity for `found_and_used`.

Retain fail-closed behavior when:
- only aggregate evidence proves Russian activity but no concrete Russian player-feedback content is actually visible/usable;
- exact-product identity is ambiguous;
- the surfaced content cannot be established as player feedback.

Review whether the two old `existence_established_*_unresolved` states are still necessary. If retained, narrow them to genuine content-unavailable/access-unresolved cases, not locator-unavailable cases.

### EVID-06 — Tiny Snow regression

Add an exact regression modelling the observed production case:

- target `Tiny Snow`, appid `1002560`;
- exact-product Russian review text is visible in a search/discovery result;
- result provides safe exact-product source metadata;
- no stable individual item locator is available;
- no transient-author identity is available or persisted;
- target page open/read fails with a transport error analogous to 436;
- the visible result still supports a Russian neutral observation;
- Russian attempt resolves as usable/found-and-used rather than `existence_established_retrieval_unresolved`;
- the game is NOT rejected solely because the per-item locator/open failed.

This does not mean the entire Dossier automatically passes: TASTE-015 coverage sufficiency must still be independently satisfied.

### EVID-07 — exact-product safety regressions

Prove the relaxed locator rule does NOT allow:
- base-game feedback for DLC;
- old/original release feedback for remaster/remake when exact release matters;
- sequel/prequel feedback;
- similarly named unrelated game;
- search result whose query mentions target but result content/URL belongs to another product;
- generic site/domain result with no exact-product binding.

### EVID-08 — provenance model

Persist enough safe provenance to answer:

> Where did the worker observe this information, and by what mode?

Do NOT attempt to answer:

> What permanent globally unique identity did this individual author/review have?

Prefer source-level fields such as:
- source URL/domain/public locator safe for persistence;
- exact-product binding evidence already available in the contract;
- evidence acquisition mode, e.g. stable_item / inspected_collection_item / search_result_observation;
- language/freshness/source type where applicable.

No raw snippets/quotes in GitHub.

### EVID-09 — validator behavior

Update strict validation so it checks:
- exact-product source/result binding;
- allowed evidence acquisition mode;
- safe provenance;
- no raw bodies/quotes/author identity;
- observation-to-source support;
- coverage sufficiency.

It must NOT reject solely because:
- no item-level URL exists;
- no stable public item ref exists;
- no transient author is retained;
- direct source open failed after a usable search-result representation had already been observed.

### EVID-10 — preserve coverage and temporal gates

The new pragmatic provenance model must not weaken:
- current 12-dimension coverage attestation;
- `materially_unresolved` rejection;
- balanced strengths/weaknesses investigation;
- current temporal completeness rules;
- exact-product identity.

The result should be: **more usable evidence, same or stronger semantic completeness**.

## REQUIRED REGRESSIONS

At minimum:

- PRAG-01 Tiny Snow search-result Russian evidence survives missing per-item locator + 436 open failure.
- PRAG-02 exact-product collection card can support evidence without stable item URL or transient author.
- PRAG-03 stable item locator still works and remains preferred auditability when available.
- PRAG-04 aggregate-only Russian activity does NOT become player-feedback evidence.
- PRAG-05 query text alone cannot bind a result to target product.
- PRAG-06 wrong appid / DLC/base / remake mismatch fails closed.
- PRAG-07 no raw quote/snippet/author/profile identity persists.
- PRAG-08 duplicate equivalent surfacing cannot artificially strengthen recurrence.
- PRAG-09 recurrence/sufficiency has no hidden minimum stable-locator count.
- PRAG-10 Russian `found_and_used` accepts allowed search-result/collection evidence.
- PRAG-11 old unresolved Russian state, if retained, is limited to genuine absence of usable concrete content/access — not missing locator alone.
- PRAG-12 TASTE-015 coverage gate still rejects localization-only/narrow dossiers.
- PRAG-13 TASTE-012 temporal checks remain intact.
- PRAG-14 no new scheduler/queue/retry/crawler/persistent author registry.
- PRAG-15 normal buffered group validation/traversal and GitHub-owned persistence/recovery remain unchanged.

Run all relevant current Dossier validation workflows/tests. Do not weaken unrelated tests to pass.

## Migration / compatibility

The evidence contract/schema/prompt binding will change. Use the normal GitHub-owned projection rebuild semantics.

Do not manually rewrite historical accepted Dossiers in place.

Do not manually recover the failed Tiny Snow group.

Old dossiers that no longer validate under the new binding should become refresh work through the normal canonical mechanism.

If schema compatibility requires a version/revision update, make it explicit and deterministic.

## Durable decisions

Update `PROJECT_DECISIONS.md` with a new decision that explicitly supersedes only the conflicting clauses of TASTE-008/TASTE-010:

- exact-product identity stays strict;
- concrete useful player feedback may be accepted from directly observed search-result/collection representations;
- item-level permanent locator and author identity are optional auditability mechanisms, not evidence-validity gates;
- provenance is for source traceability/debugging, not court-like proof;
- no raw text or personal identifiers persist;
- exact per-review counting is not a completion requirement;
- Russian `found_and_used` depends on usable observed Russian player feedback, not per-item locator availability.

Update `PROJECT_ROUTES.md` only if operational routing changes.

## Production boundaries

Do NOT:
- run/modify Scheduled Tasks;
- manually rerun Tiny Snow;
- manually recover Dossier groups;
- authorize Deep recovery;
- process production backlog manually;
- alter Fast/Deep semantic thresholds;
- alter UI/ranking/pricing behavior.

Natural GitHub rebuilds/tests caused by merged source changes are allowed.

## Durable report

Commit:
`reviews/worker_reports/taste-dossier-pragmatic-evidence-model-fix-01.md`

Required sections:
1. Final status
2. Architecture preflight
3. Old evidence-model problem
4. New allowed evidence modes
5. Exact-product safety
6. Russian gate changes
7. Dedupe/recurrence simplification
8. Provenance/privacy behavior
9. Schema/validator changes
10. Files changed
11. PRAG-01..PRAG-15 results
12. Workflow/run refs
13. Projection/binding activation
14. Production observations, if any
15. Unresolved
16. Director recommendation

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `blocked`
- `needs_user_decision`

Before completion:
- commit the final durable report to `main`;
- reread that exact committed report from fresh `main`;
- do not modify it after that reread unless repeating the final commit+reread closeout.
