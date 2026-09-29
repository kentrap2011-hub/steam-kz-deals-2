# Progressive migration current-binding regression fix 01

## 1. Task

Task: `WORKER_TASK_PROGRESSIVE_MIGRATION_CURRENT_BINDING_REGRESSION_FIX_01.md`.

Goal: remove the pre-AI blocker `AssertionError: migration target missing current binding: game:1143810` without inventing a binding, rewriting Deep state, rerunning PPD-010 semantics, or weakening PPD-012 semantic identity checks.

Repository: `kentrap2011-hub/steam-kz-deals-2`, source of truth `main`.

## 2. Architecture preflight

Architecture remains unchanged:

- GitHub owns current Progressive scope, semantic generation/identity, work IDs, PPD-012 historical-equivalence selection, attempt accounting, state persistence and migration/current-result reconciliation.
- Scheduled ChatGPT remains a bounded semantic data plane only.
- PPD-010 migration membership, accepted revisions and exact execution provenance remain immutable.
- PPD-012 still fails closed for real profile/model/taste-semantics/candidate-context/item identity changes.
- No semantic worker, retry/scheduler/backlog ownership or Scheduled Task was changed.
- The implementation changes only the deterministic regression expectation and its durable route documentation.

The existing contracts already distinguish the target set `all_current_eligible_games` from immutable historical migration membership, so no canonical contract amendment was required.

## 3. Pinned failure

Two confirmed pre-fix production failures:

- run `36458961528`, head `9cb123765884440d37632740d51695a371338483`, created `2026-09-28T17:33:28Z`, failed in `scripts/test_progressive_profile_semantic_identity_stability.py` with `migration target missing current binding: game:1143810`;
- run `36516631678`, head `c25762948500d6f64158047de01c7e4f5952911f`, created `2026-09-29T03:19:37Z`, failed at the same assertion.

The failing code iterated all 30 frozen PPD-010 migration targets and unconditionally asserted that each still had a current binding.

## 4. Black Skylands current identity

Historical/current semantic material for Black Skylands:

- family: `game:1143810`;
- taste subject: `App_1143810`;
- AppID: `1143810`;
- taste fingerprint: `be21d660fd5b8311cedd5f8ab4913c049e6f5f4a990953af74b495ea86267f04`;
- candidate-context SHA-256: `259063878eaaa43641a481b46df4dd32a20914c25defbf0de5a136572e0e7266`;
- PPD-010 work ID: `0d29c660d43d01ef3088c1f7112342a63e728b49f79eae113a20bdf314d9bf16`.

Before expiry, the persisted purchase context carried sale end `2026-09-28T15:35:00Z`.

Fresh post-fix store observation at `2026-09-29T03:45:26.876365Z` classifies `App_1143810` as inactive:

- active store entry: absent;
- inactive reason: `no_active_discounted_purchase_option`;
- fresh `progressive_candidate_context.jsonl`: no `game:1143810` row.

Therefore the current binding is correctly absent because the game is outside today's GitHub-owned Progressive current scope.

## 5. PPD-010 / PPD-012 history

PPD-010 remains a finite immutable 30-target historical migration.

PPD-012 validation run `36431916442` on head `e864f882d74d26512d1430ab1632d7c93654f058` succeeded at `2026-09-28T13:53:55Z`, before the Black Skylands sale-end boundary. At that time all 30 migration targets were current and reconciled.

The current durable PASS 2 entry for Black Skylands preserves:

- original normal first-pass revision;
- completed PPD-010 legacy reanalysis attempt;
- exact work/authority provenance;
- revision history;
- no new attempt from this task.

Important correction to the worker-task prose: repository truth does **not** show Black Skylands' accepted PPD-010 result as `analyzed_not_fit`. The accepted PPD-012 report itself lists Black Skylands as completed/fit, and current immutable state records the migration result as `analyzed_fit` with `migration_fit_outcome_changed=false`. This task did not alter that outcome. `analyzed_not_fit` currentness is covered generically by other migration targets and a synthetic regression.

## 6. First divergence

This was not introduced by a semantic-state commit.

Timeline:

- `2026-09-28T13:53:55Z`: PPD-012 core run `36431916442` succeeds while Black Skylands is still in current scope;
- `2026-09-28T15:35:00Z`: known Black Skylands sale end;
- `2026-09-28T17:33:28Z`: first confirmed failing pre-AI run `36458961528`.

The pre-AI workflow rebuilds Store/current-scope files in its working tree before running the regression and commits them only after all gates pass. Therefore the first disappearance did not have a standalone repository commit: once the live store observation crossed the sale boundary, the generated current scope dropped Black Skylands, then the old regression failed before the atomic payload commit could persist that fresh scope.

