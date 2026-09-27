# Deep positive evidence card projection fix 01

## 1. Task

Task ID: `deep-positive-evidence-card-projection-fix-01`. Mode: `IMPLEMENT / VALIDATE`.

Target: `game:1172380` / `STAR WARS Jedi: Fallen Order™`.

Repair the authoritative Deep/PASS 2 -> visual `Почему может зайти` path so accepted current Deep `positive_evidence` produces grounded Russian reasons with exact provenance. No Deep/Dossier/Fast rerun, manual backlog processing, Scheduled Task change, negative-risk repair, or ranking-weight change was allowed or performed.

Implementation baseline: `main@9525a3e402e5d33ba61285bb789ae19251f914cf`.

## 2. Architecture preflight

Before writes, verified:

- accepted Deep/PASS 2 state remains GitHub-owned semantic truth;
- effective semantic precedence remains `Deep > Fast > reusable cache`;
- visual production remains GitHub-owned;
- browser remains read-only;
- explanation projection is deterministic rendering of accepted evidence, not a second semantic-analysis stage;
- no scheduler, queue, retry, recovery, backlog, or Scheduled Task change is required;
- positive reasons remain fail-closed and cannot be invented from title, genre, score, price, discount, or rank.

The reusable path is now documented in `PROJECT_ROUTES.md`.

## 3. Verified root cause

The authoritative Jedi Deep state already contained `analyzed_fit`, `authoritative_completed=true`, `fit_level=strong`, `confidence=high`, three non-empty `positive_evidence` rows, and normalized factors `88 / 81 / 71 / 87 / 86`.

`scripts/progressive_pass2.py::semantic_taste_entry()` already copied those positive rows into the effective semantic entry. Therefore ingest/state persistence was not dropping them.

The loss occurred in the shared card renderer: both canonical visual producers call `scripts/card_explanation_policy.py::positive_reasons()`. The fail-closed mapper recognized only a bounded older phrase set; none of Jedi's accepted Deep evidence matched, so valid evidence became `why_fit=[]`.

At the same boundary, old `why_fit_provenance` recorded source/policy/evidence text but did not bind a displayed Deep reason to the exact accepted Deep generation/work/Dossier/authorization/state identity.

Root cause: **shared explanation-policy coverage plus missing exact Deep-positive provenance binding**. It was not Deep ingest loss, localization loss, or frontend loss.

## 4. Changes

Implementation PR #105:

- adds `positive_evidence_binding` to authoritative Deep semantic entries, carrying immutable PASS 2 identity plus Dossier digest, authorization, accepted time, and work authority;
- extends the shared fail-closed policy with general grounded mappings for combat mastery and ability progression, producing deterministic Russian personalized reasons;
- carries the exact binding into `why_fit_provenance.semantic_binding`;
- passes that binding through both `build_visual_feed_v2.py` and `build_final_visual_payload.py`;
- makes `validate_card_explanations.py` reject missing/mismatched Deep-positive bindings;
- adds Jedi-equivalent, stale-binding, empty-positive, and legacy Fast/cache regressions;
- runs the explanation regression inside existing PASS 2 core CI;
- documents the canonical route in `PROJECT_ROUTES.md`.

No fit conclusion, score formula, ranking weight, negative/risk mapping, Dossier behavior, worker prompt, scheduler, or Scheduled Task was changed.

## 5. Parallel reconciliation

Immediately before merge, fresh `main` had advanced to `a6013b809f29e0101d0d0b0880357544c9ebc249`. The only concurrent change from the implementation base was ЧАТ 2's report `reviews/worker_reports/jedi-deep-missing-negative-evidence-diagnostic-01.md`.

That report was read and preserved before merge. Its `DEEP_PROMPT_OR_CONTRACT_OMISSION` finding concerns the separate negative channel: successful `analyzed_fit` Deep results currently have no structured balanced-negative field. This does not contradict the positive repair and independently confirms that Jedi's accepted Deep transport/state contains the positive rows used here.

PR #105 merged only after this reconciliation. Later `main@b604ae0623281b2ff41de711c40ef83590164def` accepted the ЧАТ 2 diagnostic separately.

## 6. Validation

PR #105 final head: `c089e3f8e8ac362348d97ca2db3c8ad430dda1fb`.

Final PR checks all passed:

- PASS 2 core: run `36343137346` / #238;
- execution ownership: `36343137314` / #218;
- backlog dispositions: `36343137385` / #1316;
- package purchase value: `36343137349` / #23.

The focused policy regression reports `CARD_EXPLANATION_POLICY_TESTS=PASS count=8` and proves:

1. authoritative Jedi-equivalent Deep positives -> non-empty grounded Russian `why_fit`;
2. exact current Deep provenance is retained;
3. stale/mismatched Deep identity is not accepted as current;
4. empty positive evidence stays empty;
5. legacy Fast/cache behavior stays unchanged;
6. fit/ranking values are not changed by the explanation repair.

Post-merge normal full visual workflow `36343208462` / #817 succeeded: 393 items, `CARD_EXPLANATION_POLICY_TESTS=PASS count=8`, `CARD_EXPLANATION_VALIDATION=PASS` including Jedi, and `PRIORITY_RANKING_VALIDATION=PASS`. It committed `2b66cce6c7afb19d5c5bf7ebe3c4c20ca95d8224`; freshness artifact `10939521951`.

