/* Session credentials live only in memory. Untrusted strings are textContent. */
(function(){'use strict';
const state={token:null,csrf:null,catalog:null,uploads:[],busy:false,expired:false,job:null,preview:null,downloadURL:null,downloadRequest:0};
const node=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
function status(text,error=false){node('status').textContent=text;node('status').classList.toggle('error',error);}
async function api(url,{method='GET',body=null,authenticated=true,identity=false,authCsrf=null,contentEncoding=null}={}){
  const sessionToken=authenticated?state.token:null;
  const headers={};if(sessionToken)headers.Authorization='Bearer '+sessionToken;
  if(method!=='GET'&&authenticated)headers['X-Koevd-CSRF']=state.csrf||'';
  if(body!==null)headers['Content-Type']='application/json';
  if(contentEncoding)headers['Content-Encoding']=contentEncoding;
  if(identity&&method!=='GET')headers['X-Koevd-Auth-CSRF']=authCsrf||'';
  // HF private Docker proxy access also needs its HttpOnly cookie on analysis
  // requests. Same-origin cookies never replace the separate session token/CSRF.
  const fetchOnce=async()=>{const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),method==='GET'?60000:120000);try{return await fetch(url,{method,headers,body,credentials:'same-origin',cache:'no-store',referrerPolicy:'no-referrer',signal:controller.signal});}catch(e){if(e.name==='AbortError')throw new Error('Connection timed out. For a save/share request, check your registration history before repeating.');throw e;}finally{clearTimeout(timer);}};
  let retried=false;
  const response=await window.KoEVDPublicReads.request(fetchOnce,{method,path:url,onRetry:({attempt,maxAttempts})=>{retried=true;const notice=node('public-service-status');if(notice){notice.textContent='Checking published results again (attempt '+attempt+' of '+maxAttempts+')…';notice.classList.remove('error');}}});
  if(!response.ok){let value;try{value=await response.json();}catch{value=null;}const error=new Error(value?.error?.message||'Request failed ('+response.status+').');error.code=value?.error?.code;error.status=response.status;
    if(authenticated&&state.token===sessionToken&&error.code==='session_expired'){state.expired=true;state.token=null;state.csrf=null;state.uploads=[];clearReport();renderUploads();error.message='Your temporary session expired or the server restarted. Use Retry analysis connection, then reselect your local files or Analyze saved result. Saved registrations are separate and remain preserved.';}
    throw error;}
  if(retried){const notice=node('public-service-status');if(notice){notice.textContent='Published results checked successfully.';notice.classList.remove('error');}}
  return response;
}
function updateButtons(){node('upload').disabled=state.busy||!state.token||!node('result-files').files.length;node('analyze').disabled=state.busy||!state.uploads.length;node('delete-session').disabled=state.busy||!state.token;node('analysis-retry').disabled=state.busy;for(const b of node('uploads').querySelectorAll('button'))b.disabled=state.busy;window.dispatchEvent(new Event('koevd-workspace-change'));}
function clearPreparedDownload(){state.downloadRequest++;if(state.downloadURL)URL.revokeObjectURL(state.downloadURL);state.downloadURL=null;node('prepared-download')?.remove();}
function clearReport(){clearPreparedDownload();node('report-section').hidden=true;node('report-preview').removeAttribute('src');if(state.preview)URL.revokeObjectURL(state.preview);state.preview=null;state.job=null;}
function scopeName(scope){return ({synthetic_demo:'Synthetic demo',operator_custom:'Operator-configured custom inputs',standard:'Registered input protocol'})[scope]||scope;}
function renderUploads(){const holder=node('uploads');holder.replaceChildren();if(!state.uploads.length)holder.append(el('p','No results uploaded yet.','empty'));
  for(const run of state.uploads){const row=el('div',undefined,'run-row'),check=document.createElement('input');check.type='checkbox';check.checked=true;check.id='upload-'+run.id;check.dataset.uploadId=run.id;const detail=el('div',undefined,'run-detail'),name=el('label',run.model+(run.file_name?' · '+run.file_name:''));name.htmlFor=check.id;detail.append(name,el('p',run.run_id+' · '+run.records+' records · '+scopeName(run.scope)),el('span','Private session','tag'),el('span','Structurally validated · identity user-reported','tag'));
    const remove=el('button','Remove','secondary');remove.type='button';remove.addEventListener('click',async()=>{try{await api('/api/uploads/'+encodeURIComponent(run.id),{method:'DELETE'});state.uploads=state.uploads.filter(x=>x.id!==run.id);clearReport();renderUploads();status('Result removed from this session.');}catch(e){status(e.message,true);}});row.append(check,detail,remove);holder.append(row);}
  updateButtons();}
