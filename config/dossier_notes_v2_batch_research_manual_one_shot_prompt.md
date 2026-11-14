# Dossier Notes V2 — manual one-shot Research (simplified intake)

**Scope:** one explicitly user-launched Research run for an already owner-issued,
separately authorized, exact frozen GitHub batch. Research only, no issuer,
retry owner, Assembly, writer, canonical ingestion, production or scheduling.

Read `CHAT_PROTOCOL.md` then `CHAT_CONTEXT.md` (START), followed by this
short prompt and `config/dossier_notes_v2_research_intake_runbook.md`.
Do not manually read/execute the legacy connector JS, full transport runbook
or entire V2 contract stack for a new post-merge intake-enabled cohort.
Those checks now belong to the GitHub-owned intake workflow and strict writer.

The owner supplies exactly one `trial_id`. Read its immutable GitHub manifest
`data/control/dossier_notes_v2/manifests/{trial_id}.json` from its corresponding
`sandbox/{trial_id}` branch. Research the exact AppID, title and edition in
frozen order using neutral public feedback; note meaningful positives,
negatives, uncertainties and conflicts. No source-access log or evidence of the
search process is mandatory; public source URLs are optional. Do not claim
unread sources were opened or invent facts.

For each game, create **one plain Research input file** through GitHub's
connected `create_file` tool at
`data/ai_inbox/dossier_notes_v2_intake/{trial_id}/{appid}.json` on the exact
sandbox branch. Its content uses only `appid`, `notes` and optional
`unknowns`, `conflicts`, `source_urls`. GitHub derives the frozen
assignment, validates the one-use owner authorization and the created file,
and creates the normal Research candidate and typed receipt automatically
in its **isolated sandbox-only push workflow**. No manual Git SHA, handoff,
candidate commit, receipt commit or CAS construction in the chat.

Do not send the new plain input to a batch frozen before the GitHub intake
workflow was merged. Those immutable older batches continue to use the
existing `config/dossier_notes_v2_connector_transport_manual_runbook.md`;
never re-freeze or re-authorize them, and never modify published files.

A successful `create_file` confirms only the input submission, not a
GitHub-generated receipt or semantic acceptance. Report number of inputs
submitted and independently confirmed receipts, if checked. Fail closed
on unknown result, path collision or wrong scope. No automatic retries,
schedules or background ChatGPT work.
