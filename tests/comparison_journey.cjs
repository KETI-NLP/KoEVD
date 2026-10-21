/* Execute the shipped UI against asynchronous synthetic public APIs. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const allElements=[];
class Element {
 constructor(tag='div'){allElements.push(this);this.tagName=tag;this.children=[];this.dataset={};this.hidden=false;this.events={};this._text='';this._value='';this.classList={toggle(){},add(){},remove(){}};}
 set textContent(v){this._text=String(v);this.children=[];}get textContent(){return this._text+this.children.map(c=>c.textContent||'').join(' ');}
 get value(){return this._value||((this.tagName==='select'&&this.children[0])?this.children[0].value:'');}set value(v){this._value=String(v);}
 append(...nodes){this.children.push(...nodes);}replaceChildren(...nodes){this.children=nodes;this._text='';if(this.tagName==='select')this._value='';}
 get options(){return this.children;}get selectedOptions(){return this.children.filter(c=>c.value===this.value);}get firstChild(){return this.children[0];}
 addEventListener(k,fn){(this.events[k]??=[]).push(fn);}fire(k){for(const fn of this.events[k]||[])fn({preventDefault(){}});}
 setAttribute(k,v){this[k]=v;}removeAttribute(k){delete this[k];}focus(){}scrollIntoView(){}before(){}after(){}
 remove(){for(const n of allElements)n.children=n.children.filter(c=>c!==this);}
 querySelector(){return new Element();}querySelectorAll(){return this.children;}
}
const nodes=new Map(),node=id=>{if(!nodes.has(id)){const dynamic=allElements.find(n=>n.id===id);if(dynamic){nodes.set(id,dynamic);return dynamic;}const n=new Element(id.includes('pair-')&&!id.includes('results')&&!id.includes('build')&&!id.includes('status')||['comparison-collection','result-collection','home-sort','home-direction','leaderboard-metric','submission-upload'].includes(id)?'select':'div');nodes.set(id,n);}return nodes.get(id);};
function options(id,values){for(const v of values){const n=new Element('option');n.value=v;n.textContent=v;node(id).append(n);}}
options('comparison-collection',['paper','registered']);options('result-collection',['paper']);options('home-sort',['t3','t2','t5','name']);options('home-direction',['ascending','descending']);
const links=['models','compare','submit'].map(view=>{const a=new Element('a');a.dataset.view=view;return a;});
const events={},location={hash:'',pathname:'/',origin:'http://localhost'},history={pushState(_a,_b,h){location.hash=h;},replaceState(_a,_b,h){location.hash=h;}};
const publication=id=>({submission_id:id,artifact_sha256:id,model:{id:'SYNTHETIC-'+id,dtype:'float32'},display:{},revision:1,verification:{}});
const pubs=['a','b','c'].map(publication);pubs.push({...publication('b-alias'),artifact_sha256:'b',duplicate_of:'b',display:{display_name:'SYNTHETIC alias B'}});
const board={publications:pubs,boards:[],excluded:pubs.filter(p=>!p.duplicate_of).map(p=>({entry_id:p.submission_id,model:p.model,metric_id:'task2/variant/choose_best/accuracy_on_valid',metric:{cohort_sha256:p.submission_id==='c'?'other':'shared',direction:'higher',rate:{value:.8,numerator:4,denominator:5,sources:5},coverage:{numerator:5,denominator:5},reasons:[]}})),publication_count:4,distinct_artifact_count:3};
let pending=[],createdHome;let behaviorGate=false,behaviorPending=[];
const workspace={uploads:()=>[],ready:()=>false,api:async path=>{
 if(path==='/api/registration')return {json:async()=>({enabled:true})};
 if(path==='/api/identity')return {json:async()=>({signed_in:false})};
 if(path==='/api/public/leaderboard')return {json:async()=>board};
 if(path.split('?')[0]==='/assets/paper_models.json')return {json:async()=>JSON.parse(fs.readFileSync('src/koevd_eval/assets/paper_models.json','utf8'))};
 if(/^\/assets\/paper_behavior_/.test(path))return {json:()=>behaviorGate?new Promise((resolve,reject)=>behaviorPending.push({path,resolve,reject})):JSON.parse(fs.readFileSync('src/koevd_eval/assets/'+path.split('/').pop().split('?')[0],'utf8'))};
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
 // A loading catalog must not be reported as a completed zero-match search.
 node('home-search').value='SYNTHETIC-c';node('home-search').fire('input');
 assert.match(node('model-search-results').textContent,/Search in progress/);
 assert.doesNotMatch(node('model-search-results').textContent,/0 matching|could not be checked/);
 await tick();await tick();
 // Discover a registered model from the default historical table without mixing scores.
 node('home-search').value='SYNTHETIC-c';node('home-search').fire('input');
 assert.match(node('model-search-results').textContent,/SYNTHETIC-c/);
 const walk=n=>[n,...n.children.flatMap(walk)];
 walk(node('model-search-results')).find(n=>n.tagName==='button'&&n.textContent==='Show on leaderboard').fire('click');
 assert.equal(node('result-collection').value,'registered:other');assert.equal(window.KoEVDNavigation.current(),'models');
 node('home-search').value='SYNTHETIC alias B';node('home-search').fire('input');assert.match(node('model-search-results').textContent,/2 registrations of the same original/);
 walk(node('model-search-results')).find(n=>n.tagName==='button'&&n.textContent==='Show on leaderboard').fire('click');
 assert.equal(node('result-collection').value,'registered:shared');assert.match(node('home-status').textContent,/2\/2 distinct result files/);
 assert(!node('public-pair-left').options.some(o=>o.value==='b-alias'));
 node('published-model-choice').value='c';allElements.find(n=>n.tagName==='button'&&n.textContent==='Show model on leaderboard').fire('click');await tick();await tick();
 assert.equal(node('result-collection').value,'registered:other');assert.equal(window.KoEVDNavigation.current(),'models');assert.match(location.hash,/focus=c/);
 // Clear the model focus when conditions change; refresh and URL restoration retain the new collection.
 node('result-collection').value='paper';node('result-collection').fire('change');
 assert.equal(location.hash,'#models?collection=paper');createdHome.render(board);
 assert.equal(node('result-collection').value,'paper');assert.match(node('home-status').textContent,/12\/12 models/);
 node('result-collection').value='registered:other';node('result-collection').fire('change');
 createdHome.render(board);assert.equal(node('result-collection').value,'registered:other');
 const collectionURL=location.hash;node('result-collection').value='paper';createdHome.render(board);
 assert.equal(location.hash,collectionURL);assert.equal(node('result-collection').value,'registered:other');
 assert.match(node('score-definitions').textContent,/2,000 \+ 784 - 125 = 2,659/);
 assert.match(node('score-definitions').textContent,/Core only/);assert.match(node('score-definitions').textContent,/Both sets/);
 createdHome.clear('SYNTHETIC catalog failure');node('home-search').value='SYNTHETIC-c';node('home-search').fire('input');
 assert.match(node('model-search-results').textContent,/could not be checked: SYNTHETIC catalog failure/);
 createdHome.render(board);node('home-search').value='';node('home-search').fire('input');
 assert.equal(window.KoEVDMetrics.canonicalId(pubs,'b-alias'),'b');assert.equal(window.KoEVDMetrics.differentPublication(pubs,'b-alias').submission_id,'a');
 const names=[{name:'A',values:{}},{name:'Z',values:{}}];assert.equal(window.KoEVDHome.sortedRows(names,'name','descending')[0].name,'Z');
 await createdHome.paperDetail('Apertus 8B');assert.match(node('paper-model-detail').textContent,/50\.37%/);assert.match(node('paper-model-detail').textContent,/Low \(source code 1\)/);assert.doesNotMatch(node('paper-model-detail').textContent,/50\.368949/);
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
 node('public-pair-right').value='c';node('public-pair-right').fire('change');
 assert.equal(node('public-pair-build').disabled,true);assert.match(node('public-pair-status').textContent,/previous comparison request is finishing/);
 resolvePair(pending.shift());await tick();await tick();
 assert.equal(node('public-pair-results').textContent,'');assert.match(node('public-pair-status').textContent,/Selection changed. Select Compare/);assert.equal(node('public-pair-build').disabled,false);
 node('public-pair-build').fire('click');await tick();resolvePair(pending.shift());await tick();await tick();
 assert.match(node('public-pair-results').textContent,/SYNTHETIC-b versus SYNTHETIC-c/);assert.match(node('public-pair-results').textContent,/Download public numerical report/);
 node('public-pair-right').value='a';node('public-pair-right').fire('change');assert.equal(node('public-pair-results').textContent,'');
 node('public-pair-build').fire('click');await tick();links[0].fire('click');resolvePair(pending.shift());await tick();await tick();
 assert.equal(node('public-pair-results').textContent,'');assert.equal(window.KoEVDNavigation.current(),'models');
 // Paper detail also retains its model rather than the previous registered pair.
 await createdHome.paperDetail('GPT-5.4');links[1].fire('click');await tick();await tick();assert.equal(node('comparison-collection').value,'paper');assert.equal(node('paper-pair-left').value,'GPT-5.4');
 location.hash='#left=b&right=b-alias';window.dispatchEvent({type:'hashchange'});await tick();await tick();assert.match(node('public-pair-status').textContent,/same original/);assert.equal(pending.length,0);
 location.hash='#left=missing&right=a';window.dispatchEvent({type:'hashchange'});await tick();await tick();assert.match(node('public-pair-status').textContent,/currently published/);assert.equal(pending.length,0);
 // Late lazy assets must not overwrite a changed model pair or evaluation collection.
 behaviorGate=true;const lazy=createdHome.paperCompare('OLMo 3 7B','Gemma 4 E4B');await tick();assert.equal(behaviorPending.length,2);
 node('paper-pair-right').value='GPT-5.4';node('paper-pair-right').fire('change');const retained=node('paper-pair-results').textContent;
 for(const request of behaviorPending.splice(0))request.resolve(JSON.parse(fs.readFileSync('src/koevd_eval/assets/'+request.path.split('/').pop().split('?')[0],'utf8')));
 await lazy;assert.equal(node('paper-pair-results').textContent,retained,'A completed old asset request must not restore stale comparison tables');
 const failed=createdHome.paperCompare('Claude 4.6 Sonnet','GPT-5.4 Nano');await tick();assert.equal(behaviorPending.length,2);
 node('comparison-collection').value='registered';node('comparison-collection').fire('change');const switched=node('paper-pair-results').textContent;
 const delayed=behaviorPending.splice(0);delayed[1].resolve(JSON.parse(fs.readFileSync('src/koevd_eval/assets/'+delayed[1].path.split('/').pop().split('?')[0],'utf8')));delayed[0].reject(Error('SYNTHETIC delayed failure'));
 await failed;assert.equal(node('paper-pair-results').textContent,switched,'A failed old asset request must not append a retry control to the new selection');
 const oldDetail=createdHome.paperDetail('Ministral 3 8B');await tick();const newDetail=createdHome.paperDetail('Qwen3.5 9B');await tick();assert.equal(behaviorPending.length,2);const detailLoads=behaviorPending.splice(0);
 detailLoads[1].resolve(JSON.parse(fs.readFileSync('src/koevd_eval/assets/'+detailLoads[1].path.split('/').pop().split('?')[0],'utf8')));await newDetail;const currentDetail=node('paper-model-detail').textContent;detailLoads[0].reject(Error('SYNTHETIC old detail failure'));await oldDetail;assert.equal(node('paper-model-detail').textContent,currentDetail,'A stale detail failure must not append old retry controls');
 const oldValid=createdHome.paperCompare('Claude 4.6 Sonnet','Gemini 3.1 Pro');await tick();assert.equal(behaviorPending.length,2);await createdHome.paperCompare('Claude 4.6 Sonnet','Claude 4.6 Sonnet');const invalidMessage=node('paper-pair-results').textContent;for(const request of behaviorPending.splice(0))request.resolve(JSON.parse(fs.readFileSync('src/koevd_eval/assets/'+request.path.split('/').pop().split('?')[0],'utf8')));await oldValid;assert.equal(node('paper-pair-results').textContent,invalidMessage,'An invalid new pair must invalidate a pending old pair');
 console.log('Shipped UI: selection invalidation, late-response/navigation guard, detail context, strategy labels and descriptive order passed');
})().catch(e=>{console.error(e);process.exitCode=1});
