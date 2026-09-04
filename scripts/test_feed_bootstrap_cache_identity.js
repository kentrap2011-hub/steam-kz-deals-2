'use strict';

const assert = require('assert');
const { createFeedBootstrapResilience } = require('../web/feed-bootstrap.js');

const DATA_URL = 'https://example.test/steam-kz-deals-2/data/current.json';

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function responseFor(payload) {
  return {
    ok: true,
    status: 200,
    clone() { return responseFor(payload); },
    async json() { return clone(payload); },
  };
}

function classList(initial = []) {
  const values = new Set(initial);
  return {
    contains(value) { return values.has(value); },
    add(value) { values.add(value); },
    remove(value) { values.delete(value); },
  };
}

function createDocument() {
  const nodes = {
    gameCard: { classList: classList([]), textContent: '' },
    emptyFeed: { classList: classList(['hidden']), textContent: '' },
    feedCount: { classList: classList([]), textContent: '1' },
  };
  return {
    visibilityState: 'visible',
    getElementById(id) { return nodes[id] || null; },
    addEventListener() {},
    removeEventListener() {},
  };
}

function freshProductionPayload() {
  return {
    generated_at_utc: '2026-09-03T18:29:04.806292Z',
    production_contract: {
      mode: 'daily_precomputed_read_only_for_ui',
      source_giveaway_snapshot_blob_sha: '7102b39bf64feeb6d8af22bc204e7e72bf077159de7da71a7c0ef42c2c7f5773',
    },
    giveaways: {
      schema_version: 1,
      source_contract: 'CROSS-PLATFORM-GIVEAWAY-V1',
      state: 'active',
      accepted_offer_count_at_build: 1,
      games: [{ source: 'epic', title: 'Alone With You' }],
    },
    items: [{ appid: 1, name: 'Cached game' }],
  };
}

function staleProductionPayload() {
  const payload = freshProductionPayload();
  payload.production_contract.source_giveaway_snapshot_blob_sha = 'old-giveaway-snapshot-sha';
  payload.giveaways.state = 'absent';
  payload.giveaways.accepted_offer_count_at_build = 0;
  payload.giveaways.games = [];
  return payload;
}

async function runRefreshScenario(cachedPayload, freshPayload, { failNetwork = false } = {}) {
  let stored = responseFor(cachedPayload);
  const cache = {
    async match() { return stored; },
    async put(_url, response) { stored = response; },
    async delete() { stored = null; return true; },
  };
  const caches = { async open() { return cache; } };
  const doc = createDocument();
  const win = {
    location: { href: 'https://example.test/steam-kz-deals-2/' },
    addEventListener() {},
    removeEventListener() {},
  };
  const nativeFetch = async () => {
    if (failNetwork) throw new Error('offline');
    return responseFor(freshPayload);
  };
  const controller = createFeedBootstrapResilience({
    window: win,
    document: doc,
    fetch: nativeFetch,
    caches,
    AbortController,
    retryDelayMs: 0,
    timeoutMs: 1000,
    console: { info() {}, warn() {}, log() {} },
  });
  controller.install();

  let initCalls = 0;
  const appliedPayloads = [];
  win.init = async () => {
    initCalls += 1;
    const response = await win.fetch(DATA_URL, { cache: 'no-store' });
    appliedPayloads.push(await response.json());
  };

  const initial = await win.fetch(DATA_URL, { cache: 'no-store' });
  const delivered = await initial.json();
  await new Promise(resolve => setTimeout(resolve, 0));
  await controller.whenBackgroundIdle();
  await new Promise(resolve => setTimeout(resolve, 0));

  return { controller, delivered, initCalls, appliedPayloads };
}

async function main() {
  const fresh = freshProductionPayload();
  const stale = staleProductionPayload();
  const same = clone(fresh);

  assert.strictEqual(Array.isArray(fresh.giveaways), false, 'production giveaways must be object-shaped');
  assert.strictEqual(Object.hasOwn(fresh, 'giveaway_generated_at_utc'), false, 'fixture must not invent flat giveaway timestamp');
  assert.strictEqual(Object.hasOwn(fresh, 'giveaway_status'), false, 'fixture must not invent flat giveaway status');
  assert.strictEqual(
    fresh.generated_at_utc,
    stale.generated_at_utc,
    'giveaway-only publication change must keep ordinary feed generation unchanged',
  );
  assert.deepStrictEqual(fresh.items, stale.items, 'giveaway-only publication change must keep ordinary feed items unchanged');

  const identityProbe = createFeedBootstrapResilience({
    fetch: async () => responseFor(fresh),
    AbortController,
    console: { info() {}, warn() {}, log() {} },
  });

  assert.strictEqual(
    identityProbe.payloadIdentity(fresh),
    identityProbe.payloadIdentity(same),
    'truly identical production-shaped payload must remain identical',
  );
  assert.notStrictEqual(
    identityProbe.payloadIdentity(stale),
    identityProbe.payloadIdentity(fresh),
    'production giveaway snapshot provenance must participate in payload identity',
  );

  let scenario = await runRefreshScenario(fresh, same);
  assert.strictEqual(scenario.controller.state.refreshOutcome, 'identical');
  assert.deepStrictEqual(scenario.delivered, fresh);
  assert.strictEqual(scenario.initCalls, 0, 'identical refresh must not re-run app init');
  assert.deepStrictEqual(scenario.appliedPayloads, []);

  scenario = await runRefreshScenario(stale, fresh);
  assert.deepStrictEqual(scenario.delivered, stale, 'cache-first render must still deliver the stale LKG immediately');
  assert.strictEqual(scenario.controller.state.refreshOutcome, 'updated');
  assert.strictEqual(scenario.initCalls, 1, 'giveaway-only provenance change must apply background payload');
  assert.deepStrictEqual(scenario.appliedPayloads, [fresh], 'background app init must receive the fresh production-shaped payload');

  scenario = await runRefreshScenario(fresh, fresh, { failNetwork: true });
  assert.deepStrictEqual(scenario.delivered, fresh, 'cache-first payload must remain usable when refresh fails');
  assert.strictEqual(scenario.controller.state.source, 'cache');
  assert.strictEqual(scenario.controller.state.status, 'ready');
  assert.strictEqual(scenario.controller.state.refreshOutcome, 'failed');
  assert.strictEqual(scenario.initCalls, 0);

  console.log('giveaway cache identity production-shape regression: PASS');
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
