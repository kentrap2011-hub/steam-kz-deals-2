### Task

Реализован GitHub-owned structured duration enrichment по canonical `DURATION-ENRICHMENT-V1` без ручного lookup игр и без изменения scoring.

Production route теперь имеет все необходимые implementation-компоненты:

`current GitHub production scope -> exact Steam appids -> IGDB External Game identity -> IGDB game_time_to_beats -> normally/3600 -> data/cache/duration_estimates.json -> final visual builder -> existing duration ranking bands`.

Primary collection остаётся GitHub/GitHub Actions direct. Scheduled/interactive ChatGPT не получил queue, retry state, catalog scope или recurring duration stage.

### Verified facts

- `scripts/duration_enrichment.py` реализует Twitch OAuth2 client-credentials и server-side IGDB API access.
- Expected GitHub Secrets зафиксированы как `IGDB_CLIENT_ID` и `IGDB_CLIENT_SECRET`; secret/token values никогда не пишутся в repository artifacts/logical cache schema.
- Exact collection scope GitHub выводит из текущего production input `data/production/pre_ai/chatgpt_purchase_context.jsonl` -> `semantic_condition.base_appids`; title/fuzzy matching для построения scope не используется.
- Steam identity определяется через текущий IGDB `external_game_source`: implementation получает source table и принимает ровно один source с именем `Steam`. Deprecated `category` и legacy numeric Steam enum не используются.
- Для каждого appid допускается только exact External Game `uid == Steam appid` под доказанным Steam `external_game_source`. Missing/ambiguous/wrong-source mapping fail closed.
- IGDB raw `game_time_to_beats` сохраняет `hastily`, `normally`, `completely`, `count`, IGDB/Steam identity и provider timestamps/checksum where returned.
- Canonical estimate детерминированно равен `normally_seconds / 3600`; нулевой/отсутствующий/invalid `normally` не превращается в `0 hours`, а остаётся unresolved/unknown.
- Canonical cache создан по path `data/cache/duration_estimates.json`. Он appid-keyed, durable и provenance-preserving. В рамках этой задачи cache остаётся пустым, потому что credentials отсутствуют и реальные provider calls не выполнялись.
- Long-lived freshness реализована через `refresh_after_utc`: confirmed 180 days, durable unresolved 30 days, transient operational retry 60 minutes. Все known entries не refetch-ятся nightly без причины.
- Transient `auth_failure` / `transport_failure` не перезаписывает существующий confirmed или durable negative result; он сохраняется только как last-attempt metadata для уже существующего состояния.
- Provider pacing последовательно ограничен примерно одним запросом каждые 0.26s, то есть не превышает provider limit 4 req/s; параллельные IGDB requests implementation не запускает, поэтому <=8 concurrent также соблюдается. Эти limits не трактуются как production quota.
- `scripts/build_final_visual_payload.py` теперь использует precedence: validated structured IGDB `normally` -> legacy explicit-text compatibility fallback -> unknown.
- Structured duration provenance публикуется отдельно как `duration_estimate_provenance`; legacy fallback помечается как low-confidence compatibility provenance.
- Для visual subject с несколькими различными base appids structured aggregation намеренно не придумана: implementation fail closed к compatibility fallback/unknown вместо самовольного sum/max/average.
- Existing ranking weights/bands не менялись: duration max остаётся `3`, unknown остаётся `2/3`.
- `config/duration_enrichment_contract.json` обновлён до `implementation_status = implemented_provisioning_required` и содержит реальные implementation paths и текущие provisioning results.
- По `COMMERCIALIZATION_GUARD.md` текущий проект personal/non-commercial. Актуальная IGDB documentation была перепроверена 2026-09-01: API доступен для non-commercial use под Twitch Developer Service Agreement; отдельное user-facing attribution requirement для текущего personal/non-commercial use в просмотренной документации не найдено. Commercial partnership/attribution rules не считаются автоматически разрешёнными на будущее; любое monetization изменение требует нового review.

### Changes

Duration implementation commits в `main`:

1. `1c4ffdfbb35b59f4107108af5a6390ab6263d6fb`
   - added `scripts/duration_enrichment.py`
2. `2e6408bcc8b6c6c971b8f1ffeb51d1cddf319f37`
   - added initial `scripts/test_duration_enrichment.py`
3. `f698a0783a6e200079fd97c612d82f580fb398ba`
   - initialized empty canonical `data/cache/duration_estimates.json`
4. `01c4aebdd975b4f3a6b7ae8585ce38b5be7eb0e9`
   - integrated structured duration precedence into `scripts/build_final_visual_payload.py`
5. `4d50f2035412282b42d06684c5b2b44d36205f74`
   - initially wired duration validation/provisioning/cache refresh into existing `.github/workflows/build-daily-visual-payload.yml`
6. `da85c8575153897d379b7acac127ab290f07be0d`
   - moved the IGDB provisioning/connectivity gate before unrelated package/UI regressions so provider provisioning can be independently accepted
7. `5029a464c2dec455ee9d2df51a1d23cf87662449`
   - recorded implemented/provisioning state, exact secret names and current non-commercial licensing basis in `config/duration_enrichment_contract.json`
8. `6da723466ea3eec475fc8662b7287b746f6b0ab7`
   - updated `scripts/validate_duration_enrichment_contract.py` for implemented provisioning state and real implementation paths
