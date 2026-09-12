# WORKER TASK — Taste Steam review dossier preparer 01

Task ID: `taste-steam-review-dossier-preparer-01`

Status: `planned_waiting_user_authorization`

Mode when authorized: `IMPLEMENT_AND_VALIDATE`

## Goal

Create a separate pre-Taste preparation stage that produces one compact, neutral, reusable dossier per Steam game from Steam-native information. The downstream Taste semantic worker must consume this prepared dossier plus the canonical user Taste profile instead of spending its own execution time searching the web or trying to infer grounded personal negatives from a store description alone.

This stage is separate from `Taste Semantic Producer`. It is intended to become its own ChatGPT Scheduled Task only after the mechanism is implemented and validated. Do not create or modify Scheduled Tasks in this implementation task unless separately authorized by the user/Director.

## User decisions already fixed

1. Steam reviews are sufficient as the review source for this stage.
2. The dossier preparer may inspect the Steam information it considers materially useful for understanding the game, including the Steam store description and Steam user reviews.
3. Russian-language reviews must be included because they may reveal Russian localization / translation / voice-over problems that are absent from non-Russian reviews.
4. Do not store thousands of raw reviews per game. Persist a compact synthesis instead.
5. The dossier itself must be neutral/objective. It must not decide whether a fact is good or bad for Dmitry and must not write personalized conclusions such as “Dmitry will dislike this”. Personal interpretation belongs to the downstream Taste worker.
6. The downstream Taste worker should have one concrete prepared place containing the game information it needs and should not perform its own web/review search during normal evaluation.
7. Review sampling should be adaptive rather than a user-chosen fixed count: inspect enough Russian and other Steam reviews to form a stable picture, read more when opinions are conflicting or evidence is sparse, and stop when additional reviews are no longer materially changing the synthesis, subject to a reasonable bounded technical ceiling chosen during implementation.
8. Each dossier must record its creation date. Default freshness TTL is **20 days**, configurable rather than hard-coded into business logic.
9. At or after TTL expiry the dossier is stale and must not be used as fresh evidence. If the game is needed again, regenerate and replace it before Taste evaluation.
10. Stale dossiers not currently needed may be removed by regular cleanup so the store does not grow without bound.
11. Regeneration should replace the old dossier rather than accumulating unlimited historical copies unless a small amount of provenance/version metadata is required for correctness.

## Required dossier content

For each game/appid, persist enough structured information for a later Taste worker to understand the real game without reading raw reviews itself. At minimum include:

- `appid` and canonical title;
- `generated_at_utc`;
- `expires_at_utc` derived from configurable TTL (default 20 days);
- neutral concise description of what the game actually is / how it plays;
- important mechanics, structure, pacing, progression, repetition, difficulty/friction, multiplayer/co-op dependence and other materially recurring characteristics when supported by Steam information;
- recurring positive observations from players;
- recurring complaints / negative observations from players;
- Russian-localization / translation / voice / font / encoding / regional issues when found in Russian reviews;
- areas where player opinions materially conflict;
- indication of recurrence / support strength for synthesized observations (for example recurring / occasional / isolated, or a similarly bounded schema);
- counts or coverage metadata sufficient to know how much Russian and non-Russian review evidence was examined;
- source/provenance metadata sufficient to reproduce or audit the dossier without storing the full raw review corpus.

The exact schema is an implementation decision, but it must remain compact, machine-readable and stable enough for downstream semantic consumption.

## Semantic boundary

The preparer describes **facts and recurring player experience**.

It must NOT:
- score personal Taste fit;
- map observations to Dmitry-specific positives/negatives;
- choose INCLUDE/EXCLUDE;
- invent a personal negative;
- use price/discount/commercial urgency as Taste evidence.

The downstream Taste worker receives:
1. the fresh prepared dossier;
2. the canonical Taste profile;
3. the existing exact pinned work-unit/bindings;
and decides which dossier observations are positive, negative or low-importance specifically for the user.

A recurring public complaint is evidence that a game property/problem exists; it is not automatically a personal negative. The Taste worker must still connect it to the user profile.

## Freshness / lifecycle

Default dossier TTL: `20 days`.

Required behavior:
- fresh dossier: reusable without re-fetching reviews;
- missing dossier: prepare before Taste evaluation;
- stale dossier needed by current Taste scope: refresh/replace before Taste evaluation;
- stale dossier not needed: may be deleted by cleanup;
- cleanup and refresh must not leave Taste believing a stale dossier is fresh;
- TTL must be configuration-driven so it can later become e.g. 14 or 30 days without architecture changes.

Do not require all dossiers in the Steam catalog to exist permanently. Prepare/retain only the bounded set useful to current/future Taste work under the freshness policy.

## Integration requirement

The canonical daily sequence should ultimately become conceptually:

`GitHub prepares needed game scope -> separate Steam dossier preparer ensures fresh dossiers -> Taste Semantic Producer evaluates exact pinned games using dossier + Taste profile -> canonical ingest/persistence`

Do not make the Taste worker fall back silently to web search when a required dossier is missing/stale. The control plane must expose the missing prerequisite and fail/hold that item until a fresh dossier is available.

## Current throughput measurement impact

The existing 2026-09-12 throughput run remains valid historical evidence that 50 semantic work-items were durably accepted, but it is **not a valid final capacity measurement for full game evaluations** because:
- the run also spent time implementing/fixing mechanism defects;
- the current Taste input did not provide enough review detail for grounded negative analysis;
- negative-backfill consequently consumed later checkpoints.

Do not continue or finalize the old throughput measurement as the final capacity benchmark.

After this dossier mechanism is implemented and validated, Director should authorize a **new clean throughput measurement** in a fresh ordinary ChatGPT worker run. That measurement should:
- start with the mechanism already working;
- spend the run on actual Taste evaluation rather than implementation/debugging;
- use fresh dossiers;
- checkpoint durably in tens as already specified;
- record exact start/checkpoint/stop timing and the concrete stop reason so platform/tool-run limits can be characterized separately from semantic throughput.

## Scope boundaries

Do not in this task:
- implement age-priority queue ordering;
- change the final Taste production limit;
- modify existing `Taste Semantic Producer` Scheduled Task;
- create the separate dossier Scheduled Task without separate user/Director authorization;
- turn review sentiment percentage alone into Taste evidence;
- store unlimited raw review text;
- redesign unrelated Steam commercial crawling.

## Validation

Demonstrate at least:

1. a game with fresh dossier is reused without unnecessary re-analysis;
2. a stale dossier is rejected/refreshed before Taste consumption;
3. default TTL is 20 days and configurable;
4. Russian review evidence can produce a localization-related neutral dossier finding;
5. recurring negative Steam observations can be represented without becoming a Dmitry-specific negative in this preparer;
6. downstream Taste input contains the prepared dossier data needed to reason about positives/negatives;
7. missing/stale required dossier cannot silently fall back to store-description-only Taste evaluation;
8. storage remains synthesis/provenance based rather than raw-review archive based;
9. existing canonical pin/ingest authority remains intact.

## Durable report

Write:
`reviews/worker_reports/taste-steam-review-dossier-preparer-01.md`

Report must state:
- implemented architecture and files;
- dossier schema;
- review acquisition/sampling strategy actually used;
- Russian-review handling;
- TTL/cleanup behavior;
- downstream Taste integration behavior;
- validations run and results;
- whether the mechanism is ready for a separate Scheduled Task and a new clean throughput measurement.

## Allowed final statuses

- `complete_ready_for_separate_scheduler_and_clean_throughput_measurement`
- `blocked_requires_followup`
