# Taste historical submission archive

This directory preserves obsolete or historical Taste submission artifacts for provenance.

Lifecycle rules:
- Active Taste submissions live only at `data/ai_inbox/taste/*.json`.
- Files under `data/ai_archive/taste/**` are historical evidence and are never active ingest candidates.
- Archiving does not make an old producer identity valid. If an archived file is placed back into the active inbox, the current producer fence must reject it normally.
- Malformed or producer-mismatched files that are actually present in the active inbox remain fail-closed blockers; they must never be globally ignored by producer validation.
- Successful current submissions continue to use the existing canonical GitHub ingest path and receipt lifecycle.
