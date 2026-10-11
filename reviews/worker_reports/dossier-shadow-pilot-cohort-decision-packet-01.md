# Worker report — Dossier 18-game prospective cohort decision packet (INERT)

**Task:** `WORKER_TASK_DOSSIER_SHADOW_PILOT_COHORT_DECISION_PACKET_01.md` · **worker:** НОВЫЙ ЧАТ — ЧАТ 1 · **repo/base:** `kentrap2011-hub/steam-kz-deals-2` / `main` · **mode:** historical metadata only, synthetic tests, PR-only CI.  
**Decision status: `NOT_READY_FOR_APPROVAL`.** This is a prospective, exact **provisional preview**, not an approved pilot, selected worker manifest, frozen Research request, active trial, or source-quality assessment.

## Executive decision card (proposal, NOT approval)

| Gate | Exact status |
| --- | --- |
| Historic source | commit `95a4bf4990a60082ecb3302da5bc7f23b618d93e`; original manifest blob `ef40fc186aabc79dfd24c72864dbe43817a56039`; audit blob `8dbf4437d7ba439942f58a6f36d89d6a7ddeec7b` |
| Accepted proof | PR #201 accepted report Git blob `d10041652593024c9fcf7772580d0a8ec9c5f12d`; 20/20 historical original groups/60 games strictly Git-local eligible, independently verified GitHub writer push provenance; no external review truth proof |
| Objective | Later **read-only side-by-side calibration** of frozen Research → Assembly → strict V2 versus same exact-work one-stage historically writer-accepted Dossier, with independent player-source authenticity, material-negative preservation and usefulness review |
| Suggested calibration size | 6 indivisible original Dossier groups × 3 games = **18 exact distinct AppIDs**, provisional only; not an execution cap, rate quota or production plan |
| Sampling proposal | `dossier-shadow-6x3-calibration-proposal-v1`; 3/6 with any legacy original-work-year binding <2015 + 3/14 without; SHA-256 hash sort inside each binding stratum, restore original sequence order |
| **Provisional group sequences** | **3, 8, 13, 15, 18, 20** (18 game identities in next section), `sample_proposed=true` |
| Accepted baseline status | `baseline_integrity_verified=true` based on pre-existing #201 strict historical proof; **not** independent source/year reality check |
| Execution and quality | `pilot_authorized=false`; `semantic_quality_not_evaluated=true`; `quality_verified=false`; `canonical_readiness=false`; `deep_readiness=false` |
| Approval gate | **`NOT_READY_FOR_APPROVAL`**: missing trustworthy pre-output source-diversity/negative/Russian/temporal strata for all 20; exact product/year independent review, reviewers and thresholds have not been approved |
| Production impact/rollback | None. Existing one-stage Dossier, Fast, Deep, cache, scheduler, website, live manifests and GitHub control-plane remain unchanged; zero production cutover to roll back |

**Director/user decision now:** either authorize a **separate read-only evidence-provenance and fair-strata assessment for all 20** before any cohort authorization, or explicitly revise the prospective sampling policy/scale. Do **not** approve semantic execution on these six merely because the deterministic preview exists. Any later trial requires explicit user approval of the exact groups, independent source-evidence rules, reviewers, stop criteria, owner-controlled frozen Research/Assembly path and corresponding separate GitHub authorization.

## Reproducibility, inputs, sample method and fairness

Run in a read-only full-history Git checkout with the exact PR #201 historical commit present; do not run the semantic workers. The only active program is `scripts/dossier_shadow_pilot_cohort_preview.py`. It accepts the **three caller-pinned exact SHA arguments**, and refuses any different work/audit/source pin because #201 has proven only that exact historical frame. It checks the frozen source Git manifest/audit blobs, the accepted #201 report blob, all original group-progress/plan positions, the complete 20-row independently writer-proven acceptance table, its writer commit and Actions run, exactly three original ordered AppIDs/titles per group, and each historical writer cache blob against the immutable pinned HEAD counterpart. Only the `game_identity` year/title metadata is parsed from cache; raw review text/player/source data are not emitted. This is **reconciliation to the already proven strict receipt**, not a new strict verifier or claim of independent GitHub Actions re-verification.

