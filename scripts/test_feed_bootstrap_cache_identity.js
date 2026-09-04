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

function basePayload() {
  return {
    generated_at_utc: '2026-09-03T18:29:04Z',
    giveaway_generated_at_utc: '2026-09-03T19:16:45.220980Z',
    giveaway_status: 'complete',
    giveaways: [{ source: 'epic', title: 'Alone With You' }],
    items: [{ appid: 1, name: 'Cached game' }],
  };
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
  win.init = async () => {
    const response = await win.fetch(DATA_URL, { cache: 'no-store' });
    await response.json();
  };

  const initial = await win.fetch(DATA_URL, { cache: 'no-store' });
  const delivered = await initial.json();
  await new Promise(resolve => setTimeout(resolve, 0));
  await controller.whenBackgroundIdle();
  await new Promise(resolve => setTimeout(resolve, 0));

  return { controller, delivered };
}

async function main() {
  const identityProbe = createFeedBootstrapResilience({
    fetch: async () => responseFor(basePayload()),
    AbortController,
    console: { info() {}, warn() {}, log() {} },
  });

  const original = basePayload();
  const same = clone(original);
  assert.strictEqual(
    identityProbe.payloadIdentity(original),
    identityProbe.payloadIdentity(same),
    'same common and giveaway publication state must remain identical',
  );

  const changedGenerated = clone(original);
  changedGenerated.giveaway_generated_at_utc = '2026-09-03T20:00:00Z';
  assert.notStrictEqual(
    identityProbe.payloadIdentity(original),
    identityProbe.payloadIdentity(changedGenerated),
    'giveaway publication timestamp must participate in payload identity',
  );

  const changedStatus = clone(original);
  changedStatus.giveaway_status = 'partial';
  assert.notStrictEqual(
    identityProbe.payloadIdentity(original),
    identityProbe.payloadIdentity(changedStatus),
    'giveaway status must participate in payload identity',
  );

  const changedCount = clone(original);
  changedCount.giveaway_generated_at_utc = '2026-09-03T20:01:00Z';
  changedCount.giveaways.push({ source: 'gog', title: 'Another Giveaway' });
  assert.notStrictEqual(
    identityProbe.payloadIdentity(original),
    identityProbe.payloadIdentity(changedCount),
    'changed canonical giveaway publication/list count must not be identical',
  );

  let scenario = await runRefreshScenario(original, same);
  assert.strictEqual(scenario.controller.state.refreshOutcome, 'identical');
  assert.deepStrictEqual(scenario.delivered, original);

  scenario = await runRefreshScenario(original, changedGenerated);
  assert.strictEqual(scenario.controller.state.refreshOutcome, 'updated');

  scenario = await runRefreshScenario(original, changedStatus);
  assert.strictEqual(scenario.controller.state.refreshOutcome, 'updated');

  scenario = await runRefreshScenario(original, changedCount);
  assert.strictEqual(scenario.controller.state.refreshOutcome, 'updated');

  scenario = await runRefreshScenario(original, original, { failNetwork: true });
  assert.deepStrictEqual(scenario.delivered, original, 'cache-first payload must remain usable when refresh fails');
  assert.strictEqual(scenario.controller.state.source, 'cache');
  assert.strictEqual(scenario.controller.state.status, 'ready');
  assert.strictEqual(scenario.controller.state.refreshOutcome, 'failed');

  console.log('giveaway cache identity regression: PASS');
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
