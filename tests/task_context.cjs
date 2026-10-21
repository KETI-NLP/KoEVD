/* User journeys for search recovery and independent per-Task view restoration. */
const fs=require('node:fs');
let test=fs.readFileSync('tests/detail_charts.cjs','utf8').split('const before=JSON.stringify(summary)')[0];
test+=String.raw`
const fixture=JSON.parse(JSON.stringify(summary));
const core=fixture.analysis.tasks['3'].partitions.find(p=>p.name==='core');Object.assign(core,{valid:200,rows:200,unique_sources:200});
fixture.analysis.tasks['3'].groups=['Copyright','Personal Info'].map((value,i)=>({partition_kind:'subset',partition_name:'core',axis:'utterance_type',value,valid:i?60:118,rows:i?60:118,unique_sources:i?60:118,valid_sources:i?60:118,coverage:1,rates:{event_on_valid:r(i?2:5,i?60:118)}}));
fixture.analysis.charts.find(c=>c.id==='core').data=fixture.analysis.tasks['3'].groups.map(g=>({label:g.value,...g.rates.event_on_valid,case_filter:{subset:'core',axis:'utterance_type',value:g.value}}));
fixture.analysis.signals=[{task:3,partition_kind:'subset',partition_name:'core',axis:'utterance_type',value:'Personal Info',group_sources:60,remaining_sources:140,difference_pp:3.33,group_events:2,group_valid:60,remaining_events:0,remaining_valid:140}];
const whole=fixture.analysis.tasks['4'].partitions[0];Object.assign(whole,{strategy_inclusion:{'a_evaluation':{count:8,classified:10,rate_on_classified:.8}},valid_sources:10});
whole.co_occurrence=[{left:'a_evaluation',right:'a_evaluation',count:8,classified:10,sources:10}];
fixture.analysis.charts.push({id:'co-occurrence',task:4,kind:'count_matrix',family:'co_occurrence',title:'Strategy co-occurrence',data:whole.co_occurrence.map(d=>({...d,case_filter:{task:4}}))});
fixture.analysis.tasks['4'].groups=[{...whole,partition_kind:'all',partition_name:'all',axis:'severity_band',value:'High'}];
const stored=new Map();ctx.sessionStorage={getItem:k=>stored.get(k)||null,setItem:(k,v)=>stored.set(k,v)};
const h=new Element('div'),ui=ctx.window.KoEVDDetailCharts.mount(h,[fixture]);
const query=find(h,'Find chart labels');query.value='Copyright';query.fire('input');button(h,'Inspect group').fire('click');
assert.equal(ui.selection().group,'Personal Info');assert.equal(ui.selection().query,'');assert(!h.textContent.includes('Measured observations are hidden'));
const searchAgain=find(h,'Find chart labels');searchAgain.value='Copyright';searchAgain.fire('input');assert.match(h.textContent,/Measured observations are hidden/);button(h,'Clear label search').fire('click');assert.equal(ui.selection().group,'Personal Info');assert.equal(ui.selection().query,'');
button(h,'Task 4 · Response strategies').fire('click');const high=find(h,'Show condition');high.value='High';high.fire('change');const sort=find(h,'Bar order');sort.value='value';sort.fire('change');const term=find(h,'Find chart labels');term.value='Evaluate';term.fire('input');button(h,'Show strategy co-occurrence').fire('click');
assert.equal(ui.selection().group,'High');assert.equal(ui.selection().cooccurrence,true);
button(h,'Task 3 · Generated response safety').fire('click');assert.equal(ui.selection().group,'Personal Info');
button(h,'Task 4 · Response strategies').fire('click');assert.equal(ui.selection().group,'High');assert.equal(ui.selection().query,'Evaluate');assert.equal(ui.selection().sort,'value');assert.equal(ui.selection().cooccurrence,true);
const reloaded=new Element('div'),restored=ctx.window.KoEVDDetailCharts.mount(reloaded,[fixture]);assert.equal(restored.selection().task,'4');assert.equal(restored.selection().group,'High');assert.equal(restored.selection().query,'Evaluate');button(reloaded,'Task 3 · Generated response safety').fire('click');assert.equal(restored.selection().group,'Personal Info');
const pairHolder=new Element('div'),pairUi=ctx.window.KoEVDDetailCharts.mount(pairHolder,[fixture,{...fixture,submission_id:'other'}],{selection:ui.selection()});button(pairHolder,'Task 3 · Generated response safety').fire('click');assert.equal(pairUi.selection().group,'Personal Info');button(pairHolder,'Task 4 · Response strategies').fire('click');assert.equal(pairUi.selection().group,'High');
const missing=JSON.parse(JSON.stringify(fixture));missing.analysis.tasks['4'].groups=[];const missingHolder=new Element('div'),missingUi=ctx.window.KoEVDDetailCharts.mount(missingHolder,[missing],{selection:ui.selection()});assert.equal(missingUi.selection().group,'');assert.match(missingHolder.textContent,/saved condition is unavailable/);
assert.equal(walk(h).find(n=>n.className==='detail-key-metrics'),undefined,'Task 4 completeness must not be a hero score');assert.match(h.textContent,/Measurement completeness:.*not a performance score/);
const canonical=JSON.parse(fs.readFileSync('docs/strategy_label_map.json','utf8'));assert.equal(Object.keys(charts.STRATEGY_GUIDE).length,15);for(const [code,name]of Object.entries(canonical)){assert.equal(charts.strategyInfo(code).name,name);assert(charts.strategyInfo(code).definition);assert(charts.strategyInfo(code).example);}
assert.equal(charts.strategyInfo('Agreeing Speech').name,'Conditional Empathy');assert.equal(charts.strategyInfo('Info Providing').name,'Safe Information');assert(charts.matchesLabel({label:'c_info providing'},'Information Providing'));assert(charts.matchesLabel({label:'c_info providing'},'Safe Information'));assert.match(h.textContent,/newly written illustrations, not benchmark responses or gold annotations/);
for(const model of paper.models)for(const label of Object.keys(model.task4_rates))if(!['Model','Unsafe'].includes(label))assert(charts.strategyInfo(label),'Historical strategy alias: '+label);
const coverage={task:5,family:'paper_coverage',kind:'rate_bars'};assert.match(charts.chartCaption(coverage),/Parse coverage ↑/);assert.doesNotMatch(charts.chartCaption(coverage),/Unsafe\/error rate ↓/);
console.log('Task context journeys passed: search/candidate recovery, per-Task full views, reload/handoff, explicit fallbacks, completeness and canonical strategy illustrations');
`;
eval(test);
