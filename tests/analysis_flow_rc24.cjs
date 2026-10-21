/* First-user recovery, explicit cohort transfer and comparison evidence. */
const fs=require('node:fs');
let test=fs.readFileSync('tests/detail_charts.cjs','utf8').split('const before=JSON.stringify(summary)')[0];
test+=String.raw`
let lastScroll=null,lastFocus=null;
Element.prototype.scrollIntoView=function(){lastScroll=this;};
Element.prototype.focus=function(){lastFocus=this;};
Element.prototype.getAttribute=function(k){return this.attrs[k]??null;};
const oldRect=Element.prototype.getBoundingClientRect;
Element.prototype.getBoundingClientRect=function(){return this.className==='detail-tooltip'?{width:320,height:395,left:0,top:0}:oldRect.call(this);};
for(const viewport of [{width:1280,height:720},{width:390,height:844},{width:320,height:400}])for(const anchor of [{x:0,y:0},{x:viewport.width-1,y:viewport.height-1},{x:500,y:400}]){
 const p=charts.tooltipPosition(anchor,{width:320,height:395},viewport);
 assert(p.left>=8&&p.top>=8);assert(p.left+Math.min(320,viewport.width-16)<=viewport.width-8);assert(p.top+Math.min(395,viewport.height-16)<=viewport.height-8);
}
const f=JSON.parse(JSON.stringify(summary)),labels={utterance_type:['HIQ'],topic:['Gender'],severity_band:['High'],explicitness:['Implicit'],risk_category:['Privacy']};
f.analysis.tasks['3'].facets=[{format:'koevd-task3-facets-v1',partition_kind:'subset',partition_name:'core',buckets:[
 {labels,rows:64,valid:64,events:34,unique_sources:64,valid_sources:64},
 {labels:{...labels,topic:['Other']},rows:200,valid:200,events:10,unique_sources:200,valid_sources:200}]}];
const b4={labels,rows:64,eligible:64,valid:64,strategies:{'c_info providing':40},pairs:{'9:9':40},responses:{safe:{rows:30,valid:30,'c_info providing':20},unsafe:{rows:34,valid:34,'c_info providing':20}}};
f.analysis.tasks['4'].behavior_facets=[{partition_kind:'all',partition_name:'all',buckets:[b4]},{partition_kind:'subset',partition_name:'core',buckets:[b4]},{partition_kind:'subset',partition_name:'task5_overlap',buckets:[b4]}];
f.analysis.tasks['4'].partitions.push(p('subset','task5_overlap',64));
f.analysis.tasks['5'].behavior_facets=['safe_guided','tool_forced','unsafe_induced'].map(partition_name=>({partition_kind:'variant',partition_name,buckets:[{labels,rows:10,eligible:10,valid:9,outcomes:{unsafe_tool:2,allowed_tool:7,invalid:1},responses:{safe:{unsafe_tool:1,allowed_tool:6,invalid:1},unsafe:{unsafe_tool:1,allowed_tool:1}}}]}));
const g=JSON.parse(JSON.stringify(f));g.submission_id='second';g.model.id='SYNTHETIC-second';g.analysis.tasks['5'].behavior_facets[1].buckets[0].outcomes={unsafe_tool:3,allowed_tool:6,invalid:1};
const before=JSON.stringify([f,g]);
const transfer=charts.conditionTransferPlan([f,g],{task:'3',scope:'subset:core',filter_topic:'Gender',filter_severity_band:'High',filter_explicitness:'Implicit'},'4');
assert.equal(transfer.scope,'subset:core');assert.deepEqual(transfer.source_counts,[64,64]);assert.deepEqual(transfer.target_counts,[64,64]);assert.equal(transfer.filters.topic,'Gender');
const to5=charts.conditionTransferPlan([f,g],{task:'3',scope:'subset:core',filter_topic:'Gender'},'5');assert.equal(to5.scope,'variant:tool_forced');assert.deepEqual(to5.target_counts,[10,10]);
const from5=charts.conditionTransferPlan([f,g],{task:'5',scope:'variant:tool_forced',filter_risk_category:'Privacy',filter_topic:'Gender'},'4');assert.equal(from5.scope,'subset:task5_overlap');assert.deepEqual(from5.omitted,['Tool risk category']);assert(!Object.hasOwn(from5.filters,'risk_category'));
const missing=charts.conditionTransferPlan([f,g],{task:'3',scope:'subset:core',filter_topic:'Other'},'5');assert.deepEqual(missing.missing,['Topic: Other']);assert.deepEqual(missing.target_counts,[0,0]);
const holder=new Element('div'),ui=ctx.window.KoEVDDetailCharts.mount(holder,[f,g]);
const set=(label,value)=>{const n=find(holder,label);assert(n,label);n.value=value;n.fire('change');};
set('Analyze input by','topic');set('Minimum classified sources','100');
assert.match(holder.textContent,/Hidden by your display evidence thresholds/);assert.match(holder.textContent,/1\/2 groups shown; 1 hidden/);
button(holder,'Apply Gender and keep evidence filters').fire('click');assert.equal(ui.selection().minClassified,'100');assert.match(holder.textContent,/No groups meet the display evidence thresholds/);
button(holder,'Clear condition filters').fire('click');button(holder,'Inspect Gender and clear evidence filters').fire('click');assert.equal(ui.selection().minClassified,'0');assert.equal(ui.selection().minCompletion,'0');assert.equal(ui.selection().filter_topic,'Gender');assert.match(holder.textContent,/34 \/ 64/);assert.doesNotMatch(holder.textContent,/No groups meet the display evidence thresholds/);
button(holder,'Analyze this condition in Task 4').fire('click');assert.equal(ui.selection().task,'4');assert.equal(ui.selection().scope,'subset:core');assert.equal(ui.selection().filter_topic,'Gender');assert.match(holder.textContent,/Copied input conditions from Task 3/);
button(holder,'Task 3 · Generated response safety').fire('click');assert.equal(ui.selection().filter_topic,'Gender');assert.equal(ui.selection().scope,'subset:core');
button(holder,'Task 4 · Response strategies').fire('click');set('Focus strategy','c_info providing');
let drawing=walk(holder).find(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Strategy inclusion · all 15 labels (multi-label)'),mark=walk(drawing).find(n=>n.attrs.role==='button');
lastScroll=lastFocus=null;mark.fire('mouseenter',{clientX:990,clientY:790});assert.equal(lastScroll,null);assert.equal(lastFocus,null);let tip=walk(holder).find(n=>n.className==='detail-tooltip');assert(parseFloat(tip.style.top)+395<=window.innerHeight-8);assert.match(tip.textContent,/Select for full evidence/);assert.doesNotMatch(tip.textContent,/Strategy: Evaluate Utterance/);
mark.fire('click');assert.equal(lastScroll.attrs['aria-label'],'Selected observation');assert.equal(lastFocus,lastScroll);assert.match(holder.textContent,/Same selected observation · both models/);button(holder,'Back to selected mark').fire('click');assert.equal(lastFocus,mark);
button(holder,'Task 5 · Simulated tool choices').fire('click');
lastScroll=null;button(holder,'Response safety correspondence').fire('click');assert.equal(lastScroll.className,'detail-local-control');assert.equal(lastFocus,lastScroll);
const selected=[f,g].map(s=>charts.behaviorCharts(s,{task:'5',scope:'variant:tool_forced',axis:'risk_category',responseDenominator:'valid'}));
const composed=charts.comparisonComposition(selected.map(list=>list.find(c=>c.family==='composition')),[f,g]);assert.equal(composed.data.length,42);for(let i=0;i<2;i++)for(const framing of ['safe_guided','tool_forced','unsafe_induced']){
 const data=composed.data.filter(d=>d.seriesIndex===i&&d.left===framing);assert.equal(data.reduce((n,d)=>n+d.numerator,0),10);assert.equal(data.find(d=>d.right==='invalid').numerator,1);assert(data.every(d=>d.denominator===10));
}
drawing=walk(holder).find(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Seven outcomes · all expected inputs by framing');assert(drawing);assert.equal(walk(holder).filter(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Seven outcomes · all expected inputs by framing').length,1);assert.equal(walk(drawing).filter(n=>n.attrs.role==='button').length,42);assert.match(drawing.textContent,/Model 1/);assert.match(drawing.textContent,/Model 2/);
mark=walk(drawing).find(n=>n.attrs.role==='button'&&n.attrs['aria-label'].includes('; Unsafe tool;'));mark.fire('click');assert.match(holder.textContent,/Same selected observation · both models/);assert.match(holder.textContent,/2\/10/);
const expand=button(holder,'Expand chart height');expand.fire('click');assert.equal(expand.textContent,'Collapse chart height');expand.fire('click');assert.equal(expand.textContent,'Expand chart height');
assert.equal(JSON.stringify([f,g]),before,'View operations changed stored measurements');
console.log('Analysis flow passed: actual-size tooltip bounds, explicit evidence reveal/return, local denominator navigation, hidden-candidate recovery, exact paired compositions, both-model evidence and opt-in cross-task scope/count preview.');
`;
eval(test);