The preview serializes **all 20 groups × 3 exact identities including original-work-year *binding* and baseline Git blob SHA**, historical writer commit, Actions run, immutable group hash, seed-derived selection SHA-256, stratum and inclusion decision into a local metadata-only **OS temp** JSON. Nothing is written to tracked Git/production or sent to a worker. GitHub PR-only CI uploads this limited safe metadata output for 7 days. The code does not import/call semantic stages, quality evaluator, site builder or runtime scheduler. It keeps original sequence ordering of the **entire** accepted frame and the final selected six. Nonselected groups are never substituted after seeing future results.

**Exact hash material for each entire original group:**

`SHA256(UTF8("dossier-shadow-6x3-calibration-proposal-v1|95a4bf4990a60082ecb3302da5bc7f23b618d93e|ef40fc186aabc79dfd24c72864dbe43817a56039|4d7be57c9a1a90482d948270ab034c49eca3dd84102d28fc67b6fbc1d33f8239|<sequence>|<original_group_sha256>"))`

Sort ascending within each of the two fixed year-*binding* strata; select the first three of each; then present the six by original sequence. Tie fallback = original sequence (cryptographic tie practically irrelevant). Fixed seed cannot be chosen after comparing outputs. This implements **targeted over-sampling** of older-work-year *bindings*: inclusion fractions **3/6=50%** versus **3/14≈21.4%**, so the pilot is **not representative** of the 20 groups or a random estimate of quality prevalence. Three-per-stratum is a suggested calibration design, not proven balanced across Russian review coverage, source quality, negativity or gaps. Those dimensions are unmeasured and could invalidate/alter this provisional selection. Do not resample to convenient titles or winners.

**Version drift already observed:** historical pin is not moving `main`. At packet creation, `main` was `ea53750b72fe31b61244bee085153c232f844dfa` and its manifest Git blob was `b8389f1cc30bf1787da4448abadcc15f2898448a`, audit blob `44e431a89732f4f7dfd31160d83334e501b19ff5` (both different from pinned audit source). This **does not negate historical #201 eligibility** and does **not** authorize replacement by current groups. The preview prints `head_moved_from_pin`, `work_blob_differs`, `audit_blob_differs`, or `comparison_status=unknown` if comparison is unavailable; new run must report these explicitly.

### Exact six provisional original three-game groups

These are **original-work-year bindings in the existing accepted Dossiers**, **not** independently corroborated real release years. In particular, original-vs-storefront time and version/remaster/DLC truth remain unknown until independently checked. Cache Git SHA and full writer commit are included in generated metadata JSON for every game/group; omitted from this table only for readability.

| Original group | AppID | Exact original-work title | Existing original-work-year binding |
| ---: | ---: | --- | ---: |
| **3** | 1508750 | Xuan-Yuan Sword: Dance of the Maple Leaves | 1995 |
| 3 | 1517180 | Mindcop | 2024 |
| 3 | 1533420 | Neon White | 2022 |
| **8** | 1590230 | Tyrion Cuthbert: Attorney of the Arcane | 2023 |
| 8 | 1599600 | PlateUp! | 2022 |
| 8 | 1607130 | Lust Theory - Season 1 | 2022 |
| **13** | 1849000 | SEX with HITLER | 2022 |
| 13 | 1857090 | Norland | 2024 |
| 13 | 1868140 | DAVE THE DIVER | 2023 |
| **15** | 1999170 | Insect Swarm | 2024 |
| 15 | 1999360 | Placid Plastic Duck Simulator | 2022 |
| 15 | 2009010 | My Furry Protogen 🐾 | 2023 |
| **18** | 206420 | Saints Row IV: Re-Elected | 2013 |
| 18 | 2067050 | Squirrel with a Gun | 2024 |
| 18 | 2076140 | Tavern Talk - A Cozy Visual Novel | 2024 |
| **20** | 2124120 | SULFUR | 2024 |
| 20 | 213610 | Sonic Adventure 2 | 2012 |
| 20 | 2138710 | Sifu | 2023 |

