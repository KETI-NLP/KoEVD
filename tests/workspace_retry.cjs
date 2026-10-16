// Execute the shipped workspace against an explicitly synthetic DOM/HTTP boundary.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const labels=require('../src/koevd_eval/assets/metric_labels.js');
const elements=new Map();
function element(){return {disabled:false,hidden:false,dataset:{},files:[],children:[],classList:{toggle(){},remove(){}},addEventListener(){},querySelectorAll(){return []},append(...v){this.children.push(...v)},replaceChildren(...v){this.children=v},removeAttribute(){},setAttribute(){},remove(){}};}
const node=id=>{if(!elements.has(id))elements.set(id,element());return elements.get(id)};
let sessions=0,fail=true,uploads=0;
const catalog={synthetic_demo_enabled:true,indexes:[{label:'SYNTHETIC',mode:'synthetic_demo',expected_records:12}],baselines:[],limits:{upload_bytes:100000,max_uploads:4,ttl_seconds:600}};
const window={dispatchEvent(){},addEventListener(){},KoEVDPublicReads:{request:async fetch=>fetch()}};
vm.runInNewContext(fs.readFileSync('src/koevd_eval/assets/space.js','utf8'),{
 window,document:{getElementById:node,createElement:element},Event:class{},URL,Blob,console,
 fetch:async(url)=>{
   if(url==='/api/catalog')return {ok:true,json:async()=>catalog};
   if(url==='/api/session'){sessions++;await new Promise(r=>setTimeout(r,5));return fail?{ok:false,status:503,json:async()=>({error:{message:'SYNTHETIC unavailable'}})}:{ok:true,json:async()=>({session_token:'SYNTHETIC-token',csrf_token:'SYNTHETIC-csrf'})};}
   if(url==='/api/uploads'){uploads++;return {ok:true,json:async()=>({id:'SYNTHETIC-upload',model:'SYNTHETIC-model',records:12})};}
   throw Error('Unexpected request '+url);
 }});
(async()=>{
 const ws=window.KoEVDWorkspace;
 assert.equal(await ws.ensureReady(),false);assert.equal(sessions,1);assert.equal(node('delete-session').disabled,true);
 fail=false;assert.deepEqual(await Promise.all([ws.ensureReady(),ws.ensureReady()]),[true,true]);assert.equal(sessions,2);
 assert.equal(node('input-catalog').children.length,1);
 await ws.importResult('{}');assert.equal(uploads,1);assert.equal(ws.uploads().length,1);
 assert.equal(await ws.ensureReady(),true);assert.equal(sessions,2);assert.equal(ws.uploads().length,1);
 const metric='task2/variant/choose_best/accuracy_on_valid',board={publications:[{submission_id:'a',model:{id:'model-a'}},{submission_id:'b',display:{display_name:'My model'},model:{id:'model-b',revision:'abc'}},{submission_id:'duplicate',duplicate_of:'b',model:{id:'model-b'}}],boards:[],excluded:[{entry_id:'a',metric_id:metric,metric:{cohort_sha256:'one'}},{entry_id:'b',metric_id:metric,metric:{cohort_sha256:'two'}}]};
 assert.equal(labels.focusKey(board,'b',metric+'|one'),metric+'|two');assert.equal(labels.focusKey(board,'duplicate',metric+'|one'),metric+'|two');
 assert.equal(labels.matching(board,'my model')[0].submission_id,'b');assert.equal(labels.matching(board,'abc').length,1);assert.equal(labels.matching(board,'missing').length,0);
 assert.match(labels.rate(1,'event_on_valid'),/judgment errors/);assert.match(labels.rate(3,'event_on_valid'),/classifier-labeled unsafe/);assert.equal(labels.focusKey(board,'missing'),null);assert.match(labels.name(metric),/accuracy on valid answers/);assert.match(labels.direction('higher'),/Higher/);assert.match(labels.direction('lower'),/Lower/);assert.match(labels.direction(null),/Descriptive/);
 console.log('SYNTHETIC workspace recovery, single-flight retry, upload retention, cross-group discovery and metric labels passed');
})().catch(e=>{console.error(e);process.exitCode=1});
