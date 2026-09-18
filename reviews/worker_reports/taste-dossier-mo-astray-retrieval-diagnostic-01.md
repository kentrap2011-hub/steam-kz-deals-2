# Taste Dossier MO:Astray Retrieval Diagnostic 01

## 1. Task / repo / mode

- Task: `TASTE DOSSIER MO:ASTRAY RETRIEVAL DIAGNOSTIC 01`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Mode: `READ-ONLY DIAGNOSTIC`.
- Scope: only `MO:Astray` from current `g000011`, with `Cthulhu Saves the World` used only as the accepted control case.
- No implementation, contract/schema/prompt/validator change, PR, production candidate publication, progress mutation, Scheduled Task run, or other repository write was performed.
- The only repository write is this durable report.

## 2. Current snapshot / canonical status / g000011 / exact MO:Astray appid

The worker index was read before the diagnostic and re-read immediately before report creation. Its liveness fields remained unchanged:

- snapshot: `ec6ff4015ad01a9dcaaa2be845230cf04790c1444b99d5a1c31dad39047de872`
- canonical expected sequence: `7`
- prepared / completed / remaining: `702 / 18 / 684`
- `full_backlog_complete=false`
- group count: `234`
- active worker prompt revision: `web-evidence-v2-steam-russian-review-retrieval-improvement-v1`
- active evidence-contract revision: `contract-contradictions-fix-2026-09-18`

Authoritative live context says `g000001` through `g000010` were published create-only in the Scheduled invocation; those are buffered transport progress and not automatic canonical acceptance.

Exact `g000011` descriptor:

1. `1102190` — Monster Train
2. `1104380` — The Room VR: A Dark Matter
3. `1104660` — MO:Astray

Exact canonical MO:Astray appid is therefore **`1104660`**. The descriptor reason is `refresh_required`.

The authoritative live result for MO:Astray remains:

- exact-app Russian Steam existence signal: `144` Russian-language reviews;
- one concrete Russian Steam review card was found only through profile-scoped context;
- no contract-usable Russian/mixed item was obtained;
- state: `existence_established_retrieval_unresolved`;
- `g000011` was not published.

## 3. Diagnostic budget used

Task ceiling:

- search/web queries: maximum 16;
- opened/read source representations: maximum 32.

Actually used:

- **16 / 16 search queries**;
- **12 / 32 opened/read source representations**, conservatively counting failed direct-open attempts and the final non-thread icon click.

The 16 searches materially covered:

- accepted Cthulhu-style exact title + appid + Russian review terms on Steam Store;
- the same MO:Astray form;
- exact-app Steam Community;
- Russian review/user-review wording variants;
- title punctuation/tokenization variants (`MO:Astray`, `MO Astray`, full-width-colon form);
- appid-constrained variants;
- non-Steam/public alternatives including Russian community/search surfaces.

No production ceilings were changed.

## 4. Cthulhu control route replay

Accepted control from the prior implementation report:

- exact target: `Cthulhu Saves the World`, appid `107310`;
- the post-improvement proof used search-indexed exact-app Steam Store recovery;
- the returned non-profile exact-product Store representation visibly exposed at least one concrete Russian review card;
- no neutral stable item locator was required because the already-legal transient-author fallback prerequisites were visible on the safe exact-app Store parent;
- accepted safe parent in that proof:
  `https://store.steampowered.com/app/107310/Cthulhu_Saves_the_World/?cc=br&l=russian`.

Current diagnostic replay did **not** reproduce that same concrete-card representation:

- the exact Cthulhu search form returned no equivalent concrete-card result in the current search index;
- direct opening of the previously successful safe parent remained exact-product and exposed the Russian aggregate population, but the current parsed representation was aggregate-only rather than card-level.

Therefore the accepted Cthulhu proof remains valid evidence that the route can work, but it is also now proven to be dependent on the search/crawl representation available at a particular time. The control route is not a deterministic guarantee that every exact-app Store result will expose cards.