There are **18 distinct AppIDs**, no split/remixed groups. Some labels themselves suggest possible original-versus-storefront year or edition distinctions; **no such truth is inferred from the name**. For example, the binding `Sonic Adventure 2 → 2012` is a fact about an accepted dossier's identity field, not proof of the game's first historical release. Independent work-identity adjudication is a mandatory blocker, not a cosmetic postprocessing step.

### Complete 20-group eligible frame and transparent exclusions

All 20 rows were already strictly proven in #201, so there are **zero integrity-based exclusions**. The 14 nonselected eligible groups are excluded only by the declared sampling rule, not poor semantics, lack of source evidence, or hidden reviewer preference. Values `<2015` and `≥2015` below mean **any accepted baseline game's reported year binding**, not independently verified reality. Hash column is the first 12 hex digits of SHA-256, for inspection; the generated JSON contains the full SHA-256 and immutable descriptor/receipt hashes.

| Sequence | Original AppIDs (unchanged order) | Year binding stratum | Selection hash prefix | Outcome |
| ---: | --- | --- | --- | --- |
| 1 | 1119710, 1202690, 1409740 | ≥2015 | `c879130abd1b` | not selected |
| 2 | 1430680, 1438480, 1507190 | ≥2015 | `aebb055aa1ed` | not selected |
| 3 | 1508750, 1517180, 1533420 | <2015 | `141bafd545d2` | **provisional** |
| 4 | 1536090, 1545560, 1557740 | ≥2015 | `eb2668c4cb3d` | not selected |
| 5 | 1562430, 1574240, 1574580 | ≥2015 | `80db3b6b1352` | not selected |
| 6 | 1574820, 1578220, 1578650 | ≥2015 | `913ca6703cf4` | not selected |
| 7 | 1582650, 1583230, 1583850 | ≥2015 | `d23fe1a9f98a` | not selected |
| 8 | 1590230, 1599600, 1607130 | ≥2015 | `43e3c1b613ad` | **provisional** |
| 9 | 1620720, 1627570, 1638220 | ≥2015 | `6ec2e85ef167` | not selected |
| 10 | 1649080, 1651560, 1658150 | ≥2015 | `f4814b9f86cd` | not selected |
| 11 | 1681430, 1740300, 1808680 | ≥2015 | `b18d97a02cd1` | not selected |
| 12 | 1835240, 1836160, 1837330 | ≥2015 | `ac03643cd7c5` | not selected |
| 13 | 1849000, 1857090, 1868140 | ≥2015 | `6c2409ac0a7f` | **provisional** |
| 14 | 1898500, 1939970, 1948280 | ≥2015 | `90e893f6306b` | not selected |
| 15 | 1999170, 1999360, 2009010 | ≥2015 | `5453722345a7` | **provisional** |
| 16 | 2015240, 201810, 203750 | <2015 | `f01ce34d6019` | not selected |
| 17 | 204100, 204300, 2060130 | <2015 | `cefd421e7f5a` | not selected |
| 18 | 206420, 2067050, 2076140 | <2015 | `bc8273a25d7a` | **provisional** |
| 20 | 2124120, 213610, 2138710 | <2015 | `02090de7f853` | **provisional** |
| 21 | 2140020, 214950, 220440 | <2015 | `d4384d8e4cbe` | not selected |

**Denominator flow (historical source, not live work):** 76 original groups = 228 immutable originally prepared AppIDs → 20 accepted and proven writer-eligible groups = 60 games → 6 hash-selected groups = 18 AppIDs, 14 in-frame nonselected = 42 AppIDs, 56 groups outside accepted source = 168 games (not shadow candidates) → 0 Research stages executed → 0 Assembly stages executed → 0 quality reviews → 0 adjudications. No selected group is "accepted as good quality"; no failed/unknown future result may be replaced after unblinding.

## Known / unknown / not-measured evidence matrix

