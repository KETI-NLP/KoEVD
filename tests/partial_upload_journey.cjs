/* Actual shipped upload handler; synthetic immutable File and HTTP boundaries. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
function fixture(){
 const nodes=new Map(),stored=new Map(),requests=[],fail=new Set(),loseAck=new Set();let next=0;
 function element(){return {files:[],children:[],events:{},dataset:{},classList:{toggle(){},remove(){}},addEventListener(k,f){this.events[k]=f},querySelectorAll(){return []},append(...v){this.children.push(...v)},replaceChildren(...v){this.children=v},removeAttribute(){},setAttribute(){},remove(){}};}
 const node=id=>{if(!nodes.has(id))nodes.set(id,element());return nodes.get(id)};
 const window={dispatchEvent(){},addEventListener(){},KoEVDPublicReads:{request:async f=>f()}};
 const response=(value,code=200)=>({ok:code<400,status:code,json:async()=>value});
 vm.runInNewContext(fs.readFileSync('src/koevd_eval/assets/space.js','utf8'),{window,document:{getElementById:node,createElement:element},Event:class{},URL,Blob,console,AbortController,setTimeout,clearTimeout,
  fetch:async(path,options)=>{
   requests.push({path,method:options.method,name:options.body?.name});
   if(path==='/api/catalog')return response({indexes:[],baselines:[],limits:{upload_bytes:100000,max_uploads:4,ttl_seconds:600}});
   if(path==='/api/session')return response(options.method==='POST'?{session_token:'SYNTHETIC',csrf_token:'SYNTHETIC'}:{uploads:[...stored.values()]});
   if(path.startsWith('/api/uploads/')&&options.method==='DELETE'){for(const [k,r] of stored)if(r.id===path.split('/').pop())stored.delete(k);return response({});}
   if(path==='/api/uploads'){
    const file=options.body;
    if(fail.has(file.key))return response({error:{code:'synthetic_invalid',message:'SYNTHETIC invalid file'}},422);
    if(stored.has(file.key))return response({error:{code:'duplicate_artifact',message:'This exact result is already uploaded.'}},409);
    const run={id:'SYNTHETIC-'+(++next),model:'SYNTHETIC-'+file.key,artifact_sha256:file.key,records:12};stored.set(file.key,run);
    if(loseAck.delete(file.key))throw Error('SYNTHETIC lost acknowledgement');
    return response(run);
   }
   throw Error('Unexpected '+path);
  }});
 return {node,ws:window.KoEVDWorkspace,requests,fail,loseAck,stored,upload:async files=>{node('result-files').files=files;await node('upload').events.click();}};
}
const file=(key,name=key+'.json')=>Object.freeze({key,name,size:12});
(async()=>{
 const f=fixture(),A=file('A'),B=file('B'),C=file('C'),D=file('D');await f.ws.ensureReady();
 f.fail.add('B');await f.upload([A,B,C]);assert.equal(f.ws.uploads().length,2);assert.equal(f.ws.uploads()[0].file_name,'A.json');
 assert.match(f.node('upload-outcomes').children.map(x=>x.textContent).join(' '),/B.json.*Not added/);
 f.fail.clear();await f.upload([A,B,C]);assert.equal(f.ws.uploads().length,3);
 assert.deepEqual(f.requests.filter(r=>r.path==='/api/uploads').map(r=>r.name),['A.json','B.json','C.json','B.json']);
 assert.match(f.node('status').textContent,/1 newly validated.*2 already available.*0 failed/);
 // A reselected native File has a different object identity: reconcile its server duplicate, then continue.
 await f.upload([file('A'),D]);assert.equal(f.ws.uploads().length,4);assert(f.requests.some(r=>r.path==='/api/session'&&r.method==='GET'));
 const count=f.requests.length;await f.upload([A,file('E')]);assert.equal(f.requests.length,count);assert.match(f.node('status').textContent,/1 already available.*1 failed/);
 // Removing a retained upload invalidates the acknowledgement shortcut.
 await f.node('uploads').children[0].children.at(-1).events.click();await f.upload([A]);assert.equal(f.ws.uploads().length,4);assert.equal(f.requests.at(-1).name,'A.json');
 // Same filename, different file contents: never skip by filename/size alone.
 const g=fixture();await g.ws.ensureReady();await g.upload([file('old','result.json')]);await g.upload([file('corrected','result.json')]);assert.equal(g.ws.uploads().length,2);
 // A lost response is not blindly retried; the next explicit attempt reads the duplicate's session.
 const h=fixture();await h.ws.ensureReady();h.loseAck.add('A');await h.upload([A]);assert.equal(h.ws.uploads().length,0);assert.equal(h.stored.size,1);
 assert.equal(h.requests.filter(r=>r.path==='/api/uploads').length,1);await h.upload([A]);assert.equal(h.ws.uploads().length,1);assert.match(h.node('status').textContent,/1 already available.*0 failed/);
 console.log('Partial uploads: continue after failure, acknowledged retry skips, duplicate reconciliation, quota, removal, changed file and lost-response recovery passed');
})().catch(e=>{console.error(e);process.exitCode=1});
