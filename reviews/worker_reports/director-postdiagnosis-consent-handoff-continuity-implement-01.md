# Director postdiagnosis consent / handoff continuity — implementation report
Task: `director-postdiagnosis-consent-handoff-continuity-implement-01`
Repository/base: `kentrap2011-hub/steam-kz-deals-2` / `main` at branch creation `32a427503a459c66173eb60de938c78cdefd08fc`
Mode: bounded governance text-only IMPLEMENT; one draft source PR; **no live registration or source merge test**.

## Verified facts
- Evidence example: PR [#367](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/367), `DIAGNOSIS_COMPLETE`, report `reviews/worker_reports/dossier-v1-rejected-buffers-exact-product-binding-root-cause-01.md`; nine rejected Dossier V1 buffers, zero accepted; targeted implement is recommended but not executed by this task.
- Canonical owner: `DIRECTOR_PROTOCOL.md` §1 owns the director's typed decision gate and result→user-choice transition. `CHAT_PROTOCOL.md` PRE-SEND is a short enforcement reminder, not a second approval store.
- Architecture preflight: interactive Director manages authorized handoff; GitHub remains canonical for registry/Board/PR/CI, production and semantic control plane remain elsewhere; no new queue, stage, scheduler, retry, quota or permission-grant mechanism.

## Checked active places / disposition
| Place | Disposition | Evidence |
| --- | --- | --- |
| `DIRECTOR_PROTOCOL.md` §1 STATUS | **fixed** | line 34: newly final result can DECIDE+ASK read-only, not REGISTER |
| `DIRECTOR_PROTOCOL.md` §1 DECIDE | **fixed** | line 35: one next action and once-only question |
| `DIRECTOR_PROTOCOL.md` §1 RESULT→REGISTER / MERGE | **fixed** | lines 39 onward: yes/no/ambiguous, prewrite/CI/main/launcher, existing MERGE safety |
| `DIRECTOR_PROTOCOL.md` §4 | already aligned | task must specify one expected next step and canonical report |
| `DIRECTOR_PROTOCOL.md` §7 | already aligned | compact report, `Recommended next step`, explicit status |
| `DIRECTOR_PROTOCOL.md` §8 | **fixed** | line 217: director must act on final-result continuity, not just summarize |
| `DIRECTOR_PROTOCOL.md` §9 | already aligned | worker stays in scope; director chooses next direction |
| `DIRECTOR_PROTOCOL.md` §10 | already aligned | unique chat slots and physical chat released on final report |
| `CHAT_PROTOCOL.md` Director PRE-SEND | **fixed** | line 50: concise continuity check |
| `DIRECTOR_BOOTSTRAP.md` active top dated 2026-10-28 | already aligned as dated restart snapshot | no new registration authority; canonical current Director protocol takes precedence |
| `DIRECTOR_HANDOFF_CURRENT.md` top dated 2026-10-28 | already aligned as dated snapshot | directs exact gate checks, not authority for new work; dated lower sections archival |
| Archived snapshots under bootstrap/handoff | archival / non-authoritative | not modified |

## Acceptance walkthrough (static, **not** actual GitHub actions)
| # | Scenario | Expected result |
| --- | --- | --- |
| 1 | Worker in-progress | STATUS only; no final-result prompt, no write |
| 2 | New DIAGNOSIS_COMPLETE (#367) | 2–4 sentences: result + one scoped repair actor + one ask; STATUS read-only |
| 3 | Specific yes to that proposal | REGISTER prewrite exact main/slot/dedup/deps → PR → required exact-head CI → main → verifiable copyable launch; no second ask |
| 4 | No | No registration, no merge |
| 5 | Already assigned task | Check registry/Board; do not duplicate or reuse occupied slot |
| 6 | CHANGES_REQUIRED | Scoped repair proposal + one permission question; no independent new broad audit |
| 7 | Exact authorized source-MERGE + all gates | Actual merge same turn with HEAD-bound merge and report SHA; no second ask |
| 8 | QA green but no user-grant | BLOCKED_PERMISSION; QA report PR not source PR |
| 9 | Red/pending/skipped required CI or stale material HEAD/QA | BLOCKED_SAFETY; no merge/launch |
| 10 | Ambiguous yes for two proposals | Single clarification, no writes |
| 11 | Semantic/scheduled/production | Separate explicit authorization; no implied permission |
| 12 | Repeated STATUS same result | Do not ask again; no duplication |

All 12 scenario expectations matched against the proposed §1 rule, §8 pointer, PRE-SEND reminder and preserved §§2–3/4/7/9/10. **Static walkthrough only**; actual CI status must be checked separately at final PR HEAD. No live consent, registration, QA, source MERGE or semantic launch simulated as action.

## Changes
- `DIRECTOR_PROTOCOL.md`: clarify STATUS / DECIDE, add single canonical result→choice→REGISTER bridge, link report retrieval to it.
- `CHAT_PROTOCOL.md`: one Director PRE-SEND checkbox to prevent loss of the follow-up step.
- This report. No modifications to Board, registry, worker task files, workflows, CI or runtime.

## Validation
- Local construction guards: exact unique anchors for all textual substitutions, all 12 scenarios statically walked through, only three allowed paths.
- GitHub exact-final-HEAD PR checks: **pending verification on opened draft PR; no claim of success here**.

## Risks / rollback
- L1: text-only orchestration clarification, no material expansion of source MERGE or semantic permissions; no independent QA required under existing L1 gate. L2: none (no executable instructions/scripts). L3: none (unchanged source-merge, production, runtime and explicit permission gates).
- Rollback: revert this PR's `DIRECTOR_PROTOCOL.md`, `CHAT_PROTOCOL.md` and report in one revert commit; no state migration or production impact.

## Unresolved / status / next
- Unresolved: real director behavior in future conversations cannot be CI-enforced; GitHub PR exact-HEAD CI must be checked by Director before accepting.
- **Status:** complete (implementation in DRAFT PR; not merged).
- **Verdict:** `READY_FOR_DIRECTOR_MERGE` **only after** live exact-final-HEAD required CI, mergeability, actor rights and specific user grant, per §1.
- **Recommended next step:** Director verifies this **source PR**, exact HEAD/CI and authorized acceptance, then merges if gates pass; do not treat a QA report-only PR as source acceptance.
- Efficiency / reusable lesson: none.
