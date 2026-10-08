# Deep Stage 1 — canonical manual semantic worker (NOT ACTIVE)

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Canonical interfaces: config/deep_two_stage_architecture_contract.json, config/deep_stage1_contract.json, config/deep_stage1_result_schema.json.

## Activation gate

This document describes the future bounded Deep Stage-1 semantic worker. Presence of implementation files is NOT permission to execute. Do not perform any semantic work or create any artifact unless there is a fresh explicit user launch AND a current canonical GitHub execution/activation contract expressly authorizes deep_stage1_analysis_worker. Today the architecture contract remains frozen_not_active and production_cutover_authorized=false. If not authorized, stop cleanly.

No ChatGPT Scheduled Task may be created, edited, enabled, disabled, rescheduled or simulated. This prompt does not authorize manual production backlog processing.

## START

Read the latest CHAT_PROTOCOL.md and CHAT_CONTEXT.md on main, then execution_ownership_contract.json, deep_two_stage_architecture_contract.json, deep_stage1_contract.json and deep_stage1_result_schema.json. Read only GitHub-prepared data/production/pre_ai/deep_stage1_work.json and data/cache/deep_stage1_state.json. Check implementation_status=implemented_not_active and separately verify explicit active execution authority before doing any work.

Only GitHub owns scope, order, exact item bindings, retries, recovery, validation, acceptance, and persistence. Never rebuild or expand the manifest, select a game, make a new work ID or path, skip/reorder work, or regard a result file's presence as acceptance. Do not infer an automatic retry from incomplete, transport rejection or stale evidence.

## Exact inputs per item

For each authorized item in precise ascending sequence, read only the supplied semantic_input, the exact accepted Dossier at dossier_path and verify dossier_content_sha256 and dossier_compatibility_binding, and the exact immutable pinned gaming_taste_live profile from profile_pin. Verify the pin SHA and profile_semantic_sha256 against the binding. If the exact pin or accepted Dossier is unavailable, stop that item without substituting a mutable latest profile, alternate cache or new web research.

Dossier is the factual evidence source. No new Steam reviews, web search, rumors, invented game attributes or external research may be added. Candidate factual assertions must cite exact zero-based observation/conflict indices in the bound dossier. Positive/negative personal consequences must cite exact paths in the pinned profile. Nuances may have zero profile refs when purely evidentiary. Check cited items and profile paths really exist. Do not cite raw guesses as proven evidence.

Ignore all Wishlist state, prices, discounts, sale urgency, purchase quality, published ranking, and Stage-2 comparison neighbors. Do not read Stage-2 work/anchors. A direct user rating from the exact pinned profile is powerful personalized evidence; do not add an automatic fixed arithmetic bonus for it.

## Independent semantic analysis

Decide each game's standalone match to the pinned user's taste, without ranking or comparing it to any other game. Return in this order:

1. summary_ru — concise Russian conclusion;
2. positives — all material game-specific advantages with unique finding_id, substantive Russian text_ru, exact candidate_evidence_refs (kind observation/conflict, index 0-based), and profile_evidence_refs (pinned-profile JSON path);
3. negatives — all material concrete weaknesses/risks, with the same grounded shape;
4. nuances — uncertainty, interaction effects, contradictory or limited evidence, with the same shape and optional profile refs;
5. outcome analyzed_fit / analyzed_not_fit / analysis_incomplete and confidence medium/high;
6. provisional_deep_fit_score_0_56 — 0 to 56 at 0.1 precision for analyzed_fit only;
7. point_breakdown — an explicitly game-specific, dynamically chosen set of positive/negative/neutral contributions, each with finding_refs that refer to the returned finding IDs.

The overall fit judgment is holistic. The point breakdown EXPLAINS that judgment; do not enforce predefined factor categories, fixed weights, mandatory bonuses/penalties or cross-game numeric calibration. All points must be multiples of 0.1, have sign matching direction and sum EXACTLY to the provisional score. Discuss interacting causes rather than burying material negative findings. Generic filler, ungrounded positive claims and generic formulaic scoring are prohibited.

For analyzed_not_fit, set score=null, point_breakdown=[], analysis_issue_code=null; do not force a not-fit item onto the positive comparative ladder. For analysis_incomplete, also set score=null and breakdown=[], and use an allowed analysis_issue_code: insufficient_evidence, evidence_unavailable, stage1_worker_failure, profile_binding_unresolved or dossier_binding_unresolved. Confidence must be medium/high (frozen schema).

## Immutable result and transport

Produce exactly one JSON document per authorized current work item following config/deep_stage1_result_schema.json. Copy ALL immutable binding fields exactly: schema_version=1, contract=DEEP-STAGE1-RESULT-V1, semantic_generation_id, work_id, family_id, taste_subject_key, appid, candidate_context_sha256, profile_pin_sha256=profile_pin.pin_sha256, profile_semantic_sha256, dossier_content_sha256. Do not invent extra result fields.

Immediately before each create-only submission, re-read current main manifest and state and verify exact work_id, sequence, profile pin, semantic generation, candidate digest, accepted Dossier SHA/binding and result_submission_path remain unchanged and the item has not been canonically accepted. If stale, submit nothing. Write the JSON ONLY to the manifest's exact result_submission_path, create-only; do not overwrite, rename or choose an alternative path.

The transport is not acceptance. GitHub-owned scripts/ingest_deep_stage1.py alone validates and persists accepted results and receipts. Never write canonical Stage-1 state/results or any Dossier, Fast, Stage-2, Wishlist, ranking, purchase, site, production or Scheduled Task data. Stop after the exact authorized work; no self-managed retry/checkpoint loop.
