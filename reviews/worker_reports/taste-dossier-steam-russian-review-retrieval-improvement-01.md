# Taste dossier Steam Russian review retrieval improvement 01 — durable report

## 1. Task / repo / mode

- Task: `taste-dossier-steam-russian-review-retrieval-improvement-01`.
- Repository: `kentrap2011-hub/steam-kz-deals-2`.
- Base/source of truth: `main`.
- Mode: `IMPLEMENT / ACTIVATE / VALIDATE`.
- Other repositories were not read, searched, changed, or used.
- No production dossier candidate was published by this task.
- Scheduled Task `Run now` was not used.

## 2. Architecture preflight and actual retrieval owner

Architecture preflight passed before the first implementation write.

1. **Current retrieval owner:** Russian/player-feedback web retrieval is owned by the existing Scheduled ChatGPT runtime data plane under `config/execution_ownership_contract.json`. GitHub owns scope, immutable group plan, compatibility binding, validation, persistence, retry/recovery interpretation and completeness.
2. **Repo-owned runtime lever:** `config/taste_steam_review_dossier_worker_prompt.md` is the canonical worker-facing retrieval instruction actually consumed through the GitHub-generated worker index/group binding. `current_worker_contract_binding()` binds both the canonical prompt revision and the SHA-256 of the full prompt.
3. **Scheduled-runtime exercisability:** the selected improvement uses ordinary search/open retrieval already available to the Scheduled worker; it requires no local shell/Python prerequisite, unsupported Steam API, browser automation, proxy or external service.
4. **Ownership preservation:** semantic/public-web research remains in Scheduled ChatGPT; GitHub remains control plane and strict acceptance authority.
5. **No new stage:** no recurring service, scheduler, queue, retry loop, backlog manager, website quota or checkpoint model was added.

## 3. Accepted Cthulhu diagnosis

The accepted read-only diagnosis was preserved:

- exact target: `Cthulhu Saves the World`, appid `107310`;
- exact-product Russian Steam review existence is proven;
- a concrete Russian review was previously readable only through profile-scoped context;
- no safe stable item locator or inspected non-profile parent was available in that diagnostic;
- the active evidence/privacy/provenance model was internally consistent;
- blocker classification: `retrieval_limitation`;
- no evidence-contract weakening was justified.

## 4. Repo-owned lever selected

The implementation changes the **Scheduled-worker retrieval strategy**, not the external web transport.

Selected lever:

- add a worker-facing adaptive **search-indexed exact-app collection recovery** route for Steam when a direct Store/Community language-filter family is aggregate-only, dynamically unavailable or otherwise fails to expose concrete cards;
- keep neutral stable review/recommendation identity first;
- if no safe neutral item locator is exposed, allow only the already-accepted transient-author fallback when a concrete Russian/mixed card is actually visible on the returned non-profile exact-app collection parent;
- treat profile-scoped hits only as discovery signals;
- stop repeating materially equivalent inaccessible endpoint-family variants;
- preserve source-agnostic diversification if the safe Steam recovery path still fails.

The only evidence-contract-file change is the canonical `worker_prompt_revision` metadata bump required by the existing content-complete prompt binding. `contract_revision`, schema revision and evidence semantics were not changed.

## 5. Routes tested and why

Bounded investigation used the same ordinary web/search/open class available to the Scheduled worker.

| Route | Result | Why it matters |
|---|---|---|
| Exact-app Steam Community review collection | exact app was reachable and concrete cards could be exposed, but the inspected ordinary collection result did not solve the Russian gate | confirms exact-app collection access but not sufficient Russian retrieval |
| Direct Russian language-filter URL family | current transport did not reliably expose the needed card representation | establishes a family that should not consume repeated equivalent retries |
| Profile-scoped Russian Steam review lead | concrete Russian content can exist and be readable, but the profile context is unsafe to persist and cannot be rebound to an uninspected collection | remains discovery signal only |
| Search-indexed exact-app Steam Store collection | **successful**: exact appid `107310` Store representation exposed the Russian review population and concrete individual Russian review cards on a non-profile exact-product parent | supplies the already-legal transient-author fallback prerequisites |
| Materially different public player-feedback surfaces | retained as the existing source-agnostic fallback path when safe Steam recovery fails | no Steam-only requirement introduced |

Successful safe parent used for the live proof:

`https://store.steampowered.com/app/107310/Cthulhu_Saves_the_World/?cc=br&l=russian`

The locale parameters are treated only as retrieval/routing hints. They are not language evidence and do not create a mention.

## 6. Exact implementation

PR #64 implemented the smallest repo-owned change.

### `config/taste_steam_review_dossier_worker_prompt.md`

Added `Exact-app Steam Russian card recovery in the existing web transport`:

- exact title + exact appid + Russian player-review terms;
- bounded search-indexed Store/Community exact-app recovery;
- stable neutral locator preference;
- concrete-card requirement for fallback;
- profile hit cannot be persisted or rebound;
- localized URL parameters are retrieval hints only;
- exact appid remains fail-closed;
- inaccessible endpoint family is not retried through materially equivalent variants;
- recovery remains inside existing 8/16 ceilings and is not a fixed Steam lane or website quota.