## 5. MO:Astray route-by-route comparison

| Route | MO:Astray result | Cthulhu control difference | Diagnostic interpretation |
|---|---|---|---|
| Exact title + appid + Russian terms, Steam Store | Exact appid `1104660` resolved repeatedly; Russian population `144` visible; no concrete Russian card in returned representation | Accepted Cthulhu proof previously returned concrete Russian cards on the safe Store parent | Material indexed-representation difference |
| Exact-app Store open, Russian locale | Exact product opens in one indexed form but remains aggregate-only | Cthulhu prior proof had card-level indexed representation | Same |
| Direct Store `cc=br&l=russian` / `cc=ru&l=russian` variants | Current transport returned internal-error/unusable direct representations | Cthulhu previously successful safe URL remains openable | Route availability differs by product/current representation |
| Exact-app Steam Community root | Safe exact-product non-profile page is readable; Russian community material is visible alongside other content | Not needed for Cthulhu proof | Transport can access MO:Astray Community generally |
| Exact-app Community reviews | Concrete individual cards are readable, but the cards exposed in the returned collection were non-Russian | Cthulhu Store indexed proof exposed Russian cards | Card-level access exists, but not Russian card exposure |
| Direct Community Russian-filter form | Unusable/internal-error representation in current transport | No successful MO counterpart found | Direct locale/filter family does not close the gate |
| Exact-app Community discussions | Safe exact-product collection is readable; a Russian localization-related discussion row is indexed, but the returned list does not expose a usable child thread/post locator or inspected post body | Cthulhu did not require row-to-child recovery | MO exposes Russian activity in a list/index shape rather than a usable concrete item shape |
| Non-Steam/public alternatives | No contract-usable exact-product Russian/mixed player-feedback item appeared in the returned results within the bound | Cthulhu alternatives were unnecessary after Store proof | Does not close the gate |
| Title punctuation / Unicode variants | Colon omitted and full-width-colon forms still resolve the same exact product/surfaces; no concrete Russian card appears | n/a | Punctuation is not supported as the cause |

The exact Cthulhu recovery query pattern therefore produced **no contract-usable concrete Russian MO:Astray card**.

The key difference is not product identity resolution: appid `1104660` is stable. The difference is the **shape of the indexed/returned player-feedback representation**.

## 6. Candidate ledger

No username, display name, SteamID/account id, profile URL, raw review body, post body, quote, or excerpt is persisted below.

| Diagnostic ID | Surface/source class | Exact product | Concrete player content visible | Language | Stable neutral locator | Transient author distinguishable | Safe non-profile exact-product parent | Contract usability | FIRST rejection reason | Blocker classification |
|---|---|---|---|---|---|---|---|---|---|---|
| MO-RU-01 | Steam review, profile-scoped discovery from authoritative live run | yes, appid `1104660` | yes | Russian | no safe neutral locator reported | yes, sufficient for transient dedupe | no inspected safe parent for that item | no | concrete item is exposed only through forbidden profile-scoped provenance and cannot be re-parented | indexed/retrieval representation |
| MO-RU-02 | Steam Community exact-app screenshot/community card | yes | concrete Russian user-generated community content is visible | Russian | no accepted feedback-item locator established | not needed for rejection | exact-app Community parent exists | no | screenshot/progress-style community content is not a reliable player-feedback record for the dossier gate | semantic non-feedback lead |
| MO-RU-03 | Steam Community exact-app guide/localization-resource card | yes | concrete Russian community resource text is visible | Russian | no accepted feedback-item locator established | not needed for rejection | exact-app Community parent exists | no | instructional/localization resource is not itself a player-feedback assertion | semantic non-feedback lead |
| MO-RU-04 | Steam Community exact-app discussions index | yes | Russian discussion row is visible, but no post body was inspected | Russian activity signal only | no child thread/post locator surfaced in the returned representation | index row shows an author distinction but it cannot substitute for inspecting the item | exact-app discussions collection is safe | no | collection/list row without an inspectable concrete child item; available click target resolved only to a static forum icon | indexing/item-link exposure |

