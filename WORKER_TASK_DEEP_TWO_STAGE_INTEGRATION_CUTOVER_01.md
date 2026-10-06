# WORKER TASK — Deep two-stage integration and cutover 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Dependencies: the architecture-freeze, Stage-1 worker, Stage-2 worker, Fast/ranking migration, and site-mirror tasks must all be accepted first.
Mode: `INTEGRATE / MIGRATE / VALIDATE / CUTOVER`

Frozen interfaces (integration may activate but must not silently redefine):
- `config/deep_two_stage_architecture_contract.json`
- `config/deep_stage1_contract.json`
- `config/deep_stage1_result_schema.json`
- `config/deep_stage2_contract.json`
- `config/deep_stage2_result_schema.json`
- `config/deep_two_stage_site_projection_contract.json`
- `config/deep_two_stage_migration_contract.json`
- `config/deep_two_stage_dependency_map.json`

Integrate the independently implemented pieces.

Required:
- classify current legacy Deep results into reusable Stage-1-compatible vs semantic reanalysis required;
- prepare exact migration/calibration queues;
- ensure no mixed legacy score authority;
- prove Fast has zero production ranking authority;
- prove Wishlist +4 and 60/40 composition;
- prove Stage-1 provisional score never appears as final;
- prove Stage-2 calibrated order and displayed personal scores are monotonic/unique;
- prove site Statistics and detail view mirror canonical state;
- run bounded end-to-end acceptance.

Do not invent semantic results. If semantic Stage-1/Stage-2 execution is needed, prepare exact manual worker instructions and stop at the authorized boundary rather than fabricating completion.

No Scheduled Task changes unless separately authorized by the user.

Report: `reviews/worker_reports/deep-two-stage-integration-cutover-01.md`.
