const assert=require('assert');
const fs=require('fs');
const GiveawayUI=require('./giveaway-ui.js');

const NOW=Date.parse('2026-09-01T20:00:00Z');

function offer(storefront,id,end='2026-09-03T15:00:00Z',url=null){
  const urls={steam:'https://store.steampowered.com/app/10/',epic:'https://store.epicgames.com/en-US/p/test-game',gog:'https://www.gog.com/en/game/test_game'};
  return {storefront,source_offer_id:id,claim_url:url||urls[storefront],promotion_end_utc:end};
}
function payload(state='active',games=[]){
  return {schema_version:1,source_contract:'CROSS-PLATFORM-GIVEAWAY-V1',state,generated_at_utc:'2026-09-01T19:30:00Z',fresh_until_utc:'2026-09-03T01:30:00Z',games};
}

{
  const p=payload('active',[
    {game_key:'g:1',title:'First',offers:[offer('epic','epic:1')]},
    {game_key:'g:2',title:'Second',offers:[offer('gog','gog:2')]},
  ]);
  const nav=GiveawayUI.navState(p,NOW);
  assert.deepStrictEqual({state:nav.state,count:nav.count,label:nav.label},{state:'active',count:2,label:'(2)'});
  const list=GiveawayUI.buildListMarkup(p,NOW);
  assert.equal((list.match(/giveaway-list-card/g)||[]).length,2);
  assert(list.includes('First'));
  assert(list.includes('Second'));
  assert(list.includes('Epic Games'));
  assert(list.includes('GOG'));
  assert(list.includes('Забрать'));
  assert(list.includes('Подробнее'));
  assert(list.includes('осталось'));
  assert(!list.includes(GiveawayUI.ANALYSIS_INCOMPLETE_COPY));
  assert(!list.includes('Описание</span>'));
  assert(!list.includes('Плюсы</span>'));
  assert(!list.includes('Минусы</span>'));
}

{
  const p=payload('active',[
    {game_key:'g:one',title:'Only This Detail',offers:[offer('epic','epic:one',undefined,'https://store.epicgames.com/en-US/p/only-this')]},
    {game_key:'g:other',title:'Must Stay In List',offers:[offer('gog','gog:other')]},
  ]);
  const detail=GiveawayUI.buildDetailMarkup(p,'g:one',NOW);
  assert(detail.includes('Only This Detail'));
  assert(!detail.includes('Must Stay In List'));
  assert(detail.includes('data-giveaway-detail-back'));
  assert(detail.includes('Описание'));
  assert(detail.includes('Плюсы'));
  assert(detail.includes('Минусы'));
  assert(detail.includes(GiveawayUI.ANALYSIS_INCOMPLETE_COPY));
  assert(detail.includes('https://store.epicgames.com/en-US/p/only-this'));
  assert(detail.includes('до '));
}

{
  const p=payload('active',[{
    game_key:'g:identity-unproven',
    title:'Same Looking Title',
    steam_analysis:{summary:'UNSAFE_TITLE_ONLY_ANALYSIS',why_fit:['UNSAFE_PLUS'],risks:['UNSAFE_MINUS']},
    offers:[offer('epic','epic:unsafe')],
  }]);
  const list=GiveawayUI.buildListMarkup(p,NOW);
  const detail=GiveawayUI.buildDetailMarkup(p,'g:identity-unproven',NOW);
  for(const html of [list,detail]){
    assert(!html.includes('UNSAFE_TITLE_ONLY_ANALYSIS'));
    assert(!html.includes('UNSAFE_PLUS'));
    assert(!html.includes('UNSAFE_MINUS'));
  }
  assert(!list.includes(GiveawayUI.ANALYSIS_INCOMPLETE_COPY));
  assert(detail.includes(GiveawayUI.ANALYSIS_INCOMPLETE_COPY));
}

