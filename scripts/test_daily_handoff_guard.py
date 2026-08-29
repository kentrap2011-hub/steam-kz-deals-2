import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import validate_daily_handoff as guard


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def expect_fail(fn, text):
    try:
        fn()
    except SystemExit as exc:
        if text not in str(exc):
            raise AssertionError(f"Expected {text!r}, got {exc!r}")
    else:
        raise AssertionError(f"Expected failure containing {text!r}")


def main():
    with TemporaryDirectory() as td:
        root = Path(td)
        guard.CONTRACT = root / "contract.json"
        guard.PAYLOAD = root / "payload.json"
        guard.READY_JSON = root / "latest.json"
        guard.READY_MD = root / "latest.md"

        write_json(guard.CONTRACT, {
            "timezone": "Europe/Samara",
            "night_input_freshness": {
                "source_timestamp_field": "source_mailing_updated_at_utc",
                "maximum_age_hours_at_preparation": 18,
            },
            "daily_ready_manifest": {
                "required_fields": [
                    "schema_version",
                    "status",
                    "source_mailing_updated_at_utc",
                    "intended_delivery_local_date",
                    "prepared_at_utc",
                    "ready_text_sha256",
                ],
                "schema_version_value": 1,
                "status_complete_value": "complete",
            },
        })
        write_json(guard.PAYLOAD, {
            "status": "complete",
            "source_mailing_updated_at_utc": "2026-08-29T00:30:00+00:00",
            "ai_queue_count": 0,
        })
        now = datetime(2026, 8, 29, 1, 0, tzinfo=timezone.utc)
        guard.validate_input(now)

        stale = json.loads(guard.PAYLOAD.read_text(encoding="utf-8"))
        stale["source_mailing_updated_at_utc"] = "2026-08-28T00:00:00+00:00"
        write_json(guard.PAYLOAD, stale)
        expect_fail(lambda: guard.validate_input(now), "stale")

        stale["source_mailing_updated_at_utc"] = "2026-08-29T00:30:00+00:00"
        write_json(guard.PAYLOAD, stale)
        text = "ready mailing\n"
        guard.READY_MD.write_text(text, encoding="utf-8")
        valid_manifest = {
            "schema_version": 1,
            "status": "complete",
            "source_mailing_updated_at_utc": "2026-08-29T00:30:00+00:00",
            "intended_delivery_local_date": "2026-08-29",
            "prepared_at_utc": "2026-08-29T00:50:00+00:00",
            "ready_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
        write_json(guard.READY_JSON, valid_manifest)
        guard.validate_ready(now)

        missing_schema = dict(valid_manifest)
        missing_schema.pop("schema_version")
        write_json(guard.READY_JSON, missing_schema)
        expect_fail(lambda: guard.validate_ready(now), "missing required fields")

        wrong_hash = dict(valid_manifest)
        wrong_hash["ready_text_sha256"] = "0" * 64
        write_json(guard.READY_JSON, wrong_hash)
        expect_fail(lambda: guard.validate_ready(now), "text hash mismatch")

        wrong_source = dict(valid_manifest)
        wrong_source["source_mailing_updated_at_utc"] = "2026-08-28T00:30:00+00:00"
        write_json(guard.READY_JSON, wrong_source)
        expect_fail(lambda: guard.validate_ready(now), "different commercial snapshot")

    print("Daily handoff guard regression tests passed")


if __name__ == "__main__":
    main()
