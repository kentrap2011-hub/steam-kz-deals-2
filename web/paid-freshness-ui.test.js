const assert = require('assert');
const ui = require('./paid-freshness-ui.js');

const payload = {
  source_mailing_updated_at_utc: '2026-08-30T20:37:11+00:00',
  commercial_source_mailing_updated_at_utc: '2026-09-06T21:00:38+00:00',
  paid_list_freshness: {
    status: 'published',
    scope: 'commercial_only',
    source_mailing_updated_at_utc: '2026-09-06T21:00:38+00:00',
  },
  giveaways: {
    generated_at_utc: '2026-09-07T19:00:00+00:00',
  },
};

assert.strictEqual(
  ui.paidFreshnessTimestamp(payload),
  '2026-09-06T21:00:38+00:00',
  'paid freshness must use the paid-list publication source, not semantic or giveaway timestamps',
);
assert.ok(ui.paidFreshnessLabel(payload).startsWith('Скидки: обновлено '));

const giveawayOnlyChange = JSON.parse(JSON.stringify(payload));
giveawayOnlyChange.giveaways.generated_at_utc = '2026-09-08T10:00:00+00:00';
assert.strictEqual(
  ui.paidFreshnessTimestamp(giveawayOnlyChange),
  ui.paidFreshnessTimestamp(payload),
  'giveaway-only freshness must not advance paid-list freshness',
);

assert.strictEqual(
  ui.paidFreshnessTimestamp({ commercial_source_mailing_updated_at_utc: '2026-09-01T00:00:00Z' }),
  '2026-09-01T00:00:00Z',
  'legacy commercial freshness remains a truthful fallback',
);

console.log('PAID_FRESHNESS_UI_TESTS=PASS');