The first confirmed failing checkout is `9cb123765884440d37632740d51695a371338483`; the actual scope divergence is time/live-store driven, not a semantic commit.

## 7. Root cause

Root cause: the production-history regression conflated two different sets:

1. immutable PPD-010 historical migration membership (30 frozen targets);
2. today's current Progressive eligible catalogue/binding scope.

The old invariant effectively said: “every historical migration target must remain current forever.”

That is incompatible with current-scope semantics. Expiry/commercial eligibility can legitimately remove a game from today's Progressive coverage without deleting its accepted semantic history.

The runtime/current-binding mechanism itself behaved correctly. The regression expectation was wrong.

## 8. Should game:1143810 be current?

**No current binding is expected for `game:1143810` in the fresh current Progressive scope as of this validation.**

Reason: it is no longer an active discounted current candidate, not because its semantic fingerprint/context was rewritten.

Its immutable accepted Deep history remains valid history. If Black Skylands later re-enters current Progressive scope, it may become current again only if the normal PPD-012 historical semantic-equivalence proof succeeds against that future current binding. Migration membership alone never revives it.

## 9. Changes

Implementation commit `c6ec1064d1b7b2388a84e565dfc6f23ad87d7141` updates `scripts/test_progressive_profile_semantic_identity_stability.py`:

- every one of the 30 frozen migration targets is classified individually as:
  - `current_scope_semantically_current`;
  - `current_scope_semantically_stale`;
  - `outside_current_progressive_scope`;
- a target present in current Progressive scope is still required to have a current binding;
- an out-of-scope target is required to have no current binding but still have its durable state entry;
- a semantically changed in-scope target must not be selected current;
- only current+equivalent historical completions are forbidden from ordinary re-emission;
- out-of-scope targets are also forbidden from ordinary emission because they are not in current scope;
- reconciliation remains read-only.

The same test now contains a synthetic `analyzed_not_fit` scope-exit/re-entry regression proving that commercial/current-scope absence does not mutate durable history and the same semantic identity can become current again after re-entry.

Documentation commit `5c388651d7cb26466e976738c1c7d42ed200c57c` records the PPD-010/PPD-012 current-scope invariant in `PROJECT_ROUTES.md`.

## 10. Regression coverage

Required coverage is satisfied:

1. exact pre-fix `game:1143810` failure: runs `36458961528`, `36516631678`;
2. Black Skylands fixed for the correct reason: fresh post-merge run classifies it `outside_current_progressive_scope`;
3. all 30 PPD-010 targets are emitted in the regression's per-target classification output;
4. byte-identical profile provenance-only refresh remains current: existing PPD-012 synthetic rule retained;
5. real profile content change invalidates: retained;
6. Taste model change invalidates: retained;
7. Taste semantics change invalidates: retained;
8. candidate-context semantic change invalidates: retained;
9. wrong AppID/work identity remains rejected: retained;
10. arbitrary historical result remains rejected: retained;
11. execution provenance is not rewritten: state equality/read-only assertions retained;
12. deterministic reconciliation consumes no semantic attempt: state remains byte-equivalent in the regression;
13. `analyzed_not_fit` uses the same currentness rules as `analyzed_fit`; fresh production still has current migration not-fit targets and the synthetic scope-exit/re-entry case is `analyzed_not_fit`;
14. commercial/expiry scope exit does not erase durable semantic history;
15. legitimate out-of-current-scope migration targets validate without fabricated authority.

PR validation run `36518371885` passed the full Progressive PASS 2 core suite, including the updated PPD-012 regression and legacy migration regression.

## 11. Attempt/history preservation

No semantic attempt was created or consumed by this task.

No PASS 2 state entry, migration result, revision history, positive evidence, negative assessment, Dossier binding, Fast result or Deep result was edited.

The current Black Skylands state still carries the original normal first-pass and PPD-010 migration provenance. The regression copies state before deterministic recomputation and asserts it is unchanged afterward.

## 12. Fresh-main reconciliation

Immediately before implementation merge, fresh `main` remained at `93d3c7b969fb55c25944a5707a6c1f70b1168b71`; no conflicting ЧАТ 2 commit had landed.

Implementation PR #122 merged as `1d8b54114d5aef09adb1c244a848f356987f3048`.

The normal post-merge pre-AI run then published fresh atomic payload commit `4836bea4c7c0822baa08c954cfbcfe6651ccb0d5`.

No ЧАТ 2 task file or expired-sale implementation was modified.

After the implementation/post-merge pre-AI validation, ЧАТ 2 merged PR #121 and closed its task on `main` through `0c7b2289f93b3e10d119cb61c6cdde75fffea19a`. This report closeout was rebuilt from that fresh `main`, preserving all ЧАТ 2 changes rather than merging the older closeout branch.

## 13. Pre-AI unblock validation