Only MO-RU-01 is a proven concrete Russian review card. It fails before serialization because its provenance is profile-scoped. MO-RU-04 is the strongest safe non-profile recovery lead, but current indexed representation stops at a collection row and does not expose the concrete child needed by either stable-locator or transient-author fallback.

## 7. Search-index / Store / Community differences

The diagnostic establishes all of the following:

1. MO:Astray exact Store identity is easy to resolve; the Store representation repeatedly exposes the exact app and the `144` Russian-review existence signal.
2. Unlike the accepted Cthulhu proof, MO:Astray Store search/index representations remain aggregate-only.
3. MO:Astray exact Community reviews can expose concrete cards, proving that current transport is not globally unable to read card-level Steam content for this app; the exposed cards were non-Russian.
4. MO:Astray exact Community discussions expose Russian exact-product activity as an indexed row, but the parsed collection does not provide the concrete child target/body needed for legal item provenance.
5. The current Cthulhu replay itself no longer reproduces the prior concrete Store card, showing that the search-indexed recovery path is crawl/index-representation-sensitive over time.
6. Locale/country parameter variants did not improve MO:Astray representation and in some direct forms returned an internal error.
7. Colon/punctuation/Unicode tokenization did not materially change exact-product resolution and is not supported as the cause.

## 8. Stable locator result

**No contract-safe neutral stable locator was obtained for a concrete Russian/mixed MO:Astray player-feedback item.**

- The authoritative profile-scoped Russian review did not expose a safe neutral locator.
- Exact-app Store yielded only aggregate Russian counts.
- Exact-app Community reviews yielded concrete non-Russian cards.
- Exact-app discussions yielded a Russian list/index lead but no child thread/post locator in the returned representation.

No stable item was rejected by contract after being safely inspected. The required stable item simply was not exposed.

## 9. Transient-author fallback result

**The current fallback contract is sufficient in principle, but its retrieval prerequisites were not simultaneously satisfied.**

- Profile-scoped Russian review: concrete item + transient author distinction existed, but there was no inspected safe non-profile parent for that item.
- Store exact-app parent: safe parent existed, but no Russian concrete card was inspected there.
- Community review parent: safe parent + concrete cards existed, but the inspected cards were non-Russian.
- Community discussions parent: Russian row existed, but no concrete child post/body was inspectable through the returned representation.

Therefore no legal `transient_author_deduped` Russian record can be serialized from this diagnostic.

## 10. Non-Steam/public alternative result

Materially different public-player-feedback discovery was attempted within the 16-query ceiling, including Russian community/search forms outside the exact Steam Store route.

No returned non-Steam/public result produced a contract-usable exact-product Russian/mixed concrete player-feedback item for MO:Astray.

This means the diagnostic did not find an alternate legal item that production merely overlooked.

## 11. Primary blocker classification

**Primary result: `indexing_surface_difference`.**

Why this is primary rather than `strategy_application_gap`:

- replaying the Cthulhu-style exact-app search strategy did not yield a legal MO:Astray Russian card;
- the current diagnostic itself, with a larger 16-query ceiling, also failed to obtain one;
- therefore there is no evidence that production merely failed to execute an already-sufficient query order.

Why this is primary rather than a pure `external_transport_limitation`:

- current transport can read MO:Astray exact-app Store, exact-app Community, concrete Community review cards, discussion collections, and concrete non-profile Steam thread/card content generally;
- what differs is where and how Russian MO:Astray material is exposed: aggregate Store counts, profile-scoped review discovery, and safe Community list/index rows rather than a safe concrete Russian review/post item;
- the first blocking difference is therefore the public indexed/returned representation shape. The current inability to finish the Russian item is a consequence of that shape, not proof that the transport is globally unable to inspect MO:Astray player-feedback items.