| Dimension | Present pre-output binding | Independently proven external state | Sampling implication |
| --- | --- | --- | --- |
| Exact original group order, three AppIDs, title, writer Git commit/cache blob | **known** for 20/20 by pinned manifest plus #201 Git-local strict receipt and independent Actions provenance | no human-review source authenticity implied | usable for integrity and reproducibility |
| Original-work-year **as old dossier binding** | **known** 60/60 from existing accepted `game_identity.release_year` | *actual* original release year **unknown** (0/60 independently checked) | only explicitly labelled two year-binding strata usable |
| Steam storefront launch year versus original-work date | **not_measured**, 0/20 groups | **unknown** | no mismatch-rate or date diversity claim |
| Remaster / DLC / edition original-work identity | **not_measured**, 0/20 groups independently checked | **unknown** | possible cross-edition leakage; stop pending check |
| Russian / multilingual player-authored material | **not_measured**, 0/20 | **unknown** | do not claim coverage or absence |
| Recent/older/undated actual review publication | **not_measured**, 0/20 | **unknown** | no temporal diversity claim |
| Independent player-source parents, not duplicated wrappers | **not_measured**, 0/20 | **unknown** | source diversity unproven |
| Material negative/mixed findings, suppressed risks | **not_measured**, 0/20 | **unknown** | cannot compare preservation or assert quality |
| Technical, localization and regional risks | **not_measured**, 0/20 | **unknown** | no risk balance claim |
| Source-route gaps, unavailable evidence, targeted revisits | **not_measured**, 0/20 | **unknown** | unknown cases must be counted, never silently removed |

**Why `NOT_READY_FOR_APPROVAL`:** group integrities and the 6:14 year-*binding* population are real, but the eight requested richer pre-output fairness strata have **0/20 evaluated**. No trustworthy independent pre-output provenance descriptor currently authorizes claiming representative Russian, source-parent, temporal, negative, remaster/DLC, localization or gap coverage. Names, storefront dates, existing one-stage conclusions or release-year labels must not be repurposed as a fabricated independent evidence audit. The SHA method is useful **only as a transparent provisional mechanical draw**, not a defensible balanced finalized trial cohort.

**Non-mutating resolution:** appoint an independent bounded source-metadata auditor to inspect *all 20* original groups (not only the favorable six), recording non-personal safe parent counts, real-source presence/absence/unknown, independently corroborated original-work identity and storefront date separately, Russian review availability, review-age categories, material negative/gap flags, and each descriptor's verifiable citation + immutable source observation hash. Predeclare privacy limitations and gaps; if source lookup isn't authorized, record `not_measured`, do not infer. Then return a **new exact proposed 6-group decision packet** with a frozen seed/strata policy for user approval; do not let a worker select scope itself.

## Proposed future independent-quality gates (ALL UNAPPROVED)

**Owner and independence:** GitHub freezes the exact authorized group selection/immutable package/marker and writer acceptance binding. Reviewer **A** independently evaluates exact identity, dates, citations and player-source existence; reviewer **B** independently checks material positives/negatives, omissions and conclusion utility with the same frozen evidence but without A's preliminary verdict. An independent **C/adjudicator** resolves recorded disagreements after both reviews are saved. Director/user owns preregistration, conflict-of-interest declaration, evidence-source access rules, signed trial authorization, and final go/no-go. None of these roles is assigned or invoked here. Chat 2 develops its separate offline comparator and blinded review gate; this report does not edit or replace it.

**Proposed calibration checks for future explicit approval:** 18/18 eligible AppIDs must have exact frozen both-stage + verified historical counterpart and separately checked real-source/identity metadata **before scoring quality**; two independent evaluations per game (target 36/36 A/B entries), independently recorded first; 100% material disagreements adjudicated, 100% unknown/blocked games included in denominators. **Any one** confirmed wrong original-work identity/year lineage, invented source, privacy leak, suppressed material risk or unsupported material conclusion is a hard stop and no go; zero allowed. Suggested reviewer-interpretation calibration target: at least **85%** initial A/B exact agreement for the defined material-safety labels, but if lower, revise rubric and undertake **another separately approved** calibration rather than treating low agreement as quality proof. These are stakeholder **proposals only**, not approved thresholds or production contracts. No quality benefit or semantic parity claim can be made from a synthetic test or a schema-valid result.

