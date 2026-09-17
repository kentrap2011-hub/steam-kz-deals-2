# WORKER TASK — Taste Dossier Language Binding Fix Implement 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-language-binding-fix-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## Goal

Fix the proven production defect from `taste-dossier-parallel-buffer-live-acceptance-02` at the system level so Scheduled ChatGPT stops producing dossiers where an observation claims Russian evidence while all bound player-feedback records are non-Russian.

Do not build retry/healing logic around the bad group. The intended response is to improve the contract/prompt/generation constraints so the bad shape is not produced again, while keeping the existing strict validator fail-closed.

Also update the stale `PROJECT_ROUTES.md` section that still describes the superseded requirement for Scheduled ChatGPT to run repository Python before publication.

## Read first / START gate

Follow `CHAT_PROTOCOL.md` START gate fully. Read the minimum relevant canonical material, including:

- `CHAT_CONTEXT.md`;
- `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md`;
- `config/execution_ownership_contract.json`;
- active Taste dossier contract/schema/web-evidence contract/worker prompt;
- `reviews/worker_reports/taste-dossier-parallel-buffer-validation-implement-01.md`;
- `reviews/worker_reports/taste-dossier-parallel-buffer-live-acceptance-01.md`;
- `reviews/worker_reports/taste-dossier-parallel-buffer-live-acceptance-02.md`;
- strict validation and focused regression files relevant to language binding.

Run architecture preflight before implementation.

## Proven defect to close

Live `g000002`, specifically the `Blacksad: Under the Skin` dossier, failed strict validation with:

`observation 1 claims Russian evidence without Russian player-feedback record`

The observation declared Russian in `evidence_languages`, while all bound feedback records for that observation were marked `non_russian`.

The validator correctly rejected this. The defect is therefore not that GitHub accepted bad data; the defect is that the Scheduled worker contract/prompt still permits or encourages generation of this internally inconsistent shape, wasting a candidate group and blocking canonical progress.

## Required outcome

Implement the smallest systemic fix that makes language claims mechanically coherent with the feedback records actually bound to each observation/conflict.

Preferred invariant:

- observation/conflict language claims must be derived from, or exactly consistent with, the languages of their bound `player_feedback_ids`;
- `russian` may appear only when at least one bound feedback record is Russian or mixed in the contract-defined sense;
- `non_russian`-only bound records cannot support a Russian evidence claim;
- do not infer language from a store page, page locale, title language, search query language, or surrounding source metadata;
- do not weaken the existing strict rejection rule.

If the cleanest design is to eliminate a redundant free-form field and derive it deterministically, do so only if compatible with the current contract and downstream consumers. Otherwise keep the field but make the generation rule explicit and mechanically testable.

Do not introduce another validator truth source. GitHub canonical strict validation remains authoritative.

## Prompt/contract alignment

Update the active Scheduled worker instructions so the rule is unambiguous at generation time, not only discoverable after GitHub rejects the artifact.

The worker should be told in plain operational terms to:

- determine record language first;
- bind exact feedback records to each observation/conflict;
- derive the observation/conflict language summary only from those bound records;
- never mark Russian merely because a Russian-language search was attempted or a Russian-rendered page was opened.

Preserve the existing Russian-attempt bidirectional rule.

## Regression requirements

Add/adjust focused tests proving at least:

1. the exact live Blacksad failure shape is rejected;
2. the worker-facing contract/prompt explicitly prevents that shape before publication;
3. non-Russian-only bound feedback cannot yield `russian` in observation/conflict language claims;
4. one genuinely Russian/mixed bound record permits the correct Russian language claim;
5. Russian search attempt without Russian bound feedback does not permit a Russian claim;
6. existing RU-attempt, source binding, recurrence, recency, privacy, item identity, conflict, compatibility-binding, package-member and parallel-buffer regressions remain green;
7. group size remains 3 and GitHub contiguous-prefix behavior is unchanged.

If there are parallel fields for observations and conflicts, cover both.

## Stale route cleanup

Update the relevant `PROJECT_ROUTES.md` section so it accurately describes the active architecture:

- Scheduled ChatGPT publishes create-only candidate groups without local repository Python execution;
- GitHub asynchronously performs strict validation and accepts only the maximal contiguous valid prefix;
- later groups may remain buffered behind an invalid group;
- local repository Python is not a Scheduled runtime prerequisite.

Do not broaden this into unrelated documentation cleanup.

## Compatibility / activation

Because active semantic prompt/contract content will likely change, preserve the content-complete compatibility-binding rules already implemented.

Requirements:

- let the normal GitHub-owned activation create a fresh compatible snapshot/binding as required;
- old invalid `g000002`/later buffered artifacts from the prior snapshot must become stale/inert/quarantined through the existing normal mechanism;
- do not manually repair, overwrite, or delete the invalid candidate;
- do not create a corrected artifact under the old snapshot;
- do not run Scheduled Task `Run now` during this task;
- group size remains 3.

## Architecture invariants / prohibitions

Do not:

- move canonical control from GitHub to ChatGPT;
- reintroduce local Python execution in Scheduled ChatGPT;
- add retry/healing/per-game repair logic;
- split groups by game;
- weaken strict validation;
- change downstream Taste/ranking/pricing/commercial behavior;
- use another repository.

## PR / CI / activation

Use normal worker branch -> PR -> canonical CI -> merge -> automatic GitHub-owned activation.

After merge validate the fresh snapshot/index/group descriptors, compatibility binding, truthful zero-or-current progress, stale handling of the previous snapshot, and group size 3.

Do not run Scheduled Task.

## Definition of Done

Complete only when:

- the live language-binding defect is closed at generation-contract level;
- the strict validator remains at least as strong as before;
- deterministic tests cover the exact failure and valid Russian/non-Russian cases;
- `PROJECT_ROUTES.md` matches the active parallel-buffer architecture;
- normal compatibility activation succeeds;
- prior invalid snapshot artifacts cannot contaminate the fresh plan;
- no retry/healing/per-game architecture was added;
- durable report is in `main`.

Allowed final statuses:
- `complete_ready_for_live_acceptance`
- `blocked`

## Durable report

Publish to:

`reviews/worker_reports/taste-dossier-language-binding-fix-implement-01.md`

Report must include:

- architecture preflight;
- exact root cause of the live Blacksad defect;
- exact generation invariant added;
- whether language is derived or explicitly constrained;
- prompt/contract/schema/validator changes and why;
- regression proof;
- `PROJECT_ROUTES.md` correction;
- PR/merge/CI refs;
- post-merge activation result and fresh snapshot/binding/counts/first group;
- proof prior invalid artifacts are stale/inert;
- confirmation group size remains 3;
- confirmation no Scheduled Task `Run now` occurred;
- remaining risks;
- exactly one next step.

On success, next step should be a separate live acceptance run after the independent semantic-consistency audit has also been reviewed by the Director.

Ensure the durable report is in `main` before completion. Stop after report publication.