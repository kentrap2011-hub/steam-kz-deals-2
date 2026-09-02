# giveaway-analysis-identity-recon-01

Task: `giveaway-analysis-identity-recon-01`  
Mode: `READ-ONLY / RECON`  
Date: 2026-09-02

## Accepted UI state

The giveaway navigation/detail UX is already accepted by the user and is not under review here. No UI redesign, source recon, paid-ranking change, manual per-title mapping, new queue, or second semantic runtime is recommended.

## Existing identity authority

The repository has exact identities at the store edges, but it does **not** currently persist an exact cross-store identity that is safe enough to authorize reuse of Steam/canonical analysis for Epic/GOG giveaways.

Current exact assets:

- Steam application identity is canonical `App_X -> appid`; the existing app-identity guard explicitly prevents auxiliary Steam row data from overwriting an explicit `App_X` identity. Ref: `.github/workflows/patch-app-identity.yml` blob `6bc349641eb64dac3d6319b2a32219f34420415e`.
- Giveaway offers persist stable provider identities. Current Epic rows carry exact `source_product_id` and `source_offer_id`. Ref: `data/production/giveaways/v1/current.json` blob `a6f45abbd40d756d0421eb3492eb3e5ef8e8f510`.
- The giveaway-level `canonical_game_key` is **not** an analysis identity authority. In the current snapshot it is `meta-v1:*` with `identity_evidence.basis = exact_normalized_title_and_publishers`. That is acceptable for bounded giveaway grouping, but the task explicitly forbids using title normalization as proof for semantic reuse.
- The existing IGDB integration already proves the important canonical half of the desired bridge: exact Steam appid -> current IGDB `External Game` row -> exactly one IGDB game id, with missing/ambiguous/wrong-source mappings failing closed. Refs: `scripts/duration_enrichment.py` blob `a1a76118f7c2bae036ccc8be9adfa10ef0594abd`; implementation report `reviews/worker_reports/duration-igdb-implement-01.md` blob `27fe858c1de0e39e87e657a100c9ca6d91605dce`.

Therefore the smallest safe canonical route is:

`Epic/GOG exact provider product identity -> IGDB External Game identity -> IGDB game id -> exact Steam External Game uid/appid -> existing appid/family/Taste analysis path`

This route is fail-closed. A title/publisher comparison may discover a candidate, but it cannot authorize the binding.

The already-required `IGDB_CLIENT_ID` + `IGDB_CLIENT_SECRET` are sufficient at the provider-authentication layer for this identity task as well; no second credential/provider contract is needed. However, the current IGDB implementation has only accepted the Steam External Game source path. Exact Epic/GOG External Game source rows and their `uid` semantics must be accepted against the live provider before production binding is enabled.

## Current sample

Canonical giveaway snapshot inspected: `data/production/giveaways/v1/current.json`, blob `a6f45abbd40d756d0421eb3492eb3e5ef8e8f510`, generated `2026-09-01T20:47:04.954912Z`, complete, with two accepted Epic offers.

### Breathedge

Classification: `no_safe_binding_with_current_data`

Evidence:

- giveaway key: `meta-v1:eedcf4e120faba87d9c6928a`;
- giveaway identity basis: `exact_normalized_title_and_publishers`;
- publisher evidence: `hypetrain digital`;
- exact Epic `source_product_id`: `08ae29e4f70a4b62aa055e383381aa82:8401414902e84f2cb9afa9142f051d32`;
- exact Epic offer identity is persisted, but no IGDB game id or Steam appid is persisted on the game/offer row.

The existing metadata key is therefore insufficient to attach Steam/canonical analysis without violating the title-as-proof boundary.

### Rival Stars Horse Racing : Desktop Edition

Classification: `no_safe_binding_with_current_data`

Evidence:

- giveaway key: `meta-v1:c76eb4d804a486978fc24b06`;
- giveaway identity basis: `exact_normalized_title_and_publishers`;
- publisher evidence: `prodigy design ltd`;
- exact Epic `source_product_id`: `f570d80aa4fe463ca53c4410d1c75e1e:8f1fcf01e32e4fd4b2ae0a9737992760`;
- exact Epic offer identity is persisted, but no IGDB game id or Steam appid is persisted on the game/offer row.

Again, the current data can group the giveaway safely enough for its own list, but it cannot prove the canonical semantic-analysis identity.

Bounded sample result: **0/2 exact existing bindings; 0/2 bindings safely derivable from currently persisted canonical cross-store data; 2/2 `no_safe_binding_with_current_data`.** No manual exception is justified for either title.

## Analysis reuse route

Normal cards already have one canonical analysis/render path. Giveaway cards should reuse its facts only after exact canonical identity is resolved; they must not copy deal/rank state.

Relevant current path:

- `scripts/build_final_visual_payload.py` blob `2c7b264233191e7304a37aba41bd7f96f4b71cea`;
- Taste artifacts are defined by `scripts/refine_visual_ranking.py` blob `757caca50fcfd167bd4eeded97f69b1b4d391eaa`:
  - `data/cache/taste_fit.json`;
  - `data/cache/taste_fit.entry_overlay.json`;
  - `data/production/pre_ai/taste_projection.json`;
  - `data/production/pre_ai/chatgpt_purchase_context.jsonl`.

Safe reuse semantics after exact Steam appid/family identity is known:

