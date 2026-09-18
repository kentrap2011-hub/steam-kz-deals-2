# WORKER TASK — TASTE DOSSIER TRANSIENT AUTHOR DEDUPE FALLBACK IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-transient-author-dedupe-fallback-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный Taste dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- canonical strict/buffered validator paths;
- `PROJECT_DECISIONS.md` — evidence/privacy rationale;
- `reviews/worker_reports/taste-dossier-g000001-strict-retrieval-diagnostic-01.md`;
- `reviews/worker_reports/taste-dossier-g000001-open-russian-discovery-control-01.md`;
- `reviews/worker_reports/taste-story-dlc-scope-policy-implement-01.md` only for the current post-DLC-filter snapshot/scope.

Перед первой write выполни architecture preflight из `CHAT_CONTEXT.md`.

## User-approved direction

Пользователь разрешил использовать автора Steam review как временный способ отличить один отзыв от другого, если обычный neutral review identifier получить нельзя.

Ключевая цель:

> Если конкретные отзывы реально видны и читаются, система не должна выбрасывать их только потому, что retrieval tool не получил отдельный neutral recommendation ID. Стабильную identity автора можно использовать временно для dedupe, но имя/SteamID/profile URL не нужно сохранять или показывать.

Это разрешение НЕ означает, что можно сохранять или хэшировать пользовательские идентификаторы без ограничений.

## Problem proven by diagnostics

Strict + open control audits доказали:
- concrete Russian review bodies for Crown Trick / Hellish Quart are publicly visible;
- dominant blocker is missing stable neutral item-level locator;
- Hellish Quart also produced a direct exact-product Russian review whose only recovered URL was profile-scoped;
- current privacy/provenance contract rejects such evidence even though the feedback itself is factually useful.

Current post-story-DLC-filter g000001 is expected to contain:
1. Crown Trick — appid 1000010
2. Hellish Quart — appid 1000360
3. Tetris® Effect: Connected — appid 1003590

Re-check current canonical descriptor before implementation/validation. Do not assume stale snapshot identity.

## Design principle

Keep the existing provenance hierarchy.

### Preferred identity path — unchanged

If a neutral stable item locator exists, use it:
- Steam `recommendationid`;
- direct non-profile item URL;
- stable neutral comment/post/review token;
- existing accepted public_ref namespaces.

This remains the strongest and preferred record form.

### New fallback path

Only when a concrete player-feedback item is actually visible/inspected but no acceptable neutral item-level locator is obtainable:

1. A stable author/account/profile identity MAY be read **transiently** solely to determine whether two visible review cards/items came from the same or different authors.
2. The raw author identity MUST NOT be persisted into:
   - candidate artifact;
   - canonical dossier/cache;
   - worker report;
   - logs intentionally produced by this implementation;
   - `public_ref`;
   - URL fields;
   - source ids;
   - feedback ids.
3. Do NOT persist:
   - username/display name;
   - SteamID/account id;
   - vanity profile id;
   - profile URL;
   - direct unsalted hash of any of the above;
   - deterministic reversible/predictable pseudonym derived from public identity.
4. After transient dedupe, assign only dossier-local opaque feedback records that contain no user-derived identifier.
5. These fallback records MUST be explicitly marked with a machine-readable identity/provenance mode such as `transient_author_deduped` (exact name may vary if a cleaner existing schema extension exists).
6. Persist the exact product-level collection/source surface from which the concrete review item was inspected, plus the normal non-identifying date/language/source metadata that is actually known.
7. Do not claim stable cross-run identity for a fallback record.

## Privacy requirement

The fallback must improve privacy compared with persisting profile URLs.

A raw hash of SteamID/username is NOT acceptable as the canonical solution because a public identifier may be enumerable/re-identifiable.

Do not create a secret-management subsystem, new identity service, user mapping database or persistent reviewer registry.

This is transient in-worker dedupe only.

## Auditability / evidence-strength tradeoff

Because a `transient_author_deduped` record lacks a stable independently re-openable item locator, it is weaker than a normal item-level record.

Therefore implement explicit strength restrictions.

