# giveaway-igdb-implement-prep-01

Date: 2026-09-02

### Repo-side preparation

- Reused the existing IGDB provider/auth route in `scripts/duration_enrichment.py`; no second provider client, queue, scheduler, browser fetch, or semantic runtime was added. The existing route already owns Twitch client-credentials auth and exact Steam External Game resolution.
- Confirmed the canonical GitHub Actions secret names and consumer point in `.github/workflows/build-daily-visual-payload.yml`:
  - `IGDB_CLIENT_ID: ${{ secrets.IGDB_CLIENT_ID }}`
  - `IGDB_CLIENT_SECRET: ${{ secrets.IGDB_CLIENT_SECRET }}`
  Missing values are already represented fail-closed as `status=missing_credentials`.
- Confirmed `config/duration_enrichment_contract.json` already declares GitHub Secrets / ephemeral runtime storage, the same two secret names, and title/fuzzy matching forbidden for identity.
- Added `scripts/giveaway_igdb_identity_probe.py` as a **read-only acceptance probe**. It does not write `data/production/giveaways/**` and never authorizes a production binding by itself.
  - Input is only exact provider identity already persisted in the canonical giveaway snapshot.
  - Epic candidate tokens are derived only from the adapter-defined exact `source_product_id = <namespace>:<offer_id>` format: the complete product id, namespace, and offer id are probed as separate *candidate UID observations*. None is assumed to be IGDB's UID semantic before live evidence.
  - GOG candidate token is the exact persisted catalog product id.
  - The provider-side IGDB query is by exact `uid` values only and deliberately has **no preselected Epic/GOG `external_game_source` id**, no title search, no fuzzy matching, and no deprecated category mapping.
  - Live `external_game_sources` rows are used to label whatever source IDs IGDB actually returns.
  - Any observed IGDB game is reverse-checked through the already accepted exact Steam source route; only one decimal Steam appid is classifiable as `mapped`; missing, invalid, or multiple appids fail closed.
  - Probe output always carries `production_binding_authorized=false`; persistence is intentionally deferred until live provider source/UID semantics are accepted.
  - Probe scope is bounded (`--limit`, default `10`) and explicitly reports truncation.
- Added `scripts/test_giveaway_igdb_identity_probe.py` with deterministic no-network coverage for:
  - exact-provider-ID extraction with title text ignored;
  - malformed Epic/GOG identity fail-closed behavior;
  - no title/search/fuzzy/provider-source guess in the provider UID query;
  - observed provider rows remaining non-authoritative;
  - exact-one Steam appid reverse mapping and ambiguous/missing/invalid failure modes;
  - bounded scope;
  - conflicting live source metadata failure.
- Wired that regression test into the existing `.github/workflows/steam-test.yml`; no new workflow or schedule was created.
- Validation evidence:
  - initial run `33662052857`, job `100354680760`, caught one test-only false assertion (`"name"` was a substring of fixture value `"namespace-1"`); existing ownership and giveaway regressions passed, and production collection was skipped after the test failure, so that run changed no production giveaway data;
  - assertion corrected in commit `a141229050034104a40cd85999e5b8ba423798f3`;
  - corrected run `33662167515`, job `100355068564`: `Regression test production output ownership` = success, `Regression test cross-platform giveaways` = success, `Regression test giveaway IGDB identity probe` = success. The job then continued into the pre-existing full Steam collection; that downstream collection is not a prerequisite for accepting this prep step.
- No giveaway UI, visual contract, paid ranking, Taste semantics, or current production identity binding was changed.

### Exact user action

The remaining prerequisite is repository secret provisioning. **Do not paste either value into chat, source files, commits, issue text, or workflow YAML.**

1. Get the credentials from Twitch/IGDB:
   - open the Twitch Developer Console: `https://dev.twitch.tv/console/apps`;
   - sign in with a Twitch account and ensure 2FA is enabled;
   - choose **Register Your Application**;
   - IGDB's official setup says the OAuth Redirect URL is not used by IGDB; enter `localhost` to continue;
   - set **Client Type = Confidential** so a client secret can be generated;
   - open **Manage** for the created application, click **New Secret**, and note the **Client ID** and **Client Secret**.