Why this is not `contract_contradiction`:

- no safely inspectable accepted-shape Russian item was found and then inconsistently rejected;
- every rejection follows an existing rule already aligned across prompt/schema/evidence contract.

## 12. Whether current contract is internally consistent

**Yes.**

The active contract consistently requires:

- aggregate review/language counts to remain discovery metadata only;
- profile-scoped URLs/identity not to persist;
- stable item locator to be preferred;
- transient-author fallback to require a concrete inspected item on a safe exact-product non-profile collection;
- safe parent/child physical relationship rather than same-host re-parenting;
- Russian unresolved states to block complete dossier publication.

The MO:Astray evidence encountered here falls cleanly on those boundaries.

## 13. Whether a new contract change is justified

**No.**

No privacy, provenance, exact-product, recurrence, language, or fallback rule needs relaxation.

In particular, it would be incorrect to:

- convert the `144` aggregate Russian count into a feedback mention;
- persist the profile-scoped review locator;
- re-parent the profile-scoped card to Store/Community merely because appid matches;
- treat a discussions-index row as a concrete inspected post;
- weaken parent/child physical binding.

The missing capability is retrieval/index traversal, not evidence semantics.

## 14. Minimal next-step design direction

The narrow design direction is a **generic retrieval-route improvement**, not a contract change:

- after exact-app Russian existence is proven and Store recovery is aggregate-only, allow the existing exact-app Community recovery to progress from a safe collection/index row to a **neutral child thread/review item locator and concrete item representation**;
- keep exact appid fail-closed;
- persist no author/profile identity;
- use the existing stable-locator path when a safe child locator is exposed, otherwise the existing fallback only when the concrete child is actually inspected on the safe parent;
- do not special-case MO:Astray or title punctuation.

The exact route candidate for a bounded follow-up is:

`exact-app Community collection/index row -> safe neutral child thread/review locator -> concrete item open`.

## 15. Unresolved

The diagnostic does not establish which lower-level indexing/adapter behavior suppresses the child target for the Russian MO:Astray discussion row: search-engine indexing omission, Steam collection parsing, dynamic link rendering, or connector link extraction.

The search ceiling was reached after the Russian discussion-row lead was established. The remaining page budget could inspect known targets, but the returned collection exposed no usable child target to open; guessing a thread id was not allowed.

Also, the current Cthulhu replay no longer reproduces the previously accepted concrete-card Store representation. That confirms route volatility but does not invalidate the prior proof.

These unresolved transport details do not change the primary classification.

## 16. Status

`complete_indexing_surface_difference`

## 17. Exactly one recommended next step

Open one bounded **retrieval-route implementation** task for the existing Scheduled-worker web retrieval path: generically resolve a safe exact-app Steam Community collection/index row into its neutral non-profile child thread/review locator and concrete item representation, while preserving all current exact-product, privacy, parent-binding and Russian-evidence rules.

Do not change the evidence contract unless that implementation uncovers a separate concrete accepted-shape contradiction.

## 18. Efficiency / reusable lesson

The reusable lesson is that the successful Cthulhu search-indexed Store proof is a recovery pattern, not a guaranteed rendering contract.

For future exact-app Russian existence cases:

1. test the indexed Store representation once;
2. if it is aggregate-only, move immediately to exact-app Community card/item recovery rather than spending several variants on locale or title punctuation after identity is already proven;
3. when Community exposes a Russian list/index row but not a child target, classify that as an item-link retrieval gap instead of repeating aggregate searches;
4. only after the safe Steam paths fail, continue source-agnostic diversification.

Because this task permitted only one durable write, the reusable route candidate is recorded here rather than by editing `PROJECT_ROUTES.md` or `KNOWN_WORKER_PITFALLS.md`.