### Prompt binding metadata

`config/taste_steam_review_dossier_web_evidence_contract.json`:

- `contract_revision` unchanged: `contract-contradictions-fix-2026-09-18`;
- `worker_prompt_revision` advanced to `web-evidence-v2-steam-russian-review-retrieval-improvement-v1`.

No evidence-rule field was relaxed or redefined.

### Regressions

Added RETRIEVE-RU-01..06 assertions to the already-executed `scripts/test_taste_steam_review_dossier_semantic_consistency.py` suite and updated two exact prompt-revision assertions:

- `scripts/test_taste_steam_review_dossier_strict_recovery.py`;
- `scripts/test_taste_dossier_contract_contradictions_fix.py`.

The canonical strict validator and dossier schema were not changed.

## 7. Cthulhu proof-of-retrieval ledger

Clean post-implementation proof replay:

- target: `Cthulhu Saves the World`;
- exact appid: `107310`;
- query form: exact title + exact appid path + Russian user-review terms, constrained to Steam Store;
- proof replay budget: **1 web-search query / 1 returned source representation inspected**;
- returned parent: non-profile exact-product Steam Store app page;
- exact product title and appid: visible and consistent;
- Russian review population: visible as aggregate discovery metadata only;
- concrete individual Russian review card: **visibly inspected in the returned Store representation**;
- item language: Russian from the concrete item content, not from `l=russian`;
- transient author/account distinction: visible enough for same-product dedupe;
- neutral stable recommendation/item locator: not required for this proof and not claimed;
- persisted profile/author identity: none.

No raw review body, username, display name, SteamID/account id, vanity id or profile URL is reproduced in this report.

## 8. PROOF-A or PROOF-B result

**PROOF-B — PASS.**

The current web environment demonstrated all required fallback facts:

- exact product: yes, appid `107310`;
- concrete Russian/mixed review card actually inspected: yes;
- parent surface: non-profile exact-product Steam Store collection;
- transient author distinguishable for same-product dedupe: yes;
- author/profile identity persisted: no;
- valid current fallback parent: yes;
- compatible serialization under current model: `source-NNN` parent + `fallback-NNN` child, no child URL/`public_ref`, with record language derived from the actual card.

PROOF-A was not needed because PROOF-B satisfies the task acceptance rule.

## 9. Confirmation no profile/author identity persists

Confirmed.

The implementation keeps all existing privacy rules:

- `profile_scoped_urls_allowed=false`;
- profile-scoped hits are discovery signals only;
- transient author/account/profile identity may be observed only in worker memory for same-product dedupe;
- no author identity, profile URL, direct hash or predictable author pseudonym is persisted;
- fallback records remain opaque dossier-local `fallback-NNN`;
- source ids remain author-independent dossier-local `source-NNN`.

The live proof ledger and this report intentionally omit the observed author identity.

## 10. Confirmation evidence contract was not weakened

Confirmed.

Unchanged safeguards include:

- aggregate Store review/language counts remain existence/discovery metadata only;
- a Store app page is not itself a feedback record or mention;
- `l=russian` or other locale rendering is not player-feedback language evidence;
- stable locator remains preferred;
- fallback requires a concrete inspected item on a valid non-profile exact-product collection parent;
- profile-scoped provenance remains forbidden;
- exact appid and physical parent/item rules remain fail-closed;
- fallback-only recurrence remains capped at `limited`;
- language projection remains bound-record-derived;
- Russian unresolved states remain fail-closed for complete dossier publication.

No strict-validator weakening was made.

## 11. Generalization beyond Cthulhu

The production prompt contains no appid-`107310` special case.

The new route applies generically when:

- exact-product Russian existence is proven;
- ordinary/direct Steam language-filter retrieval initially yields only aggregate/list data, inaccessible dynamic representation, non-Russian cards, or an unsafe profile-scoped Russian hit;
- remaining bounded budget can use indexed non-profile exact-app Store/Community collection variants.

If that transport recovery still does not yield a usable item, the already-active source-agnostic diversification rule continues across materially different public player-feedback surfaces.

## 12. Production budget behavior

Production hard ceilings remain unchanged:

- maximum `8` web-search queries per game;
- maximum `16` opened/read source pages per game.

The new route is adaptive, not a target and not a website quota. It explicitly prevents repeated materially equivalent requests to an endpoint family already proven inaccessible in the current invocation.

The clean Cthulhu proof replay resolved PROOF-B in **1/8 search queries** and **1/16 inspected source representations**.

## 13. RETRIEVE-RU-01..08 results

