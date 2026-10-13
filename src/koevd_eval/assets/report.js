/* Code-owned offline UI. No metric scoring, HTML injection, eval or network calls. */
(function () {
  'use strict';
  const METRICS = {
    coverage: 'Valid output coverage', event_on_valid: 'Observed event / valid outputs',
    observed_event_on_all: 'Observed event / all inputs', accuracy_on_valid: 'Choice accuracy / valid answers',
    missed_risk_on_valid_unsafe: 'Missed risk / valid unsafe inputs', false_alarm_on_valid_safe: 'False alarm / valid safe inputs',
    coverage_unsafe: 'Coverage of unsafe inputs', coverage_safe: 'Coverage of safe inputs', unsafe_marker: 'Separate unsafe marker',
    api_failure: 'API failure', empty_final: 'Empty final response', length_limit: 'Reported length limit',
    finish_reason_unknown: 'Finish reason unknown', api_refusal: 'API refusal', reasoning_without_final: 'Reasoning without final response',
    single_character_repetition: 'Single-character repetition', parse_invalid: 'Invalid parse',
    measurement_invalid_or_missing: 'Invalid or missing measurement', classifier_disagreement: 'Classifier disagreement',
    unsafe_tool: 'Unsafe mock tool', allowed_tool: 'Allowed mock tool', other_available_tool: 'Other available tool',
    refuse: 'Refusal', answer_without_tool: 'Answer without tool', ask_clarification: 'Clarification', invalid: 'Invalid output',
    safe: 'Classifier-safe', unsafe: 'Classifier-unsafe', unclassified: 'Unclassified', missing: 'No Task 3 match',
  };
  const STRATEGIES = {
    a_evaluation:'Evaluate Utterance', 'a_boundary setting':'Set a Boundary', 'a_providing definitions':'Define Terms',
    'a_detouring q':'Detouring Question', a_reiteration:'Sanitized Reiteration', 'b_counter speech':'Counter-speech',
    'b_agreeing speech':'Conditional Empathy', 'b_neutral speech':'Neutral Framing', c_reasoning:'Reasoning',
    'c_info providing':'Safe Information', c_educating:'Educating / Safer Alternative', d_summation:'Summation',
    'd_social expressions':'Social Expression', d_redirecting:'Redirecting', e_humour:'Humour',
  };
  const AXES = {severity_band:'Severity', explicitness:'Explicitness', utterance_type:'Utterance type', topic:'Topic',
    risk_category:'Risk category', evaluation_subset:'Evaluation subset', 'severity_band × explicitness':'Severity × explicitness'};
  const TASKS = {1:'Input-risk judgment',2:'Candidate-response choice',3:'Response safety proxy',4:'Response strategies',5:'Mock-tool choice'};
  const TABS = [['overview','Overview'],['task1','Task 1 · Input risk'],['task2','Task 2 · Candidate choice'],
    ['task3','Task 3 · Response safety'],['task4','Task 4 · Strategies'],['task5','Task 5 · Mock tools'],
    ['transitions','Response → tool choice'],['metadata','Metadata'],['quality','Output quality'],
    ['comparison','Model comparison'],['cases','Cases'],['method','Method & limitations']];
  const eventLabel = task => ({1:'Judgment errors',2:'Choice errors',3:'Classifier-unsafe responses',5:'Unsafe mock-tool choices'})[task]||'Observed events';
  const label = key => STRATEGIES[key] || METRICS[key] || AXES[key] || String(key);
  const percent = value => value == null ? 'N/A' : (100 * value).toFixed(1) + '%';
  const short = (value, max=28) => String(value).length > max ? String(value).slice(0,max-1)+'…' : String(value);
  const intervalText = interval => !interval ? 'Interval not supplied' : interval.lower == null ? 'Interval: '+interval.status.replaceAll('_',' ') :
    '95% source interval '+percent(interval.lower)+'–'+percent(interval.upper);
  const allCases = data => data.runs.flatMap(p => p.cases);
  function matches(caseData, filters) {
    for (const key of ['artifact_sha256','task','variant','source_id','sample_id']) {
      if (filters[key] != null && caseData[key] !== filters[key]) return false;
    }
    const view=caseData.view;
    if (filters.subset != null && !(view.axis_values.evaluation_subset || []).includes(filters.subset)) return false;
    if (filters.axis && !(view.axis_values[filters.axis] || []).includes(String(filters.value))) return false;
    if (filters.quality_flag && !caseData.quality_flags.includes(filters.quality_flag)) return false;
    const strategies=caseData.measurement.value?.strategies || [];
    if (filters.strategy && !strategies.includes(filters.strategy)) return false;
    if (filters.strategies_all && !filters.strategies_all.every(v=>strategies.includes(v))) return false;
    if (filters.confusion && view.confusion !== filters.confusion) return false;
    if (filters.tool_outcome && (caseData.task!==5 || view.tool_outcome!==filters.tool_outcome)) return false;
    if (filters.paired_response_label && view.paired_response_label!==filters.paired_response_label) return false;
    return true;
  }
  function pairedCases(data, comparison, task, kind='all', name='all', state='all') {
    const lp=data.runs.find(p=>p.artifact_sha256===comparison.left_artifact);
    const rp=data.runs.find(p=>p.artifact_sha256===comparison.right_artifact);
    const a=new Map(lp.cases.filter(c=>c.task===task).map(c=>[c.sample_id,c]));
    const b=new Map(rp.cases.filter(c=>c.task===task).map(c=>[c.sample_id,c]));
    const part=comparison.tasks.find(t=>t.task===task).partitions.find(p=>p.kind===kind && p.name===name);
    return part.sample_ids.map(key=>({left:a.get(key),right:b.get(key)})).filter(pair=>{
      const x=pair.left,y=pair.right;
      if(x.input_sha256!==y.input_sha256) throw new Error('Paired input mismatch');
      pair.validity=x.valid && y.valid ? 'both_valid' : x.valid ? 'left_only_valid' : y.valid ? 'right_only_valid' : 'both_invalid';
      return state==='all' || state===pair.validity || task!==4 && pair.validity==='both_valid' &&
        (state==='left_event_only' && x.event && !y.event || state==='right_event_only' && y.event && !x.event);
    });
  }
  const API=Object.freeze({matches,pairedCases,percent,intervalText});
  if(typeof module !== 'undefined' && module.exports) module.exports=API;
  if(typeof document === 'undefined') return;
  const data=JSON.parse(document.getElementById('koevd-data').textContent);
  const state={run:0,tab:'overview',caseFilter:{},caseQuery:'',caseStatus:'all',casePage:0,comparison:0,compareTask:1,compareScope:'all:all',compareState:'all',comparePage:0};
  const el=(tag,className='',text=null)=>{const n=document.createElement(tag);if(className)n.className=className;if(text!==null)n.textContent=String(text);return n;};
  const button=(text,action,className='')=>{const n=el('button',className,text);n.type='button';n.addEventListener('click',action);return n;};
  const svg=(tag,attrs={})=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));return n;};
  function svgText(parent,text,x,y,attrs={}) {const n=svg('text',{x,y,...attrs});n.textContent=String(text);parent.append(n);return n;}
  function select(labelText,items,value,change,id) {
    const wrap=el('label','',labelText),n=el('select');if(id)n.id=id;
    for(const [key,text] of items){const o=el('option','',text);o.value=String(key);n.append(o);}n.value=String(value);
    n.addEventListener('change',()=>change(n.value));wrap.append(n);return wrap;
  }
  function table(headers,rows) {
    const wrap=el('div','table-wrap'),t=el('table'),head=el('thead'),tr=el('tr');
    for(const h of headers)tr.append(el('th','',h));head.append(tr);t.append(head);
    const body=el('tbody');for(const row of rows){const r=el('tr');for(const value of row){const c=el('td');if(value?.nodeType)c.append(value);else c.textContent=value==null?'N/A':String(value);r.append(c);}body.append(r);}t.append(body);wrap.append(t);return wrap;
  }
  function details(title,node,open=false) {const n=el('details');n.open=open;n.append(el('summary','',title),node);return n;}
  function note(text,cool=false){return el('div','note'+(cool?' cool':''),text);}
  function panel(title){const n=el('section','panel');if(title)n.append(el('h2','',title));return n;}
  function badge(text,kind=''){return el('span','badge '+kind,text);}
  function empty(text){return el('div','empty',text);}
  function jsonBlock(value){return el('pre','',JSON.stringify(value,null,2));}
  function download(name,text,mime='application/json') {
    const url=URL.createObjectURL(new Blob([text],{type:mime})),a=el('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  const shell=el('div','shell'),side=el('aside','sidebar'),main=el('main','main');main.id='main';main.tabIndex=-1;
  const brand=el('div','brand');brand.append(el('div','brand-icon','K'));const brandText=el('div');brandText.append(el('div','brand-title','KoEVD'),el('div','brand-sub','MULTI-STAGE MODEL DIAGNOSTICS'));brand.append(brandText);side.append(brand);
  const nav=el('nav','nav');nav.setAttribute('aria-label','Analysis sections');nav.setAttribute('role','tablist');
  TABS.forEach(([key,text],i)=>{const b=button('',()=>showTab(key));b.id='tab-'+key;b.setAttribute('role','tab');b.setAttribute('aria-controls','view');b.append(el('span','nav-index',String(i+1).padStart(2,'0')),el('span','',text));nav.append(b);});
  nav.addEventListener('keydown',event=>{if(!['ArrowDown','ArrowUp','ArrowRight','ArrowLeft','Home','End'].includes(event.key))return;
    const list=[...nav.querySelectorAll('button')],index=list.indexOf(document.activeElement);if(index<0)return;event.preventDefault();
    const next=event.key==='Home'?0:event.key==='End'?list.length-1:(index+(['ArrowDown','ArrowRight'].includes(event.key)?1:-1)+list.length)%list.length;list[next].focus();list[next].click();});
  side.append(nav,el('div','sidebar-note','Local analysis only. Upload, verification and public publication are separate steps. No combined ethics score.'));
  const top=el('div','topbar'),runSelect=select('Evaluation run',data.runs.map((p,i)=>[i,p.run.model.id+' · '+short(p.run.id,22)]),0,v=>{state.run=Number(v);state.caseFilter={};state.casePage=0;render();},'run-select');runSelect.classList.add('run-control');top.append(runSelect);
  const actions=el('div','actions');actions.append(button('Analysis JSON',()=>download('koevd-analysis.json',JSON.stringify(data,null,2))),button('Cases JSONL',()=>download('koevd-cases.jsonl',allCases(data).map(c=>{const {view,...original}=c;return JSON.stringify(original);}).join('\n')+'\n','application/x-ndjson')),button('Print view',()=>window.print()));top.append(actions);
  const view=el('div');view.id='view';view.setAttribute('role','tabpanel');main.append(top,view,el('div','footer','KoEVD · '+data.format+' · '+data.renderer_version+' · Offline rendering, no network calls. Analysis is not public registration.'));
  shell.append(side,main);document.getElementById('app').append(shell);
  const tip=el('div','tooltip');tip.hidden=true;tip.setAttribute('role','tooltip');tip.id='chart-tooltip';document.body.append(tip);
  function showTip(text,target,event){tip.textContent=text;tip.hidden=false;const r=target.getBoundingClientRect();const x=event?.clientX||r.left+15,y=event?.clientY||r.top+15;tip.style.left=Math.max(8,Math.min(x+12,window.innerWidth-355))+'px';tip.style.top=Math.max(8,Math.min(y+15,window.innerHeight-tip.offsetHeight-10))+'px';}
  function datumDescription(d,isRate){return (d.label?label(d.label):[label(d.left||d.response_label),label(d.right||d.tool_outcome)].join(' → '))+'\n'+
    (isRate?percent(d.value)+' · '+d.numerator+'/'+d.denominator:'Count '+d.count+' · denominator '+(d.denominator??d.classified??'not supplied'))+
    '\nSources '+(d.sources??'see scope')+(d.coverage!=null?' · coverage '+percent(d.coverage):'')+'\n'+(isRate?intervalText(d.interval):'Descriptive count')+'\nSelect to inspect matching cases.';}
  function interactive(group,d,isRate){const text=datumDescription(d,isRate);const title=svg('title');title.textContent=text;group.append(title);group.setAttribute('role','button');group.setAttribute('tabindex','0');group.setAttribute('aria-label',text.replaceAll('\n','; '));group.setAttribute('aria-describedby','chart-tooltip');
    group.addEventListener('mouseenter',event=>showTip(text,group,event));group.addEventListener('mousemove',event=>showTip(text,group,event));group.addEventListener('mouseleave',()=>tip.hidden=true);group.addEventListener('focus',()=>showTip(text,group));group.addEventListener('blur',()=>tip.hidden=true);
    const activate=()=>{tip.hidden=true;if(d.case_filter)openCases(d.case_filter);};group.addEventListener('click',activate);group.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();activate();}});}
  function barChart(spec){const rate=spec.kind==='rate_bars',height=50+spec.data.length*47,s=svg('svg',{viewBox:`0 0 780 ${height}`,class:'chart','aria-label':spec.title});
    const max=rate?1:Math.max(1,...spec.data.map(d=>d.count||0)),x0=240,width=340;
    for(const tick of [0,.25,.5,.75,1]){s.append(svg('line',{x1:x0+tick*width,y1:28,x2:x0+tick*width,y2:height-15,class:'grid'}));svgText(s,rate?String(tick*100)+'%':String(Math.round(tick*max)),x0+tick*width,15,{class:'axis-text','text-anchor':'middle'});}
    spec.data.forEach((d,i)=>{const y=40+i*47,g=svg('g'),value=rate?d.value:d.count;g.append(svg('rect',{x:0,y:y-3,width:780,height:44,fill:'transparent','pointer-events':'all'}));svgText(g,short(d.label==='event_on_valid'?eventLabel(spec.task)+' / valid':d.label==='observed_event_on_all'?eventLabel(spec.task)+' / all':label(d.label),33),0,y+16,{class:'bar-label'});
      if(value==null){g.append(svg('rect',{x:x0,y,width,height:23,rx:4,class:'mark bar-missing'}));svgText(g,'N/A — no valid denominator',x0+10,y+16,{class:'bar-value'});}
      else{g.append(svg('rect',{x:x0,y,width:Math.max(0,value/max*width),height:23,rx:3,class:'mark bar-mark'}));if(value===0)g.append(svg('line',{x1:x0,y1:y,x2:x0,y2:y+23,stroke:'#377aa5','stroke-width':2}));
        if(rate && d.interval?.lower!=null){const a=x0+d.interval.lower*width,b=x0+d.interval.upper*width;g.append(svg('line',{x1:a,y1:y+11,x2:b,y2:y+11,class:'ci'}),svg('line',{x1:a,y1:y+6,x2:a,y2:y+16,class:'ci'}),svg('line',{x1:b,y1:y+6,x2:b,y2:y+16,class:'ci'}));}}
      const primary=rate?percent(value)+' · '+d.numerator+'/'+d.denominator:String(d.count)+' / '+(d.denominator??'—');svgText(g,primary,598,y+12,{class:'bar-value'});svgText(g,'n='+d.sources+' sources',598,y+28,{class:'axis-text'});interactive(g,d,rate);s.append(g);});return s;}
  function matrixChart(spec){let rows,cols,get,isRate=spec.kind==='strategy_group_matrix';
    if(spec.kind==='confusion_matrix'){rows=['safe','unsafe'];cols=['safe','unsafe','unparsed'];get=(a,b)=>spec.data.find(d=>d.label===a+'->'+b)||{label:a+'->'+b,count:0,denominator:spec.data[0]?.denominator||0,sources:spec.data[0]?.sources||0,case_filter:{artifact_sha256:spec.artifact_sha256,task:1,confusion:a+'->'+b}};}
    else if(spec.kind==='transition_matrix'){rows=['safe','unsafe','unclassified','missing'];cols=['unsafe_tool','allowed_tool','other_available_tool','refuse','answer_without_tool','ask_clarification','invalid'];get=(a,b)=>spec.data.find(d=>d.response_label===a&&d.tool_outcome===b);}
    else{rows=[...new Set(spec.data.map(d=>d.left))];cols=spec.kind==='count_matrix'?rows:[...new Set(spec.data.map(d=>d.right))];get=(a,b)=>spec.data.find(d=>d.left===a&&d.right===b)||spec.data.find(d=>d.left===b&&d.right===a);}
    const cellWidth=spec.kind==='count_matrix'?32:Math.max(45,(780-200-30)/Math.max(cols.length,1));
    const rowHeight=spec.kind==='count_matrix'||isRate?34:64,left=200,top=170,width=Math.max(780,left+cols.length*cellWidth+30),height=top+rows.length*rowHeight+30;
    const s=svg('svg',{viewBox:`0 0 ${width} ${height}`,class:'chart matrix','aria-label':spec.title});const maximum=Math.max(1,...spec.data.map(d=>d.count||0));
    const axisLabel=value=>spec.kind==='confusion_matrix'?value:label(value);
    cols.forEach((col,i)=>svgText(s,short(axisLabel(col),26),left+i*cellWidth+cellWidth/2,top-10,{class:'axis-text',transform:`rotate(-45 ${left+i*cellWidth+cellWidth/2} ${top-10})`,'text-anchor':'start'}));
    rows.forEach((row,j)=>{svgText(s,short(axisLabel(row),27),left-12,top+j*rowHeight+rowHeight/2+4,{'text-anchor':'end',class:'axis-text'});
      cols.forEach((col,i)=>{const d=get(row,col);if(!d)return;const value=isRate?d.value:d.count/maximum,g=svg('g');
        g.append(svg('rect',{x:left+i*cellWidth,y:top+j*rowHeight,width:cellWidth-2,height:rowHeight-2,rx:3,fill:value==null?'#e9edf0':`rgba(55,122,165,${.08+.65*value})`,class:'mark'}));
        const text=isRate?(d.value==null?'N/A':Math.round(d.value*100)+'%'):String(d.count);svgText(g,text,left+i*cellWidth+(cellWidth-2)/2,top+j*rowHeight+rowHeight/2+4,{'text-anchor':'middle',class:'cell-number'});interactive(g,isRate?{...d,numerator:d.count}:d,isRate);s.append(g);});});return s;}
  function exportSVG(drawing){const copy=drawing.cloneNode(true),style=svg('style');style.textContent=document.querySelector('style').textContent;copy.prepend(style);copy.setAttribute('xmlns','http://www.w3.org/2000/svg');return new XMLSerializer().serializeToString(copy);}
  function chartTitle(spec){const f=spec.data[0]?.case_filter||{},scope=f.subset?'Subset '+f.subset:f.variant?'Variant '+f.variant:spec.task===3||spec.task===4?'Source union':'All inputs';
    if(spec.family==='group')return 'Task '+spec.task+' · '+(spec.task===4?'Coverage':eventLabel(spec.task)+' / valid')+' by '+label(f.axis)+' · '+scope;
    if(spec.family==='strategy_group')return 'Task 4 · Strategy inclusion by '+label(f.axis)+' · '+scope;
    if(spec.family==='label_specific')return 'Task 1 · '+(spec.title.includes('missed_risk')?'Missed risk':'False alarms')+' by Severity';
    return spec.title;
  }
  function chart(spec){const p=panel(),head=el('div','panel-head'),titles=el('div');titles.append(el('h3','',chartTitle(spec).replaceAll('event_on_valid','observed event / valid').replaceAll('missed_risk_on_valid_unsafe','missed risk').replaceAll('false_alarm_on_valid_safe','false alarm')));
    titles.append(el('div','metric-direction',spec.kind==='rate_bars'&&spec.task!==4?'Coverage/accuracy: higher is more complete/correct. Event rates: lower observed frequency; interpret with coverage.':'Descriptive behavior / counts. No combined quality score.'));head.append(titles);
    const actions=el('div','chart-actions'),drawing=spec.kind==='rate_bars'||spec.kind==='count_bars'?barChart(spec):matrixChart(spec);actions.append(button('SVG',()=>download('koevd-chart-'+spec.id.slice(0,12)+'.svg',exportSVG(drawing),'image/svg+xml')));head.append(actions);p.append(head);
    const scroll=el('div','chart-scroll');scroll.append(drawing);p.append(scroll,el('div','legend',spec.kind==='rate_bars'?'Bars: reported rate. Black whiskers: source bootstrap 95% interval where available. N/A is undefined, not zero. Click a row to inspect its scope.':'Select a cell/bar to inspect matching cases. Counts and exact denominators are in the data table.'));
    const rows=spec.data.map(d=>[d.label?label(d.label):[label(d.left||d.response_label),label(d.right||d.tool_outcome)].join(' → '),d.count??d.numerator,d.denominator??d.classified,d.sources??'See scope','value'in d?percent(d.value):'Count',intervalText(d.interval)]);
    p.append(details('Exact chart data',table(['Metric / cell','Numerator / count','Denominator','Sources','Rate','Interval'],rows)));return p;}
  function openCases(filters){state.caseFilter={...filters};state.caseQuery='';state.caseStatus='all';state.casePage=0;showTab('cases');}
  function showTab(key){state.tab=key;render();main.focus({preventScroll:true});window.scrollTo({top:0,behavior:'instant'});}
  function intro(title,description){view.append(el('div','eyebrow','Local diagnostic analysis'),el('h1','',title),el('p','page-intro',description));}
  function current(){return data.runs[state.run];}
  function scopeName(part,task=null){return part.kind==='all'?(part.name==='all'?([3,4].includes(task)?'Full source union':[2,5].includes(task)?'Pooled variants (ancillary)':task===1?'Primary input set':'All matched inputs'):part.name):part.kind==='subset'?'Subset: '+part.name:'Variant: '+part.name;}
  function scopeTable(parts,task){return table(['Scope','Rows / sources','Valid / coverage','Observed event / valid','Observed event / all'],parts.map(p=>[scopeName(p,task),p.rows+' / '+p.unique_sources,p.valid+' / '+percent(p.coverage),task===4?'Descriptive only':p.events+' / '+p.valid+' · '+percent(p.event_rate_on_valid),task===4?'No quality rank':p.events+' / '+p.rows+' · '+percent(p.event_rate_on_all)]));}
  function appendCharts(specs){for(const spec of specs)view.append(chart(spec));}

  function overview(){const profile=current();intro('Understand behavior at each decision point','Review completion and measurement limits first, then inspect task-specific behavior and the examples behind it.');
    if(profile.disclosure)view.append(note(profile.disclosure.note,true));
    const synthetic=profile.run.model.id.toUpperCase().includes('SYNTHETIC');view.append(note(synthetic?'SYNTHETIC DEMONSTRATION · Fictional outputs and labels. No inference, accuracy evidence or public baseline.':'LOCAL RESULT · Target model identity is user-reported. Task 3/4 measurements are limited; no official ranking is granted.'));
    const cards=el('div','cards');for(const [task,report]of Object.entries(profile.tasks)){const p=report.partitions[0],c=el('section','card');c.append(el('div','card-title','Task '+task+' · '+TASKS[task]),el('div','card-meta','Valid output coverage'),el('div','card-value',percent(p.coverage)),el('div','card-meta',p.valid+' / '+p.rows+' valid records · '+p.unique_sources+' sources'));
      const message=task==='4'?'Multi-label behavior, no quality score':p.events+' '+eventLabel(Number(task)).toLowerCase()+' / '+p.valid+' valid outputs · '+percent(p.event_rate_on_valid);c.append(el('div','card-meta',message),button('Explore Task '+task,()=>showTab('task'+task),'text-link'));cards.append(c);}view.append(cards);
    const summary=panel('Read these counts separately');summary.append(el('p','muted','Task 4 reuses Task 3 responses. Task 2/5 variants repeat sources; cards are not independent samples or a combined model score.'),scopeTable(profile.tasks['3'].partitions,3));view.append(summary);
    const quality=panel('Priority review');quality.append(el('p','muted','Inspect failures, missing measurement, truncation and classifier disagreement before interpreting a low observed event rate. These filters cover all records.'));
    for(const flag of ['api_failure','measurement_invalid_or_missing','length_limit','classifier_disagreement','single_character_repetition']){const counts=Object.entries(profile.quality).filter(([t])=>t!=='4').map(([t,q])=>[t,q.flag_counts[flag]||0]);if(counts.some(([,n])=>n))quality.append(button(label(flag)+' · '+counts.map(([t,n])=>'T'+t+': '+n).join(' / '),()=>openCases({artifact_sha256:profile.artifact_sha256,quality_flag:flag})));}view.append(quality);
    const signals=panel('Observed group contrasts');signals.append(el('p','muted','Screening: at least 20 valid sources and 90% coverage on each side. Topics can overlap; contrasts use disjoint remaining sources. These are descriptive review candidates.'));
    const selected=profile.signals.slice(0,8);if(!selected.length)signals.append(empty('Insufficient supported contrasts. This is not evidence of uniform behavior.'));else signals.append(table(['Scope','Group','Group events / valid','Remaining events / valid','Difference','Cases'],selected.map(s=>['T'+s.task+' · '+s.partition_kind+':'+s.partition_name,AXES[s.axis]+' = '+s.value,s.group_events+'/'+s.group_valid,s.remaining_events+'/'+s.remaining_valid,s.difference_pp.toFixed(1)+' pp',button('Inspect',()=>openCases({artifact_sha256:profile.artifact_sha256,task:s.task,variant:s.partition_kind==='variant'?s.partition_name:null,subset:s.partition_kind==='subset'?s.partition_name:null,axis:s.axis,value:s.value}))])));view.append(signals);}
  function taskPage(task){const profile=current();intro('Task '+task+' · '+TASKS[task],{
      1:'Where does the model miss risky inputs, or flag benign inputs as risky? Invalid judgments stay separate from both kinds of error.',
      2:'Can the model distinguish response candidates under four different instructions? Compare each variant’s accuracy with its answer coverage.',
      3:'How are generated responses labeled by the safety classifier? Classifier-safe is a proxy, not a universal or deployment safety guarantee.',
      4:'Which strategies appear in the same Task 3 responses? Inclusion is multi-label and descriptive; frequent use does not establish response quality.',
      5:'Which non-executable mock tool does the model select under each framing? A low unsafe-choice rate must be interpreted with output validity.'}[task]);
    if(task===3||task===4)view.append(note('MEASUREMENT LIMITED · Reported classifier labels have not resolved the known new-response accuracy / batch sensitivity concerns. These tasks are excluded from official ranking.'));
    if(task===5)view.append(note('SIMULATION ONLY · No real tool or robot action is executed. Historical partial parsing and strict valid decisions are different metrics.',true));
    const p=panel('Task scopes and denominators');p.append(scopeTable(profile.tasks[String(task)].partitions,task));view.append(p);
    if(task===1){const f1=profile.tasks['1'].partitions[0].auxiliary.macro_f1_on_valid;view.append(el('p','muted','Auxiliary macro F1 on valid judgments: '+(f1==null?'N/A':f1.toFixed(3))+'. Class-specific coverage and missed-risk / false-alarm rates remain essential.'));}
    if(task!==4){appendCharts(profile.charts.filter(c=>c.task===task && ['rates','confusion','tool_outcomes','label_specific'].includes(c.family)));return;}
    const controls=el('div','controls');let scope='union',axis='severity_band';const chartArea=el('div');
    function redraw(){chartArea.replaceChildren();const subset=scope==='union'?null:scope;
      for(const c of profile.charts.filter(c=>c.task===4&&['strategy','unsafe_marker','co_occurrence'].includes(c.family)&&(c.data[0]?.case_filter?.subset??null)===subset))chartArea.append(chart(c));
      const heat=profile.charts.find(c=>c.family==='strategy_group'&&c.data[0]?.case_filter.axis===axis&&(c.data[0]?.case_filter.subset??null)===subset);if(heat)chartArea.append(chart(heat));}
    controls.append(select('Response subset',[['union','Full source union'],...profile.tasks['4'].partitions.filter(p=>p.kind==='subset').map(p=>[p.name,'Subset: '+p.name])],scope,v=>{scope=v;redraw();},'strategy-scope'),select('Strategy metadata heatmap',Object.entries(AXES),axis,v=>{axis=v;redraw();},'strategy-axis'));view.append(controls,chartArea);redraw();}
  function transitionsPage(){const profile=current();intro('From response to tool selection','The same source can produce a classifier-safe response and an unsafe simulated tool choice. The matrix is observational, not a causal or real-world safety test.');view.append(note('Classifier-safe / unsafe are limited measurement labels. Invalid tool output and unclassified response are explicit states; pooled framings repeat the same sources.'));
    const summary=panel('Unsafe mock-tool choice, conditional on response label');const rows=[];for(const [framing,entry]of Object.entries(profile.task3_task5))for(const group of ['safe','unsafe']){const a=entry.rates[group+'/all_matched'],b=entry.rates[group+'/valid_tool_choices'];rows.push([framing,label(group),a.numerator+'/'+a.denominator+' · '+percent(a.value),b.numerator+'/'+b.denominator+' · '+percent(b.value),a.sources,intervalText(a.interval)]);}summary.append(table(['Framing','Task 3 label','Unsafe / all matched','Unsafe / valid tools','Eligible sources','All-matched interval'],rows));view.append(summary);
    let framing=profile.task3_task5.safe_guided?'safe_guided':Object.keys(profile.task3_task5)[0];const controls=el('div','controls'),area=el('div');function redraw(){area.replaceChildren();const c=profile.charts.find(c=>c.family==='transition'&&(c.data[0]?.case_filter.variant??'pooled')===framing);if(c)area.append(chart(c));}
    controls.append(select('Framing',Object.keys(profile.task3_task5).map(v=>[v,v==='pooled'?'Pooled framings (source-clustered)':v]),framing,v=>{framing=v;redraw();},'transition-framing'));view.append(controls,area);redraw();}
  function metadataPage(){const profile=current();intro('Metadata-conditioned behavior','Inspect severity, explicitness, utterance type, topic and risk category within one task and scope. Groups can overlap; do not add their totals.');view.append(note('These are observed associations under the benchmark operational criteria. They do not directly measure demographic bias, causal effects or natural risk prevalence.',true));
    let task=1,axis='severity_band',scope='all:all';const controls=el('div','controls'),area=el('div');let scopeControl;
    function redraw(){area.replaceChildren();const [kind,name]=scope.split(':');const specs=profile.charts.filter(c=>c.task===task&&['group','strategy_group','label_specific'].includes(c.family)&&c.data[0]?.case_filter.axis===axis && (kind==='subset'?c.data[0]?.case_filter.subset===name:kind==='variant'?c.data[0]?.case_filter.variant===name:!c.data[0]?.case_filter.subset&&!c.data[0]?.case_filter.variant));if(specs.length)for(const c of specs)area.append(chart(c));else area.append(empty('No chart for this scope. Empty denominators remain N/A.'));
      const groups=profile.tasks[String(task)].groups.filter(g=>g.partition_kind===kind&&g.partition_name===name&&g.axis===axis);area.append(table(['Group','Rows / sources','Valid / coverage','Events / valid','Contrast support'],groups.map(g=>[g.value,g.rows+' / '+g.unique_sources,g.valid+' / '+percent(g.coverage),task===4?'Strategies are descriptive':g.events+'/'+g.valid+' · '+percent(g.event_rate_on_valid),g.contrast_support.replaceAll('_',' ')])));}
    function scopes(){if(scopeControl)scopeControl.remove();const parts=profile.tasks[String(task)].partitions.filter(p=>p.kind!=='all'||![2,5].includes(task));scope=parts[0].kind+':'+parts[0].name;scopeControl=select('Analysis scope',parts.map(p=>[p.kind+':'+p.name,scopeName(p,task)]),scope,v=>{scope=v;redraw();},'metadata-scope');controls.append(scopeControl);}
    controls.append(select('Task',Object.entries(TASKS).map(([t,n])=>[t,'Task '+t+' · '+n]),task,v=>{task=Number(v);scopes();redraw();},'metadata-task'),select('Metadata axis',Object.entries(AXES),axis,v=>{axis=v;redraw();},'metadata-axis'));scopes();view.append(controls,area);redraw();}
  function qualityPage(){const profile=current();intro('Output and measurement quality','Quality flags identify records to review, not new safety labels. Flags overlap, and Task 4 repeats Task 3 generation metadata.');view.append(note('A missing finish reason does not prove an output was complete. The repetition flag only detects at least 128 identical characters; absence of that flag does not rule out other repetition.',true));
    const p=panel('Classifier disagreement');p.append(el('p','',profile.measurement_disagreement.count+' / '+profile.measurement_disagreement.comparable_sources+' jointly classified sources disagree between the safety label and strategy unsafe marker.'),el('p','muted',profile.measurement_disagreement.interpretation),button('Inspect disagreements',()=>openCases({artifact_sha256:profile.artifact_sha256,quality_flag:'classifier_disagreement'})));view.append(p);appendCharts(profile.charts.filter(c=>c.family==='quality'));}
  function renderCaseContent(c){const n=el('div','case-content');n.append(el('h4','','Prompt messages'),jsonBlock(c.messages),el('h4','','Final response'),el('pre','',c.response.text||'[No final text · '+c.response.status+']'));
    if(c.response.reasoning_content)n.append(details('Reasoning content (separate from final response)',el('pre','',c.response.reasoning_content)));
    n.append(el('h4','','Parsed / measurement state'),jsonBlock({valid:c.valid,event:c.event,parsed:c.parsed,measurement:c.measurement}),details('Trusted metadata and gold',jsonBlock({metadata:c.metadata,gold:c.gold})),details('Generation metadata and input identity',jsonBlock({response:{...c.response,text:'[displayed above]',reasoning_content:c.response.reasoning_content?'[separate field]':null},input_sha256:c.input_sha256,artifact_sha256:c.artifact_sha256})));return n;}
  function caseCard(c){const card=el('article','case-card'),head=el('div','case-header'),identity=el('div');identity.append(el('div','case-id',c.sample_id),el('div','muted','Task '+c.task+' · '+c.variant+' · '+c.source_id));head.append(identity);
    const status=el('div');status.append(badge(c.valid?'Valid':'Invalid / missing',c.valid?'':'warn'));if(c.event===true)status.append(badge('Observed event','fail'));if(c.task===3&&c.parsed)status.append(badge(label(c.parsed),'neutral'));if(c.task===5)status.append(badge(label(c.view.tool_outcome),'neutral'));head.append(status);card.append(head);
    const context=c.view.axis_values;card.append(el('div','case-context','Severity: '+context.severity_band.join(', ')+' · Explicitness: '+context.explicitness.join(', ')+' · Topic: '+context.topic.join(', ')));
    const actions=el('div','case-actions');actions.append(button('Same source across tasks',()=>openCases({artifact_sha256:c.artifact_sha256,source_id:c.source_id})));
    const index=data.comparisons.findIndex(p=>[p.left_artifact,p.right_artifact].includes(c.artifact_sha256)&&p.tasks.find(t=>t.task===c.task).partitions[0].sample_ids.includes(c.sample_id));if(index>=0)actions.append(button('Compare this input',()=>{state.comparison=index;state.compareTask=c.task;state.compareScope='all:all';state.compareSample=c.sample_id;state.compareState='all';state.comparePage=0;showTab('comparison');}));card.append(actions);
    if(c.quality_flags.length)card.append(el('div','case-context','Review flags: '+c.quality_flags.map(label).join(' · ')));card.append(details('Open prompt and response (may contain harmful text)',renderCaseContent(c)));return card;}
  const searchCache=new WeakMap();function caseSearch(c,query){if(!query)return true;if(!searchCache.has(c))searchCache.set(c,[c.sample_id,c.source_id,c.response.text,JSON.stringify(c.messages),JSON.stringify(c.metadata)].join('\n').toLowerCase());return searchCache.get(c).includes(query.toLowerCase());}
  function pagination(total,page,change){const n=el('div','pager'),pages=Math.max(1,Math.ceil(total/12));const prev=button('Previous',()=>change(page-1)),next=button('Next',()=>change(page+1));prev.disabled=page<=0;next.disabled=page>=pages-1;n.append(prev,el('span','statusline','Page '+(page+1)+' / '+pages),next);return n;}
  function casesPage(){const profile=current();intro('Inspect the full response set','Every validated record is available. Search and filters only change the view; they do not remove cases from metric denominators. Raw text starts folded.');
    if(state.caseFilter.artifact_sha256&&state.caseFilter.artifact_sha256!==profile.artifact_sha256){state.run=data.runs.findIndex(p=>p.artifact_sha256===state.caseFilter.artifact_sha256);document.getElementById('run-select').value=String(state.run);}const run=current();
    const controls=el('div','controls'),results=el('div');let variantControl;
    function changeFilter(key,value){state.caseFilter={...state.caseFilter,artifact_sha256:run.artifact_sha256};if(value==='')delete state.caseFilter[key];else state.caseFilter[key]=key==='task'?Number(value):value;state.casePage=0;redraw();}
    function variants(){if(variantControl)variantControl.remove();const variants=[...new Set(run.cases.filter(c=>!state.caseFilter.task||c.task===state.caseFilter.task).map(c=>c.variant))].sort();variantControl=select('Variant',[['','All variants'],...variants.map(v=>[v,v])],state.caseFilter.variant??'',v=>changeFilter('variant',v),'case-variant');controls.append(variantControl);}
    controls.append(select('Task',[['','All tasks'],...Object.entries(TASKS).map(([t,n])=>[t,'Task '+t+' · '+n])],state.caseFilter.task??'',v=>{delete state.caseFilter.variant;changeFilter('task',v);variants();},'case-task'));
    const subsets=[...new Set(run.cases.flatMap(c=>c.view.axis_values.evaluation_subset))].filter(v=>v!=='__missing__').sort();controls.append(select('Subset',[['','All subsets'],...subsets.map(v=>[v,v])],state.caseFilter.subset??'',v=>changeFilter('subset',v),'case-subset'),select('Output state',[['all','All records'],['event','Observed event'],['valid','Valid outputs'],['invalid','Invalid / missing outputs']],state.caseStatus,v=>{state.caseStatus=v;state.casePage=0;redraw();},'case-status'));
    const searchLabel=el('label','search-label','Search literal text'),search=el('input');search.id='case-search';search.type='search';search.placeholder='Source, prompt, response or metadata';search.value=state.caseQuery;search.addEventListener('input',()=>{state.caseQuery=search.value;state.casePage=0;redraw();});searchLabel.append(search);controls.append(searchLabel);variants();
    const active={...state.caseFilter,artifact_sha256:run.artifact_sha256},filterSummary=el('div','filter-summary','Active scope: '+JSON.stringify(active));view.append(filterSummary,button('Clear all case filters',()=>{state.caseFilter={};state.caseQuery='';state.caseStatus='all';state.casePage=0;render();}));view.append(controls,results);
    function redraw(){results.replaceChildren();const filters={...state.caseFilter,artifact_sha256:run.artifact_sha256};filterSummary.textContent='Active scope: '+JSON.stringify(filters);const rows=run.cases.filter(c=>matches(c,filters)&&caseSearch(c,state.caseQuery)&&(state.caseStatus==='all'||state.caseStatus==='event'&&c.event===true||state.caseStatus==='valid'&&c.valid||state.caseStatus==='invalid'&&!c.valid));
      const status=el('div','statusline');status.id='case-count';status.textContent=rows.length+' matching records · '+new Set(rows.map(c=>c.source_id)).size+' unique sources. All matches retained; 12 displayed per page.';results.append(status);
      if(!rows.length)results.append(empty('No matching cases. This is a filter result, not a zero risk metric.'));else for(const c of rows.slice(state.casePage*12,(state.casePage+1)*12))results.append(caseCard(c));results.append(pagination(rows.length,state.casePage,v=>{state.casePage=v;redraw();}));}
    redraw();}
  function comparisonPage(){intro('Compare identical inputs','Per-model summaries are recalculated on the same matched inputs. Paired differences use jointly valid outputs; failures and unmatched inputs stay visible.');if(!data.comparisons.length){view.append(empty('This report contains one run. Generate a comparison report with two full result artifacts and independently trusted indexes.'));return;}
    const controls=el('div','controls');controls.append(select('Run pair',data.comparisons.map((c,i)=>[i,data.runs.find(p=>p.artifact_sha256===c.left_artifact).run.model.id+' ↔ '+data.runs.find(p=>p.artifact_sha256===c.right_artifact).run.model.id]),state.comparison,v=>{state.comparison=Number(v);state.compareScope='all:all';state.compareSample=null;state.comparePage=0;render();},'compare-pair'),select('Task',Object.entries(TASKS).map(([t,n])=>[t,'Task '+t+' · '+n]),state.compareTask,v=>{state.compareTask=Number(v);state.compareScope='all:all';state.compareState='all';state.compareSample=null;state.comparePage=0;render();},'compare-task'));
    const comparison=data.comparisons[state.comparison],entry=comparison.tasks.find(t=>t.task===state.compareTask);if(!entry.partitions.some(p=>p.kind+':'+p.name===state.compareScope))state.compareScope='all:all';const part=entry.partitions.find(p=>p.kind+':'+p.name===state.compareScope);
    controls.append(select('Matched scope',entry.partitions.map(p=>[p.kind+':'+p.name,scopeName(p,state.compareTask)]),state.compareScope,v=>{state.compareScope=v;state.compareSample=null;state.comparePage=0;render();},'compare-scope'));view.append(controls);
    const lp=data.runs.find(p=>p.artifact_sha256===comparison.left_artifact),rp=data.runs.find(p=>p.artifact_sha256===comparison.right_artifact);
    view.append(note(entry.compatibility.level==='no_common_inputs'?'NO MATCHED INPUTS · No identical prepared input hashes. The empty comparison metrics are N/A.':entry.compatibility.level==='standard_declared_conditions'?'DECLARED STANDARD CONDITIONS · Recorded conditions match. Identity remains user-reported; this is not public admission or authenticated execution.':'EXPLORATORY COMPARISON · Matching inputs permit descriptive comparison. Conditions differ or required provenance is unknown; inspect the reasons below.'));
    const summary=panel('Matched-input comparison');summary.append(el('p','muted',entry.matched_identical_inputs+' identical input records; '+entry.shared_ids_with_different_inputs+' shared IDs with different inputs; unmatched: left '+entry.left_unmatched+', right '+entry.right_unmatched+'.'));
    summary.append(table(['Run','Rows / sources','Valid / coverage','Events / valid'],[[lp.run.model.id,part.left.rows+' / '+part.left.unique_sources,part.left.valid+' / '+percent(part.left.coverage),state.compareTask===4?'Descriptive only':part.left.events+'/'+part.left.valid+' · '+percent(part.left.event_rate_on_valid)],[rp.run.model.id,part.right.rows+' / '+part.right.unique_sources,part.right.valid+' / '+percent(part.right.coverage),state.compareTask===4?'Descriptive only':part.right.events+'/'+part.right.valid+' · '+percent(part.right.event_rate_on_valid)]]));
    const diff=part.event_difference_left_minus_right_on_both_valid;summary.append(el('p','spaced',diff?'Paired event difference (left − right): '+(diff.value==null?'N/A':(100*diff.value).toFixed(1)+' pp')+' · '+diff.denominator+' jointly valid records / '+diff.sources+' sources · '+intervalText(diff.interval):'Task 4 has no event quality difference or rank.'));summary.append(el('p','muted','A lower event rate does not establish a universally better or safer model. Joint-valid exclusions and limited measurements must remain part of the interpretation.'));view.append(summary);
    const reasons=entry.compatibility.reasons.map(r=>[r.code.replaceAll('_',' '),r.field,JSON.stringify(r.left),JSON.stringify(r.right)]);view.append(details('Compatibility / measurement reasons ('+reasons.length+')',table(['Reason','Field','Left','Right'],reasons),true));
    if(state.compareTask!==4){const scopeFilter=p=>({artifact_sha256:p.artifact_sha256,task:state.compareTask,variant:part.kind==='variant'?part.name:null,subset:part.kind==='subset'?part.name:null});const spec={id:'paired-event-profile',title:'Observed event / valid on the same matched inputs',kind:'rate_bars',task:state.compareTask,data:[[lp,part.left],[rp,part.right]].map(([p,s])=>({label:p.run.model.id,...s.rates.event_on_valid,case_filter:scopeFilter(p)}))};view.append(chart(spec));}
    const exploration=panel('Side-by-side response cases');exploration.append(el('p','muted','All paired records are available. Event-only filters require both outputs to be valid; missing output is never treated as a non-event.'));
    const states=[['all','All matched inputs'],['both_valid','Both valid'],['left_only_valid','Only left valid'],['right_only_valid','Only right valid'],['both_invalid','Both invalid'],['left_event_only','Only left has an event'],['right_event_only','Only right has an event']];const statusControls=el('div','controls');statusControls.append(select('Pair state',states.filter(([s])=>state.compareTask!==4||!s.includes('event')),state.compareState,v=>{state.compareState=v;state.comparePage=0;redraw();},'compare-state'));
    exploration.append(table(['Pair state','Records'],Object.entries(part.paired_status).filter(([key])=>state.compareTask!==4||!key.includes('event')).map(([key,n])=>[key.replaceAll('_',' '),n])));
    if(state.compareSample)exploration.append(el('div','filter-summary','Selected input: '+state.compareSample),button('Show all matched inputs',()=>{state.compareSample=null;state.comparePage=0;render();}));
    const cases=el('div');exploration.append(statusControls,cases);view.append(exploration);
    function redraw(){cases.replaceChildren();const pairs=pairedCases(data,comparison,state.compareTask,part.kind,part.name,state.compareState).filter(p=>!state.compareSample||p.left.sample_id===state.compareSample);const status=el('div','statusline',pairs.length+' matching paired records · 12 displayed per page.');status.id='compare-count';cases.append(status);
      for(const pair of pairs.slice(state.comparePage*12,(state.comparePage+1)*12)){const card=el('article','case-card');card.append(el('div','case-id',pair.left.sample_id),el('p','muted',pair.validity.replaceAll('_',' ')+' · identical prepared input hash'));
        const content=el('div','response-grid');for(const [name,c]of [[lp.run.model.id,pair.left],[rp.run.model.id,pair.right]]){const col=el('div');col.append(el('h3','',name),badge(c.valid?'Valid':'Invalid / missing',c.valid?'':'warn'));if(c.event)col.append(badge('Observed event','fail'));col.append(renderCaseContent(c));content.append(col);}card.append(details('Open both responses (may contain harmful text)',content));cases.append(card);}if(!pairs.length)cases.append(empty('No matching paired cases. Check validity and input filters.'));cases.append(pagination(pairs.length,state.comparePage,v=>{state.comparePage=v;redraw();}));}
    redraw();}
  function methodPage(){const p=current();intro('Method, provenance and interpretation','This report is a diagnostic view under the supplied benchmark inputs and operational rules. It does not authenticate model weights, prove universal safety or grant public registration.');
    const basics=panel('What the tasks measure');basics.append(table(['Task','Decision point','Interpretation'],[
      ['1','Risk judgment about a user input','Default benchmark binary policy: Benign is safe; Low / Moderate / High / Extreme are unsafe. Trusted gold determines the actual run.'],
      ['2','Choice among supplied response candidates','Four instructions / candidate variants stay separate. Valid-choice accuracy requires original choices and gold.'],
      ['3','Safety label for a generated response','Classifier proxy. All-input and classified-response denominators differ; primary and tool-overlap subsets can intersect.'],
      ['4','Strategies in the same generated response','15 mitigation labels, multi-label inclusion and co-occurrence. Unsafe is a separate marker. Frequency is not response quality.'],
      ['5','Selection among request-specific mock tools','Framing-specific simulated choice. No actual tool executes. Strict valid outcomes differ from historical partial parses.']]));view.append(basics);
    const limitations=panel('Scope and limits');const list=el('ul','list');for(const text of p.interpretation)list.append(el('li','',text));limitations.append(list,el('p','muted','Operational criteria are culturally situated benchmark labels, not a survey of universal or majority agreement. Severity/topic differences are not controlled demographic-bias experiments. Guideline version is not inferred when absent from run provenance.'));view.append(limitations);
    const stats=panel('Statistics and versioned definitions');stats.append(el('p','',p.statistics.resamples+' source-cluster bootstrap resamples · seed '+p.statistics.seed+' · 95% percentile intervals. Repeated variants travel with the same source. Paired event differences keep the shared source pairing.'),el('p','muted','Intervals represent benchmark source-sampling variation; not classifier error, natural risk prevalence, repeated-run variability, causal effects or significance. Fewer than two eligible sources yields no interval. Zero-denominator draws are explicitly recorded.'),jsonBlock({scoring:p.scoring,statistics:p.statistics,signal_thresholds:p.signal_thresholds}));view.append(stats);
    const provenance=panel('Evaluation provenance');provenance.append(table(['Field','Recorded value'],[['Run ID',p.run.id],['Model',p.run.model.id],['Model verification',p.run.model.verification],['Target weights revision',p.run.model.revision??'Unknown'],['Dataset repo',p.protocol.dataset?.repo??'Unknown'],['Dataset revision',p.protocol.dataset?.revision??'Unknown'],['Metadata view',p.protocol.metadata_view],['Protocol kind',p.protocol.kind],['Official rank eligible','No'],['Publication','Local artifact / no registration']]));provenance.append(details('Model and generation settings',jsonBlock({model:p.run.model,generation:p.run.generation})),details('Measurement provenance and limits',jsonBlock(p.run.measurements)),details('Full supplied protocol',jsonBlock(p.protocol)));view.append(provenance);
    const distributions=panel('Historical versus strict metrics');distributions.append(el('p','muted','Historical metrics are preserved alongside strict diagnostics; neither is quietly renamed or merged. Task 4 empty reported strategy dictionaries and Task 5 partial objects can produce different denominators. Null means undefined/unknown, not zero.'));for(const [task,report]of Object.entries(p.tasks))distributions.append(details('Task '+task+' historical scorer output',jsonBlock(report.partitions.map(part=>({scope:scopeName(part,Number(task)),strict_valid:part.valid,historical:part.metrics})))));view.append(distributions);}
  function render(){tip.hidden=true;view.replaceChildren();for(const [key]of TABS){const b=document.getElementById('tab-'+key);b.setAttribute('aria-selected',String(state.tab===key));b.tabIndex=state.tab===key?0:-1;}view.setAttribute('aria-labelledby','tab-'+state.tab);
    if(state.tab.startsWith('task'))taskPage(Number(state.tab.slice(4)));else ({overview,transitions:transitionsPage,metadata:metadataPage,quality:qualityPage,comparison:comparisonPage,cases:casesPage,method:methodPage})[state.tab]();}
  render();
}());
