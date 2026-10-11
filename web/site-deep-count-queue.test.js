'use strict';

// Synthetic PR-only proof of the real UI queue code. No browser, network,
// cache, user state, GitHub production artifact or scheduler is touched.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const progressive = require('./progressive-personalization-ui.js');

const root = __dirname;
const appSource = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const NOW = Date.parse('2026-10-11T12:00:00Z');
const fitId = index => `game:fit-${String(index).padStart(2, '0')}`;
const otherId = index => `game:other-${String(index).padStart(2, '0')}`;
const mockPayload = {
  source_mailing_updated_at_utc: 'synthetic-not-production',
  items: [
    ...Array.from({length: 14}, (_, i) => ({
      id: fitId(i + 1), title: `Fit ${i + 1}`,
      deep_stage_state: 'completed', deep_stage_outcome: 'fit',
      ranking_stage: 'deep_fit', ranking_stage_rank: 1,
      priority_rank: i + 1, total_score: 90 - i,
      sale_end_utc: '2026-10-22T17:00:00Z',
    })),
    ...Array.from({length: 9}, (_, i) => ({
      id: otherId(i + 1), title: `Pending ${i + 1}`,
      deep_stage_state: 'eligible_or_pending', deep_stage_outcome: null,
      ranking_stage: 'not_analyzed', ranking_stage_rank: 4,
      priority_rank: 15 + i, deterministic_purchase_score: 30 - i,
      sale_end_utc: '2026-10-22T17:00:00Z',
    })),
  ],
};

function runUi(savedState) {
  const store = new Map(savedState ? [['steam-deals-visual-state-v1', JSON.stringify(savedState)]] : []);
  const element = () => ({
    addEventListener() {},
    classList: {add() {}, remove() {}, contains() {return false;}, toggle() {}},
    setAttribute() {},
    textContent: '', value: '',
  });
  const dom = new Map();
  const document = {
    getElementById(id) {
      if (!dom.has(id)) dom.set(id, element());
      return dom.get(id);
    },
    querySelectorAll() {return [];},
    addEventListener() {},
  };
  const window = {ProgressivePersonalizationUI: progressive, scrollTo() {}};
  const context = vm.createContext({
    document, window, Date, console,
    localStorage: {
      getItem(key) {return store.get(key) || null;},
      setItem(key, value) {store.set(key, value);},
    },
    fetch: () => Promise.reject(new Error('offline synthetic test: fetching is forbidden')),
    setTimeout, clearTimeout,
    __payload: mockPayload, __now: NOW,
  });
  vm.runInContext(appSource, context, {filename: 'web/app.js', timeout: 2000});
  return vm.runInContext(
    "data=__payload; buildQueue(__now); JSON.stringify({ids:state.queue.ids, settings:state.settings, moved:Object.fromEntries(Object.entries(state.games).filter(([,v])=>v.manual_end_at)), games:state.games, source:state.queue.source})",
    context,
    {timeout: 2000},
  );
}

const fresh = JSON.parse(runUi(null));
assert.equal(fresh.ids.length, 23, '14 Deep-fit + 9 pending cards, none omitted');
assert.deepEqual(fresh.ids.slice(0, 14), Array.from({length: 14}, (_, i) => fitId(i + 1)));
assert.deepEqual(fresh.ids.slice(14), Array.from({length: 9}, (_, i) => otherId(i + 1)));

const initial = {
  games: {},
  settings: {urgency_first: true},
  queue: {source: 'old-snapshot', signature: 'old-order', ids: [], cursor: 0, version: 5},
};
for (let i = 9; i <= 14; i++) initial.games[fitId(i)] = {
  status: i === 9 ? 'liked' : (i === 10 ? 'final' : 'queue'),
  seen: i,
  first_source: 'old-snapshot',
  manual_end_at: 1000 + i,
};
const ordinary = JSON.parse(runUi(initial));
assert.equal(ordinary.ids.length, 23, 'manual-end never deletes Deep cards');
assert.deepEqual(ordinary.ids.slice(0, 8), Array.from({length: 8}, (_, i) => fitId(i + 1)));
assert.deepEqual(ordinary.ids.slice(8, 17), Array.from({length: 9}, (_, i) => otherId(i + 1)));
assert.deepEqual(ordinary.ids.slice(17), Array.from({length: 6}, (_, i) => fitId(i + 9)));
assert.equal(ordinary.settings.urgency_first, true, 'urgency preference survives queue regeneration');
assert.equal(ordinary.games[fitId(9)].status, 'liked');
assert.equal(ordinary.games[fitId(10)].status, 'final');
assert.equal(ordinary.games[fitId(10)].seen, 10);
assert.equal(Object.keys(ordinary.moved).length, 6);
assert.equal(ordinary.source, 'synthetic-not-production');

console.log('PASS: fresh profile = 14 Deep-fit first; six manual-end overrides = 8 Deep-fit + 9 not-analyzed prefix + 6 deferred Deep-fit, all settings and cards retained.');