**Proposed gates and audit denominator:** preflight frozen frame N20 → selected N6 groups/18 AppIDs → strict valid immutable Research→Assembly→V2 chain N0 now → verified old-writer paired N0 in real new chain now → independent real-source-reviewed N0 → A/B complete N0 → adjudicated N0. Record blocked, unverifiable and contradicted items with immutable Git IDs, reason, and `unknown`/rejected status; never hide them by dropping a game. The old one-stage writer remains canonical throughout any later shadow quality trial. Never read real reviews here.

**Immediate halt (hypothetical later run):** wrong AppID/title/work-year version binding; broken frozen Git chain; missing accepted writer receipt; inaccessible or invented player-authored citation; material negative omission, unsupported critical assertion; misattributed date/source parent; privacy leakage; attempted mutation of production writer/cache/Deep. Preserve diagnostics without private data; no self-repair, automatic retry, substitution or hidden count denominator revision.

**Rollback:** current packet is inert, hence rollback **no-op**. Any future separately authorized live-source shadow trial runs only against a marked disposable clone and canonical owner-frozen manifest. No canonical Dossier/Deep/Fast writes; no scheduler. A later real cutover requires a different approved contract/PR and explicit GitHub shared-writer-serialized preservation/rollback, not this packet or a flag flip.

## Local PR-only isolated checks

```sh
python -m unittest discover -s scripts -p 'test_dossier_shadow_pilot_cohort_preview.py' -v
python scripts/dossier_shadow_pilot_cohort_preview.py \
  --target-head 95a4bf4990a60082ecb3302da5bc7f23b618d93e \
  --expected-work-blob ef40fc186aabc79dfd24c72864dbe43817a56039 \
  --expected-audit-blob 8dbf4437d7ba439942f58a6f36d89d6a7ddeec7b \
  --compare-ref origin/main \
  --out "${TMPDIR:-/tmp}/dossier-shadow-cohort-preview.json"
```

Workflow `.github/workflows/validate-dossier-shadow-pilot-cohort-preview.yml` is **pull_request paths-only**, `contents:read`, credentials unpersisted, full history read for the frozen pinned snapshot; synthetic/adversarial tests (malformed frame, duplicate AppID, missing group, broken identity/year/attestation, seed repeatability, invalid main comparison) and a real metadata-only 20-group preview/assertion step. Safe output only under OS temp or GitHub `RUNNER_TEMP`; optional short-lived PR artifact. No `push`, workflow dispatch, scheduler, worker index, trial marker, terminal receipt or cache persistence, real semantic analysis, GitHub writer or site publication.

**PR completion condition:** CI proves exactly 20 frozen attested original groups, reproducible selected `[3,8,13,15,18,20]`, zero semantic work, false authorization/readiness, and `not_measured` disclosure. CI is only implementation verification; even a successful run does **not** move `NOT_READY_FOR_APPROVAL` to approved. No task registry/Board/handoff or Chat 2 files changed.

## Handoff

- **Confirmed:** 20/20 old accepted groups have PR #201's independent strict historical Git proof and successful actual writer run provenance; current script reads this attested frozen frame only. Original one-stage Dossiers remain canonical; proposal is strictly inert.
- **Proposed, not a final selection:** six original groups `3,8,13,15,18,20`; reversible proposal only until Director/user approves after resolving source-truth/stratification gaps.
- **Unknown/not measured:** external real-source authenticity/independence, real first-release year vs storefront dates/editions, Russian material, review chronology, material negative preservation and semantic quality.
- **Next bounded task (requires separate decision):** read-only pre-output verification of all 20 source-provenance and identity descriptors, with approved independent reviewer roles, then a revised fair cohort proposal/explicit authorization; do not initiate semantic trial yet.
