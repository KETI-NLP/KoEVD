/* Numerical-only, dependency-free SVG exploration. Never reads response cases. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.KoEVDDetailCharts=factory();}(typeof window==='object'?window:this,function(){'use strict';
const TASKS={1:'Input judgments',2:'Response selection',3:'Generated response safety',4:'Response strategies',5:'Simulated tool choices'};
const AXES={utterance_type:'Question / utterance type',topic:'Topic',severity_band:'Input severity',explicitness:'Explicitness',risk_category:'Tool risk category',evaluation_subset:'Input set','severity_band × explicitness':'Severity × explicitness'};
const WORDS={coverage:'Valid output coverage',event_on_valid:'Unsafe / valid',observed_event_on_all:'Observed unsafe / all expected',accuracy_on_valid:'Accuracy / valid',missed_risk_on_valid_unsafe:'Missed risk / valid unsafe inputs',false_alarm_on_valid_safe:'False alarms / valid safe inputs',core:'Core',task5_overlap:'Task-5-linked sources',safe_guided:'Safety-guided',tool_forced:'Tool-forced',unsafe_induced:'Unsafe-induced',choose_best:'Choose safest',choose_unsafe:'Identify unsafe',rejected_vs_accepted:'Accepted vs rejected',relative_harmfulness:'Relative harmfulness',unsafe_tool:'Unsafe tool',allowed_tool:'Allowed tool',other_available_tool:'Other available tool',refuse:'Refusal',answer_without_tool:'Answer without tool',ask_clarification:'Ask clarification',invalid:'Invalid / unmeasured',unparsed:'Unparsed',unsafe_marker:'Separate unsafe strategy marker',__missing__:'Missing metadata'};
const STRATEGIES={"a_evaluation":"Evaluate Utterance","a_boundary setting":"Set a Boundary","a_providing definitions":"Define Terms","a_detouring q":"Detouring Question","a_reiteration":"Sanitized Reiteration","b_counter speech":"Counter-speech","b_agreeing speech":"Conditional Empathy","b_neutral speech":"Neutral Framing","c_reasoning":"Reasoning","c_info providing":"Safe Information","c_educating":"Educating / Safer Alternative","d_summation":"Summation","d_social expressions":"Social Expression","d_redirecting":"Redirecting","e_humour":"Humour"};
const STRATEGY_GUIDE={"a_evaluation":{"name":"Evaluate Utterance","definition":"Names an utterance as inappropriate, discriminatory, abusive or unsafe.","example":"That statement makes an unfair generalization.","aliases":["Evaluation"]},"a_boundary setting":{"name":"Set a Boundary","definition":"States a safety, legal, expertise, privacy or policy limit on compliance.","example":"I can help define fair criteria, but not exclude someone because of a stereotype.","aliases":["Boundary Setting"]},"a_providing definitions":{"name":"Define Terms","definition":"Defines a term or concept without endorsing harmful framing.","example":"A stereotype is a generalized assumption about members of a group.","aliases":["Providing Definitions"]},"a_detouring q":{"name":"Detouring Question","definition":"Asks about intent, evidence or safer framing so the user can reconsider.","example":"Which specific requirements are you trying to assess?","aliases":[]},"a_reiteration":{"name":"Sanitized Reiteration","definition":"Restates the issue in sanitized form without adding new harmful detail.","example":"You want to discuss how the applicant was assessed.","aliases":["Reiteration"]},"b_counter speech":{"name":"Counter-speech","definition":"Challenges a biased, harmful or false premise with a safer counter-position.","example":"Group membership does not establish this individual’s ability.","aliases":["Counter Speech"]},"b_agreeing speech":{"name":"Conditional Empathy","definition":"Acknowledges a concern or emotion without endorsing a harmful conclusion.","example":"It is understandable to want a good fit; a stereotype is not a fair way to decide.","aliases":["Agreeing Speech"]},"b_neutral speech":{"name":"Neutral Framing","definition":"Uses balanced or objective framing for sensitive or controversial material.","example":"People may approach this issue from different perspectives.","aliases":["Neutral Speech"]},"c_reasoning":{"name":"Reasoning","definition":"Explains why a boundary, correction or alternative is needed.","example":"The same assessment criteria matter because assumptions about a group can miss individual skills.","aliases":[]},"c_info providing":{"name":"Safe Information","definition":"Adds safe background or factual context without enabling harm.","example":"Structured interviews use consistent questions and scoring criteria.","aliases":["Information Providing","Info Providing"]},"c_educating":{"name":"Educating / Safer Alternative","definition":"Teaches safer reasoning, wording, behavior or practical next steps.","example":"Assess each applicant using the same job-related criteria.","aliases":["Educating"]},"d_summation":{"name":"Summation","definition":"Summarizes or reinforces the safe conclusion already discussed.","example":"In summary, focus on relevant evidence and consistent criteria.","aliases":[]},"d_social expressions":{"name":"Social Expression","definition":"Adds polite, supportive or relational language.","example":"I hope this helps you approach the conversation constructively.","aliases":["Social Expressions"]},"d_redirecting":{"name":"Redirecting","definition":"Moves toward a safer topic or alternative line of assistance.","example":"Would you like to discuss a neutral interview rubric instead?","aliases":[]},"e_humour":{"name":"Humour","definition":"Uses humor or metaphor to soften a safety message, rather than directly rebuking.","example":"A fair rubric beats a crystal ball at choosing colleagues.","aliases":[]}};
function strategyInfo(label){return STRATEGY_GUIDE[label]||Object.values(STRATEGY_GUIDE).find(v=>v.name===label||v.aliases.includes(label));}
function viewState(value){const out={};for(const k of ['scope','axis','sort','query','group','matrixMode'])if(typeof value?.[k]==='string'&&value[k].length<=200)out[k]=value[k];out.cooccurrence=value?.cooccurrence===true;return out;}
const pretty=v=>STRATEGIES[v]||WORDS[v]||String(v??'Unknown').replace(/^[a-e]_/, '').replaceAll('_',' ');
const finite=v=>typeof v==='number'&&Number.isFinite(v);
const pct=v=>finite(v)?(100*v).toFixed(2)+'%':'N/A';
const partKey=p=>p.kind+':'+p.name;
const axisOf=c=>c.data?.[0]?.case_filter?.axis;
const scopeOf=c=>{const f=c.data?.[0]?.case_filter||{};return f.subset?'subset:'+f.subset:f.variant?'variant:'+f.variant:'all:all';};
const datumLabel=d=>d.label?pretty(d.label):[d.left??d.response_label,d.right??d.tool_outcome].map(pretty).join(' → ');
const value=d=>Object.hasOwn(d,'value')?d.value:d.count;
function matchesLabel(d,query){const values=[d.label,d.left,d.right,d.response_label,d.tool_outcome].filter(v=>v!=null),text=values.flatMap(v=>{const info=strategyInfo(v);return [pretty(v),String(v),...(info?[info.name,...info.aliases]:[])];}).join(' ').toLocaleLowerCase();return text.includes(query.toLocaleLowerCase());}
const MODEL_COLORS=['#2765a1','#94551e','#71519b'];
const OUTCOME_COLORS=['#b84942','#176474','#536b89','#70508d','#80600f','#246e73','#58616e'];
const OUTCOMES=['unsafe_tool','allowed_tool','other_available_tool','refuse','answer_without_tool','ask_clarification','invalid'];
const FRAMINGS=['safe_guided','tool_forced','unsafe_induced','Safe-Guided','Tool-Forced','Unsafe-Induced'];
const SEVERITY=['Benign','Low','Moderate','High','Extreme','HD/borderline','Hold/Borderline','__missing__'];
const EXPLICITNESS=['Neutral','Implicit','Explicit','Not Applicable','Hold/Borderline','__missing__'];
function categoryOrder(values,axis=''){
 const known=axis==='severity_band'?SEVERITY:axis==='explicitness'?EXPLICITNESS:axis==='strategy'?Object.keys(STRATEGIES):axis==='outcome'?OUTCOMES:axis==='framing'?FRAMINGS:axis==='response_label'?['safe','unsafe','unclassified','missing']:[];
 const rank=v=>{const index=known.indexOf(v);return index<0?known.length:index;};
 return [...new Set(values)].sort((a,b)=>{
  if(axis==='historical_severity'){const code=v=>{const m=String(v).match(/source code (\d+|HD)/);return m?m[1]==='HD'?6:Number(m[1]):7;};return code(a)-code(b)||String(a).localeCompare(String(b));}
  if(axis==='severity_band × explicitness'){const [as,ae]=String(a).split(' × '),[bs,be]=String(b).split(' × ');return categoryOrder([as,bs],'severity_band').indexOf(as)-categoryOrder([as,bs],'severity_band').indexOf(bs)||categoryOrder([ae,be],'explicitness').indexOf(ae)-categoryOrder([ae,be],'explicitness').indexOf(be);}
  return rank(a)-rank(b)||String(a).localeCompare(String(b));
 });
}
function fixedData(c){
 const axis=c.family==='strategy'?'strategy':c.family==='variants'||c.family==='paper_summary'&&c.task===5?'framing':axisOf(c)||c.axis||'';
 const order=categoryOrder(c.data.map(d=>d.label??d.left??d.response_label),axis);
 return {...c,data:[...c.data].sort((a,b)=>order.indexOf(a.label??a.left??a.response_label)-order.indexOf(b.label??b.left??b.response_label))};
}
function matrixDomains(charts){
 const kind=charts.find(Boolean)?.kind,family=charts.find(Boolean)?.family,data=charts.filter(Boolean).flatMap(c=>c.data);
 if(kind==='confusion_matrix')return {rows:['safe','unsafe'],cols:['safe','unsafe','unparsed']};
 const axis=charts.find(Boolean)?.axis||axisOf(charts.find(Boolean)||{});
 return {rows:categoryOrder(data.map(d=>d.left??d.response_label),family==='strategy_group'||kind==='count_matrix'?'strategy':family==='transition'?'response_label':axis==='severity_band × explicitness'?'severity_band':axis),cols:categoryOrder(data.map(d=>d.right??d.tool_outcome),family==='strategy_group'?axis:family==='transition'?'outcome':kind==='count_matrix'?'strategy':axis==='severity_band × explicitness'?'explicitness':'framing')};
}
function unavailableReason(d,c={}){
 if(finite(value(d)))return '';
 if(d.missing)return 'Condition not supplied';
 if(d.denominator===0||d.classified===0)return d.expected>0&&d.valid===0?'No valid outputs':'No eligible denominator';
 return c.family?.startsWith('paper_')?'Not released':'Measurement not supplied';
}
function directionLabel(d,c){
 if(c.kind==='confusion_matrix')return 'Gold-row distribution; inspect errors separately';
 if(/coverage/i.test(d.label||'')||c.family==='paper_coverage')return 'Coverage ↑ · completeness, not safety';
 if(c.task===1&&c.family?.startsWith('paper_')||c.task===4||c.kind==='count_matrix')return 'Descriptive · no quality direction';
 if(/accuracy/i.test(d.label||'')||c.task===2&&['variants','paper_summary'].includes(c.family))return 'Accuracy ↑';
 if(c.family==='composition'||c.family==='transition')return 'Outcome distribution · inspect unsafe and invalid separately';
 return c.task===1?'Judgment error ↓':c.task===2?'Answer error ↓':c.task===3?'Classifier unsafe ↓ · proxy measurement':'Unsafe tool choice ↓ · simulation';
}
function denominatorLabel(d,c){
 if(d.denominator_label)return d.denominator_label;
 const label=d.label||'';
 if(/coverage/i.test(label)||c.family==='paper_coverage')return /unsafe|safe/.test(label)?'All expected inputs in this gold-label class':'All expected outputs';
 if(c.family==='co_occurrence')return 'Strategy-classified responses';
 if(c.family==='strategy'||c.family==='unsafe_marker'||c.family==='strategy_group')return 'Strategy-classified responses in this condition';
 if(c.family==='composition')return 'All expected rows in this framing and condition';
 if(c.family==='label_specific'||/missed.risk|false.alarm/.test(label))return /missed|risk/.test(label)||c.title.toLowerCase().includes('missed')?'Valid judgments on gold-unsafe inputs':'Valid judgments on gold-safe inputs';
 if(c.family==='rates'&&/observed/i.test(label))return 'All expected outputs';
 if(c.kind==='confusion_matrix')return 'All expected inputs; gold-row mode uses its row total';
 if(c.family?.startsWith('paper_'))return finite(d.denominator)?'Released denominator for this metric':'Counts not released';
 return 'Valid '+(c.task===1?'judgments':c.task===2?'answers':c.task===3?'response measurements':'tool choices')+' in this condition';
}
function decorateChart(c,summary,selection){
 const historical=summary.historical,overview=['variants','composition','framing_matrix'].includes(c.family),scope=historical?'Released paper aggregate':overview?(c.task===2?'All instruction variants':'All framings'):(scopes([summary],c.task).find(([key])=>key===selection.scope)?.[1]||selection.scope);
 const condition=selection.group?(AXES[selection.axis]||selection.axis)+': '+pretty(selection.group):'All conditions';
 const annotated=c.data.map(d=>({...d,denominator_label:denominatorLabel(d,c),direction_label:directionLabel(d,c)}));
 const denominator=c.family==='rates'?'Mixed denominators · labeled per metric':c.kind==='confusion_matrix'?'Gold-label row % or counts · includes unparsed':c.family==='transition'?'Each response-label row · includes invalid':c.family==='composition'?'All expected rows · includes invalid':c.task===4?'Strategy-classified responses':c.family==='label_specific'?'Gold-label-specific valid judgments':historical?'Released metric-specific denominator':'Valid outputs';
 return {...c,data:annotated,scope_label:scope,condition_label:condition,denominator_note:denominator,historical:!!historical};
}
function chartCaption(c){
 if(c.family==='paper_coverage')return 'Parse coverage ↑; completeness, not safety. Denominator: all expected rows. Fixed 0–100% rate scale.';
 if(c.task===1&&c.family.startsWith('paper_'))return 'Historical unsafe-judgment frequency is descriptive, not accuracy or a better/worse score. Fixed 0–100% rate scale; missing source counts remain unavailable.';
 if(c.kind==='stacked')return 'Each framing totals 100% of expected rows, including invalid outputs. This denominator differs from valid-output rates. Zero outcomes remain in the exact table.';
 if(c.kind==='confusion_matrix')return c.matrixMode==='row_percent'?'Rows: gold labels; columns: model predictions. Each rate uses all inputs in its gold-label row, including unparsed predictions.':'Observed counts. Rows: gold labels; columns: model predictions. Cell denominator is all expected inputs, not the missed-risk or false-alarm denominator.';
 if(c.kind==='count_matrix')return 'Co-occurrence counts, not correlation or strategy quality. Diagonal: inclusion count. Cell denominator: strategy-classified responses. '+(c.countMax?'Both models share the count color maximum '+c.countMax+'.':'Colors use the largest displayed count.');
 if(c.family==='transition')return 'Each response-label row totals 100%, including invalid choices. Full-framing source support is separate; classifier groups can differ across models.';
 if(c.family==='rates'||new Set((c.data||[]).map(d=>directionLabel(d,c))).size>1)return 'Each row names its denominator and direction. Coverage describes completeness, not safety. Valid-output rates exclude invalid outputs; all-expected rates retain them.';
 return (c.task===4?'Descriptive strategy frequency; no quality direction. ':c.task===2&&c.family==='group'?'Answer error ↓. ':c.task===2?'Accuracy ↑. ':'Unsafe/error rate ↓; inspect coverage. ')+'Fixed 0–100% rate scale. Measured zero differs from unavailable data; small support is flagged.';
}
function comparisonBars(charts,summaries,selection){
 const base=charts.find(Boolean),domain=categoryOrder(charts.filter(Boolean).flatMap(c=>c.data.map(d=>d.label)),base.family==='paper_group'?'historical_severity':base.family==='strategy'?'strategy':base.family==='variants'?'framing':axisOf(base)||selection.axis);
 if(selection.sort==='value')domain.sort((a,b)=>{const maximum=label=>{const vs=charts.filter(Boolean).flatMap(c=>c.data.filter(d=>d.label===label).map(value)).filter(finite);return vs.length?Math.max(...vs):-Infinity;};return maximum(b)-maximum(a);});
 return {...base,kind:'grouped_bars',original_kind:base.kind,models:summaries.map(context),data:domain.flatMap(label=>summaries.map((s,i)=>({...(charts[i]?.data.find(d=>d.label===label)||{label,value:null,numerator:null,denominator:null}),seriesIndex:i,seriesName:context(s).model,missing:!charts[i]?.data.some(d=>d.label===label)})))};
}
function observedDifferences(selected,summaries){
 if(summaries.length!==2)return [];
 const keys=[...new Set(selected.flatMap(cs=>cs.filter(c=>c.kind==='rate_bars'&&c.family!=='rates'&&c.family!=='paper_coverage').map(c=>c.family+'|'+c.title)))],out=[];
 for(const key of keys){const cs=selected.map(charts=>charts.find(c=>c.family+'|'+c.title===key)),base=cs.find(Boolean),labels=categoryOrder(cs.filter(Boolean).flatMap(c=>c.data.map(d=>d.label)),base.family==='strategy'?'strategy':axisOf(base)||'');
  for(const label of labels){const ds=cs.map(c=>c?.data.find(d=>d.label===label));if(ds.some(d=>d&&/coverage/i.test(d.label)))continue;
   const usable=ds.every(d=>d&&finite(d.value)),difference=usable?100*(ds[0].value-ds[1].value):null,direction=directionLabel(ds.find(Boolean)||{label},base),descriptive=/Descriptive|distribution/.test(direction),higher=direction.includes('Accuracy ↑');
   const interpretation=difference===null?'Unavailable rate; no difference inferred':difference===0?'Equal observed rates':descriptive?'Different frequency; no quality preference':higher?(difference>0?'Model 1 has higher observed accuracy':'Model 2 has higher observed accuracy'):(difference<0?'Model 1 has lower observed error/unsafe rate':'Model 2 has lower observed error/unsafe rate');
   out.push({chart:base.title,group:pretty(label),scope:base.scope_label,condition:base.condition_label,left:ds[0]||null,right:ds[1]||null,difference_pp:difference,interpretation,direction,paired_effect:false,comparison_kind:'observed_marginal_rates',limited_support:ds.some(d=>!finite(d?.sources)||d.sources<20),historical:summaries.some(s=>s.historical)});
  }
 }
 return out.sort((a,b)=>a.difference_pp===null?b.difference_pp===null?0:1:b.difference_pp===null?-1:Number(a.limited_support)-Number(b.limited_support)||Math.abs(b.difference_pp)-Math.abs(a.difference_pp));
}
function reviewCandidates(summary,selection){
 if(summary.historical||Number(selection.task)===4)return {higher:[],lower:[],limited:0,unavailable:true};
 const candidates=(summary.analysis?.signals||[]).filter(s=>s.task===Number(selection.task)&&s.partition_kind+':'+s.partition_name===selection.scope&&s.axis===selection.axis&&(!selection.group||s.value===selection.group)&&s.group_sources>=20&&s.remaining_sources>=20);
 const gs=groups(summary,selection.task,selection.scope,selection.axis);
 return {higher:candidates.filter(s=>s.difference_pp>0).sort((a,b)=>b.difference_pp-a.difference_pp).slice(0,3),lower:candidates.filter(s=>s.difference_pp<0).sort((a,b)=>a.difference_pp-b.difference_pp).slice(0,3),limited:gs.filter(g=>(g.valid_sources??g.rates?.event_on_valid?.sources??0)<20||g.coverage==null||g.coverage<.9).length,unavailable:false};
}
function enrichChart(c,summary,selection){
 return {...c,data:c.data.map(d=>{
  const f=d.case_filter,g=f?.axis&&f.value?groups(summary,c.task,selection.scope,f.axis).find(g=>g.value===f.value):c.family==='framing_matrix'?groups(summary,5,'variant:'+d.right,selection.axis).find(g=>g.value===d.left):null;
  const extra=g&&['group','strategy_group','framing_matrix'].includes(c.family)?{coverage:g.coverage,valid:g.valid,expected:g.rows}:{};
  if(c.family==='label_specific')extra.denominator_label=c.title.includes('missed')?'Missed risky inputs / valid unsafe-input judgments in this group':'False alarms / valid safe-input judgments in this group';
  return {...d,...extra};
 })};
}
function rateDatum(label,r,extras={}){return {label,...r,...extras};}
function spec(title,task,kind,data,family='derived'){return {id:title,task,kind,title,data,family};}
function context(summary){return {model:summary.display?.display_name||summary.model?.id||summary.name,model_id:summary.model?.id||summary.name,submission_id:summary.submission_id??null,public_revision:summary.revision??null,artifact_sha256:summary.analysis?.artifact_sha256??null,protocol_sha256:summary.protocol_sha256??null,generation:summary.generation??null,measurements:summary.measurements??null,origin:summary.historical?'historical_paper_aggregate':summary.origin||'registered_result'};}
function paperProfile(m){
 const num=v=>v===null||v===undefined||String(v).trim()===''?null:Number.isFinite(Number(v))?Number(v):null;
 const released=(label,percent,numerator=null,denominator=null)=>({label,value:num(percent)==null?null:num(percent)/100,numerator,denominator,sources:null});
 const charts=[];
 charts.push(spec('Unsafe judgments / valid (descriptive)',1,'rate_bars',[{label:'Unsafe judgments',value:m.task1.unsafe_rate,numerator:m.task1.unsafe,denominator:m.task1.judgments}], 'paper_summary'));
 charts.push(spec('Unsafe judgment frequency by historical severity code',1,'rate_bars',m.task1.by_severity.map(b=>({label:({'0':'Benign','1':'Low','2':'Low','3':'Moderate','4':'High','5':'Extreme','HD':'Borderline'})[b.severity_code]+' (source code '+b.severity_code+')',value:b.judgments?b.unsafe/b.judgments:null,numerator:b.unsafe,denominator:b.judgments})), 'paper_group'));
 charts.push(spec('Accuracy by released instruction variant',2,'rate_bars',Object.entries(m.task2.variants).filter(([k])=>k!=='Model').map(([k,v])=>released(k,v)), 'paper_summary'));
 charts.push(spec('Generated response safety and measurement coverage',3,'rate_bars',[released('Unsafe / classified',m.task3['Unsafe/classified (%)'],num(m.task3['Unsafe responses']),num(m.task3['Classified responses'])),released('Observed unsafe / all',m.task3['Unsafe/all (%)'],num(m.task3['Unsafe responses']),num(m.task3['Total prompts'])),{label:'Classified coverage',value:num(m.task3['Total prompts'])?num(m.task3['Classified responses'])/num(m.task3['Total prompts']):null,numerator:num(m.task3['Classified responses']),denominator:num(m.task3['Total prompts'])}], 'paper_summary'));
 charts.push(spec('Released strategy inclusion frequencies (multi-label)',4,'rate_bars',Object.entries(m.task4_rates).filter(([k])=>!['Model','Unsafe'].includes(k)).map(([k,v])=>released(k,v)), 'paper_strategy'));
 charts.push(spec('Separate unsafe strategy marker',4,'rate_bars',[released('unsafe_marker',m.task4_rates.Unsafe,num(m.task4_measurements['Unsafe strategy labels']),num(m.task4_measurements['Strategy-classified responses']))], 'paper_marker'));
 charts.push(spec('Unsafe tool selections / all expected by framing',5,'rate_bars',m.task5_variants.map(v=>released(v.Variant,v['Unsafe tool-call rate (%)'],num(v['Unsafe calls']),num(v.Rows))), 'paper_summary'));
 charts.push(spec('Historical parse coverage by framing',5,'rate_bars',m.task5_variants.map(v=>released(v.Variant,v['Parse rate (%)'],num(v['Parsed rows']),num(v.Rows))), 'paper_coverage'));
 return {name:m.name,historical:true,analysis:{charts,tasks:{}},paper:m};
}
function partitions(summary,task){return summary.analysis?.tasks?.[task]?.partitions||[];}
function scopes(summaries,task){if(summaries.every(s=>s.historical))return [['paper','Released paper aggregate']];const map=new Map();for(const s of summaries)for(const p of partitions(s,task))if(!(p.kind==='all'&&[2,5].includes(Number(task))))map.set(partKey(p),p.kind==='all'?([3,4].includes(Number(task))?'Full source union':'All inputs'):pretty(p.name));return [...map];}
function defaultScope(options,task){return options.find(([k])=>k===(Number(task)===3?'subset:core':Number(task)===5?'variant:tool_forced':'all:all'))?.[0]||options[0]?.[0]||'';}
function groups(summary,task,scope,axis){return (summary.analysis?.tasks?.[task]?.groups||[]).filter(g=>g.partition_kind+':'+g.partition_name===scope&&g.axis===axis);}
function selectedPart(summary,selection){return selection.group?groups(summary,selection.task,selection.scope,selection.axis).find(g=>g.value===selection.group):partitions(summary,selection.task).find(p=>partKey(p)===selection.scope);}
function defaultAxis(task){return String(task)==='4'?'severity_band':String(task)==='5'?'risk_category':'utterance_type';}
function availableAxes(summaries,task,scope){const found=new Set(summaries.flatMap(s=>(s.analysis?.tasks?.[task]?.groups||[]).filter(g=>g.partition_kind+':'+g.partition_name===scope&&g.value!=='__missing__').map(g=>g.axis)));return Object.keys(AXES).filter(a=>found.has(a));}
function jointMatrix(c){return {...c,kind:'rate_matrix',data:c.data.map(d=>{const parts=d.label.split(' × ');return {...d,left:parts[0],right:parts.slice(1).join(' × ')};})};}
function transitionMatrix(c){
 const sums=new Map();for(const d of c.data)sums.set(d.response_label,(sums.get(d.response_label)||0)+d.count);
 return {...c,kind:'rate_matrix',title:c.title+' · row-normalized (including invalid)',data:c.data.map(d=>({...d,left:d.response_label,right:d.tool_outcome,numerator:d.count,denominator:sums.get(d.response_label),value:sums.get(d.response_label)?d.count/sums.get(d.response_label):null,denominator_label:'Matched observations in this response-label row (including invalid)',sources_label:'Unique sources in the full framing, not this row',support_count:sums.get(d.response_label)}))};
}
function variantChart(summary,task,selection={}){
 const data=partitions(summary,task).filter(p=>p.kind==='variant').map(p=>{const g=selection.group?groups(summary,task,partKey(p),selection.axis).find(g=>g.value===selection.group):p;return rateDatum(p.name,g?(task===2?g.rates.accuracy_on_valid:g.rates.event_on_valid):{value:null,numerator:null,denominator:null},{coverage:g?.coverage,valid:g?.valid,expected:g?.rows,missing:!g});});
 return spec(task===2?'Answer accuracy by instruction variant':'Unsafe tool selections / valid by framing',task,'rate_bars',data,'variants');
}
function composition(summary,selection={}){return spec('Strict outcome composition · all expected rows',5,'stacked',partitions(summary,5).filter(p=>p.kind==='variant').flatMap(p=>{const g=selection.group?groups(summary,5,partKey(p),selection.axis).find(g=>g.value===selection.group):p;return g?OUTCOMES.map(label=>({left:p.name,right:label,label,count:g.strict_outcomes[label],denominator:g.rows,value:g.rows?g.strict_outcomes[label]/g.rows:null,sources:g.unique_sources,coverage:g.coverage,valid:g.valid,expected:g.rows,denominator_label:'All expected rows in this framing and condition'})):[];}), 'composition');}
function framingMatrix(summary,axis){return {...spec('Unsafe tool selections / valid · '+(AXES[axis]||axis)+' × framing',5,'rate_matrix',(summary.analysis?.tasks?.['5']?.groups||[]).filter(g=>g.partition_kind==='variant'&&g.axis===axis).map(g=>({left:g.value,right:g.partition_name,...g.rates.event_on_valid,coverage:g.coverage})), 'framing_matrix'),axis};}
function selectCharts(summary,selection){
 const task=Number(selection.task),{scope,axis}=selection,all=summary.analysis?.charts||[];
 if(summary.historical)return all.filter(c=>c.task===task).map(c=>decorateChart(c.family==='paper_group'?c:fixedData(c),summary,selection));
 const chosen=selectedPart(summary,selection);if(selection.group&&!chosen)return [];
 const selected=all.filter(c=>c.task===task&&scopeOf(c)===scope),result=[];
 const add=(...families)=>result.push(...selected.filter(c=>families.includes(c.family)));
 if(task===1){add('confusion','rates');result.push(...selected.filter(c=>c.family==='label_specific'&&axisOf(c)===axis));}
 if(task===2){result.push(variantChart(summary,2,selection));add('rates');}
 if(task===3)add('rates');
 if(task===4)add('strategy','unsafe_marker','rates');
 if(task===5){result.push(variantChart(summary,5,selection),composition(summary,selection));if(axis)result.push(framingMatrix(summary,axis));add('rates');}
 const group=selected.find(c=>c.family==='group'&&axisOf(c)===axis);
 if(group&&task!==4)result.push(axis==='severity_band × explicitness'?jointMatrix(group):group);
 if(task===4){const matrix=selected.find(c=>c.family==='strategy_group'&&axisOf(c)===axis);if(matrix)result.push(matrix);if(selection.cooccurrence)add('co_occurrence');}
 if(task===5&&!selection.group){const transition=all.find(c=>c.family==='transition'&&scopeOf(c)===scope);if(transition)result.push(transitionMatrix(transition));}
 if(selection.group){for(let i=result.length-1;i>=0;i--){const c=result[i],filters={task,axis,value:selection.group};let data;
   if(c.family==='label_specific'){result.splice(i,1);continue;}
   if(c.family==='rates')data=Object.entries(chosen.rates).map(([label,r])=>({...r,label,case_filter:filters}));
   if(c.family==='confusion')data=Object.entries(chosen.confusion).map(([label,count])=>({label,count,denominator:chosen.rows,sources:chosen.unique_sources}));
   if(c.family==='strategy')data=Object.entries(chosen.strategy_inclusion).map(([label,r])=>({label,numerator:r.count,denominator:r.classified,value:r.rate_on_classified,sources:chosen.valid_sources,case_filter:filters}));
   if(c.family==='unsafe_marker'){const r=chosen.unsafe_marker;data=[{label:'unsafe_marker',numerator:r.count,denominator:r.classified,value:r.rate_on_classified,sources:chosen.valid_sources}];}
   if(c.family==='co_occurrence')data=chosen.co_occurrence.map(d=>({...d,sources:chosen.valid_sources}));
   if(c.family==='framing_matrix')data=c.data.filter(d=>d.left===selection.group);
   if(data)result[i]={...c,title:c.title+' · '+pretty(selection.group),data};
  }}
 for(let i=0;i<result.length;i++){const c=result[i],scopeName=scope.startsWith('all:')?([3,4].includes(task)?'source union':'all inputs'):pretty(scope.split(':')[1]);let title=c.title;
  if(c.family==='group')title=(task===1?'Judgment error':task===2?'Answer error':'Unsafe / valid')+' by '+(AXES[axis]||axis)+' · '+scopeName;
  if(c.family==='strategy_group')title='Strategy inclusion × '+(AXES[axis]||axis)+' · '+scopeName;
  if(c.family==='strategy')title='Strategy inclusion (multi-label) · '+scopeName+(selection.group?' · '+pretty(selection.group):'');
  result[i]={...c,title};
 }
 const order=({1:['confusion','rates','label_specific','group'],2:['variants','rates','group'],3:['group','rates'],4:['strategy','strategy_group','unsafe_marker','rates','co_occurrence'],5:['variants','composition','framing_matrix','group','transition','rates']})[task];
 return result.sort((a,b)=>order.indexOf(a.family)-order.indexOf(b.family)).map(c=>({...c,title:c.title.replaceAll('event_on_valid','unsafe events / valid').replaceAll('missed_risk_on_valid_unsafe','missed risk / valid unsafe inputs').replaceAll('false_alarm_on_valid_safe','false alarms / valid safe inputs'),data:c.data.map(d=>({...d,label:d.label==='event_on_valid'&&task<3?(task===1?'Judgment errors / valid':'Answer errors / valid'):d.label==='observed_event_on_all'&&task<3?(task===1?'Observed judgment errors / all':'Observed answer errors / all'):d.label}))})).map(c=>decorateChart(enrichChart(c.kind==='rate_bars'&&c.family!=='rates'?fixedData(c):c,summary,selection),summary,selection));
}
function observations(c,sort,query,selection){
 let data=[...c.data];const matrix=!['rate_bars','count_bars','stacked'].includes(c.kind);
 if(query&&!matrix&&c.kind!=='stacked'){const q=query.toLocaleLowerCase();data=data.filter(d=>matchesLabel(d,q));}
 if(selection?.group&&['group','strategy_group'].includes(c.family))data=data.filter(d=>(d.case_filter?.value??d.right??d.label)===selection.group);
 if(sort==='value'&&['rate_bars','count_bars'].includes(c.kind))data.sort((a,b)=>finite(value(a))&&finite(value(b))?value(b)-value(a):finite(value(a))?-1:finite(value(b))?1:0);
 return {...c,data,label_search_hidden:!!query&&!matrix&&c.kind!=='stacked'&&c.data.length>0&&data.length===0,highlightQuery:matrix?query:'',searchNote:query&&c.kind==='stacked'?'Complete compositions retain all outcomes; label search is not applied to these segments.':query&&matrix?'Matching cells are highlighted; the complete matrix and denominators are retained.':''};
}
function describe(d,c){
 const rate=Object.hasOwn(d,'value'),support=d.support_count??d.sources,low=finite(support)&&support<20;
 return [d.seriesName?'Model: '+d.seriesName:'',datumLabel(d),rate?(finite(d.value)?pct(d.value):'N/A · '+unavailableReason(d,c)):'Count '+(d.count??('N/A · '+unavailableReason(d,c))),
  d.direction_label||directionLabel(d,c),
  c.task===4&&strategyInfo(d.label??d.left)?'Strategy: '+strategyInfo(d.label??d.left).name+' · '+strategyInfo(d.label??d.left).definition:'',
  (d.denominator_label||'Numerator / denominator')+': '+(d.numerator??d.count??'not released')+' / '+(d.denominator??d.classified??'not released'),
  (d.sources_label||'Unique sources (as reported)')+': '+(d.sources??'not released'),
  d.valid!=null&&d.expected!=null?'Valid / expected: '+d.valid+' / '+d.expected+' · coverage '+pct(d.coverage):d.coverage!=null?'Valid coverage: '+pct(d.coverage):'Coverage: see scope summary',
  low&&finite(value(d))?'Small group: fewer than 20 '+(d.support_count!=null?'row observations':'reported sources')+'; descriptive only.':'',
  d.interval?.lower!=null?'Source bootstrap 95% interval: '+pct(d.interval.lower)+'–'+pct(d.interval.upper):'No interval supplied; none estimated in the browser.',
  c.family==='transition'?'Row denominator includes invalid choices. Classifier groups may contain different sources across models.':''].filter(Boolean).join('\n');
}
function mount(holder,summaries,options={}){
 const doc=holder.ownerDocument||document,el=(tag,text,cls)=>{const n=doc.createElement(tag);if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n;};
 const svg=(tag,attrs={})=>{const n=doc.createElementNS('http://www.w3.org/2000/svg',tag);if(tag==='svg')n.setAttribute('font-family','system-ui,sans-serif');for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));return n;};
 const text=(parent,label,x,y,attrs={})=>{const n=svg('text',{x,y,...attrs});n.textContent=String(label);parent.append(n);return n;};
 const button=(label,fn)=>{const b=el('button',label,'secondary');b.type='button';b.addEventListener('click',fn);return b;};
 const tasks=[...new Set(summaries.flatMap(s=>(s.analysis?.charts||[]).map(c=>String(c.task))))].sort();if(!tasks.length){holder.append(el('p','No chart observations are available for this publication.'));return;}
 const box=el('section',undefined,'detail-explorer'),tabs=el('div',undefined,'detail-tabs'),controls=el('div',undefined,'detail-controls'),help=el('p',undefined,'detail-help'),interpretation=el('details',undefined,'detail-interpretation'),filterStatus=el('p',undefined,'detail-filter-status'),view=el('div'),selectionBox=el('aside',undefined,'detail-selection');
 const state={task:tasks.includes('3')?'3':tasks[0],scope:'',axis:'utterance_type',sort:'reported',query:'',group:'',cooccurrence:false,matrixMode:'row_percent'},memory={};let activeMark=null;
 selectionBox.hidden=true;selectionBox.setAttribute('role','region');selectionBox.setAttribute('aria-label','Selected observation');selectionBox.setAttribute('aria-live','polite');box.append(el('h2',summaries.length>1?'Compare task behavior':'Explore task behavior'),el('p','Hover or focus a mark for exact values. Select a bar or cell to pin its numerical evidence. Charts use measured denominators; no combined ethics score.'),tabs,controls,filterStatus,selectionBox,view,interpretation);interpretation.append(el('summary','Interpretation and filter limits'),help);holder.append(box);
 const storageKey='koevd-chart-view:'+summaries.map(s=>(s.submission_id||s.name)+':'+(s.revision||'paper')).join('|');let notice='';
 function loadViews(input){if(input?.views&&typeof input.views==='object')for(const t of tasks)if(input.views[t]&&typeof input.views[t]==='object')memory[t]=viewState(input.views[t]);if(input&&tasks.includes(String(input.task))){state.task=String(input.task);Object.assign(state,viewState(input));}}
 try{const raw=sessionStorage.getItem(storageKey);if(raw&&raw.length<=16384)loadViews(JSON.parse(raw));}catch(_){/* Invalid or unavailable storage: retain visible defaults. */}
 if(options.selection)loadViews(options.selection);
 const tip=el('div',undefined,'detail-tooltip');tip.hidden=true;tip.setAttribute('role','tooltip');box.append(tip);
 selectionBox.addEventListener('keydown',e=>{if(e.key==='Escape')clearSelection();});
 function hideTip(){tip.hidden=true;}
 function download(name,content,type){const url=URL.createObjectURL(new Blob([content],{type})),a=el('a');a.href=url;a.download=name;doc.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 function select(label,items,current,change){const wrap=el('label',label),n=el('select');n.setAttribute('aria-label',label);for(const [v,t]of items){const o=el('option',t);o.value=v;n.append(o);}n.value=current;n.addEventListener('change',()=>change(n.value));wrap.append(n);controls.append(wrap);return n;}
 function clearSelection(){selectionBox.hidden=true;if(activeMark)activeMark.setAttribute('aria-pressed','false');activeMark=null;}
 function pin(d,c,s,g){clearSelection();activeMark=g;g.setAttribute('aria-pressed','true');selectionBox.hidden=false;selectionBox.replaceChildren(el('strong','Selected observation · '+context(s).model),button('Clear selection',clearSelection),el('pre',describe(d,c)),el('p','Selection describes this aggregate only. It does not apply an unsupported intersection or grant access to prompts or responses.'));
  if(c.task===4){for(const label of [...new Set([d.label,d.left,d.right])]){const info=strategyInfo(label);if(info){const note=el('details');note.append(el('summary',info.name+' · definition and illustration'),el('p',info.definition),el('p','Illustrative example (not benchmark data): '+info.example));selectionBox.append(note);}}}
  const f=d.case_filter;if(f?.axis&&f.value){const group=groups(s,state.task,state.scope,f.axis).find(g=>g.value===f.value);if(group)selectionBox.append(el('p','Matching group: '+group.valid+'/'+group.rows+' valid expected rows · '+group.unique_sources+' unique sources · coverage '+pct(group.coverage)));
   const signal=s.analysis?.signals?.find(g=>g.task===Number(state.task)&&g.partition_kind+':'+g.partition_name===state.scope&&g.axis===f.axis&&g.value===f.value);if(signal)selectionBox.append(el('p','Group '+signal.group_events+'/'+signal.group_valid+' versus disjoint remaining sources '+signal.remaining_events+'/'+signal.remaining_valid+' · '+signal.difference_pp.toFixed(2)+' pp. Descriptive contrast; no significance or causal claim.'));
  }
 }
 function mark(g,d,c,s){if(c.highlightQuery&&!matchesLabel(d,c.highlightQuery))g.setAttribute('opacity','.25');g.setAttribute('aria-pressed','false');const description=describe(d,c),title=svg('title');title.textContent=description;g.append(title);g.setAttribute('tabindex','0');g.setAttribute('role','button');g.setAttribute('aria-label',description.replaceAll('\n','; '));
  const show=e=>{tip.textContent=description;tip.hidden=false;const r=g.getBoundingClientRect();tip.style.left=Math.max(8,Math.min((e?.clientX??r.left)+12,window.innerWidth-340))+'px';tip.style.top=Math.max(8,Math.min((e?.clientY??r.top)+14,window.innerHeight-220))+'px';};g.addEventListener('mouseenter',show);g.addEventListener('mousemove',show);g.addEventListener('mouseleave',hideTip);g.addEventListener('focus',()=>show());g.addEventListener('blur',hideTip);g.addEventListener('click',()=>{hideTip();pin(d,c,s,g);});g.addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();hideTip();pin(d,c,s,g);}if(e.key==='Escape'){hideTip();clearSelection();}});
 }
 function bars(c,s){
  const grouped=c.kind==='grouped_bars',rate=grouped?c.original_kind==='rate_bars':c.kind==='rate_bars',labels=grouped?[...new Set(c.data.map(d=>d.label))]:c.data.map(d=>d.label),series=grouped?c.models.length:1;
  const step=grouped?22+series*48:54,height=48+labels.length*step,drawing=svg('svg',{viewBox:'0 0 900 '+height,class:'detail-svg',role:'group','aria-label':c.title}),x=295,w=345,max=rate?1:Math.max(1,...c.data.map(d=>d.count||0));
  for(const t of [0,.25,.5,.75,1]){drawing.append(svg('line',{x1:x+t*w,x2:x+t*w,y1:26,y2:height-8,stroke:'#dce5ef'}));text(drawing,rate?t*100+'%':Math.round(t*max),x+t*w,16,{'text-anchor':'middle',fill:'#52657a','font-size':12,class:rate?'detail-export-axis':''});}
  labels.forEach((label,i)=>{
   const base=35+i*step;
   if(grouped){drawing.append(svg('rect',{x:0,y:base-2,width:900,height:step-5,fill:i%2?'#f2f6fa':'#fff'}));text(drawing,pretty(label),5,base+16,{'font-size':14,fill:'#182e49'});}
   const entries=grouped?c.data.filter(d=>d.label===label):[c.data[i]];
   entries.forEach((d,j)=>{const y=base+(grouped?22+j*48:0),g=svg('g'),v=value(d),color=grouped?MODEL_COLORS[d.seriesIndex%3]:c.task===4||c.task===2||/coverage|accuracy/i.test(d.label)?'#377fa4':'#b84942';
    g.append(svg('rect',{x:0,y:y-3,width:900,height:grouped?47:51,fill:'transparent'}));text(g,grouped?'Model '+(d.seriesIndex+1):datumLabel(d).length>40?datumLabel(d).slice(0,37)+'…':datumLabel(d),5,y+16,{'font-size':13,fill:grouped?color:'#182e49'});
    g.append(svg('rect',{x,y,width:w,height:18,rx:3,fill:'#edf2f7'}));if(finite(v)&&v>0)g.append(svg('rect',{x,y,width:Math.min(1,v/max)*w,height:18,rx:3,fill:color,opacity:finite(d.sources)&&d.sources<20?.5:1}));if(v===0)g.append(svg('circle',{cx:x,cy:y+9,r:3,fill:'#fff',stroke:color,'stroke-width':1.5}));
    text(g,(finite(v)?(rate?pct(v):v):'N/A')+(finite(v)&&finite(d.sources)&&d.sources<20?' · small n':''),x+w+14,y+12,{'font-size':13,fill:'#182e49'});text(g,finite(v)?(d.numerator??d.count??'—')+' / '+(d.denominator??d.classified??'—'):unavailableReason(d,c),x+w+14,y+27,{'font-size':12,fill:'#52657a'});
    if(d.coverage!=null)text(g,'Valid '+(d.valid!=null&&d.expected!=null?d.valid+'/'+d.expected+' · ':'')+pct(d.coverage),x,y+41,{'font-size':11,fill:'#52657a'});
    if(rate&&d.interval?.lower!=null&&d.interval?.upper!=null)g.append(svg('line',{x1:x+d.interval.lower*w,x2:x+d.interval.upper*w,y1:y+11,y2:y+11,stroke:'#172c48','stroke-width':3}));
    mark(g,d,c,grouped?summaries[d.seriesIndex]:s);drawing.append(g);
   });
  });return drawing;
 }
 function matrix(c,s){
  let data=c.data;const confusion=c.kind==='confusion_matrix';
  if(c.kind==='count_matrix')data=c.data.flatMap(d=>d.left===d.right?[d]:[d,{...d,left:d.right,right:d.left}]);
  if(confusion){const original=data;data=['safe','unsafe'].flatMap(left=>['safe','unsafe','unparsed'].map(right=>{
   const d=original.find(x=>x.label===left+'->'+right),total=original.filter(x=>x.label.startsWith(left+'->')).reduce((n,d)=>n+d.count,0),cell=d?{...d,left,right}:{left,right,label:left+'->'+right,count:0,denominator:original[0]?.denominator??null,sources:original[0]?.sources??null};
   return c.matrixMode==='row_percent'?{...cell,numerator:cell.count,denominator:total,value:total?cell.count/total:null,denominator_label:'All expected inputs in this gold-label row (including unparsed)',sources_label:'Unique sources in the full input set, not this row',support_count:total}:{...cell,denominator_label:'Cell count / all expected inputs',sources_label:'Unique sources in the full input set'};
  }));}
  const domains=c.domains||matrixDomains([{...c,data}]),rows=domains.rows,cols=domains.cols,cell=90,left=235,top=105,height=top+rows.length*42+30,width=Math.max(620,left+cols.length*cell+30),rate=['rate_matrix','strategy_group_matrix'].includes(c.kind)||confusion&&c.matrixMode==='row_percent',max=c.countMax||Math.max(1,...data.map(d=>d.count||0)),drawing=svg('svg',{viewBox:'0 0 '+width+' '+height,class:'detail-svg detail-matrix',role:'group','aria-label':c.title});
  drawing.style.minWidth=width+'px';drawing.style.width=width+'px';text(drawing,rate?'Rate color scale: 0% → 100%; N/A = no denominator':'Count color maximum: '+max+(c.countMax?' (shared across models)':''),6,18,{'font-size':12,fill:'#52657a'});
  if(confusion){text(drawing,'Columns: model prediction',left,42,{'font-size':12,fill:'#182e49'});text(drawing,'Rows: gold label',6,top-15,{'font-size':12,fill:'#182e49'});}
  cols.forEach((col,i)=>text(drawing,pretty(col),left+i*cell+25,top-12,{'font-size':12,fill:'#182e49',transform:'rotate(-38 '+(left+i*cell+25)+' '+(top-12)+')'}));
  rows.forEach((row,j)=>{text(drawing,pretty(row).slice(0,32),left-10,top+j*42+24,{'text-anchor':'end','font-size':12,fill:'#182e49'});cols.forEach((col,i)=>{
   const d=data.find(d=>(d.left??d.response_label)===row&&(d.right??d.tool_outcome)===col)||{left:row,right:col,value:null},v=rate?d.value:finite(d.count)?d.count/max:null,g=svg('g');g.append(svg('rect',{x:left+i*cell,y:top+j*42,width:cell-3,height:39,rx:3,fill:finite(v)?(c.task===4||confusion&&row===col?'rgba(35,116,151,':'rgba(177,62,54,')+(.08+.7*v)+')':'#e4e9ef',stroke:finite(d.support_count??d.sources)&&(d.support_count??d.sources)<20?'#72859a':'none','stroke-dasharray':'3 2'}));text(g,rate?pct(d.value):d.count??'N/A',left+i*cell+(cell-3)/2,top+j*42+24,{'text-anchor':'middle','font-size':12,fill:'#12243b'});mark(g,d,c,s);drawing.append(g);
  });});return {drawing,data};
 }
 function stacked(c,s){
  const rows=categoryOrder(c.data.map(d=>d.left),'framing'),drawing=svg('svg',{viewBox:'0 0 900 '+(70+rows.length*65),class:'detail-svg',role:'group','aria-label':c.title}),colors=OUTCOME_COLORS;
  rows.forEach((row,i)=>{const y=30+i*65;let offset=0;text(drawing,pretty(row),0,y+17,{'font-size':13,fill:'#182e49'});for(const outcome of OUTCOMES){const d=c.data.find(d=>d.left===row&&d.right===outcome);if(!d)continue;const color=colors[OUTCOMES.indexOf(outcome)],w=(d.value||0)*630,g=svg('g');g.append(svg('rect',{x:220+offset,y,width:Math.max(0,w),height:30,fill:color}));if(w>52)text(g,pct(d.value),220+offset+w/2,y+20,{'text-anchor':'middle','font-size':12,fill:'#fff'});mark(g,d,c,s);drawing.append(g);offset+=w;}text(drawing,c.data.find(d=>d.left===row)?.denominator>0?'100% of expected rows · includes invalid':'N/A · No expected rows',220,y+47,{'font-size':11,fill:'#52657a'});});return drawing;
 }
 function chart(c,s){
  const panel=el('section',undefined,'detail-chart'),head=el('div',undefined,'detail-chart-head'),actions=el('div',undefined,'detail-chart-actions');head.append(el('h3',c.title),actions);panel.append(head);
  if(!c.data.length){panel.append(el('p',c.label_search_hidden?'Measured observations are hidden by label search. The selected group is not unmeasured.':'No observations are supplied for this view.'));if(state.query)panel.append(button('Clear label search',()=>{state.query='';rebuild();}));return panel;}
  const guide=el('div',undefined,'detail-chart-guide'),chips=el('div',undefined,'detail-chart-context');
  for(const label of [c.scope_label,c.condition_label,c.denominator_note])if(label)chips.append(el('span',label));guide.append(chips);
  const directions=[...new Set(c.data.map(d=>d.direction_label||directionLabel(d,c)))];guide.append(el('p',directions.length===1?directions[0]:'Mixed metrics · each row names its direction','detail-direction'));
  if(c.models){const legend=el('div',undefined,'detail-model-legend');for(const [i,m]of c.models.entries()){const full='Model '+(i+1)+' · '+m.model,n=el('span',full.length>65?full.slice(0,62)+'…':full);n.title=full;n.style.color=MODEL_COLORS[i%3];legend.append(n);}guide.append(legend);}
  if(c.kind==='stacked'){const legend=el('div',undefined,'detail-outcome-legend');OUTCOMES.forEach((key,i)=>{const item=el('span',pretty(key)),swatch=el('i');swatch.style.background=OUTCOME_COLORS[i];item.prepend(swatch);legend.append(item);});guide.append(legend);}
  if(['rate_bars','grouped_bars'].includes(c.kind)){const scale=el('div',undefined,'detail-bar-axis');for(const label of ['0%','25%','50%','75%','100%'])scale.append(el('span',label));guide.append(scale);}
  panel.append(guide);
  let drawing;if(c.kind==='stacked')drawing=stacked(c,s);else if(['rate_bars','count_bars','grouped_bars'].includes(c.kind))drawing=bars(c,s);else{const rendered=matrix(c,s);drawing=rendered.drawing;c={...c,data:rendered.data};}
  const scroll=el('div',undefined,'detail-chart-scroll');scroll.setAttribute('tabindex','0');scroll.setAttribute('role','region');scroll.setAttribute('aria-label',c.title+' · scroll plot');scroll.append(drawing);scroll.addEventListener('scroll',hideTip);panel.append(scroll);
  if(!['rate_bars','count_bars','grouped_bars','stacked'].includes(c.kind))guide.append(el('p','Columns: '+matrixDomains([c]).cols.map(pretty).join(' · '),'detail-axis-key'));
  if(c.searchNote)panel.append(el('p',c.searchNote,'detail-caption'));
  const exported={...(c.models?{contexts:c.models}:{context:context(s)}),selection:{...state},chart:c,note:'Numerical aggregate only. Display selection never estimates missing intersections or historical counts.'};
  actions.append(button('SVG',()=>{const copy=drawing.cloneNode(true);copy.setAttribute('xmlns','http://www.w3.org/2000/svg');copy.prepend(svg('title'));copy.firstChild.textContent=JSON.stringify({contexts:c.models||[context(s)],selection:state,title:c.title});download('koevd-task'+state.task+'.svg',new XMLSerializer().serializeToString(copy),'image/svg+xml');}),button('Chart JSON',()=>download('koevd-task'+state.task+'-chart.json',JSON.stringify(exported,null,2),'application/json')));
  const exact=el('details'),t=el('table'),tr=el('tr');for(const h of ['Model / group / outcome','Rate / count','Direction / availability','Numerator','Denominator and scope','Source support and scope','Valid coverage'])tr.append(el('th',h));const thead=el('thead');thead.append(tr);t.append(thead);const tbody=el('tbody');for(const d of c.data){const row=el('tr');for(const v of [(d.seriesName?d.seriesName+' · ':'')+datumLabel(d),Object.hasOwn(d,'value')?pct(d.value):d.count??'N/A',unavailableReason(d,c)||d.direction_label||directionLabel(d,c),d.numerator??d.count??'Not released',(d.denominator??d.classified??'Not released')+(d.denominator_label?' · '+d.denominator_label:''),(d.sources??'Not released')+(d.sources_label?' · '+d.sources_label:''),d.coverage!=null?pct(d.coverage)+(d.valid!=null&&d.expected!=null?' · '+d.valid+'/'+d.expected:''):'See scope summary'])row.append(el('td',v));tbody.append(row);}t.append(tbody);exact.append(el('summary','Exact numerical observations'),t);panel.append(exact,el('p',chartCaption(c),'detail-caption'));return panel;
 }
 function modelSummary(s){
  const node=el('section',undefined,'detail-model-summary');node.append(el('h3',context(s).model),el('p',s.historical?'Historical paper aggregate · only released per-model observations are available.':'Revision '+s.revision+' · '+(s.model?.dtype||'unknown precision')));
   const p=selectedPart(s,state);if(p)node.append(el('p',(scopes(summaries,state.task).find(([key])=>key===state.scope)?.[1]||state.scope)+' · '+(state.group?pretty(state.group)+' · ':'')+p.valid+'/'+p.rows+' valid expected rows · '+p.unique_sources+' unique sources · coverage '+pct(p.coverage),'detail-scope-summary'));
  if(p?.rates){const keys=state.task==='1'?['missed_risk_on_valid_unsafe','false_alarm_on_valid_safe']:state.task==='2'?['accuracy_on_valid']:state.task==='4'?[]:['event_on_valid','observed_event_on_all'],scores=el('div',undefined,'detail-key-metrics');
   for(const key of keys){const r=p.rates[key];if(!r)continue;const label=key==='event_on_valid'?(state.task==='3'?'Classifier unsafe / valid ↓':'Unsafe tool / valid ↓'):key==='observed_event_on_all'?'Observed unsafe / all expected ↓':key==='coverage'?'Strategy measurement coverage':pretty(key)+(state.task==='1'?' ↓':''),card=el('div');card.append(el('span',label),el('strong',pct(r.value)),el('small',(finite(r.value)?'':unavailableReason(r,{task:Number(state.task)})+' · ')+(r.numerator??'—')+' / '+(r.denominator??'—')));scores.append(card);}if(scores.children.length)node.append(scores);}
  if(state.task==='4'&&p){const r=p.rates?.coverage;node.append(el('p','Compare strategy patterns; Task 4 has no overall quality score.','detail-task-purpose'));if(r)node.append(el('p','Measurement completeness: '+pct(r.value)+' · '+r.numerator+'/'+r.denominator+' · not a performance score','detail-completeness'));const top=Object.entries(p.strategy_inclusion||{}).filter(([,v])=>finite(v.rate_on_classified)).sort((a,b)=>b[1].rate_on_classified-a[1].rate_on_classified)[0];if(top)node.append(el('p','Most frequently included (descriptive): '+pretty(top[0])+' · '+pct(top[1].rate_on_classified),'detail-strategy-preview'));}
  if(['3','4'].includes(state.task)&&!s.historical)node.append(el('p',window.KoEVDMetrics?.measurementLabel(s.measurements?.[state.task])||'Measurement settings unknown','detail-caption'));
  return node;
 }
 function reviewSummary(s){
  const r=reviewCandidates(s,state);if(r.unavailable)return null;const node=el('details',undefined,'detail-review');node.open=false;node.append(el('summary','Within-model group contrasts · '+context(s).model),el('p','Within-model descriptive contrasts against disjoint remaining sources. Both sides require at least 20 valid sources and 90% coverage. These are not significance tests, causal bias findings or confirmed strengths/weaknesses.'));
  for(const [items,title]of [[r.higher,'Higher observed error/unsafe rate'],[r.lower,'Lower observed error/unsafe rate']]){node.append(el('h4',title));if(!items.length)node.append(el('p','No supported candidates for this scope/axis; this does not establish uniform behavior.'));for(const candidate of items){const row=el('p');row.append(el('strong',pretty(candidate.value)+' · '+(candidate.difference_pp>0?'+':'')+candidate.difference_pp.toFixed(2)+' pp'),el('span',' · group '+candidate.group_events+'/'+candidate.group_valid+' vs remaining '+candidate.remaining_events+'/'+candidate.remaining_valid+' · valid sources '+candidate.group_sources+'/'+candidate.remaining_sources+' '),button('Inspect group',()=>{notice=state.query?'Label search cleared to inspect the selected group.':'';state.group=candidate.value;state.query='';rebuild();}));node.append(row);}}
  node.append(el('p',r.limited+' metadata group(s) have small/low/unknown support and remain visible in charts. A low observed rate with incomplete coverage is not evidence of safety.'));return node;
 }
 function strategyGlossary(){
  const box=el('details',undefined,'detail-strategy-glossary');box.append(el('summary','Strategy definitions and illustrative examples'),el('p','Canonical names follow the released label crosswalk and paper codebook. Examples below are newly written illustrations, not benchmark responses or gold annotations. Multiple strategies can co-occur. The separate Unsafe marker is not a sixteenth strategy.'));
  const table=el('table'),header=el('tr');for(const label of ['Strategy / internal code','Meaning','Illustrative example'])header.append(el('th',label));table.append(header);
  for(const [code,info]of Object.entries(STRATEGY_GUIDE)){const row=el('tr');row.append(el('td',info.name+' · '+code+(info.aliases.length?' · earlier label: '+info.aliases.join(', '):'')),el('td',info.definition),el('td',info.example));table.append(row);}const scroll=el('div',undefined,'detail-glossary-table-scroll');scroll.setAttribute('tabindex','0');scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Strategy definitions table');scroll.append(table);box.append(scroll);return box;
 }
 function differenceSummary(selected){
  const all=observedDifferences(selected,summaries),box=el('details',undefined,'detail-between-model');box.append(el('summary','Between-model observed rate differences · Model 1 − Model 2 (pp)'),el('p','This summary covers rate-bar charts; matrices and outcome compositions remain in their charts. Different from the within-model group contrasts below. These subtract each model’s observed rate under the displayed condition, with its own denominator. They are not jointly valid paired effects, significance tests or causal findings. The groups can contain different inputs and valid outputs. Coverage and generation/measurement conditions can differ.'));
  box.append(el('p',summaries.map((s,i)=>'Model '+(i+1)+': '+context(s).model+' · revision '+(s.revision??'paper')).join(' | '),'detail-difference-models'));
  if(!all.length){box.append(el('p','No comparable rate observations are supplied in this view.'));return box;}
  box.append(el('p','Rows with at least 20 reported sources on both sides precede small/unknown-support rows; each set is ordered by absolute observed difference. The first 8 are shown. Missing rates have no inferred difference. Descriptive Task 4 / historical judgment frequencies have no quality preference. Small or unreleased source support is flagged.'));
  const table=el('table'),header=el('tr');for(const label of ['Chart / group / condition','Model 1 rate (n/d)','Model 2 rate (n/d)','Model 1 − Model 2 (pp)','Interpretation'])header.append(el('th',label));table.append(header);
  for(const d of all.slice(0,8)){const row=el('tr'),format=r=>r&&finite(r.value)?pct(r.value)+' ('+(r.numerator??'not released')+'/'+(r.denominator??'not released')+')':'N/A';row.append(el('td',d.chart+' · '+d.group+' · '+d.scope+' · '+d.condition),el('td',format(d.left)),el('td',format(d.right)),el('td',d.difference_pp===null?'N/A':(d.difference_pp>0?'+':'')+d.difference_pp.toFixed(2)),el('td',d.interpretation+(d.limited_support?' · Small/unknown source support':'')));table.append(row);}const scroll=el('div',undefined,'detail-difference-table-scroll');scroll.setAttribute('tabindex','0');scroll.setAttribute('role','region');scroll.setAttribute('aria-label','Observed model differences table');scroll.append(table);box.append(scroll,button('Difference summary JSON',()=>download('koevd-task'+state.task+'-observed-differences.json',JSON.stringify({contexts:summaries.map(context),selection:{...state},comparison_kind:'observed_marginal_rates',paired_effect:false,rows:all},null,2),'application/json')));return box;
 }
 function redraw(){
  hideTip();clearSelection();view.replaceChildren();memory[state.task]=viewState(state);try{sessionStorage.setItem(storageKey,JSON.stringify({...state,views:memory}));}catch(_){}
  const multi=summaries.length>1,overview=el('div',undefined,'detail-context-grid');view.append(overview);
  for(const s of summaries)overview.append(modelSummary(s));
  filterStatus.textContent='Chart view: '+(scopes(summaries,state.task).find(([key])=>key===state.scope)?.[1]||'Released aggregates')+' · '+(AXES[state.axis]||'Released axes')+' · '+(state.group?pretty(state.group):'All conditions')+(summaries.length>1?' · Matched-input statistics retain their separate partitions.':'');
  if(state.query){filterStatus.append(el('span',' · Label search: '+state.query),button('Clear label search',()=>{state.query='';rebuild();}));}if(notice)filterStatus.append(el('span',' · '+notice));
  if(state.task==='4')view.append(strategyGlossary());
  const selected=summaries.map(s=>selectCharts(s,state).map(c=>observations({...c,matrixMode:state.matrixMode},multi?'reported':state.sort,state.query,state)));
  if(multi)view.append(differenceSummary(selected));
  if(!multi){for(const c of selected[0]){const panel=chart(c,summaries[0]);if(c.family==='rates'&&['2','3','4','5'].includes(state.task)){const fold=el('details');fold.append(el('summary','Coverage and additional measured rates'),panel);view.append(fold);}else view.append(panel);}}
  else{
   const keys=[...new Set(selected.flatMap(cs=>cs.map(c=>c.family+'|'+c.title)))];
   for(const key of keys){const charts=selected.map(cs=>cs.find(c=>c.family+'|'+c.title===key)||null),base=charts.find(Boolean);let panel;
    if(charts.filter(Boolean).every(c=>['rate_bars','count_bars'].includes(c.kind)))panel=chart(comparisonBars(charts,summaries,state),summaries[0]);
    else{panel=el('section',undefined,'detail-comparison-section');panel.append(el('h3',base.title));const grid=el('div',undefined,'detail-paired-matrices'),domains=matrixDomains(charts),maximum=Math.max(1,...charts.filter(Boolean).flatMap(c=>c.data.map(d=>d.count||0)));for(const [i,s]of summaries.entries()){const cell=el('div');cell.append(el('h4',context(s).model));if(charts[i])cell.append(chart({...charts[i],domains,countMax:['confusion_matrix','count_matrix'].includes(base.kind)&&!(base.kind==='confusion_matrix'&&state.matrixMode==='row_percent')?maximum:null},s));else cell.append(el('p','No observations for this model and selected condition. Missing is not zero.'));grid.append(cell);}panel.append(grid);}
    if(base.family==='rates'&&['2','3','4','5'].includes(state.task)){const fold=el('details');fold.append(el('summary','Coverage and additional measured rates'),panel);view.append(fold);}else view.append(panel);
   }
  }
  const reviews=el('div',undefined,'detail-review-grid');for(const s of summaries){const review=reviewSummary(s);if(review)reviews.append(review);}view.append(reviews);
  for(const s of summaries){if(state.task==='5'&&state.group)view.append(el('p','Conditional Task 3→5 transitions are not supplied for this metadata group; the whole-scope transition matrix is hidden. Clear Show condition to inspect it.','detail-caption'));if(!selected[summaries.indexOf(s)].length)view.append(el('p',context(s).model+': no observations for the selected scope/condition.'));
   if(s.historical){const notes={1:'Unsafe-judgment frequency is descriptive; it is not missed risk or a confusion matrix. Severity source codes 1 and 2 remain separate.',2:'Only released instruction variants are shown. The common-three mean differs from the original open-model four-variant summary. Counts and intervals are not reconstructed from rounded percentages.',3:'No model-specific question/topic/severity breakdown was released here. Pooled all-model tables cannot establish this model’s weaknesses.',4:'Only released selected strategies are shown. Missing strategy labels are not zero. Strategies can co-occur; their percentages need not sum to 100%. Unsafe is a separate marker.',5:'Historical unsafe/all and partial parse coverage differ from current strict valid-output measures. No seven-way composition is inferred from partial aggregates.'};view.append(el('p',context(s).model+' · '+notes[state.task],'detail-help'));}
  }
  options.onChange?.({...state});
 }
 function rebuild(){if(!['reported','value'].includes(state.sort))state.sort='reported';if(!['count','row_percent'].includes(state.matrixMode))state.matrixMode='row_percent';controls.replaceChildren();tabs.replaceChildren();for(const t of tasks){const b=button('Task '+t+' · '+TASKS[t],()=>{if(state.task===t)return;memory[state.task]=viewState(state);state.task=t;Object.assign(state,{scope:'',axis:defaultAxis(t),sort:'reported',query:'',group:'',cooccurrence:false,matrixMode:'row_percent'},memory[t]||{});notice='';rebuild();});b.setAttribute('aria-pressed',String(t===state.task));tabs.append(b);}
  const opts=scopes(summaries,state.task);if(!opts.some(([k])=>k===state.scope)){if(state.scope)notice='The saved input scope is unavailable for these models; the displayed default scope is used.';state.scope=defaultScope(opts,state.task);state.group='';}
  select('Input scope / framing',opts,state.scope,v=>{notice='';state.scope=v;state.group='';rebuild();});const axes=availableAxes(summaries,state.task,state.scope);if(!axes.includes(state.axis)){if(state.axis&&axes.length)notice='The saved metadata axis is unavailable; the displayed axis is used.';state.axis=axes[0]||'';}
  if(axes.length)select('Analyze by',axes.map(a=>[a,AXES[a]]),state.axis,v=>{notice='';state.axis=v;state.group='';rebuild();});
  const values=categoryOrder(summaries.flatMap(s=>groups(s,state.task,state.scope,state.axis).map(g=>g.value)),state.axis);if(!values.includes(state.group)){if(state.group)notice='The saved condition is unavailable for these models; all available conditions are shown.';state.group='';}if(values.length)select('Show condition', [['','All available conditions'],...values.map(v=>[v,pretty(v)])],state.group,v=>{state.group=v;redraw();});
  select('Bar order',[['reported','Fixed category order'],['value',summaries.length>1?'Shared rows: maximum observed value first':'Observed value: high to low']],state.sort,v=>{state.sort=v;redraw();});const search=el('input');search.type='search';search.maxLength=200;search.value=state.query;search.setAttribute('aria-label','Find chart labels');search.placeholder='Find chart labels';search.addEventListener('input',()=>{notice='';state.query=search.value;redraw();});controls.append(search,button('Reset view',()=>{notice='';Object.assign(state,{scope:defaultScope(opts,state.task),axis:defaultAxis(state.task),sort:'reported',query:'',group:'',cooccurrence:false,matrixMode:'row_percent'});rebuild();}));
  if(state.task==='1'&&!summaries.every(s=>s.historical))select('Confusion matrix values',[['row_percent','Percent within gold-label row'],['count','Observed counts']],state.matrixMode,v=>{state.matrixMode=v;redraw();});
  if(state.task==='4')controls.append(button(state.cooccurrence?'Hide strategy co-occurrence':'Show strategy co-occurrence',()=>{state.cooccurrence=!state.cooccurrence;rebuild();}));
  const notes={1:'Missed risk and false alarms use different gold-label denominators. Confusion rows are gold labels; columns are predictions. Unparsed outputs stay separate.',2:'Compare per-variant answer accuracy and coverage. The same sources can appear under multiple instructions; do not sum variants as independent examples.',3:'Classifier-labeled unsafe is a proxy measurement. Core is the default; core and Task-5-linked sources overlap, so their counts do not add to the source union.',4:'Multi-label strategy inclusion is descriptive. Percentages can exceed 100% in total. Frequent strategy use is not better quality; the unsafe strategy marker differs from Task 3 safety.',5:'Simulation only: no tool or robot is executed. Compare unsafe/valid with coverage and all-row outcomes. Transition cells use their response-label row total, including invalid choices.'};
  help.textContent=notes[state.task]+' Scope + one metadata axis uses exact precomputed groups. Severity × explicitness is an exact joint view. Other multi-axis intersections are unavailable; label search filters bars, highlights matrix cells and retains every outcome in composition charts. Denominators never change from label search. Public summary charts contain no response cases.';
  if(summaries.every(s=>s.historical))help.textContent=({1:'Historical unsafe-judgment frequency is descriptive, not missed risk or accuracy.',2:'Historical accuracy is shown only for released instruction variants; counts and intervals are not reconstructed.',3:'Historical classifier-labeled unsafe rates have no released per-model question/topic breakdown here.',4:'Historical strategy inclusion is multi-label and descriptive. Only selected released labels are available; missing labels are not zero.',5:'Historical unsafe/all rates and partial parse coverage differ from the current strict-output metrics. No strict outcome composition is inferred.'})[state.task]+' These are released per-model aggregates. Metadata-condition filters and supported contrast candidates are unavailable. Label search does not change denominators.';
  if(['2','5'].includes(state.task)&&!summaries.every(s=>s.historical))help.textContent+=' Variant overview and outcome-composition charts include all available framings/instructions for the selected metadata condition; other detail charts use the selected scope.';
  if(summaries.length>1)help.textContent+=' Both models share the selected scope, axis and fixed rate scales. Each retains its own denominator; this is not a paired-effect estimate.'+(summaries.every(s=>s.historical)?' Historical aggregates do not provide matched-case comparisons.':' Metadata filters affect these descriptive charts only. Matched-input tables above keep their own partitions and are not recalculated for a selected metadata condition.');redraw();
 }
 rebuild();return {selection:()=>({...state,views:Object.fromEntries(Object.entries(memory).map(([t,v])=>[t,{...v}]))}),refresh:rebuild};
}
return {categoryOrder,OUTCOMES,OUTCOME_COLORS,matchesLabel,STRATEGY_GUIDE,strategyInfo,viewState,observedDifferences,unavailableReason,directionLabel,decorateChart,comparisonBars,matrixDomains,chartCaption,reviewCandidates,mount,paperProfile,selectCharts,scopes,defaultScope,availableAxes,observations,transitionMatrix,jointMatrix,context,describe,selectedPart};
}));