function renderCatalog(){const c=state.catalog;node('demo-note').hidden=!c.synthetic_demo_enabled;node('retention').textContent='Maximum '+Math.round(c.limits.upload_bytes/1024/1024)+' MiB per file · '+c.limits.max_uploads+' uploaded results · session expires after '+Math.round(c.limits.ttl_seconds/60)+' minutes. '+(c.reference_disclosure?'Your session outputs retain raw text. Configured reference text is withheld; measured labels and metrics remain available.':'Downloads retain raw text.');
  node('input-catalog').replaceChildren();for(const input of c.indexes)node('input-catalog').append(el('li',input.label+' · '+scopeName(input.mode)+' · '+input.expected_records+' expected records'));
  const holder=node('baselines');holder.replaceChildren();if(!c.baselines.length)holder.append(el('p','No approved raw-response references are configured. Upload a second result to compare runs.','empty'));
  for(const base of c.baselines){const row=el('div',undefined,'run-row'),check=document.createElement('input');check.type='checkbox';check.id='baseline-'+base.id;check.dataset.baselineId=base.id;const detail=el('div',undefined,'run-detail'),name=el('label',base.label);name.htmlFor=check.id;detail.append(name,el('p',base.model+' · '+(base.scope==='synthetic_demo'?'Fictional demonstration reference':'Operator reference measurements (response text may be withheld)')));row.append(check,detail);holder.append(row);}}
let starting=null;
async function ensureReady({verify=false}={}){if(starting)return starting;if(state.token&&!verify)return true;
  starting=(async()=>{if(state.token){try{await api('/api/session');status('Current private session checked; validated uploads are retained.');return true;}catch(e){if(e.code!=='session_expired'){status('Could not check the private session. Try Retry analysis connection again; retained uploads have not been discarded. '+e.message,true);return false;}}}return start();})();try{return await starting;}finally{starting=null;}}
