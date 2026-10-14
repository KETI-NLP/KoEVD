/* Server-confirmed identity only. Untrusted names/reasons are textContent. */
(function(){'use strict';
const $=id=>document.getElementById(id), workspace=window.KoEVDWorkspace;
const state={identity:null,current:null,busy:false,next:null,publicNext:null,keys:new Map(),board:null};
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
function message(text,error=false){$('submission-status').textContent=text;$('submission-status').classList.toggle('error',error);}
function controls(){for(const n of $('registration-section').querySelectorAll('button'))n.disabled=state.busy;
  $('submission-create').disabled=state.busy||!$('submission-upload').value||!workspace.ready();
  $('submission-revise').disabled=state.busy||!state.current||!$('submission-upload').value||state.current.owner!==state.identity?.subject||state.current.workflow==='withdrawn';}
async function api(url,options={}){return (await workspace.api(url,{...options,authCsrf:state.identity?.csrf_token})).json();}
async function perform(task){if(state.busy)return;state.busy=true;controls();try{await task();}catch(e){message(e.message,true);}finally{state.busy=false;controls();}}
function payload(url,value){const fingerprint=url+JSON.stringify(value);let key=state.keys.get(fingerprint);if(!key){if(state.keys.size>=100)state.keys.delete(state.keys.keys().next().value);key=crypto.randomUUID();state.keys.set(fingerprint,key);}return JSON.stringify({...value,key});}
async function mutate(url,value){return api(url,{method:'POST',body:payload(url,value)});}
function uploads(){const select=$('submission-upload'),previous=select.value;select.replaceChildren();select.append(el('option','Select a validated private upload'));select.firstChild.value='';
  for(const run of workspace.uploads()){const option=el('option',run.model+' · '+run.records+' records · '+run.id.slice(0,8));option.value=run.id;select.append(option);}select.value=[...select.options].some(n=>n.value===previous)?previous:'';controls();}
async function signIn(){const info=await api('/api/identity',{authenticated:false});state.identity=info.signed_in?info:null;
  $('identity-status').textContent=info.signed_in?'Signed in as '+info.username+'. Submission permissions are checked by the server.':'Not signed in. Sign in in a separate tab, then check again.';
  $('identity-logout').hidden=!info.signed_in;$('submission-controls').hidden=!info.signed_in;
  if(!info.signed_in){state.current=null;$('submission-list').replaceChildren();$('submission-detail').hidden=true;}
  else{uploads();await list();}controls();}
async function list(after=''){const result=await api('/api/submissions?after='+encodeURIComponent(after));state.next=result.next_cursor;$('submissions-next').hidden=!state.next;const holder=$('submission-list');holder.replaceChildren();
  if(!result.items.length)holder.append(el('p','No visible submissions on this page.','empty'));
  for(const item of result.items){const button=el('button',item.id.slice(0,8)+' · revision '+item.head_revision+' · '+item.workflow+' · '+item.publication.status,'secondary');button.type='button';button.dataset.submissionId=item.id;button.addEventListener('click',()=>perform(async()=>show(await api('/api/submissions/'+encodeURIComponent(item.id)))));holder.append(button);}}
function show(item){state.current=item;$('submission-detail').hidden=false;$('submission-title').textContent=(item.display?.display_name||'Submission')+' · '+item.id.slice(0,8);$('submission-display-name').value=item.display?.display_name||'';$('submission-description').value=item.display?.description||'';
  $('submission-state').textContent='Current revision '+item.head_revision+' · '+item.workflow+' · publication '+item.publication.status+(item.publication.revision?' (revision '+item.publication.revision+', '+item.publication.scope+')':'')+'. Generation is user-reported; measurements remain limited.';
  const owner=item.owner===state.identity.subject, reviewer=state.identity.reviewer&&!owner;
  $('submission-metadata-save').hidden=!owner||item.workflow==='withdrawn';$('consent-controls').hidden=!owner;$('review-controls').hidden=!reviewer;
  const holder=$('submission-actions');holder.replaceChildren();const actions=[];
  if(owner&&state.summaryPublication&&['draft','rejected','registered'].includes(item.workflow)&&item.publication.revision!==item.head_revision)actions.push(['publish_summary','Publish numerical summary']);
  if(owner&&['draft','rejected','registered'].includes(item.workflow))actions.push(['request_review','Request publication review']);
  if(reviewer&&item.workflow==='pending')actions.push(['start_review','Start review']);
  if(reviewer&&item.workflow==='under_review')actions.push(['approve','Approve permission review'],['reject','Reject submission']);
  if(state.identity.admin&&!owner&&item.workflow==='approved'&&item.publication.revision!==item.head_revision)actions.push(['publish','Publish approved candidate']);
  if((owner||state.identity.admin)&&item.workflow!=='withdrawn')actions.push(['withdraw','Withdraw publication']);
  for(const [name,label] of actions){const button=el('button',label);button.type='button';button.dataset.action=name;button.addEventListener('click',()=>perform(async()=>{const url='/api/submissions/'+encodeURIComponent(item.id)+'/actions';const body={name,expected_version:item.version,reason:$('submission-reason').value};
    if(name==='request_review'||name==='publish_summary')body.consent={scope:$('publication-scope').value,accepted:$('publication-consent').checked,rights_statement:$('publication-rights').value};
    if(name==='approve')body.rights_evidence=$('review-evidence').value;
    const saved=await mutate(url,body);show(await api('/api/submissions/'+encodeURIComponent(saved.id)));await list();await published();message('Action recorded. Reloaded state includes any exact-request replay.');}));holder.append(button);}controls();}
async function download(url,name){const response=await workspace.api(url,{authCsrf:state.identity?.csrf_token});const blob=URL.createObjectURL(await response.blob());const a=el('a');a.href=blob;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(blob),10000);}
function clearBoard(text,error=false){state.board=null;$('leaderboard-values').replaceChildren();$('leaderboard-metric').replaceChildren();$('leaderboard-metric').disabled=true;$('leaderboard-status').textContent=text;$('leaderboard-status').classList.toggle('error',error);}
async function publicMetrics(id){const holder=$('public-metrics');holder.replaceChildren(el('p','Loading candidate metrics…'));
  try{metrics(await api('/api/public/submissions/'+encodeURIComponent(id),{authenticated:false}));}
  catch(e){holder.replaceChildren(el('p','Candidate metrics unavailable: '+e.message,'error'));}}
async function published(after=''){const holder=$('public-submissions');state.publicNext=null;$('public-next').hidden=true;holder.replaceChildren(el('p','Loading published candidates…'));$('public-metrics').replaceChildren();clearBoard('Loading published metric comparison…');
  let data;try{data=await api('/api/public/submissions?after='+encodeURIComponent(after),{authenticated:false});}
  catch(e){holder.replaceChildren(el('p','Published candidates unavailable: '+e.message,'error'));clearBoard('Comparison unavailable: '+e.message,true);return;}
  state.publicNext=data.next_cursor;$('public-next').hidden=!state.publicNext;holder.replaceChildren();
  if(!data.items.length)holder.append(el('p','No published candidates on this page.','empty'));
  for(const item of data.items){const row=el('div',undefined,'run-row');const button=el('button',(item.display?.display_name||item.submission_id.slice(0,8))+' · revision '+item.revision+' · '+item.scope,'secondary');button.type='button';button.dataset.publicId=item.submission_id;
    button.addEventListener('click',()=>perform(()=>publicMetrics(item.submission_id)));row.append(button);
    if(item.scope==='responses'){const add=el('button','Add responses to private comparison','secondary');add.type='button';add.addEventListener('click',()=>perform(async()=>{const response=await workspace.api('/api/public/submissions/'+encodeURIComponent(item.submission_id)+'/result',{authenticated:false});await workspace.importResult(await response.text());uploads();message('Published original added to private analysis. Select it with your result above to compare.');}));row.append(add);}holder.append(row);}await board();}
const reasonLabels={policy_not_ratified:'Official ranking policy awaiting approval',unregistered_protocol_or_input_set:'Input set is outside the approved standard',nonstandard_evaluation:'Custom evaluation',decoding_policy_mismatch_or_unknown:'Generation settings differ from the standard or are unknown',immutable_target_revision_missing:'Target model revision is unknown',generation_conditions_incomplete:'Generation conditions are incomplete',independent_generation_evidence_missing:'Target generation has no independent verification',measurement_limited:'Classifier accuracy remains limited',incomplete_valid_outputs:'Some expected outputs are missing or invalid',undefined_denominator:'No eligible observations for this denominator',descriptive_only:'Descriptive metric',strategy_is_not_quality:'Strategy frequency does not measure quality',model_dependent_conditioning:'The classified group contains different examples for each model'};
function metrics(summary){const holder=$('public-metrics');holder.replaceChildren();holder.append(el('h3',summary.display?.display_name||summary.model.id),el('p','Original model: '+summary.model.id),el('p','Policy '+summary.rank_policy_status+' · no combined ethics score. Original publication scope: '+summary.scope+'.'));
  const wrapper=el('div',undefined,'metric-scroll'),table=el('table');const head=el('tr');for(const label of ['Metric / scope','Observed ratio','Valid coverage','Rank status and reasons'])head.append(el('th',label));const thead=el('thead');thead.append(head);table.append(thead);const body=el('tbody');
  for(const m of summary.rank_admission.metrics){const row=el('tr'),value=m.rate.value===null?'N/A':(100*m.rate.value).toFixed(2)+'%';row.append(el('td',m.id.replaceAll('_',' ')),el('td',value+' ('+m.rate.numerator+'/'+m.rate.denominator+')'),el('td',m.coverage.numerator+'/'+m.coverage.denominator),el('td',(m.rank_eligible?'Eligible':'Excluded')+' · '+m.reasons.map(r=>reasonLabels[r]||r.replaceAll('_',' ')).join('; ')));body.append(row);}table.append(body);wrapper.append(table);holder.append(wrapper);}
async function board(){
  // Clear old values before requesting a new complete projection. A failed
  // recheck or capacity error must not leave withdrawn rows on screen.
  clearBoard('Loading published metric comparison…');
  try{state.board=await api('/api/public/leaderboard',{authenticated:false});}
  catch(e){clearBoard('Comparison unavailable: '+e.message,true);return;}
  const result=state.board,select=$('leaderboard-metric');
  $('leaderboard-status').textContent=result.publication_count+' published result(s) · policy '+result.policy_status+
    (result.official_ranking_enabled?' · eligible metrics ranked separately.':' · official ranks disabled; excluded values are descriptive.');
  const groups=new Map();
  for(const b of result.boards)groups.set(b.metric_id+'|'+b.cohort_sha256,{id:b.metric_id,cohort:b.cohort_sha256});
  for(const row of result.excluded)groups.set(row.metric_id+'|'+row.metric.cohort_sha256,{id:row.metric_id,cohort:row.metric.cohort_sha256});
  const ordered=[...groups.entries()].sort((a,b)=>a[0].localeCompare(b[0]));
  for(const [key,group] of ordered){const n=ordered.filter(x=>x[1].id===group.id).findIndex(x=>x[0]===key)+1;
    const option=el('option',group.id.replaceAll('_',' ')+' · evaluation group '+n);option.value=key;select.append(option);}
  select.disabled=!ordered.length;drawBoard();
}
function drawBoard(){
  const holder=$('leaderboard-values');holder.replaceChildren();const result=state.board,key=$('leaderboard-metric').value;
  if(!result||!key){holder.append(el('p','No published metric values to compare.','empty'));return;}
  const [metricId,cohort]=key.split('|'),rows=[];
  for(const b of result.boards)if(b.metric_id===metricId&&b.cohort_sha256===cohort)for(const row of b.rows)rows.push({...row,eligible:true});
  // Excluded rows retain submission identity order, never a provisional rank.
  for(const row of result.excluded)if(row.metric_id===metricId&&row.metric.cohort_sha256===cohort)rows.push({...row,eligible:false});
  const wrapper=el('div',undefined,'metric-scroll'),table=el('table',undefined,'leaderboard-table'),thead=el('thead'),head=el('tr');
  for(const label of ['Model / revision','Observed ratio','Valid coverage','Rank','Status and reasons'])head.append(el('th',label));thead.append(head);table.append(thead);
  const body=el('tbody');for(const entry of rows){const m=entry.metric,ratio=m.rate.value===null?'N/A':(100*m.rate.value).toFixed(2)+'%',row=el('tr');row.dataset.boardEntry=entry.entry_id;
    row.append(el('td',entry.model.id+' · '+(entry.model.revision?entry.model.revision.slice(0,12):'unknown revision')),
      el('td',ratio+' ('+m.rate.numerator+'/'+m.rate.denominator+') · '+m.rate.sources+' sources'),el('td',m.coverage.numerator+'/'+m.coverage.denominator),
      el('td',entry.eligible?String(entry.rank):'—'),el('td',entry.eligible?'Eligible':m.reasons.map(r=>reasonLabels[r]||r.replaceAll('_',' ')).join('; ')));body.append(row);}
  table.append(body);wrapper.append(table);holder.append(wrapper);
}
$('leaderboard-refresh').addEventListener('click',()=>perform(board));$('leaderboard-metric').addEventListener('change',drawBoard);
$('identity-refresh').addEventListener('click',()=>perform(signIn));$('identity-logout').addEventListener('click',()=>perform(async()=>{await api('/api/identity/logout',{method:'POST',body:'{}'});await signIn();message('Signed out. Preserved submissions remain private or published in their recorded scope.');}));
$('submission-upload-refresh').addEventListener('click',uploads);$('submission-upload').addEventListener('change',controls);
$('submissions-refresh').addEventListener('click',()=>perform(()=>list()));$('submissions-next').addEventListener('click',()=>perform(()=>list(state.next)));
$('public-refresh').addEventListener('click',()=>perform(()=>published()));$('public-next').addEventListener('click',()=>perform(()=>published(state.publicNext)));
$('submission-create').addEventListener('click',()=>perform(async()=>{const saved=await mutate('/api/submissions',{upload_id:$('submission-upload').value,display_name:$('submission-display-name').value.trim()||null,description:$('submission-description').value});show(await api('/api/submissions/'+encodeURIComponent(saved.id)));await list();message('Private original saved. Publication review has not been requested.');}));
$('submission-revise').addEventListener('click',()=>perform(async()=>{const item=state.current;const saved=await mutate('/api/submissions/'+encodeURIComponent(item.id)+'/revisions',{upload_id:$('submission-upload').value,expected_version:item.version,kind:$('revision-kind').value,reason:$('submission-reason').value});show(await api('/api/submissions/'+encodeURIComponent(saved.id)));await list();message('New private revision saved. Any earlier published revision stays visible until explicitly replaced or withdrawn.');}));
$('submission-metadata-save').addEventListener('click',()=>perform(async()=>{const item=state.current;const saved=await mutate('/api/submissions/'+encodeURIComponent(item.id)+'/metadata',{display_name:$('submission-display-name').value,description:$('submission-description').value,expected_version:item.version});show(saved);await list();await published();message('Display metadata saved. Original model identity and result are unchanged.');}));
$('submission-original').addEventListener('click',()=>perform(()=>download('/api/submissions/'+encodeURIComponent(state.current.id)+'/result','koevd-private-original.json')));
$('submission-history').addEventListener('click',()=>perform(()=>download('/api/submissions/'+encodeURIComponent(state.current.id)+'/history','koevd-submission-history.json')));
(async()=>{try{const config=await api('/api/registration',{authenticated:false});if(!config.enabled)return;state.summaryPublication=config.self_reported_summaries_enabled===true;$('registration-section').hidden=false;
  if(config.official_ranking_enabled)$('rank-policy-notice').textContent='Operator policy permits eligible metrics to be ranked separately. Signing in does not verify model generation; classifier limitations and descriptive metrics stay excluded.';
  $('workspace-footer').textContent='Submission review is a local candidate workflow. Inspect each metric’s denominators, eligibility and measurement limits.';await signIn();await published();}catch(e){message(e.message,true);}})();
}());