Post-merge `Build pre-AI deterministic payload` run `36518529454` succeeded end-to-end.

Critical evidence:

- expired-offer guard: success;
- current Store snapshot rebuild: success;
- item-level PASS 1 work build: success;
- step 18 `Regression test progressive personalization and PASS 1`: **success**, so the former `game:1143810` blocker is gone;
- PASS 2 eligibility recomputation: success;
- Russian translation runtime validation: success;
- Russian translation-scope build: success;
- atomic pre-AI commit: success.

Fresh regression output:

- migration targets total: 30;
- current+equivalent: 18;
- current+stale: 0;
- outside current Progressive scope: 12;
- Black Skylands: `outside_current_progressive_scope`;
- no current+equivalent or out-of-scope migration target was emitted as ordinary work.

Post-merge Progressive core run `36518529457` also succeeded.

## 14. Russian translation-scope evidence

The previously unreachable translation-scope stage now runs and persists normally.

Fresh translation status:

- scope records: 283;
- translation queue: 71;
- direct Russian resolved: 212;
- nontranslatable blockers: 0;
- queue SHA-256: `589adef43b55f4cda2fffc971e301d3154ecc555ff31667b22f8f8fa6aa9df60`.

Persisted required requests include:

- `App_13500` — Prince of Persia: Warrior Within™, request `27225b9f54b8d69ec53efe61680eac730e562fe5d282a0c983481b8684bc6a72`, exact source from Steam Store appdetails, `non_ru`;
- `App_1155970` — Roadwarden, request `a1d2a12697d36c96921da9d7fa655e1dc5ec5ee0896351faa4ae48b72bb57a90`, exact source from IStoreBrowseService, `non_ru`.

No translation was fabricated or manually written. Both are now governed by the normal existing translation pipeline.

## 15. Changes not made

Not changed:

- Black Skylands semantic outcome;
- any PPD-010 result or migration target;
- PASS 1/Fast semantic content;
- Dossier semantic content;
- PASS 2/Deep semantic content;
- attempt/recovery counters;
- worker prompts;
- scheduler/retry ownership;
- Scheduled Tasks;
- Russian translation cache/results;
- stale-visual rebase race;
- expired-sale UI work owned by ЧАТ 2;
- Atelier explanation mapping;
- RANK-013/ranking behavior.

## 16. Unresolved

No blocker remains for this task.

The task text's statement that Black Skylands' PPD-010 result was `analyzed_not_fit` is inconsistent with canonical accepted repository state/report, which say `analyzed_fit`. Repository truth was preserved rather than rewriting state to match the task prose.

Russian translations themselves remain pending by design; this task only restored their normal persisted scope.

## 17. Status

`complete_ready_for_director_acceptance`

## 18. Recommended next step

Director reviews and accepts this completed report; subsequent Russian translation processing remains a separate existing workflow/task.

## 19. Exact PR / commit / run / artifact refs

Implementation:

- branch: `fix/progressive-migration-current-binding-regression-01`;
- code commit: `c6ec1064d1b7b2388a84e565dfc6f23ad87d7141`;
- current-task tracking commit: `00f494e72df90c526dfa3a0678e84bfd036239aa`;
- route documentation commit: `5c388651d7cb26466e976738c1c7d42ed200c57c`;
- PR #122;
- merge: `1d8b54114d5aef09adb1c244a848f356987f3048`.

Pre-fix evidence:

- PPD-012 success before expiry: run `36431916442`, head `e864f882d74d26512d1430ab1632d7c93654f058`;
- failing pre-AI: run `36458961528`, head `9cb123765884440d37632740d51695a371338483`;
- failing post-Russian-fix pre-AI: run `36516631678`, head `c25762948500d6f64158047de01c7e4f5952911f`.

Validation:

- PR PASS 2 core: run `36518371885` — success;
- PR backlog dispositions: run `36518371882` — success;
- post-merge pre-AI: run `36518529454`, job `109246122451` — success;
- post-merge PASS 2 core: run `36518529457` — success;
- fresh atomic pre-AI payload: `4836bea4c7c0822baa08c954cfbcfe6651ccb0d5`.

No separate workflow artifact is required/created by this task; the durable evidence is the merged code, Actions logs and canonical pre-AI commit.

## 20. Efficiency / reusable lesson

A fixed historical migration set is not a perpetual current-scope set. Regression order must be:

1. determine current GitHub-owned scope;
2. require a binding for items that are actually current;
3. only then test PPD-012 semantic equivalence/current selection;
4. preserve immutable history for items outside current scope.

Also, when an atomic producer fails before commit, the repository may still contain an older “current” artifact. For time-sensitive current-scope bugs, inspect the workflow's freshly generated in-run state and live classification boundary rather than treating the last committed pre-AI payload as proof of what the failed run saw.
