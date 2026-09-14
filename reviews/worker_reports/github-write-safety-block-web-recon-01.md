# GitHub write safety block web recon 01

Status: `web_recon_complete_specific_trigger_unobservable`

## Scope

Public-internet-only follow-up for TPI-001. No GitHub safety probes, production Taste work, Scheduled Tasks, dossier backlog, runtime/config/prompt/contract changes, or safety bypasses were performed. This file is the single explicitly allowed durable report write after research.

## Bottom line

The observed TPI-001 behavior belongs to a publicly reported class of OpenAI pre-dispatch safety-check blocking affecting ChatGPT apps/connectors/MCP tools. There is an especially close public precedent in which the ChatGPT GitHub Application's `create_file` and `update_file` actions returned the same message, and the reporter stated the calls never reached GitHub. OpenAI Support acknowledged the broader issue and said engineering was working on it.

OpenAI's official documentation also confirms the general mechanism: write/modify actions can be blocked by ChatGPT's safety layer rather than merely presented for approval. However, no official source found in this recon publishes the exact classifier/root cause, a stable threshold, or a guaranteed workaround for benign false positives.

Narrow classification for TPI-001 after web recon:

`known class of OpenAI pre-dispatch safety-check false positives affecting connectors/MCP, with an exact GitHub create_file/update_file precedent; the specific trigger/root cause for the current session remains unobservable`

## Official OpenAI information

### 1. Safety layer can block app/MCP actions

Source: OpenAI Help — Developer mode and MCP apps in ChatGPT
https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt-beta

OpenAI states that for write/modify actions ChatGPT may request confirmation depending on permissions/context/impact, and that some especially risky actions may be blocked instead of being presented for approval. OpenAI also describes red-teaming, monitoring, and warnings around write actions.

This establishes the existence of a pre-execution safety decision layer, but does not explain benign false positives.

### 2. Official connector write-action outage

Source: OpenAI Status — Partial Disruption of ChatGPT Workspace Connector Write Actions
https://status.openai.com/incidents/01KQDM1K1826RP1FFN86ZNA3WG

- identified: 2026-04-29;
- resolved: 2026-05-05;
- OpenAI reported that write actions for some ChatGPT workspace connectors were automatically disabled and later fully recovered.

Similarity: medium. It proves a real OpenAI-side connector write-action availability failure, but the status page does not say it used the same safety-check message or the same mechanism as TPI-001.

### 3. Exact GitHub Application safety-block precedent, acknowledged by OpenAI Support

Source: OpenAI Developer Community — MCP Connector "Resource not found" thread, comment by `tgravagno`
https://community.openai.com/t/mcp-connector-resource-not-found-tools-call-never-reaches-server/1370632/22

Date: 2026-04-30.

Reported behavior:
- ChatGPT GitHub Application;
- `create_file` and `update_file` specifically;
- exact message: `This tool call was blocked by OpenAI’s safety checks. Please double check what you are sending.`;
- reporter states the call did not reach GitHub and no GitHub JSON response existed; the message was produced on the OpenAI side.

OpenAI Support replies in the same topic:
- 2026-04-20: team actively looking into the issue;
- 2026-05-10: team actively working to fix it;
- 2026-07-12: continuing investigation, coordinating with multiple teams;
- 2026-07-19: OpenAI Support announced that a fix had been deployed for the topic and asked users to report continued occurrences.

Relevant URLs:
https://community.openai.com/t/mcp-connector-resource-not-found-tools-call-never-reaches-server/1370632/21
https://community.openai.com/t/mcp-connector-resource-not-found-tools-call-never-reaches-server/1370632/23
https://community.openai.com/t/mcp-connector-resource-not-found-tools-call-never-reaches-server/1370632/35
https://community.openai.com/t/mcp-connector-resource-not-found-tools-call-never-reaches-server/1370632/36

Similarity: very high for the GitHub `create_file`/`update_file` subcase and exact error text. Caution: the overall topic also covered a separate `Resource not found`/MCP routing problem, so the announced topic-level fix cannot be assumed to explain every later safety block.

### 4. OpenAI Support later acknowledged incorrect safety blocks still occurring

Source: OpenAI Developer Community — ChatGPT App MCP tool calls blocked before reaching MCP server
https://community.openai.com/t/chatgpt-app-mcp-tool-calls-blocked-by-openai-safety-checks-before-reaching-mcp-server/1386059

Initial report date: 2026-07-08.

Reported behavior:
- benign read-only MCP calls blocked with the same safety-check message;
- no server request observed;
- trace showed `externalCallTimeMs: null`, consistent with pre-dispatch blocking;
- multiple users described intermittent behavior and identical calls later succeeding unchanged.

OpenAI Support update, 2026-08-16:
https://community.openai.com/t/chatgpt-app-mcp-tool-calls-blocked-by-openai-safety-checks-before-reaching-mcp-server/1386059/24

Support stated that improvements had been rolled out to reduce incorrect safety blocks affecting legitimate read-only tool calls, but some requests could still be affected and investigation was continuing. Support requested approximate failure time, app/connector, conversation/request ID, and whether the MCP server received the request.

Similarity: high for pre-dispatch false-positive/intermittent safety blocking; lower than the exact GitHub case because this topic primarily documents MCP/read-only calls.

## Additional public user observations

### Custom MCP write actions

Source:
https://community.openai.com/t/write-actions-blocked-on-custom-mcp-server-business-plan-workspace-developer-mode-unavailable-at-workspace-level/1384381

