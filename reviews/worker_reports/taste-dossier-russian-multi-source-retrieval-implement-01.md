# Taste dossier Russian multi-source retrieval implement 01

## 1. Task / repo / mode

- Task: `taste-dossier-russian-multi-source-retrieval-implement-01`
- Worker task: `WORKER_TASK_TASTE_DOSSIER_RUSSIAN_MULTI_SOURCE_RETRIEVAL_IMPLEMENT_01.md`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Base/source of truth: `main`
- Mode completed: IMPLEMENT / ACTIVATE / VALIDATE
- Scheduled Task `Run now`: **not launched**
- Scheduled Task settings: **unchanged**
- Other repositories: **not read, searched, changed, or used**

## 2. Architecture preflight

Before the first write, the architecture preflight from `CHAT_CONTEXT.md` was reconciled against `config/execution_ownership_contract.json`, the dossier control-plane contract, and the active evidence contract:

- GitHub/GitHub Actions remains the control plane for exact scope, immutable group plan, compatibility binding, validation, persistence, recovery, canonical progress and completeness.
- Scheduled ChatGPT remains the bounded semantic/data worker responsible for ordinary multi-source player-feedback research and neutral synthesis.
- This task changes only the worker-facing Russian retrieval strategy inside the already-authorized bounded multi-source evidence mode.
- No GitHub control-plane responsibility moved to Scheduled ChatGPT or the interactive chat.
- No new recurring stage, scheduler, queue, retry/healing loop, checkpoint model, crawler, backlog manager or production quota was created.
- Group size remains `3`.
- Hard per-game bounds remain <=8 web-search queries and <=16 opened/read source pages.

## 3. Reconciled prior live evidence

The prior bounded discovery audit and Russian existence/retrieval-gate implementation were read in full. They were reconciled with the authoritative manual live result supplied for the existing Scheduled Task.

The observed live state was:

- snapshot `093952f414cc1020388559e4f390593d921df2b96fd64df831450feec3258296`;
- expected group `g000001`;
- exact-product Russian player-feedback existence was proven for Baldur's Gate 3 - Digital Deluxe Edition DLC and Hellish Quart via exact Steam appid surfaces;
- no contract-usable attributable item-level Russian/mixed record was obtained for those products in that invocation;
- the existing `existence_established_retrieval_unresolved` gate therefore correctly stopped complete group publication.

The gate itself was not the defect. The proven problem was the retrieval strategy after existence proof: the worker could spend its bounded effort around Steam/Steam-like aggregate or list surfaces instead of materially diversifying across public player-feedback surfaces.

## 4. Exact multi-source retrieval rule

The active worker policy now requires an explicit **retrieval diversification phase** when all of these are true:

1. reliable exact-product Russian player-feedback existence is established;
2. no contract-usable Russian/mixed attributable item-level player-feedback record has yet been obtained;
3. bounded search/page budget remains.

If the first reasonable retrieval surface yields only aggregate/list/index/non-item evidence or otherwise no usable item, the worker may not immediately finish as `existence_established_retrieval_unresolved` while at least one materially different public player-feedback surface class is reasonably discoverable and budget remains.

It must try at least one materially different surface class. If that diversified step still does not resolve retrieval and budget remains, it must continue adaptively toward the most promising reasonably discoverable distinct surface classes until:

- a usable exact-product Russian/mixed item is found;
- a hard bound is reached; or
- no reasonably discoverable distinct player-feedback surface class remains.

Materially different means a different public player-feedback mechanism/community context, not merely another query wording, locale, aggregate/list page or same-surface variant.

## 5. Why Steam is an existence/source option, not a required retrieval source

Steam may:

- prove exact-product Russian player-feedback existence through a reliable exact-appid player-activity signal;
- provide a usable Steam Community/review item when one is obtainable;
- be one of several ordinary player-feedback retrieval surfaces.

Steam is **not** required to supply the usable Russian item after existence is proven. The retrieval obligation is source-agnostic.

The worker may use, when exact-product relevance is actually supported:

- Steam Community/review item surfaces;
- Reddit exact-product threads/comments;
- public Russian-language gaming forums;
- public community discussions/comment threads;
- public store user-review item surfaces;
- Pikabu or analogous public user-generated discussion surfaces;
- other credible public player-feedback surfaces.

There is no fixed named-site quota and no requirement to visit every listed class.

## 6. Search-budget diversification

The existing hard ceilings are unchanged:

- <=8 web-search queries per game;
- <=16 opened/read source pages per game.

Within those ceilings, budget allocation is now explicit:

- after existence proof, item-level discovery takes priority over repeated aggregate/list lookups;
- repeated same-domain/same-surface aggregate/list/index query variants have diminishing return;
- when a first reasonable surface fails and a distinct player-feedback surface is reasonably discoverable, remaining budget must diversify rather than continue consuming budget on the same surface;
- after the first diversified attempt, the worker continues adaptively while useful budget and discoverable distinct surface classes remain.

