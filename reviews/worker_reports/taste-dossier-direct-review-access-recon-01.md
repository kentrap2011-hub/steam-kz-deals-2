# Taste Dossier Direct Review Access Recon 01

- Task ID: `taste-dossier-direct-review-access-recon-01`
- Mode: `READ-ONLY / RECON`
- Date: `2026-09-15`
- Final status: `recon_complete_setup_required`
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Baseline `main` HEAD before this report: `f1191907239d0bcde78c5cd516656c315714219e` (`director: add direct Steam review access recon task`)

## 1. Scope and non-actions

This recon evaluated whether the existing live Taste Steam Review Dossier Scheduled Task can be given a **stateless direct read capability** for the official Steam `appreviews` source, so that Scheduled ChatGPT can fetch fresh individual review bodies during semantic analysis, decide whether another page is required, and discard raw bodies after synthesis.

No dossier `Run now` was pressed. No Scheduled Task UI was changed. No workflow was manually dispatched. No production runtime/config/code was changed. No current g1/g2 artifact was changed or recovered. Taste Semantic Producer was not changed. No raw-review archive, cache, database, object-store collection, or GitHub review-body artifact was created.

The only repository write authorized and performed by this recon is this durable report.

## 2. Architecture preflight

The required START gate was completed against the current repository baseline, including:

- `CHAT_PROTOCOL.md`
- `DIRECTOR_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `PROJECT_ROUTES.md` relevant routes
- `PROJECT_DECISIONS.md` relevant decisions
- `reviews/worker_reports/taste-dossier-review-source-recon-01.md`
- `reviews/worker_reports/taste-dossier-non-review-defect-repair-01.md`
- `reviews/worker_reports/taste-dossier-full-defect-sweep-01.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `config/taste_steam_review_dossier_schema.json`
- `config/execution_ownership_contract.json`

Preflight result:

1. GitHub/GitHub Actions remains the canonical control plane for work scope, ordering, canonical progress, validation, persistence, recovery, retry/gap interpretation and completeness.
2. Scheduled ChatGPT remains the semantic data-plane worker.
3. A direct Steam review tool is architecture-compatible only as a bounded **read-only data-plane capability**. It must not own queueing, retry backlog, completion, canonical dossier persistence or scheduling.
4. The tool must not write canonical artifacts or hold durable raw-review state.
5. The existing dossier schema and repaired non-review pipeline do not require a durable raw-review archive. Compact final provenance/hashes are sufficient.

No ownership change is required for the direct design.

## 3. Why the prior GitHub-prefetch design is being reconsidered

`taste-dossier-review-source-recon-01` selected GitHub-prepared review evidence because, at that time, the existing Scheduled Task web path could not deterministically fetch concrete `store.steampowered.com/appreviews/<appid>` JSON URLs. GitHub Actions access to the endpoint was proven, so prefetch was the only proven production transport.

The user has now explicitly rejected the storage shape of that recommendation as the preferred architecture. The desired behavior is instead:

`Scheduled Task -> fresh stateless Steam review read -> semantic analysis -> optional next page -> compact dossier`

This is preferable if it can be made production-safe because:

- no review-body batches are committed or staged in GitHub;
- evidence is fresher at semantic-analysis time;
- ChatGPT itself decides whether another batch is semantically useful;
- the existing adaptive sampling logic remains with the semantic worker;
- GitHub remains unchanged as control plane.

The question in this recon is therefore not whether Steam exposes review bodies; that was already established. The question is whether a direct callable path can be made available to the actual Scheduled Task runtime.

## 4. Steam source contract remains suitable

Valve's current official Steamworks documentation still defines the public endpoint:

`GET https://store.steampowered.com/appreviews/<appid>?json=1`

Official documentation:

- https://partner.steamgames.com/doc/store/getreviews?l=english

Valve documents all fields required by the dossier worker:

- `reviews[].recommendationid`
- `reviews[].language`
- `reviews[].review` — the written review body
- `reviews[].timestamp_created`
- `reviews[].timestamp_updated`
- `reviews[].voted_up`
- response `cursor`

Valve also documents:

- `language=<Steam language code>|all`;
- `cursor=*` for the first page, then the returned cursor for the next page;
- cursor values may require URL encoding;
- `filter=recent` or `updated` is appropriate for cursor traversal toward exhaustion;
- `num_per_page` supports up to 100 reviews.

The current dossier contract uses semantic batches of 20, so `num_per_page=20` is the preferred direct-tool default even though Steam permits larger pages.

### Russian lane

Use Steam `language=russian`.

The returned objects independently identify `language`, so the tool/worker can verify the lane rather than relying on store-page locale.

### Non-Russian lane

The dossier contract means **non-Russian**, not merely English. The clean source recipe therefore remains:

1. request Steam with `language=all`;
2. exclude response objects whose `language == "russian"`;
3. preserve the source cursor and continue if the semantic worker needs more evidence.

Because filtering can reduce the number of eligible non-Russian reviews in one source page, the tool must report both upstream count and returned eligible count and must expose the next cursor exactly.

### Representative appids

The prior source recon already established the required representative group-3 set and live body availability/public review populations:

- `1158890` — White Shadows
- `1164940` — Trepang2
- `1169040` — Necesse
- `1172380` — STAR WARS Jedi: Fallen Order™

That earlier recon also observed live individual Steam Community bodies for all four appids and Russian review evidence/populations for the set, while Valve's official `appreviews` schema supplies the deterministic language/body/id/polarity/timestamp/cursor contract needed here.

Per the current task's source-baseline instruction, this recon did not repeat broad source discovery or create a raw-body sample archive. The unresolved layer is delivery into Scheduled ChatGPT.

## 5. Candidate direct-access mechanisms investigated

### Candidate A — existing Steam or generic HTTP/REST plugin

The current Plugin Directory was searched for:

- `Steam`
- `HTTP`
- `REST`
- `fetch API request URL`
- webhook/Pipedream/Zapier/Make/generic HTTP-request variants

No Steam-specific review plugin and no generic arbitrary HTTP/REST fetch plugin suitable for this task was found. Broad `REST`/automation searches returned unrelated product plugins, not an arbitrary GET capability.

The currently exposed connected-tool set also does not contain a generic HTTP connector. GitHub is available, but its connector is repository-specific and is not an external Steam HTTP proxy.

Result: **no install-now existing plugin solves this task in the current environment.**

### Candidate B — native Scheduled Task web/search path

Ordinary web/search is not equivalent to the structured source and remains rejected as the production sampler.

The previous recon and live group-3 attempt established the practical problem: store/search/community surfaces may expose aggregates or individual crawled bodies, but they do not provide a deterministic review-ID stream, exact language lane and cursor continuation contract.

The current interactive text-web safety path also does not establish arbitrary parameterized `appreviews/<appid>` fetch as a stable callable contract. A concrete raw JSON URL can be rejected when it has not been surfaced through the web safety/navigation path.

Result: **do not rely on ordinary search/web scraping for production dossier review sampling.**

### Candidate C — ChatGPT Work cloud browser directly opening `appreviews`

There is materially stronger product support in current OpenAI documentation than existed in the old Tasks model.

OpenAI currently documents that:

- Work can run through Scheduled Tasks;
- Scheduled Tasks can use connected apps and browser;
- cloud browser can read public websites and continue after the user leaves;
- public websites can still block automated browser agents.

Current sources:

- https://openai.com/index/chatgpt-for-your-most-ambitious-work/
- https://help.openai.com/en/articles/20001275/
- https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt
- https://help.openai.com/en/articles/10291617-chatgpt-tasks

Therefore a **Work Scheduled Task browser** is a plausible direct stateless transport to a public JSON endpoint.

However it is not yet production-proven for this dossier worker because:

1. the existing live dossier Scheduled Task has not been changed or run in Work/browser mode during this recon;
2. the current task explicitly forbids `Run now` and Scheduled UI changes;
3. OpenAI warns that sites may block cloud-browser automation;
4. the previous production worker already failed to establish reliable structured Steam API access through its then-current web surface;
5. browser navigation is broader and less contract-bound than the desired narrow Steam-specific tool.

Result: **plausible, but insufficiently proven to declare the direct production path selected.** It is useful as an acceptance fallback, not the preferred narrow interface.