1. **Description** — use the same canonical `resolve_description_for_appids(...)` path and its existing Russian translation/provenance fields (`summary`, `description_status`, source locale/quality/appid/path/text). Do not copy text by title equality.
2. **Pros** — use the same `taste_subject_key -> effective_taste_entries() -> positive_evidence -> card_explanation_policy.positive_reasons(...)` path. The giveaway receives only the grounded player-facing explanation, not paid ranking effects.
3. **Confirmed cons** — use the same negative-evidence path and `visible_risk_payload(...)` readiness/provenance rule. Structural/derived heuristics may continue to exist for paid scoring, but they must not be exposed as giveaway facts unless the existing V4/grounded-negative visibility contract marks them grounded.
4. **Readiness** — exact identity does not imply analysis readiness. If there is no unique ready canonical description/Taste entry for the resolved game, the giveaway detail remains explicitly incomplete. No guessed pros/cons are generated.

The current giveaway visual handoff does not yet carry any analysis identity or semantic facts: `scripts/giveaway_visual_handoff.py` blob `ec49195af509934f058a1b3de880ae9152ee0f64` publishes only `game_key`, `title`, storefront offer identity, claim URL and deadline. That is the correct fail-closed current behavior.

## Missing prerequisite / identity gap

Exact blocker:

1. `data/production/giveaways/v1/current.json` currently persists provider product IDs plus a title/publisher-derived `meta-v1` grouping key, but no authoritative cross-store canonical id, IGDB game id, or exact Steam appid binding.
2. The existing IGDB integration that can serve as the canonical cross-store authority is still in `implemented_provisioning_required` state because GitHub Actions secrets `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` were not provisioned in the accepted implementation run. Ref: `reviews/worker_reports/duration-igdb-implement-01.md` blob `27fe858c1de0e39e87e657a100c9ca6d91605dce`.
3. Until provider connectivity is available, exact Epic/GOG External Game source identity/uid semantics cannot be acceptance-tested and therefore cannot safely be promoted into production identity bindings.

This is an identity blocker, not a UI blocker and not a reason to create another semantic worker.

## Production ownership

Smallest authorized production handoff:

- **Persisted identity:** extend each canonical giveaway game in `data/production/giveaways/v1/current.json` with a provenance-preserving analysis-identity block containing exact provider identity, authoritative IGDB game id, resolved exact Steam appid(s), resolution timestamp/status, and provider/source refs. The existing `meta-v1` key remains a giveaway grouping key only and must not become the semantic key.
- **Owner:** keep `scripts/giveaway_production.py` as the single writer of `data/production/giveaways/**`; it owns the provider IDs already present and should persist the resolved binding. Reuse the already-implemented IGDB client/provider contract rather than adding a parallel network/runtime contract.
- **Visual consumption:** `scripts/giveaway_visual_handoff.py` should pass only a fresh `resolved` canonical analysis identity plus explicit analysis readiness; `scripts/build_final_visual_payload.py` can then attach description/pros/grounded cons through the same precomputed canonical analysis path used by normal cards.
- **Missing/ambiguous/stale:** represent the analysis identity as unresolved/not-ready and keep description/pros/cons unavailable. Ambiguous or stale provider mappings must never fall back to title matching.
- **No second browser fetch:** the browser continues to consume only precomputed `data/current.json`; no Epic/GOG/IGDB request is added to browser code.
- **No second scheduler/queue:** run identity enrichment inside the existing GitHub-owned production workflow/provider route. If the resolved game lacks a ready Taste entry, only the existing semantic producer may eventually create it; the giveaway path itself must not own a new semantic queue.

Efficiency / reusable lesson: `provider-scoped giveaway grouping identity != canonical semantic-analysis identity`; ref `data/production/giveaways/v1/current.json` blob `a6f45abbd40d756d0421eb3492eb3e5ef8e8f510`.

## Status

`blocked`

The architecture is clear and the bounded sample is conclusive, but current production data cannot safely bind either active Epic giveaway to existing analysis until the already-selected IGDB authority is provisioned and its exact Epic/GOG External Game source mapping is accepted.

## Recommended next step

`IMPLEMENT after user secrets` — provision the already-required GitHub Actions secrets `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET`, then perform one bounded implementation that reuses the existing IGDB provider route to resolve exact Epic/GOG provider product identity -> IGDB game -> exact Steam appid, persists that binding in the canonical giveaway snapshot, and lets the existing visual/analysis path consume only resolved+ready canonical facts. No title/fuzzy fallback, manual mapping, new queue, second semantic runtime, or browser fetch.

## Exact refs

- Task: `WORKER_TASK_GIVEAWAY_ANALYSIS_IDENTITY_RECON_01.md` blob `3743061a2d0c339bccba7ab22a8c2faa6633e35d`
- Current giveaway snapshot: `data/production/giveaways/v1/current.json` blob `a6f45abbd40d756d0421eb3492eb3e5ef8e8f510`
- Giveaway visual handoff: `scripts/giveaway_visual_handoff.py` blob `ec49195af509934f058a1b3de880ae9152ee0f64`
- Final visual/analysis attachment path: `scripts/build_final_visual_payload.py` blob `2c7b264233191e7304a37aba41bd7f96f4b71cea`
- Taste artifact path definitions: `scripts/refine_visual_ranking.py` blob `757caca50fcfd167bd4eeded97f69b1b4d391eaa`
- Existing IGDB exact Steam identity implementation: `scripts/duration_enrichment.py` blob `a1a76118f7c2bae036ccc8be9adfa10ef0594abd`
- IGDB provisioning/blocker report: `reviews/worker_reports/duration-igdb-implement-01.md` blob `27fe858c1de0e39e87e657a100c9ca6d91605dce`
- Steam canonical app identity guard: `.github/workflows/patch-app-identity.yml` blob `6bc349641eb64dac3d6319b2a32219f34420415e`
