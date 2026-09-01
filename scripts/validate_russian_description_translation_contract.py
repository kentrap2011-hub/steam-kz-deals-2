#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

from russian_description_quality import classify_description, normalize_description

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def fail(message):
    raise SystemExit(f"RUSSIAN_DESCRIPTION_TRANSLATION_CONTRACT_INVALID: {message}")


def require(condition, message):
    if not condition:
        fail(message)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def request_id(contract_id, source_key, source_text_sha256):
    serialized = "\n".join([contract_id, source_key, source_text_sha256])
    return sha256_text(serialized)


def validate_required_and_unknown(record, required, optional=()):
    required = set(required)
    optional = set(optional)
    keys = set(record)
    missing = required - keys
    unknown = keys - required - optional
    return missing, unknown


contract = load_json("config/russian_description_translation_contract.json")
result_contract = load_json("config/russian_description_translation_result_contract.json")
cache_contract = load_json("config/russian_description_translation_cache_entry_contract.json")
ownership = load_json("config/execution_ownership_contract.json")
daily = load_json("config/daily_execution_contract.json")

require(contract.get("contract") == "RUSSIAN-DESCRIPTION-TRANSLATION-V1", "unexpected request/orchestration contract id")
require(contract.get("status") == "canonical", "request/orchestration contract must be canonical")
require(result_contract.get("contract") == "RUSSIAN-DESCRIPTION-TRANSLATION-RESULT-V1", "unexpected result contract id")
require(result_contract.get("status") == "canonical", "result contract must be canonical")
require(cache_contract.get("contract") == "RUSSIAN-DESCRIPTION-TRANSLATION-CACHE-ENTRY-V1", "unexpected cache-entry contract id")
require(cache_contract.get("status") == "canonical", "cache-entry contract must be canonical")

require(ownership.get("contract") == "PRODUCTION-EXECUTION-OWNERSHIP-V1", "unexpected ownership contract id")
require(daily.get("contract") == "DAILY-VISUAL-EXECUTION-V2", "unexpected daily execution contract id")
require(contract.get("ownership_contract") == "config/execution_ownership_contract.json", "translation contract is not bound to canonical ownership contract")
require(contract.get("daily_execution_contract") == "config/daily_execution_contract.json", "translation contract is not bound to canonical daily execution contract")
require(contract.get("result_contract") == "config/russian_description_translation_result_contract.json", "result contract path mismatch")
require(contract.get("cache_entry_contract") == "config/russian_description_translation_cache_entry_contract.json", "cache-entry contract path mismatch")
require(result_contract.get("request_contract") == "config/russian_description_translation_contract.json", "result contract request binding mismatch")
require(cache_contract.get("request_contract") == "config/russian_description_translation_contract.json", "cache contract request binding mismatch")
require(cache_contract.get("result_contract") == "config/russian_description_translation_result_contract.json", "cache contract result binding mismatch")

runtime = contract.get("runtime_reuse") or {}
require(runtime.get("reuse_existing_nightly_scheduled_chatgpt_runtime") is True, "existing nightly scheduled ChatGPT runtime must be reused")
require(runtime.get("existing_daily_contract_id") == daily.get("contract"), "runtime reuse is bound to the wrong daily contract")
require(runtime.get("separate_recurring_translation_schedule_allowed") is False, "separate recurring translation schedule must remain forbidden")
require(runtime.get("translation_is_additional_semantic_work_type_inside_existing_cycle") is True, "translation must be part of the existing nightly semantic cycle")
require(runtime.get("taste_specific_input_or_result_schema_may_be_reused") is False, "Taste-specific result schema must not be overloaded")

scope = contract.get("scope") or {}
require(set(scope.get("eligible_description_statuses") or []) == {"needs_translation", "needs_ru_rewrite"}, "translation scope must be exactly the two unresolved semantic states")
require(set(scope.get("eligible_source_qualities") or []) == {"non_ru", "weak_ru"}, "translation source-quality scope must be exactly non_ru/weak_ru")
require({"ready_ru", "technical_source", "missing_source"}.issubset(set(scope.get("not_semantic_translation_work") or [])), "non-translation states are not explicitly excluded")
require(scope.get("no_daily_item_quota") is True, "daily translation item quota must remain disabled")
require(scope.get("checkpointing_is_transport_only") is True, "checkpointing must not become scope/quota semantics")

owners = contract.get("ownership") or {}
github_owns = set((owners.get("github_control_plane") or {}).get("owns") or [])
for marker in [
    "derive the exact current unresolved description scope",
    "construct and order the immutable translation work input",
    "track unresolved state, retries, checkpoints, and completeness",
    "validate returned keys, hashes, statuses, and Russian text quality",
    "merge validated results into the canonical translation cache",
    "rebuild downstream visual artifacts and enforce the final Russian-description gate",
]:
    require(marker in github_owns, f"GitHub ownership marker missing: {marker}")
worker_forbidden = set((owners.get("scheduled_chatgpt_data_plane") or {}).get("forbidden") or [])
for marker in [
    "discover or add games independently",
    "manage retries or completeness",
    "write directly to the canonical translation cache",
    "create a separate recurring scheduler or daily quota",
]:
    require(marker in worker_forbidden, f"scheduled worker prohibition missing: {marker}")