### Candidate D — custom narrow ChatGPT app/plugin backed by a remote stateless Steam tool

OpenAI currently supports custom apps built on MCP / Apps SDK. The relevant current documentation states that ChatGPT can call approved app tools, and a remote MCP endpoint can expose a deliberately narrow operation.

Sources:

- https://help.openai.com/en/articles/11487775-connectors-in-chatgpt
- https://help.openai.com/en/articles/12515353-build-with-the-apps-sdk
- https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt
- https://help.openai.com/en/articles/20001256/

This is the best technical fit for the requested architecture because the app can expose exactly one read operation and can prevent arbitrary URL access.

Important current product boundary:

- Scheduled Tasks are documented to use **supported apps**, including connected-app workflows.
- The existing production dossier Scheduled Task has already empirically used the GitHub app/connector during one invocation, including repeated repository reads and publication of multiple buffered groups. Thus app invocation from Scheduled execution is real, not theoretical.
- OpenAI custom-app documentation does **not** provide a blanket guarantee that every arbitrary custom MCP app/plugin is automatically available to every existing Scheduled Task surface.
- Private custom MCP/developer-mode setup is currently documented for Business/Enterprise/Edu, with Pro supporting read/fetch MCPs in developer mode. The current personal Plus surface is not documented as providing private custom-MCP developer-mode attachment.
- The Plugin Directory is visible across ChatGPT plans, but individual plugin/app availability still depends on plan, surface, rollout and included capabilities.

Therefore the custom-tool architecture is technically sound, but **installation/distribution plus Scheduled Task availability must be proven on the actual account/surface before production use**.

Result: **best direct architecture, but needs product setup and acceptance.**

### Candidate E — repository-hosted public stateless proxy called through browser

A tiny serverless endpoint could live from repository-managed source and proxy bounded Steam `appreviews` requests without persisting bodies. This would satisfy the intermediary statelessness requirement.

But if the Scheduled Task calls it only through generic browser/web navigation, the decisive Scheduled-runtime URL-access problem has merely moved from Steam to another parameterized endpoint. It also provides less tool-level input validation and provenance than an MCP/app operation.

Result: **not preferred as a standalone solution.** The same serverless code is useful as the backend of the narrow app/plugin described above.

### Candidate F — custom GPT action

Current Scheduled Tasks documentation explicitly lists GPTs as unsupported by Tasks.

Source:

- https://help.openai.com/en/articles/10291617-chatgpt-tasks

Result: **not viable.** Do not put the Steam action inside a custom GPT and expect the dossier Scheduled Task to invoke it.

## 6. Scheduled Task compatibility evidence

### Proven now

1. Scheduled Tasks are a current supported ChatGPT execution surface.
2. Current OpenAI documentation says Scheduled Tasks can use supported connected apps.
3. Current Work documentation says Scheduled Tasks can use connected apps and browser.
4. The existing dossier Scheduled Task has already used the GitHub connector live during production acceptance, proving that an external app/tool can participate in a scheduled invocation and can be called repeatedly during the same run.
5. Read-only app calls are the correct permission class for this use case; no per-review write approval is conceptually required.

### Not proven now

1. No suitable Steam/HTTP plugin is currently installed or discoverable.
2. No custom Steam app/plugin has been deployed or connected.
3. No current official product statement was found that guarantees an arbitrary custom MCP app is callable from this exact existing Scheduled Task simply because it is callable in an interactive chat.
4. The existing dossier task was not modified or `Run now` tested, per task prohibition.
5. No empirical repeated custom-tool pagination test has therefore been performed from Scheduled execution.

This missing proof is exactly why the correct status is setup-required rather than direct-path-selected.

## 7. Exact minimal stateless tool shape

Preferred operation:

`get_steam_reviews(appid, lane, cursor?, page_size?)`

Use a lane instead of a free-form URL or unrestricted query object so the tool remains purpose-built and cannot become an arbitrary web proxy.

### Input

```json
{
  "appid": 1169040,
  "lane": "russian",
  "cursor": "*",
  "page_size": 20
}
```

Contract:

