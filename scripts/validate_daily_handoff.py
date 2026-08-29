import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/daily_execution_contract.json"
PAYLOAD = ROOT / "data/production/pre_ai/chatgpt_payload.json"
READY_JSON = ROOT / "data/production/daily_ready/latest.json"
READY_MD = ROOT / "data/production/daily_ready/latest.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_utc(value, field):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as exc:
        raise SystemExit(f"{field} is not valid ISO-8601: {exc}")
    if dt.tzinfo is None:
        raise SystemExit(f"{field} must be timezone-aware")
    return dt.astimezone(timezone.utc)


def validate_input(now):
    contract = load(CONTRACT)
    payload = load(PAYLOAD)
    freshness = contract["night_input_freshness"]
    if payload.get("status") != "complete":
        raise SystemExit("pre-AI payload status is not complete")
    field = freshness["source_timestamp_field"]
    value = payload.get(field)
    if not value:
        raise SystemExit(f"pre-AI payload missing {field}")
    source = parse_utc(value, field)
    age_hours = (now - source).total_seconds() / 3600
    if age_hours < -0.25:
        raise SystemExit(f"pre-AI source timestamp is unexpectedly in the future: {age_hours:.2f}h")
    if age_hours > float(freshness["maximum_age_hours_at_preparation"]):
        raise SystemExit(f"pre-AI payload is stale: {age_hours:.2f}h")
    if payload.get("ai_queue_count", 0) < 0:
        raise SystemExit("ai_queue_count cannot be negative")
    return contract, payload, source


def validate_manifest_shape(contract, manifest):
    spec = contract["daily_ready_manifest"]
    missing = [field for field in spec["required_fields"] if field not in manifest]
    if missing:
        raise SystemExit(f"daily_ready manifest missing required fields: {', '.join(missing)}")
    if manifest.get("schema_version") != spec["schema_version_value"]:
        raise SystemExit("daily_ready manifest schema_version mismatch")
    if manifest.get("status") != spec["status_complete_value"]:
        raise SystemExit("daily_ready manifest status is not complete")
    digest = manifest.get("ready_text_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise SystemExit("daily_ready ready_text_sha256 is not lowercase SHA-256 hex")


def validate_ready(now):
    contract, payload, source = validate_input(now)
    if not READY_JSON.exists() or not READY_MD.exists():
        raise SystemExit("daily_ready latest.json/latest.md are not both present")
    manifest = load(READY_JSON)
    validate_manifest_shape(contract, manifest)
    expected_source = payload[contract["night_input_freshness"]["source_timestamp_field"]]
    if manifest.get("source_mailing_updated_at_utc") != expected_source:
        raise SystemExit("daily_ready is bound to a different commercial snapshot")
    tz = ZoneInfo(contract["timezone"])
    expected_date = now.astimezone(tz).date().isoformat()
    if manifest.get("intended_delivery_local_date") != expected_date:
        raise SystemExit(
            f"daily_ready delivery date mismatch: expected {expected_date}, "
            f"got {manifest.get('intended_delivery_local_date')}"
        )
    prepared = parse_utc(manifest.get("prepared_at_utc", ""), "prepared_at_utc")
    if prepared < source:
        raise SystemExit("daily_ready was prepared before its source snapshot")
    if prepared > now + timedelta(minutes=15):
        raise SystemExit("prepared_at_utc is unexpectedly in the future")
    text = READY_MD.read_bytes()
    if not text.strip():
        raise SystemExit("daily_ready latest.md is empty")
    digest = hashlib.sha256(text).hexdigest()
    if manifest.get("ready_text_sha256") != digest:
        raise SystemExit("daily_ready text hash mismatch")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["input", "ready"])
    parser.add_argument("--now-utc")
    args = parser.parse_args()
    now = parse_utc(args.now_utc, "--now-utc") if args.now_utc else datetime.now(timezone.utc)
    if args.mode == "input":
        validate_input(now)
        print("Daily handoff input is valid")
    else:
        validate_ready(now)
        print("Daily ready handoff is valid")


if __name__ == "__main__":
    main()
