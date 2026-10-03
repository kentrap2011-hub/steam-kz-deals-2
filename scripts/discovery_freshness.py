from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

MAX_DISCOVERY_AGE_HOURS = 18
PRODUCTION_CYCLE_TZ = ZoneInfo('Europe/Samara')


def _parse_timestamp(value, field):
    if not value:
        raise ValueError(f'missing {field}')
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError(f'invalid {field}: {value!r}') from exc
    if parsed.tzinfo is None:
        raise ValueError(f'{field} must be timezone-aware')
    return parsed.astimezone(timezone.utc)


def assess_discovery_freshness(
    manifest,
    shortlist_index,
    mailing_index,
    commercial_observed_at,
    *,
    maximum_age_hours=MAX_DISCOVERY_AGE_HOURS,
):
    observed = (
        commercial_observed_at
        if isinstance(commercial_observed_at, datetime)
        else _parse_timestamp(commercial_observed_at, 'commercial_observed_at')
    )
    if observed.tzinfo is None:
        raise ValueError('commercial_observed_at must be timezone-aware')
    observed = observed.astimezone(timezone.utc)

    source_text = mailing_index.get('source_updated_at_utc')
    source = _parse_timestamp(source_text, 'mailing.source_updated_at_utc')
    manifest_text = manifest.get('updated_at_utc')
    shortlist_text = shortlist_index.get('source_updated_at_utc')

    source_chain_aligned = bool(
        source_text
        and manifest_text == source_text
        and shortlist_text == source_text
    )
    source_complete = bool(
        manifest.get('complete') is True
        and manifest.get('source_has_known_gaps') is not True
        and shortlist_index.get('source_complete') is True
        and shortlist_index.get('source_has_known_gaps') is not True
        and mailing_index.get('source_complete') is True
        and mailing_index.get('manifest_complete') is True
    )

    manifest_count = int(manifest.get('shortlist_items') or -1)
    shortlist_count = int(shortlist_index.get('item_count') or -1)
    mailing_count = int(mailing_index.get('item_count') or -1)
    mailing_source_count = int(mailing_index.get('source_item_count') or -1)
    source_counts_aligned = bool(
        manifest_count >= 0
        and manifest_count == shortlist_count == mailing_count == mailing_source_count
    )

    age_hours = (observed - source).total_seconds() / 3600.0
    age_nonnegative = age_hours >= 0
    within_age_limit = age_nonnegative and age_hours <= float(maximum_age_hours)

    discovery_cycle_date = source.astimezone(PRODUCTION_CYCLE_TZ).date().isoformat()
    commercial_cycle_date = observed.astimezone(PRODUCTION_CYCLE_TZ).date().isoformat()
    same_production_cycle = discovery_cycle_date == commercial_cycle_date

    reasons = []
    if not source_chain_aligned:
        reasons.append('discovery_source_chain_mismatch')
    if not source_complete:
        reasons.append('discovery_source_incomplete_or_has_known_gaps')
    if not source_counts_aligned:
        reasons.append('discovery_candidate_count_chain_mismatch')
    if not age_nonnegative:
        reasons.append('discovery_source_timestamp_is_in_future')
    elif not within_age_limit:
        reasons.append('discovery_source_older_than_allowed')
    if not same_production_cycle:
        reasons.append('candidate_universe_not_rebuilt_for_current_production_cycle')

    fresh = not reasons
    return {
        'schema_version': 1,
        'status': 'fresh' if fresh else 'stale',
        'discovery_generated_at_utc': source.isoformat(),
        'commercial_observed_at_utc': observed.isoformat(),
        'source_binding': {
            'manifest_updated_at_utc': manifest_text,
            'shortlist_source_updated_at_utc': shortlist_text,
            'mailing_source_updated_at_utc': source_text,
            'source_chain_aligned': source_chain_aligned,
            'source_counts_aligned': source_counts_aligned,
            'manifest_shortlist_item_count': manifest_count,
            'shortlist_item_count': shortlist_count,
            'mailing_item_count': mailing_count,
            'mailing_source_item_count': mailing_source_count,
        },
        'source_complete_without_known_catalog_gaps': source_complete,
        'maximum_age_hours': float(maximum_age_hours),
        'discovery_age_hours_at_commercial_observation': round(age_hours, 6),
        'production_cycle_timezone': str(PRODUCTION_CYCLE_TZ),
        'discovery_cycle_date': discovery_cycle_date,
        'commercial_cycle_date': commercial_cycle_date,
        'candidate_universe_rebuilt_for_current_cycle': same_production_cycle and fresh,
        'price_refresh_can_substitute_for_discovery_refresh': False,
        'fresh': fresh,
        'stale_reasons': reasons,
    }


def require_fresh_discovery(
    manifest,
    shortlist_index,
    mailing_index,
    commercial_observed_at,
    *,
    maximum_age_hours=MAX_DISCOVERY_AGE_HOURS,
):
    result = assess_discovery_freshness(
        manifest,
        shortlist_index,
        mailing_index,
        commercial_observed_at,
        maximum_age_hours=maximum_age_hours,
    )
    if not result['fresh']:
        raise RuntimeError(
            'Fresh deal discovery prerequisite failed: '
            + ','.join(result['stale_reasons'])
            + f"; discovery={result['discovery_generated_at_utc']}"
            + f"; commercial={result['commercial_observed_at_utc']}"
        )
    return result


def require_store_snapshot_freshness(store_snapshot):
    freshness = store_snapshot.get('discovery_freshness') or {}
    if (
        freshness.get('status') != 'fresh'
        or freshness.get('fresh') is not True
        or freshness.get('candidate_universe_rebuilt_for_current_cycle') is not True
        or freshness.get('price_refresh_can_substitute_for_discovery_refresh') is not False
    ):
        raise ValueError('Commercial publication requires a fresh current-cycle discovery universe')
    if freshness.get('commercial_observed_at_utc') != store_snapshot.get('observed_at_utc'):
        raise ValueError('Store freshness commercial timestamp does not match store observation')
    if freshness.get('discovery_generated_at_utc') != store_snapshot.get('discovery_source_updated_at_utc'):
        raise ValueError('Store freshness discovery timestamp does not match store source binding')
    return freshness