async function start(){try{state.catalog=await (await api('/api/catalog',{authenticated:false})).json();renderCatalog();const info=await (await api('/api/session',{method:'POST',authenticated:false})).json();state.token=info.session_token;state.csrf=info.csrf_token;status(state.expired?'New private session ready. Reselect local result files or use Analyze saved result. Expired temporary uploads are unavailable; saved registrations are preserved.':'Private session ready. Choose your result JSON to begin.');state.expired=false;updateButtons();return true;}catch(e){status('Analysis connection unavailable. Use Retry analysis connection. '+e.message,true);updateButtons();return false;}}
node('result-files').addEventListener('change',updateButtons);
// A File is immutable. Only skip an unchanged object after its acknowledged run
// is still present in this session; removing a result makes it uploadable again.
const validatedFiles=new WeakMap();
node('upload').addEventListener('click',async()=>{
  state.busy=true;updateButtons();const outcomes=node('upload-outcomes');outcomes.replaceChildren();
  let added=0,reused=0,failed=0;
  const outcome=(file,text)=>outcomes.append(el('li',file.name+' — '+text));
  try{
    const files=[...node('result-files').files];
    if(files.length>state.catalog.limits.max_uploads)throw new Error('Select at most '+state.catalog.limits.max_uploads+' files per attempt. Existing validated results stay available.');
    for(const [index,file] of files.entries()){
      const prior=validatedFiles.get(file);
      if(prior&&state.uploads.some(r=>r.id===prior)){reused++;outcome(file,'Already validated; retained without uploading again.');continue;}
      try{
        if(state.uploads.length>=state.catalog.limits.max_uploads)throw new Error('Session result limit reached. Remove a result or use the validated results already listed.');
        if(file.size>state.catalog.limits.upload_bytes)throw new Error('File exceeds the upload limit.');
        let body=file,contentEncoding=file.name.toLowerCase().endsWith('.json.gz')?'gzip':null;
        if(!contentEncoding&&file.size>=1024*1024&&typeof CompressionStream==='function'){
          status('Compressing '+file.name+' for transfer; the original JSON stays unchanged…');
          const compressed=await new Response(file.stream().pipeThrough(new CompressionStream('gzip'))).blob();
          if(compressed.size<file.size){body=compressed;contentEncoding='gzip';}
        }
        status('Validating '+file.name+' against server-selected trusted inputs'+(contentEncoding?' (compressed transfer)':'')+'…');
        const run=await (await api('/api/uploads',{method:'POST',body,contentEncoding})).json();
        run.file_name=file.name;state.uploads.push(run);validatedFiles.set(file,run.id);added++;clearReport();renderUploads();outcome(file,'Validated and available for analysis or registration.');
      }catch(e){
        if(e.code==='duplicate_artifact'){
          try{
            // This is a read, not a replay of a write. It also recovers an
            // acknowledged server upload whose response did not reach the page.
            const current=await (await api('/api/session')).json();
            if(!Array.isArray(current.uploads)||!current.uploads.length)throw new Error('The duplicate could not be confirmed in this session.');
            const names=new Map(state.uploads.map(r=>[r.id,r.file_name]));state.uploads=current.uploads.map(r=>({...r,file_name:names.get(r.id)}));clearReport();renderUploads();reused++;outcome(file,'This exact original is already in the session; current uploads checked.');continue;
          }catch(check){e=new Error('Could not check the reported duplicate: '+check.message);}
        }
        failed++;outcome(file,'Not added/confirmed: '+e.message);
        if(state.expired){for(const remaining of files.slice(index+1)){failed++;outcome(remaining,'Not attempted: reconnect the expired session before selecting files again.');}break;}
      }
    }
    if(!failed)node('result-files').value='';
    status(state.expired?'Temporary session expired. Use Retry analysis connection, then reselect your files or Analyze saved result. Saved registrations are preserved.':added+' newly validated · '+reused+' already available · '+failed+' failed/unconfirmed. '+(failed?'Successful results stay listed. Retry unchanged selected files explicitly to skip acknowledged successes; after correcting a file on disk, select that corrected file again.':'Continue with the validated results below.'),failed>0);
  }catch(e){status(e.message,true);}finally{state.busy=false;updateButtons();}
});
async function download(kind){
  // A visible Save link keeps the final download inside the user's click.
  // Do not silently auto-click after an asynchronous authenticated request.
  const job=state.job;if(!job)return;clearPreparedDownload();const request=state.downloadRequest;
  const name=({html:'report-v2.html',profile:'profile-v2.json',cases:'cases-v2.jsonl',csv:'metrics-v2.csv',markdown:'report-v2.md'})[kind];
  status('Preparing '+name+'…');const response=await api('/api/reports/'+encodeURIComponent(job)+'/'+kind),blob=await response.blob();
  if(request!==state.downloadRequest||job!==state.job)return;
  state.downloadURL=URL.createObjectURL(blob);const ready=el('p',undefined,'download-ready');ready.id='prepared-download';
  const link=el('a','Save '+name);link.href=state.downloadURL;link.download=name;
  link.addEventListener('click',()=>status('Save requested. Check your browser’s download list.'));
  ready.append(link,el('span',state.catalog.reference_disclosure?' · Personal output text retained; reference text withheld.':' · Contains original response text.'));node('downloads').append(ready);
  status('File ready. Use the Save link below the report buttons to download it.');
}
async function showReport(job){state.job=job.id;const base='/api/reports/'+encodeURIComponent(job.id)+'/';const profile=await (await api(base+'profile')).json();const response=await api(base+'html');state.preview=URL.createObjectURL(new Blob([await response.text()],{type:'text/html'}));node('report-preview').src=state.preview;node('report-summary').textContent=profile.runs.length+' analyzed run(s) · '+profile.comparisons.length+' paired comparison(s) · '+state.catalog.limits.bootstrap_resamples+' source-cluster resamples. Local and app reports use the same engine and recorded seed.';
  const holder=node('downloads');holder.replaceChildren();for(const [kind,name] of [['html','Offline HTML'],['profile','Analysis JSON'],['cases','All cases JSONL'],['csv','Metrics CSV'],['markdown','Summary Markdown']]){const button=el('button',name,'secondary');button.type='button';button.addEventListener('click',()=>download(kind).catch(e=>status(e.message,true)));holder.append(button);}node('report-section').hidden=false;node('job-status').textContent='Analysis complete. Coverage, undefined values and measurement limits are retained.';status('Report ready. Explore the charts below or download the offline HTML.');}