The ceilings remain safety bounds, not targets and not website quotas.

## 7. Machine contract / prompt changes

Implementation PR #49 changed the task-scoped evidence behavior without creating a second validator truth source.

`config/taste_steam_review_dossier_web_evidence_contract.json`:
- evidence contract revision: `russian-multi-source-retrieval-2026-09-18`;
- worker prompt revision: `web-evidence-v2-russian-multi-source-retrieval-v1`;
- added machine-readable `adaptive_research.russian_discovery.retrieval_diversification` invariants for:
  - phase trigger;
  - source-agnostic goal;
  - example surface classes;
  - mandatory materially different second surface when reasonably discoverable and budget remains;
  - continued adaptive diversification;
  - diminishing-return same-surface behavior;
  - no professional/editorial substitution;
  - no Steam requirement;
  - no fixed website quota or visit-all requirement;
  - no premature unresolved terminal state while a distinct surface remains reasonably discoverable within budget;
  - preservation of exact-product identity.

`config/taste_steam_review_dossier_worker_prompt.md`:
- added `Russian retrieval diversification after existence proof`;
- makes the source-agnostic obligation explicit in worker-facing prose;
- explicitly distinguishes a materially different feedback surface from another same-surface query/list/locale variant;
- preserves the existing bounded stopping and fail-closed behavior.

The dossier schema was not changed because the existing `russian_attempt` states already represent the required result states. No new state was necessary.

## 8. Strict validator impact

The canonical strict validator was **not weakened and did not need implementation changes**.

Existing `scripts/taste_steam_review_dossier_strict.py` already:

- accepts ordinary allowed non-Steam public player-feedback source types when compact provenance and all other invariants are valid;
- does not require a Steam item-level record;
- rejects `existence_established_retrieval_unresolved` and `existence_established_access_unresolved` as complete-dossier states;
- rejects professional/context sources masquerading as player feedback;
- preserves item-level provenance, language binding, temporal coherence, recurrence/count, summary and conflict guards;
- preserves the exact Steam appid guard when a Steam player-feedback URL exposes `/app/{appid}/`.

Therefore adaptive retrieval strategy remains worker-facing, while the strict validator remains the single GitHub-side structural/evidence consistency truth source.

## 9. RUS-MS-01..07 regressions

Focused deterministic regressions were added in `scripts/test_taste_steam_review_dossier_semantic_consistency.py`.

- **RUS-MS-01 — Steam existence -> non-Steam usable Russian item:** a Steam exact-product existence/context signal can coexist with a usable Russian Reddit item; the completed `found_and_used` dossier validates and Steam is not required as the item-level source.
- **RUS-MS-02 — do not stop after one failed surface:** machine policy and worker prompt prohibit premature unresolved termination when budget remains and a materially different reasonable surface is discoverable.
- **RUS-MS-03 — diversified search still unresolved:** fixture logic represents at least two materially distinct surface classes; if no usable item exists after diversification, `existence_established_retrieval_unresolved` remains correct and strict validation still rejects a complete dossier.
- **RUS-MS-04 — non-Steam provenance accepted:** a valid exact-product Russian forum item satisfies ordinary compact provenance and validates with no Russian Steam item-level record.
- **RUS-MS-05 — journalism does not satisfy gate:** Russian `professional_context` cannot create player feedback or make `found_and_used` valid.
- **RUS-MS-06 — identity remains strict:** Steam base-game appid `1086940` remains invalid for exact BG3 Digital Deluxe DLC appid `2378500`.
- **RUS-MS-07 — no fixed website quota:** machine contract and prompt explicitly keep adaptive diversification, no visit-all requirement, no Steam retrieval requirement, and the unchanged 8/16 hard ceilings.

Final focused PR run:
- workflow: `Validate buffered Steam review dossier runtime`;
- run: `35352803497` / #71;
- job: `105624742624`;
- result: **success**;
- compile: success;
- execution ownership: success;
- daily snapshot: success;
- buffered submission: success;
- same-day preservation: success;
- strict recovery: success;
- prepublication parity: success;
- contract gaps: success;
- language binding: success;
- semantic consistency including RUS-MS-01..07: success;
- package identity: success;
- parallel candidate / maximal-contiguous-prefix validation: success.

Two earlier PR runs found test-maintenance issues rather than semantic/runtime defects:
- #69 exposed a stale hard-coded prior `worker_prompt_revision`;
- #70 exposed a Markdown-sensitive substring assertion in the new RUS-MS-07 test.
Both were corrected before merge; no evidence rule or strict validator was weakened.

## 10. Exact identity preservation

Multi-source diversification does not relax work identity.

In particular:

- base-game feedback does not become BG3 Digital Deluxe DLC feedback merely because it is Russian or mentions Baldur's Gate 3;
- exact descriptor title/appid/year safeguards remain active;
- where a Steam player-feedback URL exposes `/app/{appid}/`, the appid must equal the exact dossier appid;
- non-Steam feedback still must establish exact-product relevance under the active identity contract;
- ambiguous exact-product binding remains fail-closed.