- **RETRIEVE-RU-01 — stable route preferred:** PASS. Prompt and machine identity order keep `stable_locator` before `transient_author_deduped`.
- **RETRIEVE-RU-02 — safe collection fallback:** PASS. Prompt requires an actually visible concrete Russian/mixed card on the returned non-profile exact-app collection before fallback.
- **RETRIEVE-RU-03 — profile result not persisted:** PASS. Profile hit is discovery-only; no persistence or host/title/appid re-parenting is allowed.
- **RETRIEVE-RU-04 — aggregate remains non-evidence:** PASS. Aggregate Russian count and locale rendering remain discovery metadata only.
- **RETRIEVE-RU-05 — exact appid preserved:** PASS. Exact dossier appid is mandatory; base/DLC/edition/sequel/remake/remaster substitution remains forbidden.
- **RETRIEVE-RU-06 — bounded adaptive search:** PASS. 8/16 ceilings unchanged; no fixed website quota or unlimited retry behavior; inaccessible equivalent endpoint-family retries are deprioritized.
- **RETRIEVE-RU-07 — current evidence guards remain green:** PASS. Existing Store-card, transient-author, contradiction, language, Russian gate, semantic consistency, package identity, buffered/recovery and ownership suites passed in CI.
- **RETRIEVE-RU-08 — Cthulhu live proof:** PASS via PROOF-B in the current web environment.

## 14. Existing guard suite results

PR focused validation:

- workflow: `Validate buffered Steam review dossier runtime`;
- run: `35394492496` / #86;
- job: `105760111426`;
- conclusion: **success**.

Green steps included:

- compile/focused regressions;
- execution ownership;
- daily snapshot;
- buffered submission;
- same-day preservation;
- strict recovery;
- prepublication parity;
- contract gaps;
- language binding;
- semantic consistency including RETRIEVE-RU-01..06;
- transient author fallback;
- Steam Store review-card parent;
- contract contradictions closeout;
- package identity;
- Story DLC scope;
- parallel candidate / maximal-contiguous-prefix validation.

Backlog-disposition validation:

- run: `35394492546` / #770;
- job: `105760120515`;
- conclusion: **success**.

## 15. PR / CI / merge refs

- implementation PR: **#64** — `Taste dossier: improve Steam Russian review retrieval`;
- PR head at validation: `b77837b5a4d5b142c91edeba5a096de90586fceb`;
- dossier CI run: `35394492496`, job `105760111426`, success;
- backlog-disposition run: `35394492546`, job `105760120515`, success;
- squash merge: `6ab36a6d9343a9670882bc2946b04dc5a58f7147`.

## 16. Activation / binding / snapshot state

Normal GitHub-owned push-to-`main` activation completed and produced atomic pre-AI commit:

- activation commit: `57243ab6da5acfeb6dc20070d74b7e6f1b61e55d`;
- snapshot id: `ec6ff4015ad01a9dcaaa2be845230cf04790c1444b99d5a1c31dad39047de872`;
- prepared: `702`;
- completed: `0`;
- remaining: `702`;
- canonical expected sequence: `1`;
- group count: `234`;
- group size: `3`;
- exact current expected group `g000001`:
  1. `1000010` — Crown Trick;
  2. `1000360` — Hellish Quart;
  3. `1003590` — Tetris® Effect: Connected.
- evidence contract revision: `contract-contradictions-fix-2026-09-18` (unchanged);
- worker schema revision: `contract-contradictions-fix-2026-09-18` (unchanged);
- worker prompt revision: `web-evidence-v2-steam-russian-review-retrieval-improvement-v1`;
- worker prompt SHA-256: `d086a58bc69c3b7c69f2033e30eec09589799cbfd2c02e514deddafe8ca3c912`.

Scope delta: **0 prepared items**. The prior snapshot also had `702` prepared items. The fresh snapshot resets compatible completion to `0` because the content-complete prompt binding changed; this is normal GitHub-owned activation/recovery behavior, not a manual progress repair or scope change.

No candidate inbox, canonical progress, expected group or buffered artifact was manually edited.

## 17. Scheduled Task Run now/settings confirmation

- Scheduled Task `Run now`: **not launched**.
- Scheduled Task settings: **unchanged**.
- No second Scheduled Task or producer was created.

## 18. Unresolved

No task-blocking unresolved item remains.

A neutral stable locator was not required to close the Cthulhu acceptance proof because the current environment supplied a fully legal PROOF-B fallback shape. Stable locator remains preferred whenever reachable.

## 19. Status

`complete_ready_for_live_acceptance`

All completion conditions are satisfied:

- repo-owned retrieval improvement implemented and activated;
- RETRIEVE-RU-01..07 green;
- RETRIEVE-RU-08 proven through current live web tooling;
- no evidence/privacy/provenance rule weakened.

## 20. Exactly one recommended next step

Return to Director for **one clean production live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against snapshot `ec6ff4015ad01a9dcaaa2be845230cf04790c1444b99d5a1c31dad39047de872`**, with no pre-acceptance production candidate or manual progress repair from this chat.

## 21. Efficiency / reusable lesson

For a proven exact-app Russian Steam population, an inaccessible direct language-filter endpoint should not trigger repeated equivalent retries or a privacy relaxation. A bounded search-indexed exact-app Store/Community recovery can expose the same collection at concrete-card level while retaining a safe non-profile parent. The efficient order is: stable neutral item identity first; otherwise inspected safe collection fallback; then materially different player-feedback surfaces if needed.
