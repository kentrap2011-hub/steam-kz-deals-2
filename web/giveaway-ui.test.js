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
function fakeToggleHost(){
  const attrs={'aria-expanded':'false'};
  const button={
    getAttribute(name){return attrs[name]},
    setAttribute(name,value){attrs[name]=String(value)},
    addEventListener(type,handler){if(type==='click')this.clickHandler=handler},
  };
  const content={hidden:true};
  const classes=new Set();
  const host={
    querySelector(selector){if(selector==='.giveaway-toggle')return button;if(selector==='.giveaway-content')return content;return null},
    classList:{
      toggle(name,on){if(on)classes.add(name);else classes.delete(name)},
      contains(name){return classes.has(name)},
    },
  };
  return {host,button,content};
}

{
  const p=payload('active',[{game_key:'g:1',title:'Example',offers:[offer('epic','epic:1')]}]);
  const vm=GiveawayUI.viewModel(p,NOW);
  assert.equal(vm.state,'active');
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes('🎁'));
  assert(html.includes('Бесплатные раздачи'));
  assert(html.includes('(1)'));
  assert(html.includes('aria-expanded="false"'));
  assert(/class="giveaway-content" hidden/.test(html));
  assert(html.includes('Забрать в Epic Games'));
  assert(html.includes('https://store.epicgames.com/en-US/p/test-game'));
}

{
  const {host,button,content}=fakeToggleHost();
  GiveawayUI.bindToggle(host);
  assert.equal(button.getAttribute('aria-expanded'),'false');
  assert.equal(content.hidden,true);
  button.clickHandler();
  assert.equal(button.getAttribute('aria-expanded'),'true');
  assert.equal(content.hidden,false);
  assert.equal(host.classList.contains('is-expanded'),true);
  button.clickHandler();
  assert.equal(button.getAttribute('aria-expanded'),'false');
  assert.equal(content.hidden,true);
  assert.equal(host.classList.contains('is-expanded'),false);
  button.clickHandler();
  assert.equal(button.getAttribute('aria-expanded'),'true');
  assert.equal(content.hidden,false);
}

{
  const p=payload('active',[{
    game_key:'g:identity-unproven',
    title:'Same Looking Title',
    steam_analysis:{summary:'UNSAFE_TITLE_ONLY_ANALYSIS',why_fit:['UNSAFE_PLUS'],risks:['UNSAFE_MINUS']},
    offers:[offer('epic','epic:unsafe')],
  }]);
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes('Анализ пока неполный'));
  assert(html.includes('Описание'));
  assert(html.includes('Плюсы'));
  assert(html.includes('Минусы'));
  assert(html.includes('не переносим Steam-анализ по названию'));
  assert(!html.includes('UNSAFE_TITLE_ONLY_ANALYSIS'));
  assert(!html.includes('UNSAFE_PLUS'));
  assert(!html.includes('UNSAFE_MINUS'));
}

{
  const html=GiveawayUI.buildMarkup(payload('empty',[]),NOW);
  assert(html.includes('нет активных'));
  assert(html.includes(GiveawayUI.EMPTY_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('unavailable',[]);
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes('проверка недоступна'));
  assert(html.includes(GiveawayUI.UNAVAILABLE_COPY));
  assert(!html.includes('giveaway-claim'));
}

{
  const p=payload('active',[{game_key:'g:expired',title:'Expired',offers:[offer('epic','epic:expired','2026-09-01T19:59:59Z')]}]);
  const html=GiveawayUI.buildMarkup(p,NOW);
  assert(html.includes('обновление'));
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
  const index=fs.readFileSync(require.resolve('./index.html'),'utf8');
  const giveaway=index.indexOf('id="giveawayBlock"');
  const paidPosition=index.indexOf('class="position-row"');
  assert(giveaway>=0&&paidPosition>giveaway);
  assert(index.includes('aria-expanded="false"'));
  assert(index.includes('class="giveaway-content" hidden'));
}

{
  const before={items:[{id:'paid:1'}],queue:{cursor:3},games:{'paid:1':{status:'final'}}};
  const copy=JSON.parse(JSON.stringify(before));
  GiveawayUI.viewModel(payload('active',[{game_key:'g:1',title:'Free',offers:[offer('epic','epic:1')]}]),NOW);
  const {host}=fakeToggleHost();
  GiveawayUI.toggleExpanded(host);
  GiveawayUI.toggleExpanded(host);
  assert.deepStrictEqual(before,copy);
}

console.log('GIVEAWAY_UI_TESTS=PASS');
