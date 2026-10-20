/* Actual historical models through the same shipped renderer and controls. */
const fs=require('node:fs');
let script=fs.readFileSync('tests/detail_charts.cjs','utf8').split('const before=JSON.stringify(summary)')[0];
script+=String.raw`
const profiles=paper.models.map(charts.paperProfile);let observations=0,pairs=0;
for(const profile of profiles){
 const source=profile.paper.task3_types,selection={task:'3',scope:'paper',task3Metric:'rate',task3Outcome:'both',task3Axis:'topic'};
 const data=charts.task3TypeData(profile,'paper');assert.equal(data.length,11);assert.equal(data.reduce((n,d)=>n+d.valid,0),source.valid);assert.equal(data.reduce((n,d)=>n+d.safe_count,0),source.safe);
 for(const metric of ['rate','count'])for(const outcome of ['both','safe','unsafe'])for(const type of ['',...data.map(d=>d.label)])for(const axis of type?['topic','severity_band','explicitness']:['topic']){
  const c=charts.task3TypeChart(profile,{...selection,task3Metric:metric,task3Outcome:outcome,task3Axis:axis},type);assert(c);
  for(const d of c.data){assert.equal(d.safe_count+d.unsafe_count,d.valid);assert.equal(d.denominator,d.valid);assert.equal(d.coverage,d.valid/d.expected);if(d.valid){assert.equal(d.safe_rate,d.safe_count/d.valid);assert.equal(d.unsafe_rate,d.unsafe_count/d.valid);}else{assert.equal(d.safe_rate,null);assert.equal(d.unsafe_rate,null);}observations++;}
 }
 const h=new Element('div'),ui=ctx.window.KoEVDDetailCharts.mount(h,[profile]);assert.equal(ui.selection().scope,'paper');assert.match(h.textContent,/Historical paper experiment: 13,552/);assert.doesNotMatch(h.textContent,/No model-specific question/);
}
for(let i=0;i<profiles.length;i++)for(let j=i+1;j<profiles.length;j++)for(const metric of ['rate','count'])for(const outcome of ['both','safe','unsafe']){
 const selection={task:'3',scope:'paper',task3Metric:metric,task3Outcome:outcome},cs=[profiles[i],profiles[j]].map(s=>charts.task3TypeChart(s,selection)),c=charts.comparisonBars(cs,[profiles[i],profiles[j]],{sort:'value'});assert.equal(c.data.length,22);assert(c.data.every(d=>!d.missing));pairs++;
}
const left=profiles.find(p=>p.name==='GPT-5.4'),right=profiles.find(p=>p.name==='Claude Haiku 4.5'),holderPaper=new Element('div');let comparison=0;
const uiPaper=ctx.window.KoEVDDetailCharts.mount(holderPaper,[left],{onCompare:()=>comparison++});const type=find(holderPaper,'Filter Question / utterance type');type.value='Expressing Opinion';type.fire('change');const axis=find(holderPaper,'Analyze input by');axis.value='severity_band';axis.fire('change');button(holderPaper,'Compare this cohort with another model').fire('click');assert.equal(comparison,1);
const pairedPaper=new Element('div'),pairUi=ctx.window.KoEVDDetailCharts.mount(pairedPaper,[left,right],{selection:uiPaper.selection()});assert.equal(pairUi.selection().filter_utterance_type,'Expressing Opinion');assert.equal(pairUi.selection().facetAxis,'severity_band');assert.match(pairedPaper.textContent,/not jointly valid paired effects/);assert.match(pairedPaper.textContent,/Safe .*Unsafe/);
const mode=find(pairedPaper,'Chart measure');mode.value='count';mode.fire('change');assert.equal(pairUi.selection().task3Metric,'count');const show=find(pairedPaper,'Response safety shown');show.value='unsafe';show.fire('change');assert.match(pairedPaper.textContent,/Observed unsafe count/);
const old={...left,paper:{...left.paper,task3_types:null}},oldHolder=new Element('div');assert.equal(charts.task3TypeData(old,'paper').length,0);ctx.window.KoEVDDetailCharts.mount(oldHolder,[old]);assert.match(oldHolder.textContent,/Per-model type breakdowns were not released/);
console.log(JSON.stringify({passed:true,models:12,observations,pair_views:pairs,distinct_pairs:66,raw_cases_exposed:false}));
`;
eval(script);