require((owners.get("interactive_chat") or {}).get("production_catalog_translation_allowed") is False, "interactive chat must not translate the production catalog")
require((owners.get("interactive_chat") or {}).get("manual_cache_population_allowed") is False, "interactive chat must not populate translation cache")

boundary = contract.get("implementation_boundary") or {}
require(boundary.get("this_task_is_contract_only") is True, "task boundary must remain contract-only")
require(boundary.get("translation_producer_or_ingest_implementation_in_scope") is False, "producer/ingest implementation leaked into contract-only task")
require(boundary.get("mass_translation_in_scope") is False, "mass translation leaked into contract-only task")
require(boundary.get("production_cache_population_in_scope") is False, "cache population leaked into contract-only task")

artifacts = contract.get("reserved_artifacts_for_followup_implementation") or {}
expected_artifacts = {
    "request_work_input": "data/production/pre_ai/chatgpt_ru_description_queue.jsonl",
    "request_status_manifest": "data/production/pre_ai/chatgpt_ru_description_status.json",
    "runtime_submission_glob": "data/ai_inbox/russian_descriptions/*.json",
    "canonical_cache": "data/cache/russian_description_translations.json",
}
for key, expected in expected_artifacts.items():
    require(artifacts.get(key) == expected, f"reserved artifact path mismatch for {key}")

identity = contract.get("request_identity") or {}
require(identity.get("hash_algorithm") == "sha256", "request/source hash algorithm must be sha256")
require(identity.get("stable_entity_key_format") == "App_<steam_appid>", "stable entity key must be App_<steam_appid>")
require(identity.get("source_version_format") == "sha256:<source_text_sha256>", "source version must be hash-bound")
require(identity.get("request_id_canonical_fields_in_order") == ["contract_id", "source_key", "source_text_sha256"], "request identity canonical fields/order changed")
require(identity.get("request_id_serialization") == "UTF-8 strings joined by LF with no trailing LF", "request identity serialization changed")

request_schema = contract.get("request_schema") or {}
require(request_schema.get("schema_version") == 1, "request schema version must be 1")
require(request_schema.get("additional_fields_allowed") is False, "request schema must reject unknown fields")
request_required = request_schema.get("required_fields") or []
for field in ["request_id", "source_key", "source_appid", "source_text", "source_text_sha256", "source_version", "source_locale_state", "source_quality", "source_path", "target_locale"]:
    require(field in request_required, f"request schema missing required field {field}")

result_submission_schema = result_contract.get("submission_schema") or {}
result_record_schema = result_contract.get("result_record_schema") or {}
require(result_submission_schema.get("additional_fields_allowed") is False, "submission schema must reject unknown fields")
require(result_record_schema.get("additional_fields_allowed") is False, "result record schema must reject unknown fields")
for field in contract.get("worker_output_binding", {}).get("must_echo_exact_fields") or []:
    require(field in (result_record_schema.get("required_fields") or []), f"result record does not require exact echo field {field}")
require(contract.get("worker_output_binding", {}).get("unknown_request_keys_allowed") is False, "unknown result request keys must be forbidden")
require(contract.get("worker_output_binding", {}).get("worker_may_return_subset_checkpoint") is True, "bounded subset checkpoints should be allowed as transport only")

validation = contract.get("github_validation") or {}
require(validation.get("exact_current_request_match_required") is True, "exact current request binding must be required")
require(validation.get("translated_text_quality_function") == "scripts/russian_description_quality.py::classify_description", "result quality must use existing classifier")
require(validation.get("accepted_translated_text_quality") == "good_ru", "only good_ru may be accepted")
require(validation.get("fail_closed") is True, "translation validation must fail closed")
require((result_contract.get("acceptance") or {}).get("placeholder_or_technical_is_rejected") is True, "placeholder/technical results must be rejected")

persistence = contract.get("persistence_and_invalidation") or {}
require(persistence.get("cache_owner") == "github_control_plane", "GitHub must own cache")
require(persistence.get("worker_direct_cache_write_allowed") is False, "worker direct cache writes must be forbidden")
require(set(persistence.get("cache_hit_requires") or []) >= {"exact source_key", "exact source_text_sha256", "exact source_version", "translated_text_ru still classifies as good_ru"}, "cache-hit binding is incomplete")
require(persistence.get("arbitrary_daily_retranslation_allowed") is False, "unchanged source must not be arbitrarily retranslated")

retry = contract.get("retry_and_completeness") or {}
require(retry.get("owner") == "github_control_plane", "GitHub must own retry/completeness")
require(retry.get("chatgpt_retry_loop_allowed") is False, "ChatGPT retry loop must be forbidden")
require(retry.get("chatgpt_batch_quota_allowed") is False, "ChatGPT batch quota must be forbidden")
require(retry.get("production_completion_decider") == "GitHub only", "GitHub alone must decide completion")

