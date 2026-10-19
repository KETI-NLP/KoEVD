/* Real shipped handlers; expiring sessions and failures are synthetic HTTP. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const nodes=new Map(),requests=[];let expired=false,sessions=0,checkFailure=false,next=0,delayed;
function element(){return {files:[],children:[],events:{},dataset:{},classList:{toggle(){},remove(){}},addEventListener(k,f){this.events[k]=f},querySelectorAll(){return []},append(...v){this.children.push(...v)},replaceChildren(...v){this.children=v},removeAttribute(){},setAttribute(){},remove(){}};}
const node=id=>{if(!nodes.has(id))nodes.set(id,element());return nodes.get(id)};
const window={dispatchEvent(){},addEventListener(){},KoEVDPublicReads:{request:async f=>f()}};
const response=(value,status=200)=>({ok:status<400,status,json:async()=>value});
vm.runInNewContext(fs.readFileSync('src/koevd_eval/assets/space.js','utf8'),{window,document:{getElementById:node,createElement:element},Event:class{},URL,Blob,console,AbortController,setTimeout,clearTimeout,fetch:async(path,options)=>{
 requests.push({path,method:options.method});
 if(path==='/api/SYNTHETIC-delayed')return new Promise(resolve=>{delayed=resolve;});
 if(path==='/api/catalog')return response({indexes:[],baselines:[],limits:{upload_bytes:100000,max_uploads:4,ttl_seconds:600}});
 if(path==='/api/session'&&options.method==='POST'){sessions++;expired=false;return response({session_token:'SYNTHETIC-'+sessions,csrf_token:'SYNTHETIC'});}
 if(checkFailure&&path==='/api/session')return response({error:{code:'synthetic_unavailable',message:'SYNTHETIC unavailable'}},503);
 if(expired)return response({error:{code:'session_expired',message:'Session is missing or expired. Create a new one.'}},401);
 if(path==='/api/session')return response({uploads:[]});
 if(path==='/api/uploads')return response({id:'SYNTHETIC-upload-'+(++next),model:'SYNTHETIC',records:12});
 throw Error('Unexpected '+path);
}});
(async()=>{
 const ws=window.KoEVDWorkspace;await ws.ensureReady();await ws.importResult('{}');expired=true;
 await assert.rejects(ws.importResult('{}'),/Retry analysis connection/);
 assert.equal(ws.ready(),false);assert.equal(ws.uploads().length,0);
 const posts=requests.filter(r=>r.path==='/api/uploads').length;
 await Promise.all([node('analysis-retry').events.click(),node('analysis-retry').events.click()]);
 assert.equal(sessions,2);assert.equal(ws.ready(),true);assert.match(node('status').textContent,/New private session ready.*saved registrations are preserved/i);
 assert.equal(requests.filter(r=>r.path==='/api/uploads').length,posts,'no implicit result replay');
 await ws.importResult('{}');checkFailure=true;
 assert.equal(await node('analysis-retry').events.click(),false);assert.equal(ws.uploads().length,1);assert.equal(sessions,2);
 checkFailure=false;await node('analysis-retry').events.click();assert.equal(sessions,2);assert.equal(ws.uploads().length,1);
 // Expiry discovered by an explicit connection check, before another upload.
 expired=true;await node('analysis-retry').events.click();assert.equal(sessions,3);assert.equal(ws.uploads().length,0);
 // A late expiry from an older session must not invalidate a newly connected one.
 const old=ws.api('/api/SYNTHETIC-delayed').catch(e=>e);expired=true;await node('analysis-retry').events.click();
 delayed(response({error:{code:'session_expired',message:'SYNTHETIC old session expired'}},401));await old;assert.equal(ws.ready(),true);assert.equal(sessions,4);
 // Do not send the remaining selected files after the session expires.
 expired=true;node('result-files').files=[{name:'A.json',size:2},{name:'B.json',size:2}];
 const before=requests.length;await node('upload').events.click();
 assert.equal(requests.slice(before).filter(r=>r.path==='/api/uploads').length,1);
 assert.match(node('upload-outcomes').children.map(x=>x.textContent).join(' '),/B.json.*Not attempted/);
 assert.match(node('status').textContent,/Temporary session expired/);assert.equal(node('upload').disabled,true);
 console.log('Session expiry: explicit recovery, single-flight creation, no write replay, transient retention and partial-upload stop passed');
})().catch(e=>{console.error(e);process.exitCode=1});
