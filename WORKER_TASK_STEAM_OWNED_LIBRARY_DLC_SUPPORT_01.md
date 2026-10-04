# WORKER TASK — Steam owned library and DLC support 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base/source of truth: `main`

## Mode
RECON / CONTRACT first. Implement only if the repository already has a safe canonical credential/data path or after the required contract is explicitly established.

## Goal
Learn how to obtain the user's owned Steam games safely and durably, then use that ownership set to extend DLC discovery.

Current temporary behavior from the hard-50 task:
- DLC is considered only when its base game passes normal suitability/eligibility.

Target behavior after this task:
- DLC may be considered when its base game is either:
  1. a normally suitable/eligible game; **or**
  2. owned by the user in Steam.

Ownership does not automatically make a DLC good. DLC must still pass the normal quality/value/current-sale rules.

## Required investigation
Determine the best current Steam-supported method to obtain the user's owned games, including:
- exact identifier required;
- whether the library must be public;
- whether an API credential is required;
- where any secret may safely live under the existing repository/GitHub architecture;
- refresh frequency and failure behavior;
- how AppIDs are normalized and persisted;
- how ownership freshness is shown to the user.

Do not ask the user to publish a secret in repository files.

## Architecture requirements
- GitHub remains control plane and canonical owner of the owned-game snapshot.
- Do not create a ChatGPT recurring worker to poll the Steam library.
- Reuse an existing GitHub secret/runtime path if one is suitable; otherwise propose the smallest explicit contract change.
- Ownership is context, not taste evidence and not a positive ranking bonus by itself.

## DLC behavior
After a current owned-game snapshot exists:
- resolve DLC -> base-game relation deterministically;
- allow DLC into the normal candidate path only when the base AppID is suitable/eligible or in the owned-game set;
- preserve ordinary DLC quality/value checks;
- expose why the DLC was admitted: `base_suitable` or `base_owned`;
- do not recommend DLC merely because the user owns the base game.

## Acceptance
- exact owned-game acquisition method documented and validated on a bounded test;
- secrets, if any, never appear in committed files or site data;
- owned AppID snapshot has provenance/freshness;
- regression tests cover owned-base DLC, suitable-but-unowned-base DLC, and unrelated DLC;
- no new independent scheduler or ChatGPT Scheduled Task;
- durable report written to:
  `reviews/worker_reports/steam-owned-library-dlc-support-01.md`.