9. `d14b3bf8abb19fd0b34d4353d44e5b8a554819c1`
   - extended duration regressions with final-builder compile/integration guard
10. report commit
   - adds only this implementation report.

No scoring/UI/Taste/package economics behavior was changed by this worker. The workflow file necessarily contains surrounding existing package/UI validation steps, but the unrelated failing package/UI contract was not modified.

### Validation

GitHub Actions acceptance evidence:

- `Build daily visual payload` run `33513512202` (run 147), head `d14b3bf8abb19fd0b34d4353d44e5b8a554819c1`:
  - `Validate canonical duration enrichment contract` -> **success**;
  - validator output -> `DURATION_ENRICHMENT_CONTRACT_VALIDATION=PASS`;
  - recorded contract state:
    - `implementation_status=implemented_provisioning_required`;
    - provider `igdb`;
    - executor `github_actions_direct`;
    - selected metric `normally`;
    - production collection `false`;
    - credentials `provisioning_required`;
    - licensing `satisfied_for_current_personal_noncommercial_use`;
    - connectivity `implementation_acceptance_required`;
    - scoring unknown points `2`.
  - `scripts/test_duration_enrichment.py` -> **12/12 passed**;
  - final-builder integration compile guard passed;
  - exact/fail-closed identity tests, seconds->hours, freshness, transient merge, structured-over-text precedence and no multi-app invented aggregation all passed.
- Same run's `Check IGDB duration provisioning and connectivity` step -> **success as a gate**, with explicit result:
  - `DURATION_IGDB_PROVISIONING=missing_credentials expected_secrets=IGDB_CLIENT_ID,IGDB_CLIENT_SECRET`.
  - Both environment values were empty in GitHub Actions.
- Therefore no OAuth call, no IGDB source request, no game lookup, no duration value and no cache population occurred.
- The same workflow run later failed in the pre-existing/unrelated package/UI regression:
  - `AssertionError: missing package UI override contract: window.renderPackageDeal=function(g)`.
  - Duration validation/provisioning had already completed successfully before that failure. This worker did not modify package/UI code because it is outside the task hard boundaries.

Previous run `33512993909` independently produced the same missing-credentials provisioning result and had green duration contract/regression steps.

### Provisioning

Current blocker is **only the provider credential/connectivity enablement path**, not missing duration implementation code.

Exact user-side provisioning required:

1. In Twitch Developer Console, use/register an application suitable for IGDB API server-side access and obtain its **Client ID** and generated **Client Secret**. Twitch account requirements such as 2FA must be satisfied according to current IGDB/Twitch setup documentation.
2. In GitHub repository `kentrap2011-hub/steam-kz-deals-2` open:
   `Settings -> Secrets and variables -> Actions`.
3. Add repository secret:
   - name: `IGDB_CLIENT_ID`
   - value: Twitch application Client ID
4. Add repository secret:
   - name: `IGDB_CLIENT_SECRET`
   - value: Twitch application Client Secret
5. Do **not** send the secret values to ChatGPT and do not commit them anywhere in the repository.
6. Re-run/dispatch the existing `Build daily visual payload` workflow. Its `Check IGDB duration provisioning and connectivity` step will perform the bounded GitHub Actions OAuth + IGDB `external_game_sources` connectivity/schema check.
7. Only after that step outputs `DURATION_IGDB_CONNECTIVITY=PASS` should `production_collection_enabled` be changed from `false` to `true` in the canonical duration contract in a bounded follow-up change. The following run can then populate missing/stale exact appids and rebuild the final payload.

Licensing/attribution provisioning is currently recorded as satisfied **only for the existing personal/non-commercial project status**. `COMMERCIALIZATION_GUARD.md` remains a hard stop before any monetization/public commercial use; provider terms must be reviewed again at that point.

### Production handling

- `production_collection_enabled` remains `false` by design.
- Canonical cache exists but has no provider entries.
- Existing production behavior remains safe/backward-compatible while blocked:
  - structured cache hit if one later exists;
  - otherwise existing explicit-text duration fallback;
  - otherwise existing unknown -> `2/3`.
- Missing IGDB provisioning does not block the entire visual product because duration is a fail-soft ranking enrichment.
- Collection scope, stale selection, retry state and cache merge are GitHub-owned; no manual per-game backlog processing is required or authorized.
- No new ChatGPT recurring task, queue or catalog batch was created.

### Unresolved

- GitHub Actions Secrets `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` are not provisioned.
- Consequently real GitHub Actions OAuth/IGDB connectivity acceptance is not yet possible.
- Consequently production collection remains disabled and real `game_time_to_beats` coverage for current Steam scope is not measured.
- The exact live IGDB query behavior against current production identities has not been accepted until the bounded connectivity test runs with credentials.
- Multi-base-app visual subject aggregation has no canonical duration semantic; implementation intentionally does not invent one.
- The existing daily visual workflow currently has an unrelated package/UI regression after the green duration steps. Fixing that belongs to the package/UI worker, not this duration task.

### Status

`blocked`

### Recommended next step

Provision only the two GitHub Actions secrets `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET`, then run the existing `Build daily visual payload` workflow once for the bounded IGDB OAuth/connectivity acceptance. If it emits `DURATION_IGDB_CONNECTIVITY=PASS`, perform one bounded duration follow-up that flips `production_collection_enabled` to `true`, lets GitHub populate the missing/stale canonical cache and validates structured-duration propagation into the final payload without changing scoring.
