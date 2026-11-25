# ЧАТ 2 — isolated Lean Dossier six-item GitHub writer acceptance

Task: `dossier-lean-fresh6-isolated-writer-acceptance-01`  
Repository (exclusive): `kentrap2011-hub/steam-kz-deals-2`  
Canonical source branch: `main`; source PR: [#478](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/478) (draft, **NOT MERGED**)  
Source branch: `implement/dossier-lean-fresh6-isolated-writer-acceptance-20261124`  
Initial main SHA: `f9974ec85b6d4b7e2ac6ca2699a404339f8561b7`. Task registration source SHA `213163eb85a4fe389cd5bf64a6d6f277f1e26d62` is historical, not substituted for LIVE main.

## Outcome: SOURCE IMPLEMENTED / REAL ISOLATED ACCEPTANCE PENDING

**Persisted isolated accepted 0/6; source-only PR is not live acceptance.** No owner sandbox writer dispatched. This worker did not self-merge. Before runtime: final exact-HEAD GitHub CI, independent L3 security/owner QA and Director source acceptance/merge. After merging: one authenticated exact-owner first-attempt GitHub workflow dispatch through the preexisting locked writer; independently verify success plus all exact committed sandbox bytes and six receipts at the actual final sandbox branch HEAD. Do not call `strict_item_valid_pending_existing_atomic_group_ingest` accepted.

## START and preflight

Read LIVE `CHAT_PROTOCOL.md`, `CHAT_CONTEXT.md`, task, `PROJECT_ROUTES.md`, pertinent `PROJECT_DECISIONS.md`, `config/execution_ownership_contract.json`, Notes V2/Batch/Generic/Lean versioned contracts, existing buffer writer, Lean validator, Research/Assembly receipts, workflow and existing tests. GitHub identity `kentrap2011-hub` (`315790060`) confirmed. No other repository used.

Frozen trial: `dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4`  
Immutable sandbox branch: `sandbox/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4`  
Observed pre-acceptance HEAD: `d1b9a9e78dcde879a03370682ade4969763fd9d1`  
Frozen marker: `b267882dd3d056a1fc18d6a3fb75380ac38bd9cd`  
Owner authorization: `c15483d834ad2196377b5a8ed5a2a71ec743e2bd`  
Request: `8adeee166cbc9d78107b76e28f253e4f547dfedc`, nonce `cdcdb4951e2fc98336729af75b954da4`  
GitHub Actions issuer run: [45243093290](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/45243093290); verified `completed/success`, first attempt, owner actor ID `315790060`, push on exactly matching request branch; this proves source issuer, **not** writer acceptance. Original Research and all earlier trials remain immutable.

## Frozen six items

| Order | AppID | Title / edition | group | Research commit | Assembly commit |
|---|---|---|---:|---|---|
| 1 | 1000010 | Crown Trick | 1 | `89fe218181a3c397b962f2c5a4686780074e717f` | `36a40b619ec2652c243a2c963f1b6032fd21fe6c` |
| 2 | 102600 | Orcs Must Die! | 1 | `557efc8a6f9978daeec6868a42085f96d995a9e6` | `954f0e897f16c8c2cd3e7d9693de7e47c8132d82` |
| 3 | 1029690 | Sniper Elite 5 | 1 | `6044f4e00873a0611ee916073c7fed3c9f071864` | `d38cbb3721e010f3fd3c733cf9d63698cf1f728c` |
| 4 | 49520 | Borderlands 2 | 70 | `9f021495335484fbc42a37bd5082ed8cfc316225` | `efa7ad5652e00fc0418773dc548764f4fdeb8586` |
| 5 | 499180 | Braid, Anniversary Edition | 70 | `f62e49f7fe101c9f600fe02bf239c815a560e897` | `2a9fff3214106bcd1a5ac1592f4ac997364ae51a` |
| 6 | 501590 | Bulletstorm: Full Clip Edition | 70 | `3e31fd57d0e3e2b37b78deff5244b8673356e3a5` | `bc0471f1102b275d09fa6828d86050313d713d26` |

Six immutable Assembly candidates were observed with `outcome=assembled_candidate_ready`, Lean schema, exact title/AppID, 14-day TTL. Six separate typed Assembly receipts had staging/transport disposition `strict_item_valid_pending_existing_atomic_group_ingest` and `canonical_acceptance=false`. Source-specific typed receipt Git blob SHA and assignment IDs frozen in `config/dossier_notes_v2_isolated_lean_acceptance.json`. Neither a receipt label nor an issuer Actions success substitutes for independent GitHub writer verification.

## Narrow source changes (PR #478)

1. `config/dossier_notes_v2_isolated_lean_acceptance.json`: exact six AppIDs, immutable Research/Assembly/typed transport blobs, issuer authorization, frozen sandbox HEAD, single-use GitHub sandbox writer grant; canonical/main/Deep/retry OFF.
2. `scripts/dossier_lean_canonical_dual.py::require_isolated_sandbox_writer`: protect six-item exact trial and **exact pre-acceptance HEAD**, authenticated-issuer structural binding, immutable original typed receipt Git blobs, collision/duplicate defense and all global Lean flags OFF. Never grants production Lean.
3. Existing `scripts/taste_steam_review_dossier_buffered.py::_drain_notes_v2_individual`: only exact user-approved sandbox grant selects Lean; rechecks existing immutable Git Research/Assembly and typed receipt, independent `validate_writer_lean` (AppID, exact edition, original year, 14-day TTL, privacy, safe sources, temporal dates, balanced strengths/tradeoffs) before stage. Binds canonical JSON digest separately from raw persisted bytes digest. An incomplete or rejected six-item group raises *before* Git staging/commit/push.
4. Existing shared workflow `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`: retains shared `taste-steam-review-dossier-canonical-writer` lock and existing batch destinations, imports merged main writer code via isolated temp worktree for this exact historical sandbox (without modifying original semantic candidate/receipt files), verifies exact twelve-file stage and Git commit, performs one non-force sandbox-only push and readback. All other strict and V1/Deep/main workflows remain unchanged.
5. `scripts/dossier_notes_v2_isolated_lean_readback.py`: six stored Lean docs + six exact Git committed receipts, no path escape/other staged paths, hash/domain and original Assembly equality, before and after Git commit.
6. `scripts/test_dossier_notes_v2_isolated_lean_acceptance.py`: disposable Git staged/committed positive plus negative (missing receipt, partial group, duplicate/unrelated path, edition/AppID, raw SHA, unsafe source, invalid TTL, fake branch, canonical flags); exercises the existing writer for six with synthetic owner/lineage mocks clearly **not** real authorization.
7. `.github/workflows/validate-dossier-research-notes-v2.yml`: PR-only regression hook. Existing strict V1/V2 tests kept.

### No-live boundary

- No new Research or Assembly, no semantic replay, no schedule/retry, no production/canonical main store writes.
- No normal Deep or Taste, all `lean_writer_enabled`, `lean_reader_enabled`, `lean_deep_enabled` remain FALSE.
- No self merge; owner security review not waived by user.
- Existing strict batches still run through unmodified strict path.

## CI and director gates

Exact final source HEAD and all mandatory GitHub workflow conclusions: **pending final verification**; do not infer from pre-existing CI. This text is a source-worker handoff, **not** a live owner acceptance assertion.

After independent security QA and Director merge, use GitHub Actions existing `Ingest Steam review dossier checkpoint` workflow, run on `main`, as the real owner `kentrap2011-hub`, first attempt only, with:

- `notes_v2_writer=false`, `notes_v2_original18_pilot_writer=false`, `notes_v2_batch_pilot_writer=true`.
- `notes_v2_trial_id=dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4`.
- `notes_v2_marker_commit=b267882dd3d056a1fc18d6a3fb75380ac38bd9cd`.
- `notes_v2_item_commits_json` (exact all-six JSON):

```json
{
  "1000010": {"research_commit": "89fe218181a3c397b962f2c5a4686780074e717f", "assembly_commit": "36a40b619ec2652c243a2c963f1b6032fd21fe6c"},
  "102600": {"research_commit": "557efc8a6f9978daeec6868a42085f96d995a9e6", "assembly_commit": "954f0e897f16c8c2cd3e7d9693de7e47c8132d82"},
  "1029690": {"research_commit": "6044f4e00873a0611ee916073c7fed3c9f071864", "assembly_commit": "d38cbb3721e010f3fd3c733cf9d63698cf1f728c"},
  "49520": {"research_commit": "9f021495335484fbc42a37bd5082ed8cfc316225", "assembly_commit": "efa7ad5652e00fc0418773dc548764f4fdeb8586"},
  "499180": {"research_commit": "f62e49f7fe101c9f600fe02bf239c815a560e897", "assembly_commit": "2a9fff3214106bcd1a5ac1592f4ac997364ae51a"},
  "501590": {"research_commit": "3e31fd57d0e3e2b37b78deff5244b8673356e3a5", "assembly_commit": "bc0471f1102b275d09fa6828d86050313d713d26"}
}
```

Connected GitHub connector does not expose an approved `workflow_dispatch` action. **Do not simulate issuer, manually insert accepted files, or relaunch semantic Assembly as workaround.** After valid real run, verify exact final isolated branch SHA, six independent original Lean docs and committed accepted receipts, entire previous candidate/receipt sandbox Git history unaltered, exact 12 new files, run status/actor/attempt, main canonical and Deep unchanged. If any fails, report per-game BLOCKED/REJECTED and do not retry unilaterally.