{
  const empty=payload('empty',[]);
  assert.equal(GiveawayUI.navState(empty,NOW).label,'(0)');
  const html=GiveawayUI.buildListMarkup(empty,NOW);
  assert(html.includes(GiveawayUI.EMPTY_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const unavailable=payload('unavailable',[]);
  assert.equal(GiveawayUI.navState(unavailable,NOW).label,'(!)');
  const html=GiveawayUI.buildListMarkup(unavailable,NOW);
  assert(html.includes(GiveawayUI.UNAVAILABLE_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('active',[{game_key:'g:expired',title:'Expired',offers:[offer('epic','epic:expired','2026-09-01T19:59:59Z')]}]);
  assert.equal(GiveawayUI.navState(p,NOW).state,'updating');
  const html=GiveawayUI.buildListMarkup(p,NOW);
  assert(html.includes(GiveawayUI.UPDATING_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('active',[{game_key:'g:future',title:'Future',offers:[offer('epic','epic:future')]}]);
  p.fresh_until_utc='2026-09-01T19:59:59Z';
  assert.equal(GiveawayUI.navState(p,NOW).state,'unavailable');
  const html=GiveawayUI.buildListMarkup(p,NOW);
  assert(html.includes(GiveawayUI.UNAVAILABLE_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('active',[{game_key:'g:multi',title:'Multi',offers:[offer('epic','epic:1'),offer('gog','gog:1')]}]);
  const list=GiveawayUI.buildListMarkup(p,NOW);
  assert.equal((list.match(/giveaway-claim/g)||[]).length,2);
  assert.equal((list.match(/giveaway-list-card/g)||[]).length,1);
}

{
  const before={items:[{id:'paid:1'}],queue:{cursor:3},games:{'paid:1':{status:'final'}},wishlist:['paid:1']};
  const copy=JSON.parse(JSON.stringify(before));
  GiveawayUI.viewModel(payload('active',[{game_key:'g:1',title:'Free',offers:[offer('epic','epic:1')]}]),NOW);
  GiveawayUI.navState(payload('active',[{game_key:'g:1',title:'Free',offers:[offer('epic','epic:1')]}]),NOW);
  assert.deepStrictEqual(before,copy);
}

{
  const app=fs.readFileSync(require.resolve('./app.js'),'utf8');
  assert(app.includes("const DATA_URL='data/current.json'"));
  assert(!app.includes('data/production/giveaways'));
  assert(!app.includes('giveaways/v1/current.json'));
  assert(app.includes("document.querySelectorAll('.tab').forEach"));
  assert(app.includes("$('wishlistView').classList.toggle('hidden',currentTab!=='wishlist')"));
}

{
  const index=fs.readFileSync(require.resolve('./index.html'),'utf8');
  assert(index.includes('data-tab="giveaway"'));
  assert(index.includes('id="giveawayCount"'));
  assert(index.includes('id="giveawayView" class="hidden list-view giveaway-view"'));
  assert(index.includes('id="wishlistView" class="hidden list-view"'));
  assert(index.includes('data-giveaway-exit'));
  const feedStart=index.indexOf('<section id="feedView">');
  const giveawayView=index.indexOf('<section id="giveawayView"');
  const feedHtml=index.slice(feedStart,giveawayView);
  assert(feedStart>=0&&giveawayView>feedStart);
  assert(!feedHtml.includes('giveaway-list'));
  assert(!feedHtml.includes('giveaway-detail'));
  assert(!feedHtml.includes('giveawayBlock'));
  assert(!index.includes('aria-expanded="false" aria-controls="giveawayContent"'));
}

{
  const source=fs.readFileSync(require.resolve('./giveaway-ui.js'),'utf8');
  assert(source.includes("button.dataset.tab==='giveaway'"));
  assert(source.includes("document.getElementById('giveawayView')?.classList.remove('hidden')"));
  assert(source.includes("document.getElementById('giveawayView')?.classList.add('hidden')"));
  assert(source.includes("data-giveaway-detail-back"));
  assert(source.includes(".tab[data-tab=\"${target}\"]"));
  assert(!source.includes('steam_analysis.summary'));
}

console.log('GIVEAWAY_UI_TESTS=PASS');
