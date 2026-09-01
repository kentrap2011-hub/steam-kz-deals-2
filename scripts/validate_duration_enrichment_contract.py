#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def fail(message):
    raise SystemExit(f"DURATION_ENRICHMENT_CONTRACT_INVALID: {message}")


def require(condition, message):
    if not condition:
        fail(message)


def normalize_hours(seconds, contract):
    norm = contract["normalization"]
    if not isinstance(seconds, (int, float)) or isinstance(seconds, bool):
        return None
    if norm.get("selected_metric_must_be_positive") and seconds <= 0:
        return None
    return float(seconds) / float(norm["conversion_divisor"])


def validate_raw_record(record, contract):
    spec = contract["raw_provider_record"]
    missing = [field for field in spec["required_fields"] if field not in record]
    require(not missing, f"raw provider record missing fields: {missing}")
    require(record["provider"] == spec["provider_value"], "raw provider must be igdb")
    require(record["provider_schema"] == spec["provider_schema_value"], "raw provider schema mismatch")

    appid = str(record["steam_appid"])
    uid = str(record["steam_external_game_uid"])
    require(appid.isdecimal() and int(appid) > 0, "steam_appid must be a positive decimal string")
    require(uid == appid, "IGDB External Game uid must equal the Steam appid")
    require(isinstance(record["igdb_game_id"], int) and record["igdb_game_id"] > 0, "igdb_game_id must be positive")
    require(
        isinstance(record["steam_external_game_source_id"], int)
        and record["steam_external_game_source_id"] > 0,
        "external_game_source id must be positive",
    )
    for field in ("hastily_seconds", "normally_seconds", "completely_seconds"):
        value = record[field]
        require(
            value is None or (isinstance(value, int) and not isinstance(value, bool) and value >= 0),
            f"{field} must be a non-negative integer or null",
        )
    count = record["count"]
    require(
        count is None or (isinstance(count, int) and not isinstance(count, bool) and count >= 0),
        "count must be a non-negative integer or null",
    )
    return True


