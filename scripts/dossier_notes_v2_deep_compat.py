#!/usr/bin/env python3
"""Read-only dual-format Deep compatibility gate for an isolated Notes V2 pilot.

Never creates canonical Deep work, changes accepted V2 dossier bytes, submits
a result, or opts the production writer into a lean dossier. Only the explicit
test-only preview caller may use this lean gate. Normal Deep keeps its V2 path.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from dossier_notes_v2_lean_final import LEAN_SCHEMA, SCHEMA_PATH, validate_lean_final

_SANDBOX_PATH = re.compile(
    r"^data/control/dossier_notes_v2/"
    r"(?:batch_pilot_store/[a-z0-9][a-z0-9-]{7,99}|pilot_store)/"
    r"App_[0-9]+\\.json$"
)

def preview_binding():
    import progressive_pass2 as deep
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return {
        "contract": "DOSSIER-NOTES-V2-LEAN-DEEP-PREVIEW-V1",
        "schema_sha256": deep.canonical_sha256(schema),
        "sandbox_only": True,
    }

def lean_preview_eligibility(
    *, binding, semantic_input, dossier_record, current_binding, now=None
):
    """Return (allowed, reason) for a separate sandbox preview, never production."""
    import progressive_pass2 as deep
    if current_binding != preview_binding():
        return False, "lean_preview_binding_mismatch"
    if not isinstance(dossier_record, dict):
        return False, "lean_preview_missing_record"
    doc = dossier_record.get("doc")
    path = dossier_record.get("path")
    if not isinstance(doc, dict) or doc.get("schema") != LEAN_SCHEMA:
        return False, "lean_preview_wrong_schema"
    if not isinstance(path, str) or not _SANDBOX_PATH.fullmatch(path):
        return False, "lean_preview_not_an_isolated_sandbox_path"
    if dossier_record.get("content_sha256") != deep.canonical_sha256(doc):
        return False, "lean_preview_dossier_digest_mismatch"
    if not isinstance(binding, dict) or not isinstance(semantic_input, dict):
        return False, "lean_preview_missing_deep_identity"
    if str(binding.get("appid") or "") != doc.get("appid"):
        return False, "lean_preview_wrong_appid"
    if semantic_input.get("title") != doc.get("title"):
        return False, "lean_preview_wrong_title_or_edition"
    if not deep._cross_stage_release_year_compatible(
        (doc.get("game_identity") or {}).get("release_year"), semantic_input
    ):
        return False, "lean_preview_unresolved_original_release_year"
    try:
        validate_lean_final(
            doc, expected_appid=str(binding["appid"]),
            expected_title=semantic_input["title"], now=now,
        )
    except (ValueError, TypeError, KeyError) as exc:
        return False, "lean_preview_invalid: " + str(exc)[:190]
    return True, "eligible_lean_sandbox_preview_only"

def make_preview_work_item(binding, semantic_input, dossier_record, *, now=None):
    """Ephemeral Deep input for testing real score/negative handlers only.

    Not accepted by GitHub canonical work-issuer, and does not authorize Deep.
    """
    import progressive_pass2 as deep
    allowed, reason = lean_preview_eligibility(
        binding=binding, semantic_input=semantic_input,
        dossier_record=dossier_record, current_binding=preview_binding(), now=now
    )
    if not allowed:
        raise ValueError("lean Deep preview rejected: " + reason)
    return {
        "appid": str(binding["appid"]),
        "dossier_path": dossier_record["path"],
        "dossier_content_sha256": dossier_record["content_sha256"],
        "dossier_compatibility_binding": preview_binding(),
        "_dossier_record": dossier_record,
        "_sandbox_lean_preview": True,
        "score_evidence_contract": deep.SCORE_EVIDENCE_CONTRACT,
        "preview_only": True,
    }
