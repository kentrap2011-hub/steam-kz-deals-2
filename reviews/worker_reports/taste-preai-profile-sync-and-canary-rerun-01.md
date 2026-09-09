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

## Progress
Report created durably in `main` before any task mutation. Required reading and architecture preflight are in progress.
