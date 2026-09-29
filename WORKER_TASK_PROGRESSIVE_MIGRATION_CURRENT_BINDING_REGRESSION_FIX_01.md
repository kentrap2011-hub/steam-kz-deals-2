# WORKER TASK — PROGRESSIVE MIGRATION CURRENT-BINDING REGRESSION FIX 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `progressive-migration-current-binding-regression-fix-01`
Mode: `DIAGNOSE -> CONTRACT-FIRST IMPLEMENT / VALIDATE`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/progressive-migration-current-binding-regression-fix-01.md`

## User decision

Fix the current Progressive pre-AI blocker:

`AssertionError: migration target missing current binding: game:1143810`

Do not patch only `game:1143810` by hand. First prove why the canonical current binding disappeared or became unresolvable, then fix the generic mechanism that allowed this state.

## Known identity

- family: `game:1143810`
- AppID: `1143810`
- title: `Black Skylands`

The previously accepted PPD-012 report proved this game had a current reconciled authoritative Deep result:
- source: `progressive_pass2`
- PPD-010 migration result: `analyzed_not_fit`
- currentness restored through PPD-012 historical semantic-equivalence logic.

Therefore the current failure must not be dismissed as “this migration target never had a current result.” Determine what changed after that accepted state.

## Why this task exists now

The accepted Russian-description blocker fix is merged, but the normal pre-AI workflow cannot reach the Russian translation-scope step because it fails earlier on this Progressive regression.

Confirmed runs:
- pre-existing failing pre-AI run: `36458961528`
- fresh post-Russian-fix failing pre-AI run: `36516631678`
- both fail in `scripts/test_progressive_profile_semantic_identity_stability.py` with the same missing-current-binding assertion for `game:1143810`.

This blocker existed before PR #119 and was not caused by the Russian-description fix.

Until this is repaired:
- App_13500 cannot have its newly valid translation request persisted through the normal pre-AI route;
- Roadwarden translation work also remains unresolved;
- fresh canonical visual publication remains blocked.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and complete its START gate.

Then read:
1. this task fully;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. PPD-010 and PPD-012 decisions in `PROJECT_DECISIONS.md`;
4. accepted report `reviews/worker_reports/progressive-profile-semantic-identity-stability-fix-01.md`;
5. accepted PPD-010 migration task/report;
6. `config/progressive_personalization_contract.json`;
7. `config/progressive_pass2_contract.json`;
8. `config/execution_ownership_contract.json`;
9. `scripts/test_progressive_profile_semantic_identity_stability.py`;
10. only the smallest current Progressive state/work/reconciliation code and data required to prove the failure.

Do not begin unrelated work.

## Mandatory architecture preflight

Before writes prove:

- GitHub remains sole owner of semantic identity/generation, historical-equivalence selection, migration/current-result reconciliation, work identity, attempt accounting and persistence;
- Scheduled ChatGPT remains bounded semantic execution only;
- no semantic result may be rewritten merely to make a test pass;
- no completed PPD-010 migration result may be duplicated or re-run merely because a current binding is missing;
- exact historical execution provenance must remain immutable;
- PPD-012 content-semantic equivalence must remain fail-closed;
- real profile/model/taste-semantics/candidate-context changes must still invalidate currentness;
- no scheduler/retry/backlog/Scheduled Task ownership changes;
- no Dossier/Fast/Deep semantic worker execution is authorized by this task.

## Phase A — exact diagnosis

Pin a fresh failing `main` state and determine exactly what “current binding” the regression expects for `game:1143810`.

Trace all of the following for Black Skylands:

1. current catalogue/candidate presence;
2. current semantic generation and profile semantic identity;
3. current item/taste fingerprint and candidate-context identity;
4. current PASS 2 state entry/revision history;
5. PPD-010 migration revision and immutable migration authority;
6. PPD-012 historical semantic-equivalence proof inputs;
7. current effective-result selection;
8. any current work/pre-AI binding map used by the regression;
9. whether the game is now filtered commercially/expired/not visible and whether that is incorrectly conflated with semantic currentness;
10. exact commit where the expected current binding first disappeared, if determinable without broad archaeology.

Classify the root cause precisely, for example:
- current candidate/context identity legitimately changed and the regression wrongly assumes every historical migration target remains current;
- historical equivalence remains valid but one deterministic current-binding index fails to project it;
- migration target is intentionally outside current scope but regression treats absence as an error;
- current binding generation dropped analyzed_not_fit items;
- a profile/context refresh changed an identity field that PPD-012 should or should not treat as semantic;
- another exact mechanism.

Do not implement until this is proven.

## Required decision test

The worker must explicitly answer:

**Should `game:1143810` be current under today's canonical semantic identity, or should the regression stop requiring it to be current?**

Those are materially different fixes.

- If it SHOULD be current: repair the generic current-binding/reconciliation path.
- If it SHOULD NOT be current because a real semantic identity changed: repair the regression/expectation so it validates the correct invariant without reviving stale semantic truth.
- Never force the result current solely because it appeared in the old 30-game migration.

## Phase B — implementation

Implement the smallest generic correction supported by the diagnosis.

Hard requirements:
- no AppID-specific runtime bypass;
- AppID may appear only in focused regression fixtures/expected historical target data;
- preserve PPD-010 immutable migration history;
- preserve PPD-012 separation of semantic identity vs execution provenance;
- preserve one-attempt/recovery accounting;
- do not create fake accepted results;
- do not copy/relabel an old result to a new semantic identity;
- do not make arbitrary historical results reusable;
- do not modify Fast/Dossier/Deep semantic contents.

## Required regressions

At minimum prove:

1. exact current `game:1143810` failure reproduces before the fix;
2. the fixed invariant passes for Black Skylands for the correct reason;
3. all 30 PPD-010 migration targets retain correct current/stale classification individually;
4. byte-identical profile provenance-only commit refresh remains current under PPD-012;
5. real profile content change still invalidates;
6. Taste model change still invalidates;
7. Taste semantics binding change still invalidates;
8. candidate-context semantic change still invalidates;
9. wrong AppID/work identity remains rejected;
10. stale arbitrary historical Deep result remains rejected;
11. exact execution provenance remains unchanged;
12. no semantic attempts are consumed by deterministic reconciliation;
13. analyzed_not_fit currentness is handled consistently with analyzed_fit and is not dropped merely because the card is not visible;
14. commercial/expiry visibility filtering cannot incorrectly erase semantic currentness if contracts separate those layers;
15. if a migration target is legitimately no longer current, the regression validates that state without inventing authority.

## Pre-AI unblock validation

After merge, validate the normal GitHub-owned pre-AI path.

Required evidence:
- `scripts/test_progressive_profile_semantic_identity_stability.py` passes;
- `Build pre-AI deterministic payload` gets past the former `game:1143810` failure;
- it reaches the Russian-description translation-scope step that was previously unreachable;
- the current App_13500 translation request can be generated/persisted normally if still required by fresh `main`;
- Roadwarden remains governed by the same normal translation pipeline;
- do not manually execute or fabricate semantic translations.

If another independent blocker appears later in pre-AI, report it precisely and stop rather than broadening scope.

## Publication boundary

This task is not the stale-visual rebase-race fix.

Do NOT silently repair:
- the visual stale-snapshot rebase race;
- Russian description semantic translations themselves;
- expired-sale UI work active in ЧАТ 2;
- Atelier positive-explanation mapping;
- ranking/RANK-013.

If pre-AI becomes healthy but publication later remains blocked by one of those independent issues, report the exact next blocker.

## Interaction with active ЧАТ 2

ЧАТ 2 is currently working on:
`WORKER_TASK_EXPIRED_SALE_IMMEDIATE_VISIBILITY_FIX_01.md`

Do not modify or overwrite its files/work.

Reconcile fresh `main` before PR/merge because ЧАТ 2 may advance the branch concurrently.

## Hard prohibitions

Do not:
- run Fast/Dossier/Deep semantic workers;
- manually change a Deep outcome;
- manually create a current binding for AppID 1143810;
- rerun PPD-010 migration semantics;
- reset Progressive state;
- weaken semantic identity matching;
- bypass the failing test;
- modify Russian translation cache manually;
- change Scheduled Tasks.

## Report

Write:
`reviews/worker_reports/progressive-migration-current-binding-regression-fix-01.md`

Required sections:
1. `Task`
2. `Architecture preflight`
3. `Pinned failure`
4. `Black Skylands current identity`
5. `PPD-010 / PPD-012 history`
6. `First divergence`
7. `Root cause`
8. `Should game:1143810 be current?`
9. `Changes`
10. `Regression coverage`
11. `Attempt/history preservation`
12. `Fresh-main reconciliation`
13. `Pre-AI unblock validation`
14. `Russian translation-scope evidence`
15. `Changes not made`
16. `Unresolved`
17. `Status`
18. `Recommended next step` — exactly one bounded next step or `none`
19. exact PR/commit/run/artifact refs
20. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete_ready_for_director_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Do not start another task after this one.
