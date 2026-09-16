# WORKER TASK — Taste Package / Edition Quality RECON 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If a tool opens another repository by default, stop and switch back to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-package-edition-quality-recon-01`
Mode: `READ-ONLY / RECON`

## Goal
Determine the correct architectural place, data model, evidence source, and scoring/warning behavior for the quality of a specific package/remaster/edition separately from the Taste quality of its member games.

No implementation in this task.

## Product decision to preserve
For a multi-game package/collection/remaster edition:

- member games are evaluated independently for Taste;
- if at least one member game is a sufficiently good match, the package is NOT hard-excluded at the Taste stage;
- weak member games do not simply average down a strong member;
- quality problems of the specific edition/package may be a very strong negative signal;
- that negative signal must be prominently visible to the user and must materially reduce the existing final score/ranking;
- it must NOT directly hard-exclude the package at the Taste stage;
- if the resulting existing total score falls below the normal inclusion threshold, the product may disappear naturally there.

Control example:
`GTA: The Trilogy – Definitive Edition` may contain strong personal matches such as Vice City or San Andreas while the Definitive Edition itself has a poor technical/release reputation. The system should preserve the package as a candidate because of the strong member(s), but separately carry a strong edition-quality warning/penalty so it ranks low if warranted.

DLC is not the target of this RECON. Do not redesign DLC behavior.

## Read first
- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- relevant `PROJECT_ROUTES.md`
- relevant `PROJECT_DECISIONS.md`
- current ranking/score policy and contracts
- current Taste evidence/dossier schema and review evidence contracts
- package/member commercial model and package-quality/risk fields if any
- `reviews/worker_reports/taste-dossier-identity-edge-case-audit-01.md`
- `reviews/worker_reports/taste-dossier-package-identity-fix-01.md`
- `WORKER_TASK_TASTE_PACKAGE_MEMBER_DOSSIER_AGGREGATION_01.md`
- `config/execution_ownership_contract.json`

Run architecture preflight.

## Questions to answer
1. Where should the package/edition-quality signal canonically live so that it is separate from member-game Taste and does not create a second ranking system?
2. Can the existing dossier ordinary-web evidence model gather evidence about the quality of the specific edition/package, or does that need a distinct bounded evidence object linked to the offer?
3. What exact identity should research use for edition quality (package/Sub identity, collection App identity, edition title/year, member version identity, etc.)?
4. How can the system distinguish durable game-quality criticism from edition-specific criticism such as bugs, performance, missing content, bad remastering, altered graphics/audio, launcher/DRM issues, or poor port quality?
5. How should recent evidence be weighted for technical problems that may have been fixed after launch?
6. Which existing visible score/risk component can carry a strong penalty without adding a competing final sort formula?
7. What existing warning/explanation surface can make severe edition-quality problems prominent to the user?
8. What severity/confirmation states are needed so weak or anecdotal complaints do not cause an excessive penalty?
9. How should the rule behave if an edition has strong member-game Taste but severe edition-quality problems?
10. What should happen if edition-quality evidence is unavailable or ambiguous? Fail neutral vs fail closed must be justified.

## Required architecture constraint
Do not create a separate final ranking or hidden package-specific score system. Reuse the existing canonical final-score/risk architecture if feasible.

Taste fit of member games and edition/package quality must remain separate dimensions. Price/commercial value also remains separate.

## Evidence model considerations
RECON should consider at least:
- current/recent player feedback for technical state;
- durable criticism of edition/remaster changes;
- multiple independent sources where practical;
- Russian-language evidence where localization/voice/font/regional issues matter;
- no raw review bodies persisted;
- no launch-only issue treated as current when newer evidence shows it fixed.

Do not perform broad live research for hundreds of products. Use only a few bounded control examples sufficient to validate the proposed model, if repository/browser access makes that appropriate.

## Required output
Produce a concrete proposal containing:
- canonical data owner/location;
- proposed compact schema/fields;
- evidence freshness/status rules;
- severity/confirmation model;
- exact connection to existing final score/risk components;
- exact warning/explanation behavior;
- fail-neutral/fail-closed behavior when evidence is missing;
- interaction with member-game Taste aggregation;
- one or more regression control examples, including a GTA Definitive Edition-style case;
- implementation boundaries and files/areas likely affected;
- whether implementation should be one task or split into evidence acquisition vs ranking integration.

## Restrictions
- READ-ONLY except durable report publication.
- Do not modify schemas, code, ranking policy, prompts, production data, workflows, Scheduled Tasks, or PR #31.
- Do not press `Run now`.
- Do not change Taste Semantic Producer.
- Do not create a second scoring/ranking mechanism.
- Do not use any other repository.

## Durable report
Publish to `main`:
`reviews/worker_reports/taste-package-edition-quality-recon-01.md`

Report must include:
- architecture preflight;
- findings for all 10 questions;
- proposed data/evidence/severity model;
- integration with existing scoring/risk/warning surfaces;
- control examples;
- implementation task breakdown;
- exactly one recommended next step.

Allowed final statuses:
- `complete`
- `blocked`

Do not change `CURRENT_TASK.md`.
Stop after durable report.