## 11. Journalism/context does not satisfy player-feedback gate

Professional/editorial/journalistic Russian content remains `professional_context` only.

It may help with context or relevance where otherwise allowed, but it:

- is not a player-feedback record;
- cannot create a player mention or recurrence;
- cannot satisfy `found_and_used`;
- is not counted as a materially different **player-feedback** surface for satisfying the diversification obligation.

RUS-MS-05 covers this deterministically.

## 12. PR / CI / merge refs

Implementation:
- PR: **#49** — `Taste dossier: diversify Russian retrieval across public player-feedback surfaces`;
- merged commit: `2d098c74889ddd30990f171fea2d1e8a0b09b6ce`;
- final focused green run: `35352803497` / #71;
- focused job: `105624742624`.

Normal GitHub-owned activation:
- workflow: `Build pre-AI deterministic payload`;
- run: `35352856938` / #133;
- result: **success**;
- atomic pre-AI commit: `f805fc1628a9e2eed8c989a3195ea0f903951509`.

No Scheduled Task `Run now` was involved in activation.

## 13. Activation / binding / snapshot state

The normal push-to-`main` activation rebuilt the incompatible content-complete binding through the canonical GitHub-owned pre-AI path.

Current canonical dossier state after activation:

- snapshot id: `cc99c7e33c2094de955c14c2fdfcf8a39eb9836f22afb9313ac01ff2fc4ecc86`;
- prepared: `732`;
- completed: `0`;
- remaining: `732`;
- canonical expected sequence: `1` / `g000001`;
- group count: `244`;
- group size: `3`;
- full backlog complete: `false`;
- evidence contract revision: `russian-multi-source-retrieval-2026-09-18`;
- worker schema revision: `russian-existence-retrieval-gate-2026-09-18`;
- worker prompt revision: `web-evidence-v2-russian-multi-source-retrieval-v1`.

Current `g000001` remains exact ordered scope:
1. `2378500` — Baldur's Gate 3 - Digital Deluxe Edition DLC
2. `1000010` — Crown Trick
3. `1000360` — Hellish Quart

Its descriptor binding exactly matches the active worker index binding.

Previous snapshot:
- `093952f414cc1020388559e4f390593d921df2b96fd64df831450feec3258296`.

Because the evidence contract/prompt content-complete binding changed incompatibly, the old snapshot was not rebound or repaired. The normal GitHub-owned activation generated `cc99c7...` and replaced the active worker projection; old-snapshot artifacts are stale/inert under the canonical compatibility/recovery behavior. No queue/cache/progress/receipt/candidate was manually repaired or rebound.

## 14. PROJECT_DECISIONS ref

`PROJECT_DECISIONS.md`, adjacent to **TASTE-008 — Russian existence proof creates an item-level retrieval gate**, now records the source-agnostic retrieval rationale:

- existence proof creates a retrieval obligation;
- the obligation is source-agnostic;
- Steam aggregate may prove existence without making Steam the mandatory usable-record source;
- after one failed surface, bounded adaptive diversification across materially different public player-feedback surface classes is required while budget remains and such surfaces are reasonably discoverable;
- no fixed website quota or visit-all rule;
- exact-product identity remains strict;
- professional/editorial material remains context-only.

The corresponding operational route was also added to `PROJECT_ROUTES.md`.

## 15. Scheduled Task confirmation

- Scheduled Task `Run now`: **not launched**.
- Scheduled Task settings: **not changed**.
- No second Scheduled Task, producer, crawler or recurring stage was created.

## 16. Unresolved

None within this IMPLEMENT / ACTIVATE / VALIDATE task.

Live behavior under the newly activated binding is intentionally reserved for the separate acceptance step required by the task.

## 17. Status

`complete_ready_for_live_acceptance`

## 18. Recommended next step

Exactly one next step:

Run one separate live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against the current compatible snapshot `cc99c7e33c2094de955c14c2fdfcf8a39eb9836f22afb9313ac01ff2fc4ecc86`, with the Scheduled Task UI result supplied manually by the user. Do not run Proactive Auditor before that clean live acceptance.

## 19. Efficiency / reusable lesson

The implementation stayed narrow because the existing strict validator already supported non-Steam public player-feedback provenance; only worker generation policy, machine-readable retrieval invariants, rationale/route and deterministic regressions required changes.

Two avoidable CI detours were exposed:
- hard-coding a previous prompt revision in an alignment test creates maintenance-only failures on deliberate content-binding changes;
- Markdown-sensitive exact prose assertions are brittle.

Within this task, the prompt-revision alignment was updated and the new no-fixed-quota test was made markup-safe. The reusable rule is to test machine invariants structurally and use prose checks only for stable semantic anchors, while keeping strict-validation truth centralized rather than creating a second retrieval-trace validator.
