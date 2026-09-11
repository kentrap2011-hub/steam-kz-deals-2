# QUEUED TASK — steam-error-notification-watch-01

Status: `queued_later_do_not_start_now`
Mode when authorized later: `IMPLEMENT_AND_CREATE_AUTOMATION`

## Goal

Create a separate ChatGPT scheduled check for Steam refresh problems after the Steam partial-publish/problem-list mechanism is implemented and producing a durable canonical report in GitHub.

## Intended behavior

- Run approximately once per hour.
- Read only the latest canonical Steam refresh problem summary/list from GitHub.
- If there are no unresolved problems, do not notify the user.
- If there is a new or changed unresolved problem set, notify the user with a concise summary such as: `10 games and 1 catalog segment require review`.
- Do not repeat the same unchanged notification every hour.
- The notification should distinguish failed known games from failed/unread catalog segments.
- The check must not repair, retry, mutate, or investigate the failed games automatically.
- After notification, the Director/user can inspect each problem separately.

## Dependency

Do not create or enable this scheduled task until `steam-partial-publish-failure-queue-01` is implemented and the exact durable GitHub report path/schema is known and verified.

## Explicit user instruction

Add this to the queue now, but do not work on or create the scheduled task yet.