Minimum required behavior:
- fallback record may support an observation as real player feedback;
- distinct fallback records may be created only when the worker actually observed distinct authors on concrete review items;
- same transient author observed twice on the same product must dedupe to one physical feedback item unless a normal stable item identifier proves multiple distinct items;
- fallback-only evidence MUST NOT by itself establish `moderate` or `strong` recurrence;
- fallback-only evidence may establish at most `limited` recurrence;
- if stable-locator records also support the observation, normal recurrence may use the stable records under existing rules; design the smallest deterministic rule for mixed stable+fallback sets and document it clearly;
- do not let five anonymous collection cards silently become `strong` merely because five local opaque ids were assigned.

Choose a minimal deterministic recurrence/count model and enforce it in the canonical validator. Do not leave this only in prose.

## Russian existence/retrieval gate interaction

A concrete Russian/mixed fallback record that satisfies all new fallback requirements MAY satisfy `russian_attempt = found_and_used`.

Thus Crown Trick / Hellish Quart should no longer remain blocked solely because neutral recommendation ID retrieval failed, if concrete Russian review items with transiently distinguishable authors are actually visible.

Aggregate counts alone still do not satisfy `found_and_used`.

## Collection surface restriction

Do NOT broadly convert collection/list pages into player-feedback records.

Fallback is allowed only for concrete individual review/post/comment cards/items that the worker actually inspected within a reliable exact-product player-feedback surface.

Required:
- exact product identity is established;
- item content is visibly a distinct player-generated feedback item;
- language is classified from that concrete item;
- transient author identity is available strongly enough for dedupe;
- the parent collection/source surface is persisted normally;
- no author identity leaves transient worker state.

A generic review-count page, search results page, aggregate statistics page, or list with no concrete review items is still not feedback.

## Exact identity

Preserve exact-product identity.

- Crown Trick feedback must relate to Crown Trick.
- Hellish Quart feedback must relate to Hellish Quart.
- Tetris Effect feedback must relate to Tetris Effect.
- Story-DLC policy remains unchanged.
- Do not reintroduce BG3 Digital Deluxe into scope.

## Machine-readable schema

Implement the smallest compatible extension needed to represent the fallback clearly.

Possible shape, illustrative only:
- feedback record `identity_mode = stable_locator | transient_author_deduped`;
- stable mode retains existing item URL/public_ref requirement;
- transient-author mode requires exact parent source + no item/profile URL + no user-derived public_ref + explicit local-only provenance classification.

Do not use this illustrative naming if existing schema has a cleaner field.

The validator must be able to distinguish stable records from transient-author fallback records and apply different recurrence/auditability rules.

## Strict validator requirements

Canonical GitHub strict validator remains the single authority.

It must reject:
- any persisted username/display name/SteamID/profile id/profile URL in fallback records;
- direct hash/pseudonym formats that encode user identity when detectable by schema/format;
- fallback marked as stable;
- fallback without a valid exact-product player-feedback parent surface;
- fallback created from aggregate statistics without a concrete item;
- duplicate local fallback records that violate the deterministic per-source/per-observation model;
- moderate/strong recurrence derived only from fallback records;
- `found_and_used` without at least one valid Russian/mixed stable or fallback concrete player-feedback record.

Do not weaken existing stable-locator validation for normal records.

## Preferred retrieval order

Worker prompt must say:

1. Try to obtain neutral stable item identity first.
2. If unavailable but a concrete review is visibly inspectable and author identity is available, use author identity transiently for dedupe.
3. Persist no author identity.
4. Use fallback evidence with reduced recurrence strength.
5. Do not spend the entire bounded budget repeatedly chasing a neutral locator after a valid fallback is available unless stronger evidence is reasonably obtainable within remaining budget.

Hard search/page ceilings remain unchanged unless current canonical contract says otherwise.

## Required regressions

### AUTHOR-FB-01 — recommendationid remains preferred
A Steam review with neutral recommendationid uses normal stable record path, not fallback.

### AUTHOR-FB-02 — transient author fallback accepted
Exact-product Russian review card has no neutral item locator but has a distinct stable author identity visible transiently. Persisted artifact contains no author data and validates as fallback.

### AUTHOR-FB-03 — same author dedupes
Two renderings/cards attributable to the same transient author on the same product do not become two independent fallback mentions.

