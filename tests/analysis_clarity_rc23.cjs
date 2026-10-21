/* Regressions for observed denominators, evidence-only filtering and live grids. */
const fs=require('node:fs');
let test=fs.readFileSync('tests/detail_charts.cjs','utf8').split('const before=JSON.stringify(summary)')[0];
test+=String.raw`
const f=JSON.parse(JSON.stringify(summary));
const labels={utterance_type:['HIQ'],topic:['Gender'],severity_band:['High'],explicitness:['Implicit'],risk_category:['Privacy']};
f.analysis.tasks['3'].facets=[{format:'koevd-task3-facets-v1',partition_kind:'subset',partition_name:'core',buckets:[
 {labels,rows:98,valid:69,events:6,unique_sources:98,valid_sources:69},
 {labels:{...labels,topic:['Small']},rows:10,valid:10,events:3,unique_sources:10,valid_sources:10},
 {labels:{...labels,topic:['Complete']},rows:100,valid:100,events:20,unique_sources:100,valid_sources:100}]}];
const strategies={'c_info providing':46,'a_evaluation':12};
f.analysis.tasks['4'].behavior_facets=[{partition_kind:'all',partition_name:'all',buckets:[{labels,rows:98,eligible:69,valid:69,strategies,pairs:{'9:9':46,'0:0':12,'0:9':6},responses:{safe:{rows:63,valid:63,'c_info providing':42},unsafe:{rows:6,valid:6,'c_info providing':4},unclassified:{rows:29,valid:0}}}]}];
f.analysis.tasks['5'].behavior_facets=['safe_guided','tool_forced','unsafe_induced'].map(partition_name=>({partition_kind:'variant',partition_name,buckets:[{labels,rows:784,eligible:784,valid:783,outcomes:{unsafe_tool:140,allowed_tool:625,refuse:18,invalid:1},responses:{safe:{unsafe_tool:137,allowed_tool:611,refuse:17,invalid:1},unsafe:{unsafe_tool:3,allowed_tool:14,refuse:1}}}]}));
const original=JSON.stringify(f),g=JSON.parse(JSON.stringify(f));g.submission_id='second';g.model.id='other';g.analysis.tasks['3'].facets[0].buckets[0].valid=98;g.analysis.tasks['3'].facets[0].buckets[0].valid_sources=98;
const st={scope:'subset:core',facetAxis:'topic'},specs=[f,g].map(s=>charts.facetChart(s,st));
const raw=JSON.stringify(specs),evidenceFiltered=charts.evidenceViews(specs,{minClassified:'20',minCompletion:'90'});
assert.equal(evidenceFiltered.total,3);assert.equal(evidenceFiltered.shown,1);assert.equal(evidenceFiltered.charts[0].data[0].label,'Complete');assert.equal(evidenceFiltered.charts[0].data[0].denominator,100);assert.equal(JSON.stringify(specs),raw);
const masked=charts.evidenceViews([f,g].map(s=>charts.facetChart(s,{...st,crossAxis:'severity_band'},true)),{minClassified:'20',minCompletion:'90'},true);
assert(masked.charts[0].data.find(d=>d.left==='Gender').evidence_hidden);assert.equal(masked.charts[0].data.find(d=>d.left==='Gender').denominator,69);
const holder=new Element('div'),ui=ctx.window.KoEVDDetailCharts.mount(holder,[f,g]);
const set=(label,value)=>{const n=find(holder,label);assert(n,label);n.value=value;n.fire('change');};
set('Analyze input by','topic');set('Minimum classified sources','20');set('Minimum classification completion','90');
assert.match(holder.textContent,/1\/3 groups shown; 2 hidden/);assert.match(holder.textContent,/209 \/ 209|179 \/ 208/);assert.match(holder.textContent,/cohort|Cohort/);
set('Filter Topic','Gender');assert.match(holder.textContent,/No groups meet the display evidence thresholds/);assert.doesNotMatch(holder.textContent,/No inputs match these condition filters/);assert.match(holder.textContent,/6 \/ 69/);button(holder,'Clear condition filters').fire('click');button(holder,'Clear evidence filters').fire('click');assert.equal(ui.selection().minClassified,'0');assert.match(holder.textContent,/3\/3 groups shown; 0 hidden/);
button(holder,'Task 4 · Response strategies').fire('click');set('Co-occurrence view','conditional');
const live=walk(holder).find(n=>n.className==='detail-live-matrix');assert(live);assert.equal(live.attrs.role,'table');assert.equal(walk(live).filter(n=>n.className==='detail-matrix-row-heading').length,15);assert.equal(walk(live).filter(n=>n.attrs.role==='button').length,225);
const selected=walk(live).find(n=>n.attrs.role==='button'&&n.attrs['aria-label'].startsWith('Safe Information → Safe Information;'));selected.fire('click');assert.match(holder.textContent,/Unique input sources in this group: 98/);assert.match(holder.textContent,/Strategy-classified input sources in this cohort: 69/);assert.match(holder.textContent,/Valid \/ expected: 69 \/ 98/);
const compact=walk(holder).find(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Strategy inclusion · all 15 labels (multi-label)');assert(Number(compact.attrs.viewBox.split(' ')[3])<800);assert.equal(walk(compact).filter(n=>n.attrs.role==='button').length,30);assert.match(compact.textContent,/M1 66.67% · 46\/69/);
button(holder,'Task 5 · Simulated tool choices').fire('click');
let variant=charts.behaviorCharts(f,ui.selection()).find(c=>c.family==='variants').data[0];assert.equal(variant.input_sources,784);assert.equal(variant.sources,783);
set('Response-group denominator','all');let bar=charts.behaviorCharts(f,ui.selection()).find(c=>c.family==='response_correspondence').data.find(d=>d.label==='Tool-forced · classifier-safe');assert.equal(bar.input_sources,766);assert.equal(bar.sources,765);assert.equal(bar.denominator,766);
const nodes=walk(holder),localIndex=nodes.findIndex(n=>n.className==='detail-local-control'),compositionIndex=nodes.findIndex(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Seven outcomes · all expected inputs by framing'),responseIndex=nodes.findIndex(n=>n.tagName==='svg'&&n.attrs['aria-label'].startsWith('Unsafe tool choice by Task 3 response label'));assert(compositionIndex<localIndex&&localIndex<responseIndex);
const framing=walk(holder).find(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Unsafe tool selections / valid by framing'),safe=walk(framing).find(n=>n.attrs.role==='button'&&n.attrs['aria-label'].includes('; Safety-guided;'));safe.fire('click');button(holder,'View this framing').fire('click');assert.equal(ui.selection().scope,'variant:safe_guided');button(holder,'Back one condition').fire('click');assert.equal(ui.selection().scope,'variant:tool_forced');
const html=fs.readFileSync('src/koevd_eval/assets/space.html','utf8');assert(!html.includes('Numerical comparisons use identical inputs and jointly valid outputs.'));assert(html.includes('each model’s own valid-output denominator'));
const contrast=(fg,bg)=>{const lum=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);return (Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05);};for(const c of [[35,116,151],[177,62,54],[23,100,116]])assert(contrast([18,36,59],c.map(v=>v*.46+255*.54))>=4.5);
assert.equal(JSON.stringify(f),original);
console.log('Analysis clarity passed: evidence thresholds leave cohorts unchanged; shared support masking, unique/valid/row counts, live matrix axes and contrast, compact strategy pairs, framing action/undo and local denominator scope.');
`;
eval(test);
