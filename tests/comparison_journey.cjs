/* Execute the shipped UI against asynchronous synthetic public APIs. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag='div'){this.tagName=tag;this.children=[];this.dataset={};this.hidden=false;this.events={};this._text='';this._value='';this.classList={toggle(){},add(){},remove(){}};}
 set textContent(v){this._text=String(v);this.children=[];}get textContent(){return this._text+this.children.map(c=>c.textContent||'').join(' ');}
 get value(){return this._value||((this.tagName==='select'&&this.children[0])?this.children[0].value:'');}set value(v){this._value=String(v);}
 append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.children=nodes;this._text='';if(this.tagName==='select')this._value='';}
 get options(){return this.children;}get selectedOptions(){return this.children.filter(c=>c.value===this.value);}get firstChild(){return this.children[0];}
 addEventListener(k,fn){(this.events[k]??=[]).push(fn);}fire(k){for(const fn of this.events[k]||[])fn({preventDefault(){}});}
 setAttribute(k,v){this[k]=v;}removeAttribute(k){delete this[k];}focus(){}scrollIntoView(){}before(){}after(){}
 querySelector(){return new Element();}querySelectorAll(){return this.children;}
}
const nodes=new Map(),node=id=>{if(!nodes.has(id)){const n=new Element(id.includes('pair-')&&!id.includes('results')&&!id.includes('build')&&!id.includes('status')||['comparison-collection','result-collection','home-sort','home-direction','leaderboard-metric','submission-upload'].includes(id)?'select':'div');nodes.set(id,n);}return nodes.get(id);};
function options(id,values){for(const v of values){const n=new Element('option');n.value=v;n.textContent=v;node(id).append(n);}}
options('comparison-collection',['paper','registered']);options('result-collection',['paper']);options('home-sort',['t3','t2','t5','name']);options('home-direction',['ascending','descending']);
const links=['models','compare','submit'].map(view=>{const a=new Element('a');a.dataset.view=view;return a;});
const events={},location={hash:'',pathname:'/',origin:'http://localhost'},history={pushState(_a,_b,h){location.hash=h;},replaceState(_a,_b,h){location.hash=h;}};
const publication=id=>({submission_id:id,artifact_sha256:id,model:{id:'SYNTHETIC-'+id,dtype:'float32'},display:{},revision:1,verification:{}});
const pubs=['a','b','c'].map(publication),board={publications:pubs,boards:[],excluded:[],publication_count:3};
let pending=[],createdHome;
const workspace={uploads:()=>[],ready:()=>false,api:async path=>{
 if(path==='/api/registration')return {json:async()=>({enabled:true})};
 if(path==='/api/identity')return {json:async()=>({signed_in:false})};
 if(path==='/api/public/leaderboard')return {json:async()=>board};
 if(path==='/assets/paper_models.json')return {json:async()=>JSON.parse(fs.readFileSync('src/koevd_eval/assets/paper_models.json','utf8'))};
 if(path.includes('/profile')){const id=path.split('/')[4];return {json:async()=>({...pubs.find(p=>p.submission_id===id),scope:'summary',rank_admission:{metrics:[]},generation:{},protocol_sha256:'SYNTHETIC-protocol'})};}
 if(path.startsWith('/api/public/compare?'))return {json:()=>new Promise(resolve=>pending.push({path,resolve}))};
 throw Error('Unexpected '+path);
}};
const window={KoEVDWorkspace:workspace,KoEVDMetrics:require('../src/koevd_eval/assets/metric_labels.js'),KoEVDPublicReads:{explanation:e=>e.message},KoEVDHome:require('../src/koevd_eval/assets/home.js'),addEventListener(k,fn){(events[k]??=[]).push(fn);},dispatchEvent(e){for(const fn of events[e.type]||[])fn(e);}};window.self=window.top=window;
const context={window,document:{getElementById:node,createElement:tag=>new Element(tag),querySelector:node,querySelectorAll:selector=>selector==='#page-navigation a[data-view]'?links:[]},location,history,CustomEvent:class{constructor(type,init){this.type=type;this.detail=init?.detail;}},URLSearchParams,console};
for(const file of ['navigation','leaderboard'])vm.runInNewContext(fs.readFileSync('src/koevd_eval/assets/'+file+'.js','utf8'),context);
const create=window.KoEVDHome.create;window.KoEVDHome.create=args=>(createdHome=create(args));
vm.runInNewContext(fs.readFileSync('src/koevd_eval/assets/registration.js','utf8'),context);
const tick=()=>new Promise(resolve=>setImmediate(resolve));
function resolvePair(request){const p=new URLSearchParams(request.path.split('?')[1]);request.resolve({left:pubs.find(x=>x.submission_id===p.get('left')),right:pubs.find(x=>x.submission_id===p.get('right')),comparison:{note:'SYNTHETIC pair',tasks:[]}});}
(async()=>{
 await tick();await tick();
 await createdHome.paperCompare('Claude Haiku 4.5','Apertus 8B');
 assert.match(node('paper-pair-results').textContent,/Same most frequent strategy/);
 assert.doesNotMatch(node('paper-pair-results').textContent,/Strategy labels differ/);
 node('paper-pair-right').value='GPT-5.4';node('paper-pair-right').fire('change');
 assert.match(node('paper-pair-results').textContent,/Selection changed/);assert.doesNotMatch(node('paper-pair-results').textContent,/versus/);
 // A descriptive tab must not silently keep the preceding quality-score order.
 node('task-tabs').children.find(b=>b.dataset.task==='2').fire('click');
 node('task-tabs').children.find(b=>b.dataset.task==='1').fire('click');assert.equal(node('home-sort').value,'name');
 // Follow the public profile URL, then use the actual global Compare link.
 location.hash='#model=b';window.dispatchEvent({type:'hashchange'});await tick();await tick();
 assert.match(node('public-metrics').textContent,/SYNTHETIC-b/);links[1].fire('click');await tick();
 assert.equal(node('comparison-collection').value,'registered');assert.equal(node('public-pair-left').value,'b');assert.equal(pending.length,1);
 // Change the selection before the old network request completes.
 node('public-pair-right').value='c';node('public-pair-right').fire('change');resolvePair(pending.shift());await tick();await tick();
 assert.equal(node('public-pair-results').textContent,'');assert.match(node('public-pair-status').textContent,/Selection changed/);
 node('public-pair-build').fire('click');await tick();resolvePair(pending.shift());await tick();await tick();
 assert.match(node('public-pair-results').textContent,/SYNTHETIC-b versus SYNTHETIC-c/);assert.match(node('public-pair-results').textContent,/Download public numerical report/);
 node('public-pair-right').value='a';node('public-pair-right').fire('change');assert.equal(node('public-pair-results').textContent,'');
 node('public-pair-build').fire('click');await tick();links[0].fire('click');resolvePair(pending.shift());await tick();await tick();
 assert.equal(node('public-pair-results').textContent,'');assert.equal(window.KoEVDNavigation.current(),'models');
 // Paper detail also retains its model rather than the previous registered pair.
 await createdHome.paperDetail('GPT-5.4');links[1].fire('click');await tick();await tick();assert.equal(node('comparison-collection').value,'paper');assert.equal(node('paper-pair-left').value,'GPT-5.4');
 console.log('Shipped UI: selection invalidation, late-response/navigation guard, detail context, strategy labels and descriptive order passed');
})().catch(e=>{console.error(e);process.exitCode=1});
