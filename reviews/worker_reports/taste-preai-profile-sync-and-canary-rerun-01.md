# taste-preai-profile-sync-and-canary-rerun-01

## Status
`in_progress`

## Task
Synchronize canonical pre-AI Taste state once against the current live recommendation profile, then rerun only `Chernobylite Complete Edition` (`App_1016800`, AppID `1016800`) through the same generation-2 Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`, verify normal canonical acceptance, and restore/verify DAILY 01:00 Europe/Samara without widening production or starting System Audit.

## Scope guard
- one bounded canonical pre-AI regeneration attempt only;
- no manual profile/binding SHA substitution;
- no second Scheduled Task;
- no other game;
- no mass/backlog semantic analysis;
- no System Audit.

## Checkpoint
- Required task/protocol/ownership files were read.
- Current live recommendation profile was read from `kentrap2011-hub/stopgame-ratings-data/gaming_taste_live.json`; pre-regeneration blob SHA observed: `cfc12e032723c7a442ffaca8985f2b8f01875d00`.
- Canonical pre-AI generation path was confirmed to be GitHub-owned and atomic (`scripts/refresh_pre_ai_payload.py` plus the existing production workflow chain); generated bindings will not be hand-edited.
- Existing production workflow run `34274404165` / original `collect` job `102223729156` was identified. Its canonical production path had previously produced the atomic pre-AI refresh commit `4662895180d40ac8c503dc94d816fb62425c1d97`.
- Exactly one bounded rerun was initiated through the existing GitHub Actions job, not by creating or editing a workflow: new rerun job id `102329869100`.
- At this checkpoint, rerun job `102329869100` is `in_progress`; Steam catalog collection is running. No second rerun will be attempted even if the profile changes again.
- No Scheduled Task mutation or semantic canary execution has occurred yet in this task.

## Next gate
Wait for the one bounded canonical regeneration chain to finish, then re-read the current live profile and prepared pre-AI binding exactly once. If they differ, stop fail-closed and finalize without chasing the profile. If they match, bind and run only Chernobylite through Scheduled Task `6aa032f37e688191a5c9a1a83f91c5d9`, verify canonical acceptance/queue advancement, and restore/verify permanent 01:00 Europe/Samara.
