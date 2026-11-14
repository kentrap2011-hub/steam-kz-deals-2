# Dossier V2 — short Research intake route (new cohorts only)

Research is semantic work. The chat **does not** handle Git SHA, markers, manifests,
handoff hashes, schema assignments, typed receipts or CAS writes.

## Launch
- Only after the owner has created and separately authorized a new one-use V2
  batch. Use its exact `trial_id` and `sandbox/{trial_id}` branch.
- The sandbox must have been frozen **after** the Research intake workflow was
  merged to `main`. Earlier immutable batches (including the already published
  fresh6 trial) keep the legacy transport; do not retrofit or re-authorize them.
- Read the GitHub-frozen manifest **once** and Research each exact AppID/edition
  in its listed order. Do not invent items or repeat already submitted paths.

## One write per game
Use the connected `mcp__GitHub__create_file` operation with:
- `repository_full_name: kentrap2011-hub/steam-kz-deals-2`
- `branch: sandbox/{trial_id}`
- `path: data/ai_inbox/dossier_notes_v2_intake/{trial_id}/{appid}.json`
- `content`: UTF-8 JSON in this small shape:

```json
{
  "appid": "1000010",
  "notes": "Neutral observations on gameplay, player reactions and limitations.",
  "unknowns": "Optional unresolved issues.",
  "conflicts": "Optional conflicting impressions.",
  "source_urls": []
}
```

Only `appid` and `notes` are required. Up to 20 optional public HTTPS links can
be supplied; there is no search-history, access-proof, quote or date log.
If no findings were available, use `"notes": ""`, no links and say so plainly.
Never invent findings or private source information.

A GitHub `push` workflow on the isolated sandbox validates the original owner's
approval and the immutable assignment, then produces the unchanged strict V2
Research candidate plus typed Research receipt. It performs one create-only
fast-forward push. It neither runs Research/Assembly nor retries and it cannot
publish to canonical Dossier, V1, Deep or production.

After a successful GitHub `create_file` response, continue to the next distinct
game without maintaining a JS session handoff. The submission itself is **not**
a confirmed receipt or final acceptance. Report separately: plain submissions,
confirmed GitHub receipts (only if checked), and any unresolved/failed intake.
On uncertain or rejected write, stop that item and inspect its exact path; never
write an alternate path or overwrite it.

The older two-call connector runbook remains available for Assembly and
already-issued immutable cohorts. Do not change their history.