downstream = contract.get("downstream") or {}
require(downstream.get("final_quality_gate") == "scripts/validate_russian_descriptions.py", "existing final Russian-description gate must remain canonical")
require(downstream.get("final_gate_must_remain_fail_closed") is True, "final visual gate must remain fail closed")
require(downstream.get("unresolved_translation_may_not_become_normal_summary") is True, "unresolved text may not silently become a summary")

# Contract-level deterministic fixtures. These exercise identity, shape and quality semantics
# without implementing or populating any production queue/cache.
source_text = normalize_description("A tactical adventure about escaping a haunted station.")
source_hash = sha256_text(source_text)
source_key = "App_123456"
sample_request = {
    "request_id": request_id(contract["contract"], source_key, source_hash),
    "source_key": source_key,
    "source_appid": "123456",
    "title": "Fixture Game",
    "work_type": "translate_to_ru",
    "source_text": source_text,
    "source_text_sha256": source_hash,
    "source_version": f"sha256:{source_hash}",
    "source_locale_state": "non_ru",
    "source_quality": "non_ru",
    "source_path": "fixture/source",
    "target_locale": "ru",
}
missing, unknown = validate_required_and_unknown(sample_request, request_required)
require(not missing and not unknown, f"sample request shape invalid: missing={sorted(missing)} unknown={sorted(unknown)}")
require(re.fullmatch(r"[0-9a-f]{64}", sample_request["request_id"]) is not None, "sample request_id is not lowercase sha256")
require(sample_request["source_key"] == f"App_{sample_request['source_appid']}", "sample stable entity identity mismatch")
require(sample_request["source_text_sha256"] == sha256_text(normalize_description(sample_request["source_text"])), "sample source hash mismatch")
require(sample_request["source_version"] == f"sha256:{sample_request['source_text_sha256']}", "sample source version mismatch")

changed_source_hash = sha256_text(normalize_description(source_text + " Changed."))
require(request_id(contract["contract"], source_key, changed_source_hash) != sample_request["request_id"], "changed source text must invalidate request identity")
require(request_id(contract["contract"], "App_654321", source_hash) != sample_request["request_id"], "changed source entity must invalidate request identity")

result_required = result_record_schema.get("required_fields") or []
result_optional = result_record_schema.get("allowed_optional_fields") or []
sample_result = {
    "request_id": sample_request["request_id"],
    "source_key": sample_request["source_key"],
    "source_appid": sample_request["source_appid"],
    "source_text_sha256": sample_request["source_text_sha256"],
    "source_version": sample_request["source_version"],
    "status": "translated",
    "translated_text_ru": "Тактическое приключение о побеге с проклятой космической станции, где приходится исследовать окружение и искать путь к спасению.",
}
missing, unknown = validate_required_and_unknown(sample_result, result_required, result_optional)
require(not missing and not unknown, f"sample result shape invalid: missing={sorted(missing)} unknown={sorted(unknown)}")
for field in contract["worker_output_binding"]["must_echo_exact_fields"]:
    require(sample_result[field] == sample_request[field], f"sample result exact echo mismatch for {field}")
require(classify_description(sample_result["translated_text_ru"]) == "good_ru", "accepted fixture must classify as good_ru")
require(classify_description("Русское краткое описание для этой игры пока не подготовлено.") == "placeholder_or_technical", "known placeholder must remain rejected by classifier")
require(classify_description("This remains English and is not a valid Russian translation.") != "good_ru", "English fixture must not pass Russian quality gate")

stale_result = dict(sample_result, source_text_sha256=changed_source_hash, source_version=f"sha256:{changed_source_hash}")
require(any(stale_result[field] != sample_request[field] for field in contract["worker_output_binding"]["must_echo_exact_fields"]), "stale fixture must be detectable by exact binding")

unknown_result = dict(sample_result, unexpected_field="nope")
_, unknown = validate_required_and_unknown(unknown_result, result_required, result_optional)
require(unknown == {"unexpected_field"}, "unknown result fields must be detectable")

cache_schema = cache_contract.get("entry_schema") or {}
cache_required = cache_schema.get("required_fields") or []
sample_cache = {
    "request_id": sample_request["request_id"],
    "source_key": sample_request["source_key"],
    "source_appid": sample_request["source_appid"],
    "source_text_sha256": sample_request["source_text_sha256"],
    "source_version": sample_request["source_version"],
    "translated_text_ru": sample_result["translated_text_ru"],
    "target_locale": "ru",
    "validated_quality": "good_ru",
    "result_contract": result_contract["contract"],
    "ingested_at_utc": "2026-09-01T00:00:00Z",
}
missing, unknown = validate_required_and_unknown(sample_cache, cache_required)
require(not missing and not unknown, f"sample cache-entry shape invalid: missing={sorted(missing)} unknown={sorted(unknown)}")
require(classify_description(sample_cache["translated_text_ru"]) == "good_ru", "cache fixture must revalidate as good_ru")
require(sample_cache["request_id"] == sample_request["request_id"], "cache fixture request binding mismatch")

print("RUSSIAN_DESCRIPTION_TRANSLATION_CONTRACT_VALID")
