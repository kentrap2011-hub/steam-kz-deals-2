#!/usr/bin/env python3
"""Explicit version dispatch for inactive two-stage Dossier only.

Legacy V1 remains byte-for-byte and behavior-for-behavior on its own route.
V2 cannot be upgraded from V1 or mixed with the original frozen trial.
No autonomous execution, transport write or canonical acceptance is performed.
"""
from dossier_research_notes_v2 import (
    prepare_research as prepare_notes_v2,
    classify_research as classify_notes_v2,
    assembly_work as assemble_notes_v2,
    inspect_assembly as inspect_notes_v2,
)

def prepare_research_versioned(version, **kwargs):
    if version == "DOSSIER-RESEARCH-NOTES-V2":
        return prepare_notes_v2(**kwargs)
    if version == "DOSSIER-RESEARCH-PACKAGE-V1":
        from dossier_two_stage_research_worker import prepare_research_transport
        return prepare_research_transport(**kwargs)
    raise ValueError("unknown version; implicit schema migration forbidden")

def inspect_research_versioned(version, **kwargs):
    if version == "DOSSIER-RESEARCH-NOTES-V2":
        return classify_notes_v2(**kwargs)
    if version == "DOSSIER-RESEARCH-PACKAGE-V1":
        from dossier_two_stage_async_buffer import receive_buffered_research
        return receive_buffered_research(**kwargs)
    raise ValueError("unknown version; fail closed")

def provisional_assembly_versioned(version, **kwargs):
    if version == "DOSSIER-RESEARCH-NOTES-V2":
        return assemble_notes_v2(**kwargs)
    if version == "DOSSIER-RESEARCH-PACKAGE-V1":
        from dossier_two_stage_async_buffer import provisional_assembly_work
        return provisional_assembly_work(**kwargs)
    raise ValueError("unknown version; fail closed")

def inspect_assembly_versioned(version, **kwargs):
    if version == "DOSSIER-RESEARCH-NOTES-V2":
        return inspect_notes_v2(**kwargs)
    if version == "DOSSIER-RESEARCH-PACKAGE-V1":
        from dossier_two_stage_async_buffer import inspect_buffered_assembly_candidate
        return inspect_buffered_assembly_candidate(**kwargs)
    raise ValueError("unknown version; fail closed")