The receipt says `degraded/no_fresh_build: deterministic_refresh_preserved_semantic_history` because this projection-only task intentionally reused already accepted semantic history and explicitly forbade a Deep rerun. The full visual workflow and general Pages deployment still succeeded and the staged payload was bound to that receipt.

Following Pages deployment `36343242275` / #857 succeeded; artifact `10939772150`. A later commercial-only refresh `9dbd73daff4a4259a59e2140799c9709afcaceaa` preserved semantics, and latest verified Pages deployment `36343288465` / #858 also succeeded; artifact `10939991495`.

## 7. Published result

Pre-fix visual blob `56c72e5fe7ae7661190706f91287d0106c5b6c1b` had:

- effective source `deep`;
- semantic generation `4596b03979956f78c308551a75fdbe9f432ed3f80925c29b0835bdb052222033`;
- `why_fit=[]`;
- `has_described_fit=false`;
- `grounding=insufficient_evidence`.

Direct inspection of deployed Pages artifacts #857 and #858 now shows:

- same effective source `deep` and same semantic generation;
- two Russian `why_fit` reasons: combat mastery grounded in parrying/dodging, and ability progression grounded in abilities opening/changing gameplay;
- `has_described_fit=true`;
- `grounding=grounded`;
- each reason bound to Deep work `9ae7b3ff76e8f91f25d6f66285c2c4f47e8b9d97fd343eb4d23798276b9658e2`, Dossier SHA-256 `e06c17a567e1f9a249d2ece40eadad045933262562b8ff35aad74c42bf33b144`, authorization `a54bba18a1bacab918c0de4022b6192f1eb9a3c6a667369edc712801a5082ee6`, accepted time `2026-09-27T17:16:49+00:00`, and work authority `f8f8370bf647edf05db79eeb4ec82caeee3d5148`.

Fit/ranking is unchanged before -> after:

- rank `1 -> 1`;
- fit `strong -> strong`;
- total `68.6 -> 68.6`;
- personal `43.6 -> 43.6`;
- purchase `25 -> 25`;
- taste points `41.6 -> 41.6`;
- factors remain `88 / 81 / 71 / 87 / 86`.

## 8. Unresolved

The separate missing-negative/risk problem found by ЧАТ 2 remains intentionally unresolved. Current successful-fit Deep result contracts cannot carry a balanced negative assessment. This task does not alter that contract and does not manufacture risks.

No positive-projection blocker remains for the tested authoritative Deep path.

## 9. Status

`complete_ready_for_director_acceptance`

## 10. Recommended next step

Director: accept this positive-projection task as complete; keep the separate ЧАТ 2 negative-contract remediation outside this task.

## 11. Exact PR/commit/run/artifact refs

Implementation:

- branch `fix/deep-positive-evidence-card-projection-01`;
- PR #105 `Project authoritative Deep positives into card why-fit`;
- final head `c089e3f8e8ac362348d97ca2db3c8ad430dda1fb`;
- merge `21c3331eec471a18889de0264776216490bee7bf`.

Key implementation commits:

- `3d2e3e881791b3c81ae353617fa5d50ad56d660a` mapper/provenance;
- `3c47ce5b8d6fada95fdea35cc193fe9cde42e64c` Deep binding;
- `d33f61a72e8673926a7480e4d4d619f233e6863f` visual-feed handoff;
- `b622580c545fefe866911c861445d4ac00888370` final-payload handoff;
- `0001c1c99b19167e522a7235ab006198b29effcb` validator;
- `021c973311c78e0daf8c28a24dbd069b6533fc0c` focused regression;
- `dbedc6570cf63cf0aa0701abb1f7cbc3a4516f51` PASS 2 CI integration;
- `c089e3f8e8ac362348d97ca2db3c8ad430dda1fb` route documentation/final head.

Parallel refs:

- pre-merge fresh main `a6013b809f29e0101d0d0b0880357544c9ebc249`;
- later ЧАТ 2 acceptance main `b604ae0623281b2ff41de711c40ef83590164def`.

Publication refs:

- full visual run `36343208462` / #817;
- visual commit `2b66cce6c7afb19d5c5bf7ebe3c4c20ca95d8224`;
- freshness artifact `10939521951`;
- following Pages run `36343242275` / #857;
- Pages artifact `10939772150`;
- later commercial refresh `9dbd73daff4a4259a59e2140799c9709afcaceaa`;
- latest Pages run `36343288465` / #858;
- latest Pages artifact `10939991495`;
- latest inspected visual blob `5aaebc0abe331f008f154b5a523799421ad06905`;
- pre-fix visual blob `56c72e5fe7ae7661190706f91287d0106c5b6c1b`.

## 12. Efficiency / reusable lesson

For future “authoritative Deep fit but empty `Почему может зайти`” cases, use:

`PASS 2 state -> semantic_taste_entry() -> effective_taste_entries() -> card_explanation_policy.positive_reasons() -> final visual why_fit/provenance -> deployed Pages artifact`.

Check first whether accepted `positive_evidence` already survives into `semantic_taste_entry()`. If it does, ingest/frontend investigation can be skipped and the problem is bounded to explanation rendering/provenance. This route is stored in `PROJECT_ROUTES.md`, and the Jedi-equivalent regression now runs inside existing PASS 2 core CI.