async function poll(job,token=state.token){if(!token||state.token!==token)return;try{const value=await (await api('/api/analyses/'+encodeURIComponent(job.id))).json();if(state.token!==token)return;node('job-status').textContent='Analysis '+value.status+'.';if(value.status==='complete'){await showReport(value);state.busy=false;updateButtons();}else if(value.status==='failed'){throw new Error(value.error||'Analysis failed.');}else setTimeout(()=>poll(job,token),1000);}catch(e){if(state.token!==token&&!state.expired)return;status(e.message,true);node('job-status').textContent='Analysis stopped.';state.busy=false;updateButtons();}}
node('analyze').addEventListener('click',async()=>{state.busy=true;updateButtons();clearReport();try{const upload_ids=[...node('uploads').querySelectorAll('input:checked')].map(n=>n.dataset.uploadId),baseline_ids=[...node('baselines').querySelectorAll('input:checked')].map(n=>n.dataset.baselineId);if(!upload_ids.length)throw new Error('Select at least one uploaded run.');const job=await (await api('/api/analyses',{method:'POST',body:JSON.stringify({upload_ids,baseline_ids})})).json();status('Analysis queued. The server will rescore and compare matching inputs.');poll(job);}catch(e){status(e.message,true);state.busy=false;updateButtons();}});
node('delete-session').addEventListener('click',async()=>{try{await api('/api/session',{method:'DELETE'});clearReport();state.token=null;state.csrf=null;state.uploads=[];renderUploads();status('Session data deleted. Use Retry analysis connection to start a new temporary session. Saved registrations are separate.');updateButtons();}catch(e){status(e.message,true);}});
window.KoEVDWorkspace={ensureReady,uploads:()=>state.uploads.map(r=>({...r})),
  api:(url,options={})=>api(url,{...options,identity:true}),
  importResult:async serialized=>{if(!await ensureReady())throw new Error('Analysis connection unavailable. Retry analysis connection first.');if(typeof serialized!=='string')throw new Error('Import the unchanged result JSON text.');if(state.busy)throw new Error('Wait for the active analysis operation.');state.busy=true;updateButtons();try{let run;try{run=await(await api('/api/uploads',{method:'POST',body:serialized})).json();}catch(e){if(e.code==='duplicate_artifact'){const existing=state.uploads.find(r=>r.artifact_sha256===JSON.parse(serialized).content_sha256);if(existing){status('This validated original is already in your private session. Select it for analysis.');return existing;}}throw e;}state.uploads.push(run);clearReport();renderUploads();status('Result added to your private analysis session. Select it with another run or reference to compare.');return run;}finally{state.busy=false;updateButtons();}},
  ready:()=>Boolean(state.token)&&!state.busy};
window.addEventListener('pagehide',()=>{clearPreparedDownload();if(state.preview)URL.revokeObjectURL(state.preview);});updateButtons();node('analysis-retry').addEventListener('click',()=>ensureReady({verify:true}));window.addEventListener('koevd-view-change',e=>{if(e.detail==='submit')ensureReady();});if(window.location?.pathname==='/submit'||['#submit','#registration-section','#upload-section'].includes(window.location?.hash))ensureReady();
}());