- `appid`: integer, `>= 1`.
- `lane`: enum `russian | non_russian`.
- `cursor`: opaque string returned by the previous call; default `*`.
- `page_size`: integer, default `20`, allowed `20..100`; production dossier prompt should use `20`.

No caller-supplied hostname, URL, filter, path, headers, cookies or arbitrary query parameters.

### Upstream mapping

For `lane=russian`:

- host fixed to `https://store.steampowered.com`;
- path fixed to `/appreviews/{appid}`;
- `json=1`;
- `filter=recent`;
- `language=russian`;
- `review_type=all`;
- `purchase_type=all`;
- `num_per_page=page_size`;
- `cursor=<opaque cursor>`.

For `lane=non_russian`:

- identical request except `language=all`;
- remove objects with `review.language == "russian"` before returning them to the model;
- do **not** synthesize a new cursor; return Steam's next cursor from the exact source page consumed.

### Response

```json
{
  "success": true,
  "appid": 1169040,
  "lane": "russian",
  "cursor_used": "*",
  "next_cursor": "<opaque Steam cursor>",
  "upstream_review_count": 20,
  "returned_review_count": 20,
  "source_exhausted": false,
  "reviews": [
    {
      "recommendationid": "<string>",
      "language": "russian",
      "review": "<body>",
      "voted_up": true,
      "timestamp_created": 0,
      "timestamp_updated": 0
    }
  ]
}
```

Only these review fields are required by the direct transport. Do not return reviewer SteamID, username/profile identity, owned-game lists or unrelated personal metadata.

Recommended optional field only if later proven useful to the dossier contract:

- `playtime_at_review`

The response should also expose a bounded structured error on upstream/network/schema failure, without embedding an HTML error body.

## 8. Statelessness and persistence rules

The app/backend must intentionally persist **no review bodies**.

Allowed transient behavior:

- hold the Steam response in memory for the duration of one tool request;
- filter/project the response;
- return the bounded projection to Scheduled ChatGPT;
- discard the response after the request completes.

Allowed operational logging:

- timestamp;
- appid;
- lane;
- HTTP status;
- latency;
- upstream count / returned count;
- error class;
- optionally a hash of cursor/recommendation IDs for diagnostics.

Forbidden logging/storage:

- review body text;
- usernames/SteamIDs;
- full raw Steam JSON;
- durable page cache;
- GitHub review-body artifacts;
- object-storage/database archive.

The final canonical dossier may continue to store compact provenance and hashes under the existing contract. Platform-level ChatGPT/app-provider retention is governed by those products' own data policies; this design creates no additional project-owned raw-review archive.

## 9. Hosting, auth and setup requirements

### Tool runtime

Use a small remote HTTPS stateless service implementing MCP / Apps SDK tool semantics. A serverless runtime is sufficient; it only needs outbound HTTPS access to `store.steampowered.com` and enough execution time for one bounded GET.

The code may be repository-owned, but the request path must be live and synchronous. It must not trigger GitHub Actions and wait for a committed artifact.

### Steam credentials

None expected. The official `appreviews` endpoint is public and the prior project recon already established unauthenticated access semantics.

### ChatGPT-side credentials

Prefer a no-auth read-only app if the distribution surface allows it. No Steam OAuth/login should be introduced.

If the app-distribution surface requires its own service authentication, that authentication should protect the tool endpoint only; it must not change the Steam source contract.

### Current account/product setup issue

The current product docs do not establish a zero-setup private custom-MCP path for a personal Plus account. Private custom-app developer mode is documented for Business/Enterprise/Edu, and read/fetch MCP developer mode is documented for Pro. A Plugin Directory app can be visible across plans, but actual install/invoke support is capability- and surface-dependent.

Therefore a production implementation must include one of these supported distribution outcomes and then prove it on the actual Scheduled surface:

- an installable Plugin Directory listing containing the Steam Reviews app; or
- an account/workspace surface that explicitly supports attaching the custom read-only app to Scheduled execution.

No plan change is authorized by this recon.

## 10. Adaptive paging feasibility

The tool shape supports the exact desired semantic loop:

1. worker requests Russian page 1;
2. worker analyzes it;
3. worker requests the returned Russian cursor only if more evidence is needed;
4. worker repeats for non-Russian pages;
5. worker stops under the existing semantic stability/ceiling rules;
6. raw bodies are discarded after synthesis.