June/July 2026 reports describe:
- same `This tool call was blocked by OpenAI’s safety checks` message;
- write actions blocked before server receipt;
- inconsistent behavior, with retries sometimes succeeding unchanged;
- some users later seeing the same blocks even on read-only tools;
- one user estimated varying block rates across tools rather than a deterministic all-or-nothing failure.

A user reported that OpenAI Support suggested making tool descriptions explicitly non-destructive. That is a user-reported support interaction, not a published official root-cause statement or guaranteed fix. It is not adopted here as a workaround.

Similarity: high for erratic pre-dispatch safety blocking, but custom MCP rather than the built-in GitHub application.

### Reddit: GitHub connector, August and September 2026

Sources:
https://www.reddit.com/r/ChatGPT/comments/1vnlnin/blocked_by_openai_safety_checks_errors_with_the/
https://www.reddit.com/r/OpenAI/comments/1vnlol5/blocked_by_openai_safety_checks_errors_with_the/

Original post date: 2026-08-13.

Reported behavior:
- GitHub connector used for normal repository work;
- reads and some writes worked while other legitimate GitHub operations were blocked before reaching GitHub;
- similar writes could succeed or fail inconsistently;
- discussion explicitly mentions `create_file`, `create_blob`, workflows, and other GitHub write operations;
- a Google Drive user described the exact same operation failing repeatedly and later succeeding unchanged;
- a 2026-09-13 comment says the issue began on Sep 12 after months of normal use and describes `block block block, allowed, 2 min later same file - block`.

Cause: not established. These are user reports, not official OpenAI findings.

Similarity: very high phenomenologically, including current September timing, but evidence quality is lower than OpenAI documentation/support posts.

## Session/context-related public evidence — indirect

Source: openai/codex issue #44279, opened 2026-09-09
https://github.com/openai/codex/issues/44279

A reporter described a benign local build request repeatedly blocked by a safety check in a long resumed Codex session while the exact same prompt succeeded in a brand-new session. The reporter says OpenAI Support requested that fresh-session A/B test.

This is not a connector/GitHub tool-call case and uses a different visible safety message. It therefore does not prove that TPI-001 is session-context-driven. It only shows that session-dependent safety false positives have been publicly reported in another OpenAI surface.

Similarity: medium/indirect.

## Current status / release-note check

OpenAI Status history reviewed through 2026-09-14 contains recent ChatGPT/Work incidents, including Sept 10–12 general errors, but no current incident found that specifically names connector/MCP safety-check false positives or GitHub write-action safety blocking.

Relevant status history:
https://status.openai.com/history

Release/help materials document app write actions and safety controls, but this recon found no release note that publishes a complete root cause for the benign safety-block class or promises that the GitHub `create_file` case is permanently eliminated.

## Confirmed vs observed vs speculative

### Confirmed official/publicly acknowledged

- ChatGPT has a safety layer that can block write/modify app actions rather than merely ask for approval.
- OpenAI has experienced connector write-action outages.
- The OpenAI Developer Community contains an exact GitHub Application `create_file`/`update_file` safety-block report with the same error string and stated pre-GitHub blocking.
- OpenAI Support publicly acknowledged investigation/fix work on the associated connector issue.
- OpenAI Support later acknowledged incorrect safety blocks on legitimate MCP calls and said improvements were deployed while some cases still remained.

### User observations

- identical benign calls may fail and then later pass unchanged;
- reads may work while selected writes fail;
- behavior can appear transient, session-dependent, or action-dependent;
- recent Reddit comments describe the same GitHub pattern in August and September 2026.

### Not established

- the internal classifier or policy rule that blocked TPI-001;
- a stable rate limit, write-count threshold, filename/content pattern, or action quota;
- that accumulated conversation context caused TPI-001;
- that the Apr/May connector-write outage, July MCP routing issue, and present September safety block share one root cause;
- a guaranteed supported workaround that safely prevents false positives.

## Workaround / mitigation finding

No official guaranteed workaround for benign false-positive safety blocks was found.

OpenAI Support's most directly relevant published diagnostic guidance is to capture the approximate failure time, app/connector, conversation or request ID, and whether the downstream server received the request. That is evidence collection, not a bypass.

Community suggestions such as retries, changing tool descriptions, changing approval settings, reconnecting, or starting a new session are not sufficiently authoritative or universally reliable to recommend as a safety bypass. This recon did not apply any of them.

## TPI-001 interpretation

The prior local classification `exact policy cause unobservable` remains correct at the per-incident level, but the web evidence adds an important higher-level fact: the symptom is not unique to this repository or account and has an exact public GitHub connector precedent acknowledged in an OpenAI support thread.

Therefore TPI-001 should not be described merely as an unexplained local GitHub failure. The evidence supports describing it as a member of a known publicly reported OpenAI pre-dispatch safety-block false-positive class, while keeping the specific trigger/root cause unobservable.

## Recommended next step

Do not bypass or repeatedly probe the safety system. If the issue recurs during legitimate work, preserve one diagnostic record containing:
- exact timestamp/timezone;
- ChatGPT surface/session/thread identifier when available;
- connector/app name;
- exact action name and nonsecret arguments;
- exact visible safety message;
- whether a downstream GitHub request/commit was created;
- any exposed request/error/classification metadata.

If escalation is needed, send that bounded evidence to OpenAI Support. No repository/runtime architecture change is justified by this web recon alone.
