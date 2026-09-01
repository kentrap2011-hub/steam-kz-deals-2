const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {createCommitGuard}=require('./image-swipe-sync.js');

function simulateGuard(sequence,resolutionOrder){
  const guard=createCommitGuard();
  const requests=new Map();
  const commits=[];
  for(const key of sequence)requests.set(key,guard.begin(key));
  for(const key of resolutionOrder){
    const request=requests.get(key);
    if(guard.isCurrent(request))commits.push(key);
  }
  return commits;
}

assert.deepEqual(
  simulateGuard(['A','B','C'],['B','A','C']),
  ['C'],
  'late A/B image loads must not overwrite the current C card',
);

const pending=[];
const shot={
  src:'old.jpg',
  alt:'',
  style:{visibility:''},
  removeAttribute(name){if(name==='src')delete this.src;},
};
const bg={style:{backgroundImage:'url("old.jpg")'}};
const elements={
  shot,
  galleryBg:bg,
  galleryCount:{textContent:''},
  dots:{innerHTML:''},
  title:{textContent:''},
  price:{textContent:''},
};
class FakeImage{
  constructor(){this.complete=false;this.naturalWidth=0;pending.push(this);}
  set src(value){this._src=value;}
  get src(){return this._src;}
  resolve(){this.complete=true;this.naturalWidth=100;this.onload?.();}
}
const games={
  A:{id:'A',title:'Game A',price:'100 ₽',screenshots:['A.jpg']},
  B:{id:'B',title:'Game B',price:'200 ₽',screenshots:['B.jpg']},
  C:{id:'C',title:'Game C',price:'300 ₽',screenshots:['C.jpg']},
};
const context=vm.createContext({elements,Image:FakeImage,games,activeGame:games.A,document:{}});
vm.runInContext(`
  let currentShot=0;
  function $(id){return elements[id]}
  function shotUrls(g){return g.screenshots||[]}
  function currentGame(){return activeGame}
  function setShot(){}
  function renderGame(g){
    activeGame=g;
    $('title').textContent=g.title;
    $('price').textContent=g.price;
    setShot(g,0);
  }
`,context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'image-swipe-sync.js'),'utf8'),context);

vm.runInContext('renderGame(games.A)',context);
vm.runInContext('renderGame(games.B)',context);
vm.runInContext('renderGame(games.C)',context);
assert.equal(elements.title.textContent,'Game C','text must already belong to current game C');
assert.equal(elements.price.textContent,'300 ₽','price must already belong to current game C');
assert.equal(shot.src,undefined,'old bitmap source must be cleared while C is loading');
assert.equal(shot.style.visibility,'hidden','old image must not remain visible during a card switch');
assert.equal(bg.style.backgroundImage,'none','old blurred background must be cleared too');

pending[1].resolve();
assert.equal(shot.src,undefined,'late B must be rejected');
assert.equal(elements.title.textContent,'Game C');
assert.equal(elements.price.textContent,'300 ₽');
pending[0].resolve();
assert.equal(shot.src,undefined,'late A must be rejected');
assert.equal(elements.title.textContent,'Game C');
assert.equal(elements.price.textContent,'300 ₽');
pending[2].resolve();
assert.equal(shot.src,'C.jpg','only C may commit after A -> B -> C');
assert.equal(elements.title.textContent,'Game C','C image must be paired with C text');
assert.equal(elements.price.textContent,'300 ₽','C image must be paired with C price');
assert.equal(shot.style.visibility,'','current image becomes visible after commit');
assert.equal(bg.style.backgroundImage,'url("C.jpg")');

vm.runInContext('renderGame(games.C)',context);
vm.runInContext('renderGame(games.B)',context);
assert.equal(elements.title.textContent,'Game B');
assert.equal(elements.price.textContent,'200 ₽');
pending[3].resolve();
assert.equal(shot.src,undefined,'quick reverse swipe must reject the previous C load');
assert.equal(elements.title.textContent,'Game B');
assert.equal(elements.price.textContent,'200 ₽');
pending[4].resolve();
assert.equal(shot.src,'B.jpg','quick reverse swipe must commit the latest B image');
assert.equal(elements.title.textContent,'Game B','B image must be paired with B text');
assert.equal(elements.price.textContent,'200 ₽','B image must be paired with B price');

const guard=createCommitGuard();
const stale=guard.begin('A');
guard.invalidate();
assert.equal(guard.isCurrent(stale),false,'invalidated requests must stay stale');

console.log('image swipe regression: PASS');