At the current dossier batch size of 20, the normal hard ceiling of 80 accepted reviews per lane means four full eligible semantic batches per lane. The non-Russian lane can require extra source calls if a `language=all` page contains Russian reviews that are filtered out, so the Scheduled worker must retain the existing global evidence ceiling and an explicit bounded request ceiling.

No current OpenAI documentation found in this recon publishes a guaranteed per-invocation custom-app call count sufficient to replace acceptance testing. Therefore repeated page calls must be part of the acceptance proof rather than assumed.

No user interaction should occur per read call after the app is installed/authorized. The operation must be configured as read-only and should not request confirmation for each page.

## 11. Operational limits and risks

1. **Scheduled custom-app surface support:** main unresolved product proof. Interactive app support is not enough.
2. **Plugin/app distribution on the current Plus account:** must be verified before production wiring.
3. **Steam availability/rate behavior:** Valve does not publish a numeric client rate limit in the reviewed contract. Keep calls bounded and back off transient failures.
4. **Cursor freshness:** treat cursors as run-local opaque values; do not persist them as durable queue state.
5. **Changing source during a run:** new Steam reviews can arrive while paging. Deduplicate by `recommendationid` inside the semantic run if needed; do not make the tool a durable dedupe store.
6. **Untrusted review text:** review bodies are evidence, never instructions. The worker must ignore prompt-like content inside reviews.
7. **Cloud-browser fallback:** Steam or another site may block automated browser agents, so browser success must not be assumed from ordinary human browser access.
8. **Token/time cost:** return only the minimal bounded review projection; do not return author/profile metadata or aggregate fields the dossier does not use.
9. **Failure behavior:** malformed JSON, schema drift, upstream 4xx/5xx or repeated cursor must fail closed for that evidence lane; the tool must not fabricate reviews or silently switch to search snippets.

## 12. Comparison with GitHub-prefetched evidence

| Property | Direct stateless tool | GitHub-prefetched review evidence |
|---|---|---|
| Fresh at semantic-analysis time | yes | snapshot/preparation-time |
| Raw bodies committed to GitHub | no | design must take special measures to avoid durable archive |
| Model decides when to fetch next batch | yes | only if enough prepared evidence was made available in advance |
| Deterministic Steam source | yes | yes |
| GitHub remains control plane | yes | yes |
| Production delivery path proven today | **not yet** | **yes** |
| Current user preference | preferred | fallback only |

GitHub-prefetched evidence therefore remains the **only already-proven production delivery path today**, but it is no longer the preferred target architecture if the direct app/tool acceptance succeeds.

## 13. Decision

The direct design is **technically viable and architecture-compatible**, and a narrow Steam-specific read tool is preferable to permanent or staged review-body collections.

It cannot yet be labeled production-ready because the decisive product fact — repeated invocation of this new custom app/plugin by the actual Scheduled execution surface — has not been empirically proven, and the current task forbids the UI/setup/run changes needed to prove it.

This is not a Steam-source blocker. It is a **ChatGPT product setup + Scheduled-surface acceptance blocker**.

Final status: `recon_complete_setup_required`

## 14. One next step only

Create one separate `IMPLEMENT + ACCEPTANCE` task whose scope is limited to the direct read capability:

- implement the remote stateless `get_steam_reviews` operation above;
- package/expose it through a supported ChatGPT app/plugin distribution path available to the actual account;
- install/connect it once with read-only/no-per-request-approval behavior;
- use an isolated non-production Scheduled Task to prove that scheduled execution can call the tool without the user present, fetch Russian and non-Russian bodies for the representative appids, consume the returned cursor for at least a second page in the **same invocation**, and leave no review bodies in GitHub or application storage;
- if the current account/surface cannot attach the app to Scheduled execution, stop there and record that product limitation instead of changing plans or falling back silently;
- do not touch the production dossier Scheduled Task, g1/g2, runtime pipeline or Taste Semantic Producer until that isolated acceptance passes.

Recommendation: `direct_stateless_review_tool_possible_but_needs_product_setup`