### AUTHOR-FB-04 — two distinct authors
Two concrete exact-product Russian review items with distinct transient authors can produce two local fallback records and limited recurrence, with no persisted identity.

### AUTHOR-FB-05 — fallback recurrence cap
Three/five fallback-only records cannot produce moderate/strong recurrence. Validator rejects overstatement.

### AUTHOR-FB-06 — mixed stable + fallback
Define and validate deterministic recurrence/count semantics for an observation supported by both stable-locator and transient-author fallback records.

### AUTHOR-FB-07 — profile URL not persisted
Hellish Quart diagnostic shape: direct profile-scoped Steam recommendation may be inspected, but resulting persisted fallback must not contain profile URL/SteamID/name/hash.

### AUTHOR-FB-08 — aggregate still invalid
Russian review count / exact Steam store page without concrete item remains existence signal only.

### AUTHOR-FB-09 — Russian gate
Valid Russian fallback record can satisfy `found_and_used`.

### AUTHOR-FB-10 — exact identity preserved
Fallback cannot bypass exact appid/product identity.

### AUTHOR-FB-11 — no direct-hash workaround
Fixture with persisted direct hash/pseudonym derived from account id is rejected/not generated according to the chosen schema.

### AUTHOR-FB-12 — current g000001 fixture
Deterministic fixture representing Crown Trick/Hellish Quart collection-card shapes proves they can become usable Russian feedback when concrete items + transient distinct-author evidence are available, without requiring a persisted profile identity.

## PROJECT_DECISIONS

Add one compact decision adjacent to the current evidence/provenance decisions:

Rationale:
- neutral item ID remains preferred;
- public review content should not be discarded solely because the retrieval tool cannot expose its neutral ID;
- transient author identity may be used only for within-run dedupe;
- author identity never persists;
- direct hashing is not accepted as anonymization;
- fallback evidence has reduced recurrence/auditability strength;
- privacy and exact-product identity remain fail-closed.

Do not rewrite unrelated decisions.

## Architecture constraints

Do not change:
- GitHub control-plane ownership;
- Scheduled ChatGPT role;
- group size = 3;
- parallel buffer / maximal contiguous prefix;
- story-DLC scope policy;
- source-agnostic Russian discovery;
- ranking/pricing/package/giveaway/UI;
- retry/healing architecture.

Do not create:
- reviewer identity database;
- secret service;
- persistent cross-game reviewer mapping;
- new recurring stage;
- new queue.

## Compatibility / activation

This changes evidence schema/contract/prompt/validator semantics and therefore likely changes content-complete binding.

Use normal flow:
- bounded branch/PR;
- focused CI/regressions + ownership validation;
- merge only green;
- normal GitHub-owned activation/rebuild;
- fresh compatible snapshot when required;
- stale old artifacts handled only by canonical recovery;
- no manual rebind/progress repair.

## Scheduled Task

Do NOT run Scheduled Task `Run now`.
Do not change Scheduled Task settings.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-transient-author-dedupe-fallback-implement-01.md`

Required sections:
1. Task / repo / mode.
2. Architecture/privacy preflight.
3. Exact fallback model.
4. Why direct username/SteamID hash was rejected.
5. Preferred stable locator path.
6. Transient author dedupe mechanics.
7. Persisted schema shape and proof no identity persists.
8. Deterministic recurrence/count semantics including mixed stable+fallback.
9. Russian gate interaction.
10. Strict validator changes and confirmation stable path was not weakened.
11. AUTHOR-FB-01..12 results.
12. Crown Trick / Hellish Quart diagnostic fixture result.
13. Exact identity/story-DLC preservation.
14. PR / CI / merge refs.
15. Activation/binding/snapshot state:
    - snapshot id;
    - prepared/completed/remaining;
    - expected sequence;
    - group count;
    - group size;
    - exact g000001.
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

## CURRENT_TASK.md

Update only according to `CHAT_PROTOCOL.md`; preserve unrelated concurrent work.

## Exactly one next step after success

Return to Director. Do not launch Run now inside this task. Director decides whether to perform one live acceptance against the fresh/current compatible g000001.