def main():
    contract = load_json("config/duration_enrichment_contract.json")
    ownership = load_json("config/execution_ownership_contract.json")
    daily = load_json("config/daily_execution_contract.json")
    ranking = load_json("config/final_ranking_policy.json")

    require(contract.get("contract") == "DURATION-ENRICHMENT-V1", "unexpected contract id")
    require(contract.get("version") == "1.0", "unexpected contract version")
    require(contract.get("status") == "canonical", "contract must be canonical")
    require(contract.get("implementation_status") == "provisioning_required", "production must remain gated")

    bindings = contract.get("bindings") or {}
    require(bindings.get("ownership_contract") == "config/execution_ownership_contract.json", "ownership binding mismatch")
    require(bindings.get("daily_execution_contract") == "config/daily_execution_contract.json", "daily binding mismatch")
    require(bindings.get("final_ranking_policy") == "config/final_ranking_policy.json", "ranking binding mismatch")

    require(ownership.get("contract") == "PRODUCTION-EXECUTION-OWNERSHIP-V1", "unexpected ownership contract")
    control = set((ownership.get("github_control_plane") or {}).get("responsibilities") or [])
    for responsibility in (
        "collect every source GitHub can access directly",
        "decide the exact current production scope",
        "own retry state and unresolved-item state",
        "own checkpoint merge logic and completeness accounting",
        "persist validated canonical caches",
    ):
        require(responsibility in control, f"GitHub ownership missing: {responsibility}")

    inv = daily.get("execution_invariants") or {}
    require(inv.get("github_owns_control_plane") is True, "daily execution must remain GitHub-owned")
    require(inv.get("per_day_item_quota_allowed") is False, "daily item quota must remain disabled")
    require(inv.get("interactive_chat_is_production_executor") is False, "interactive chat must not execute production")

    authority = contract.get("authority") or {}
    require(authority.get("primary_provider") == "igdb", "IGDB must be primary")
    require(authority.get("duration_endpoint") == "game_time_to_beats", "unexpected duration endpoint")
    require(authority.get("rawg_is_fallback_provider") is False, "RAWG must not be a duration fallback")
    require(
        authority.get("rawg_average_playtime_is_completion_duration") is False,
        "RAWG average playtime must not be treated as completion duration",
    )
    require(
        authority.get("howlongtobeat_scraping_or_unofficial_wrappers_authorized") is False,
        "unofficial HLTB access must remain unauthorized",
    )

    owner = contract.get("ownership") or {}
    require(owner.get("collection_executor") == "github_actions_direct", "duration executor must be GitHub-direct")
    require(owner.get("scheduled_chatgpt_primary_collection_allowed") is False, "scheduled ChatGPT primary collection forbidden")
    require(owner.get("interactive_chat_primary_collection_allowed") is False, "interactive ChatGPT primary collection forbidden")
    require(owner.get("chat_owned_queue_allowed") is False, "chat-owned queue forbidden")
    require(owner.get("daily_item_quota_allowed") is False, "duration daily item quota forbidden")

    identity = contract.get("identity") or {}
    mapping = identity.get("igdb_mapping") or {}
    require(identity.get("canonical_input") == "steam_appid", "canonical identity must be Steam appid")
    require(mapping.get("source_reference_field") == "external_game_source", "must use current external_game_source")
    require("category" in set(identity.get("deprecated_fields_forbidden") or []), "deprecated category must be forbidden")
    require(identity.get("legacy_numeric_steam_enum_must_not_be_hardcoded") is True, "legacy Steam enum must not be hardcoded")
    require(identity.get("title_only_mapping_allowed") is False, "title-only mapping forbidden")
    require(identity.get("fuzzy_mapping_allowed") is False, "fuzzy mapping forbidden")

    access = contract.get("provider_access") or {}
    limits = access.get("provider_limits") or {}
    require(access.get("transport") == "https", "IGDB transport must be HTTPS")
    require(access.get("authentication") == "twitch_oauth2_client_credentials", "unexpected OAuth mode")
    require(access.get("credentials_must_never_be_committed") is True, "credentials must never be committed")
    require(limits.get("requests_per_second") == 4, "IGDB rate limit must be 4 requests/second")
    require(limits.get("max_concurrent_requests") == 8, "IGDB max concurrent requests must be 8")
    require(limits.get("limits_are_production_quota") is False, "provider limits must not become production quotas")

    raw = contract.get("raw_provider_record") or {}
    require(raw.get("duration_fields_unit") == "seconds", "raw duration unit must be seconds")
    require(raw.get("count_semantics") == "provider_submission_count", "count provenance must be preserved")
    require(raw.get("numerical_confidence_threshold") is None, "contract must not invent confidence threshold")

    norm = contract.get("normalization") or {}
    require(norm.get("selected_metric") == "normally", "canonical estimate must select normally")
    require(norm.get("conversion_divisor") == 3600, "seconds-to-hours divisor must be 3600")
    require(norm.get("output_field") == "estimated_duration_hours", "unexpected normalized output field")
    require(norm.get("rounding_required_in_canonical_cache") is False, "canonical cache must not force rounding")
    require(norm.get("zero_seconds_is_valid_duration") is False, "zero seconds must not become valid duration")

    cache = contract.get("canonical_cache") or {}
    require(cache.get("path") == "data/cache/duration_estimates.json", "unexpected canonical cache path")
    require(cache.get("population_in_this_contract_task") is False, "contract task must not populate cache")
    schema = cache.get("entry_schema") or {}
    durable = set(schema.get("durable_unresolved_statuses") or [])
    transient = set(schema.get("transient_error_statuses") or [])
    require(
        durable == {"provider_row_missing", "steam_mapping_missing", "steam_mapping_ambiguous", "invalid_values"},
        "durable unresolved states mismatch",
    )
    require(transient == {"auth_failure", "transport_failure"}, "transient error states mismatch")
    merge = cache.get("merge_rules") or {}
    require(merge.get("transient_error_must_not_replace_confirmed") is True, "transient error may replace confirmed cache")
    require(merge.get("transient_error_is_not_durable_negative_cache") is True, "transient error encoded as durable negative")
    require(merge.get("negative_or_error_state_must_never_encode_zero_hours") is True, "negative state may encode zero hours")
    require(
        merge.get("durable_unresolved_must_not_replace_confirmed_without_explicit_invalidation") is True,
        "durable unresolved state may silently erase confirmed duration",
    )

    scope = contract.get("scope_and_completeness") or {}
    require(scope.get("github_derives_exact_required_steam_appids") is True, "GitHub exact scope ownership missing")
    require(scope.get("full_catalog_prefill_required") is False, "contract must not require full-catalog prefill")
    require(scope.get("github_owns_retry_state") is True, "GitHub retry ownership missing")
    require(scope.get("github_owns_completeness_accounting") is True, "GitHub completeness ownership missing")
    require(scope.get("unresolved_duration_may_handoff_as_unknown") is True, "unknown fail-soft handoff missing")
    require(scope.get("unresolved_duration_blocks_visual_production") is False, "duration must not become a new hard production gate")

    freshness = contract.get("freshness") or {}
    require(freshness.get("data_class") == "long_lived", "duration must be long-lived data")
    require(freshness.get("fetch_on_first_required_appearance_if_missing") is True, "missing first-use fetch rule absent")
    require(freshness.get("refetch_all_known_rows_every_nightly_cycle") is False, "nightly full refetch forbidden")
    require(freshness.get("confirmed_soft_stale_after_days") == 180, "confirmed stale policy mismatch")
    require(freshness.get("durable_unresolved_retry_after_days") == 30, "unresolved retry freshness mismatch")

    handoff = contract.get("final_handoff") or {}
    require(
        handoff.get("precedence") == [
            "validated_structured_igdb_normally",
            "legacy_text_explicit_duration_phrase",
            "unknown",
        ],
        "final handoff precedence mismatch",
    )
    legacy = handoff.get("legacy_text_fallback") or {}
    require(legacy.get("enabled") is True, "legacy explicit-text compatibility fallback must be explicit")
    require(legacy.get("must_not_write_into_igdb_cache") is True, "legacy fallback must not pollute IGDB cache")
    require(legacy.get("must_not_override_structured_igdb") is True, "legacy fallback may override structured IGDB")

    duration_cfg = (((ranking.get("score_model") or {}).get("personal") or {}).get("duration") or {})
    require(duration_cfg.get("max") == 3, "duration max score changed")
    require((duration_cfg.get("band_points") or {}).get("unknown") == 2, "unknown duration score must remain 2/3")
    unknown = handoff.get("unknown_behavior") or {}
    require(unknown.get("ranking_points") == 2 and unknown.get("ranking_max_points") == 3, "handoff scoring invariant mismatch")

    migration = contract.get("schema_migration_guard") or {}
    require(migration.get("required_current_identity_field") == "external_game_source", "migration guard missing current field")
    require(migration.get("deprecated_identity_field_forbidden") == "category", "migration guard missing deprecated field")
    require(migration.get("hardcoded_legacy_steam_enum_forbidden") is True, "legacy enum hardcoding not forbidden")

    gates = contract.get("provisioning_gates") or {}
    require(gates.get("production_collection_enabled") is False, "production collection enabled before provisioning")
    require((gates.get("credentials") or {}).get("status") == "provisioning_required", "credential gate must be unresolved")
    require((gates.get("licensing_attribution") or {}).get("status") == "provisioning_required", "licensing gate must be unresolved")
    require(
        (gates.get("github_actions_connectivity") or {}).get("status") == "implementation_acceptance_required",
        "GitHub Actions connectivity gate missing",
    )

    boundaries = contract.get("implementation_boundaries") or {}
    for key in (
        "api_client_implemented_by_this_contract",
        "provider_calls_performed_by_this_contract",
        "cache_population_performed_by_this_contract",
        "final_builder_integration_performed_by_this_contract",
        "scoring_math_changed_by_this_contract",
        "unknown_2_of_3_changed_by_this_contract",
    ):
        require(boundaries.get(key) is False, f"contract task crossed implementation boundary: {key}")

    synthetic = {
        "provider": "igdb",
        "provider_schema": "game_time_to_beats",
        "steam_appid": "999999999",
        "igdb_game_id": 999999999,
        "steam_external_game_uid": "999999999",
        "steam_external_game_source_id": 999999999,
        "hastily_seconds": 18000,
        "normally_seconds": 36000,
        "completely_seconds": 72000,
        "count": 42,
        "fetched_at_utc": "2099-01-01T00:00:00Z",
    }
    validate_raw_record(synthetic, contract)
    require(normalize_hours(synthetic["normally_seconds"], contract) == 10.0, "deterministic seconds-to-hours conversion failed")
    require(normalize_hours(0, contract) is None, "zero seconds must normalize to unknown")
    require(normalize_hours(None, contract) is None, "missing seconds must normalize to unknown")

    print(json.dumps({
        "status": "PASS",
        "contract": contract["contract"],
        "provider": authority["primary_provider"],
        "executor": owner["collection_executor"],
        "cache_path": cache["path"],
        "selected_metric": norm["selected_metric"],
        "synthetic_normalized_hours": 10.0,
        "production_collection_enabled": gates["production_collection_enabled"],
        "scoring_unknown_points": duration_cfg["band_points"]["unknown"],
    }, ensure_ascii=False, indent=2))
    print("DURATION_ENRICHMENT_CONTRACT_VALIDATION=PASS")


if __name__ == "__main__":
    main()
