const assert=require('assert');
const fs=require('fs');
const GiveawayUI=require('./giveaway-ui.js');

const NOW=Date.parse('2026-09-01T20:00:00Z');

function offer(storefront,id,end='2026-09-03T15:00:00Z'){
  const urls={steam:'https://store.steampowered.com/app/10/',epic:'https://store.epicgames.com/en-US/p/test-game',gog:'https://www.gog.com/en/game/test_game'};
  return {storefront,source_offer_id:id,claim_url:urls[storefront],promotion_end_utc:end};
}
function payload(state='active',games=[]){
  return {schema_version:1,source_contract:'CROSS-PLATFORM-GIVEAWAY-V1',state,generated_at_utc:'2026-09-01T19:30:00Z',fresh_until_utc:'2026-09-03T01:30:00Z',games};
}

{
  const p=payload('active',[{game_key:'g:1',title:'Example',offers:[offer('epic','epic:1')]}]);
  const vm=GiveawayUI.viewModel(p,NOW);
  assert.equal(vm.state,'active');
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes('Бесплатные раздачи'));
  assert(html.includes('Забрать в Epic Games'));
  assert(html.includes('https://store.epicgames.com/en-US/p/test-game'));
}

{
  const html=GiveawayUI.buildMarkup(payload('empty',[]),NOW);
  assert(html.includes(GiveawayUI.EMPTY_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('unavailable',[]);
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes(GiveawayUI.UNAVAILABLE_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('active',[{game_key:'g:expired',title:'Expired',offers:[offer('epic','epic:expired','2026-09-01T19:59:59Z')]}]);
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes(GiveawayUI.UPDATING_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('active',[{game_key:'g:1',title:'Future',offers:[offer('epic','epic:1')]}]);
  p.fresh_until_utc='2026-09-01T19:59:59Z';
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes(GiveawayUI.UNAVAILABLE_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('active',[{game_key:'g:multi',title:'Multi',offers:[offer('epic','epic:1'),offer('gog','gog:1')]}]);
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert.equal((html.match(/giveaway-claim/g)||[]).length,2);
  assert(html.includes('Забрать в Epic Games'));
  assert(html.includes('Забрать в GOG'));
}

{
  const p=payload('active',[
    {game_key:'g:a',title:'Game',offers:[offer('epic','epic:a')]},
    {game_key:'g:b',title:'Game ',offers:[offer('gog','gog:b')]},
  ]);
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes('data-giveaway-key="g:a"'));
  assert(html.includes('data-giveaway-key="g:b"'));
}

{
  const app=fs.readFileSync(require.resolve('./app.js'),'utf8');
  assert(app.includes("const DATA_URL='data/current.json'"));
  assert(!app.includes('data/production/giveaways'));
  assert(!app.includes('giveaways/v1/current.json'));
}

{
  const before={items:[{id:'paid:1'}],queue:{cursor:3},games:{'paid:1':{status:'final'}}};
  const copy=JSON.parse(JSON.stringify(before));
  GiveawayUI.viewModel(payload('active',[{game_key:'g:1',title:'Free',offers:[offer('epic','epic:1')]}]),NOW);
  assert.deepStrictEqual(before,copy);
}

console.log('GIVEAWAY_UI_TESTS=PASS');
