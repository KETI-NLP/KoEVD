/* Only code-owned Python executes; uploaded UTF-8 JSON stays original bytes. */
'use strict';
importScripts('runtime/pyodide.js');
async function checked(item){
  if(!/^(engine\.zip|data\/[a-z0-9-]+\.json)$/.test(item.path))throw Error('Invalid deployment asset path');
  const r=await fetch(item.path);if(!r.ok)throw Error('Deployment asset unavailable');
  const b=await r.arrayBuffer();if(b.byteLength>128*1024*1024)throw Error('Deployment asset too large');
  const h=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('');
  if(h!==item.sha256)throw Error('Deployment asset checksum mismatch');return new Uint8Array(b);
}
self.onmessage=async e=>{
  let py;
  try{
    const c=await(await fetch('config.json')).json();
    const {buffers,reference,resamples,seed}=e.data;
    if(c.format!=='koevd-static-candidate-v1'||!Array.isArray(buffers)||buffers.length<1||buffers.length+(reference?1:0)>4||buffers.some(b=>!(b instanceof ArrayBuffer)||b.byteLength>128*1024*1024)||buffers.reduce((n,b)=>n+b.byteLength,0)>256*1024*1024)throw Error('Invalid result selection');
    py=await loadPyodide({indexURL:'runtime/'});
    const archive=await checked(c.engine);py.unpackArchive(archive,'zip',{extractDir:'/engine'});
    py.FS.mkdir('/inputs');const indexes=[];
    for(let i=0;i<c.indexes.length;i++){const p='/inputs/index-'+i+'.json';py.FS.writeFile(p,await checked(c.indexes[i]));indexes.push(p);}
    const results=buffers.map((b,i)=>{const p='/inputs/result-'+i+'.json';py.FS.writeFile(p,new Uint8Array(b));return p;});
    if(reference){const b=c.baselines.find(v=>v.id===reference);if(!b)throw Error('Unknown configured reference');const p='/inputs/reference.json';py.FS.writeFile(p,await checked(b));results.push(p);}
    self.postMessage({progress:'고정 입력으로 검증·분석 중… 파일을 서버에 전송하지 않습니다.'});
    py.globals.set('bridge_job',JSON.stringify({results,indexes,resamples,seed}));
    const result=await py.runPythonAsync(`
import sys, json
sys.path.insert(0, '/engine')
from koevd_eval.browser_bridge import analyze_files
job = json.loads(bridge_job)
receipt = analyze_files(job['results'], job['indexes'], '/output', resamples=job['resamples'], seed=job['seed'])
json.dumps(receipt)
`);
    const receipt=JSON.parse(result),outputs=receipt.files.map(name=>({name,bytes:py.FS.readFile('/output/'+name).slice().buffer}));
    self.postMessage({receipt,outputs},outputs.map(o=>o.bytes));
  }catch(x){self.postMessage({error:String(x.message||x)});}
  finally{self.close();}
};