2. Add them to this exact repository: `kentrap2011-hub/steam-kz-deals-2` → **Settings** → **Secrets and variables** → **Actions** → **Secrets** → **New repository secret**.
3. Create two repository secrets, separately, with these exact names:
   - `IGDB_CLIENT_ID` = Twitch application Client ID
   - `IGDB_CLIENT_SECRET` = Twitch application Client Secret

Official provider reference used for the handoff: IGDB API docs, **Getting Started → Account Creation / Authentication** (`https://api-docs.igdb.com/`). GitHub's repository-secret UI path is the standard Actions repository-secret path documented by GitHub.

### Post-secret continuation

After the user reports that both repository secrets have been added, continue in this same task line without asking for their values:

1. Verify the **existing** IGDB route first: execute the existing connectivity gate / `python scripts/duration_enrichment.py --connectivity-only` under GitHub Actions secrets and require `DURATION_IGDB_CONNECTIVITY=PASS` with the live-resolved Steam External Game source.
2. Run the new bounded read-only acceptance probe against the current canonical giveaway snapshot, initially `python scripts/giveaway_igdb_identity_probe.py --limit 10`.
3. For the bounded Epic/GOG sample, accept no provider mapping unless live IGDB evidence establishes an exact provider External Game source/UID semantic and a unique IGDB game. Do not infer source IDs or UID meaning from names/titles, and do not add manual per-game mappings.
4. Reverse-map each accepted IGDB game through the exact Steam External Game source and require exactly one decimal Steam appid. Missing/ambiguous/invalid mappings remain unresolved.
5. Only after that live acceptance, implement the smallest persistence path under the existing single writer `scripts/giveaway_production.py`: provider exact identity + accepted IGDB identity + exact Steam appid + resolution status/provenance/timestamp. No title/fuzzy fallback.
6. Extend only the existing precomputed visual handoff/build path so a resolved giveaway can reuse canonical description, positive Taste evidence, and grounded player-visible negative evidence. If analysis readiness is incomplete, render/retain explicit incomplete state; do not invent pros/cons and do not copy price/rank/wishlist state into analysis.
7. Run canonical tests/build/deploy and verify the accepted giveaway UI remains unchanged apart from now receiving resolved canonical analysis where available.

### Status

`blocked_on_user_secrets`

All safe repository-side preparation that does not require live IGDB credentials or unverified Epic/GOG External Game semantics is in place. The next necessary operation is live IGDB connectivity/provider acceptance, which requires `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` to exist as GitHub Actions repository secrets.

Efficiency / reusable lesson: keep provider-identity discovery as a read-only exact-ID probe with `production_binding_authorized=false`; only promote a mapping into the canonical producer after live source/UID semantics and the reverse Steam identity are both exact and unambiguous.

Exact refs:
- task blob: `276aa72b30311edb19af908958533b4482bec9f5`
- previous identity recon report blob: `faa254b9abd2bdd18e615f4f7ad5d0f0d6d6165d`
- existing IGDB client / exact Steam route blob: `a1a76118f7c2bae036ccc8be880ae9152ee0f64` is **not** used here; canonical `scripts/duration_enrichment.py` blob is `a1a76118f7c2bae036ccc8be9adfa10ef0594abd`
- duration enrichment contract blob: `6bdd2471eaf6f567ee7fcd26c72f7231127a6923`
- existing IGDB secret/connectivity workflow blob: `2d56b81f822412c433852d55a749a4db8ce33b78`
- current giveaway snapshot blob used as probe input contract evidence: `a6f45abbd40d756d0421eb3492eb3e5ef8e8f510`
- new probe blob: `c9d7d59045deb2864ac622db0a05e346d0b80bbe`
- new probe tests blob: `554347eebb922e7925750d2740f0985fea1b0145`
- existing workflow with probe regression wired in: `53c10a7357883ec869d9a8a430b191bc77130d35`
- probe creation commit: `6788be1eafb87129fff723349de291d1d3af96be`
- probe-test creation commit: `c871642ca854d859b581a81b41c73da17146e142`
- workflow wiring commit: `de280e8a838c3510e3f8a0e0338c353d00bb8499`
- corrected probe-test commit: `a141229050034104a40cd85999e5b8ba423798f3`
- corrected validation run/job: `33662167515` / `100355068564`
