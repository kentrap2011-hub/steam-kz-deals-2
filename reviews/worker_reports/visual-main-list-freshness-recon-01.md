# Visual main-list freshness recon 01

Task: `WORKER_TASK_VISUAL_MAIN_LIST_FRESHNESS_RECON_01.md`  
Mode: `READ-ONLY / RECON`  
Priority: `VERY_HIGH_USER_PRIORITY`

## Executive conclusion

As of 2026-09-07, the published **main paid-discount list is stale and must not be treated as a list of currently active Steam discounts**.

The last proven commercial/source snapshot behind the published `items` is the snapshot whose timestamp is rendered to the user as:

`31 авг. 2026, 00:37`

A later full visual-payload rebuild happened on **2026-09-01 08:20:42 UTC**, but that rebuild reused the already-old commercial source and therefore did **not** make the paid discount list fresher. Later changes on 2026-09-05/06 were giveaway-only semantic refreshes; that path explicitly preserves the paid `items`, so those commits also do not count as main-list refreshes.

Therefore the date of the artifact/commit and the date of the commercial list freshness are different things. For the user, the relevant freshness date is the last successful refresh of the paid discount `items`, not the last write to `current.json` and not the last giveaway refresh.

## 1. When the main discount list was really last successfully updated

### Commercial list freshness

Last proven successful commercial snapshot currently represented by the published paid `items`:

**31 Aug 2026, 00:37 — the source timestamp currently rendered by the site.**

That is the meaningful freshness point for the main list.

### Later writes that must not be mistaken for a commercial refresh

- **2026-09-01 08:20:42 UTC** — a full `Refresh daily visual payload` rebuild occurred, but it did not advance the commercial source snapshot used for the paid list.
- **2026-09-05/06** — giveaway refreshes changed giveaway semantics/data while deliberately guarding the paid `items` against mutation.

So neither of those later writes makes the main discount list current.

## 2. Why the first visible games show `скидка закончилась`

This status is not evidence that the frontend randomly broke and it is not a reason to manually delete the rows.

The frontend derives the expired state from the stored `sale_end_utc`. Once current time is later than that stored end time, the already-published row is rendered as `скидка закончилась`.

Verified top examples from the published payload:

| Game | Stored sale end | What happened |
| --- | --- | --- |
| `Fable Anniversary` | `2026-09-01 17:00 UTC` | The stored discount end passed after the commercial snapshot. Because the paid list was not refreshed, the old row remained in the payload and the frontend now truthfully marks it expired. The stored discount price must no longer be treated as a current price. |
| `Psychonauts 2` | `2026-09-01 17:00 UTC` | Same mechanism: the sale deadline passed, the stale commercial row remained, and the frontend switched the row to the expired state. |

The same rendering rule explains the other visible upper rows that currently show `скидка закончилась`: they are rows from the old commercial snapshot whose stored sale deadline has already passed. They are **not** being intentionally retained by a fresh commercial refresh; they remain because the commercial `items` snapshot itself has not advanced.

Classification of the observed problem:

- the sale deadline in the stored snapshot really passed after that snapshot;
- the UI intentionally keeps rendering the row that is still present in the payload and marks it expired instead of pretending the discount is active;
- the stored price/discount data is stale after expiry and cannot be assumed current;
- the underlying reason the rows are still there is that the **main list has not received a fresh commercial refresh**.

## 3. Can the main list currently be trusted as a list of active discounts?

**No.**

It can still truthfully show that a previously known discount has expired, but the collection as a whole cannot currently be trusted as an up-to-date list of active discounts because its commercial snapshot is from 31 Aug while the site is being viewed on 7 Sep.

The expired badges are therefore useful evidence of staleness, not the root bug themselves.

No manual removal of expired games and no manual price update should be used to hide this state.

## 4. Exact blocker preventing a fresh main list from being published

The Steam collection side is not the blocker.

The existing daily Steam collector is running and had a successful fresh run as recently as **2026-09-06**. Its output goes to the production shortlist path.

The blocker is the **missing active handoff from that fresh daily shortlist into the canonical commercial mailing/visual build used by the website**:

1. the daily Steam collector refreshes `data/production/shortlist`;
2. the visual build consumes the canonical commercial source (`data/raw/mail/current.json` / its mailing handoff), not the fresh shortlist directly;
3. `build-daily-visual-payload.yml` exists as the canonical visual builder, but there is no active scheduled chain that takes each successful fresh shortlist through the existing commercial handoff and into a new paid `items` payload;
4. deployment itself is alive, and giveaway refreshes demonstrate that the published visual artifact can still be updated;
5. therefore the precise failure is a **commercial refresh handoff/orchestration gap**, not a dead Steam fetcher and not a dead deploy.

This must not be “fixed” by creating a second writer or a second scheduler. The existing single-writer/fail-closed architecture should be preserved.

## 5. What freshness information should be shown to the user

The old proposal to simply rename:

`Данные:` -> `Рассылка:`

is insufficient and must remain cancelled.

A single generic timestamp is misleading because the paid discount list and giveaways can refresh independently.

The minimal honest UI should expose **freshness by data domain**:

- `Скидки: обновлено <time of last successful paid-list refresh>`
- `Раздачи: обновлено <time of last successful giveaway refresh>`

For the current stale paid list, the header must additionally surface an explicit stale state, for example:

`Скидки: обновлено 31 авг., 00:37 · список устарел`

The timestamp used for `Скидки` must advance **only after a successful canonical paid-list refresh has passed the existing gates and been published**. A giveaway-only patch must not advance it.

If the paid-list freshness exceeds the accepted freshness window, the UI should say that the list is stale rather than leaving the user to infer that from expired rows.

## 6. One minimal next IMPLEMENT

### `WORKER_TASK_VISUAL_MAIN_LIST_REFRESH_HANDOFF_IMPLEMENT_01`

Minimal goal:

**Repair/reconnect the existing canonical handoff so that a successful daily Steam shortlist refresh reaches the existing single commercial mailing/visual build-and-publish path and produces fresh paid `items`. Do not add another scheduler or writer.**

Required boundaries for that IMPLEMENT:

- reuse the existing canonical writer/build path;
- preserve freshness gates and fail-closed behavior;
- do not change Taste;
- do not manually delete expired rows;
- do not manually patch prices;
- expose/persist the actual successful paid-list refresh timestamp separately from giveaway freshness so the header can truthfully show stale/current state.

This is the single next IMPLEMENT. No further implementation is started by this recon report.

## Non-actions / scope confirmation

This recon did **not**:

- modify application code;
- modify prices or discount rows;
- delete expired games;
- weaken freshness/fail-closed rules;
- change Taste;
- create a second writer or scheduler;
- execute `WORKER_TASK_VISUAL_HEADER_DATA_LABEL_IMPLEMENT_01.md` or the cancelled `Данные:` -> `Рассылка:` change;
- start the next task.
