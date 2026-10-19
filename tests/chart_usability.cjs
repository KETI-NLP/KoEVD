/* Regression journeys for the reported ordering, composition and comparison defects. */
const fs=require('node:fs');
let test=fs.readFileSync('tests/detail_charts.cjs','utf8').split('const before=JSON.stringify(summary)')[0];
test+=String.raw`
assert.deepEqual(charts.categoryOrder(['Extreme','Benign','Moderate','High','Low'],'severity_band'),['Benign','Low','Moderate','High','Extreme']);
assert.deepEqual(charts.categoryOrder(['Explicit','Implicit','Neutral'],'explicitness'),['Neutral','Implicit','Explicit']);
const fixture=JSON.parse(JSON.stringify(summary));
const whole=fixture.analysis.tasks['4'].partitions[0];
const inclusion={'a_boundary setting':{count:4,classified:10,rate_on_classified:.4},'a_evaluation':{count:8,classified:10,rate_on_classified:.8}};
Object.assign(whole,{strategy_inclusion:inclusion,unsafe_marker:{count:1,classified:10,rate_on_classified:.1},co_occurrence:[],valid_sources:10});
fixture.analysis.tasks['4'].groups=[{...whole,partition_kind:'all',partition_name:'all',axis:'severity_band',value:'High'}];
fixture.analysis.charts.find(c=>c.task===4).data=[{label:'a_evaluation',...r(8,10)},{label:'a_boundary setting',...r(4,10)}];
const allStrategies=charts.selectCharts(fixture,{task:'4',scope:'all:all',axis:'severity_band',group:''}).find(c=>c.family==='strategy');
const highStrategies=charts.selectCharts(fixture,{task:'4',scope:'all:all',axis:'severity_band',group:'High'}).find(c=>c.family==='strategy');
assert.deepEqual(highStrategies.data.map(d=>d.label),allStrategies.data.map(d=>d.label),'Condition selection moved the strategy rows');
const c1={kind:'rate_bars',task:3,family:'group',title:'Types',data:[{label:'A',...r(2,10)},{label:'B',...r(4,10)},{label:'Zero',...r(0,10)}]};
const c2={...c1,data:[{label:'A',...r(8,10)},{label:'B',...r(1,10)}]};
const grouped=charts.comparisonBars([c1,c2],[fixture,{...fixture,model:{id:'OTHER'}}],{sort:'value',axis:'utterance_type'});
assert.deepEqual(grouped.data.map(d=>d.label),['A','A','B','B','Zero','Zero']);
assert.equal(grouped.data[4].value,0);assert.equal(grouped.data[5].value,null);assert.equal(grouped.data[5].missing,true);
const chosen={task:'4',scope:'all:all',axis:'severity_band',group:'High',sort:'reported'};
const mount=new Element('div');const active=ctx.window.KoEVDDetailCharts.mount(mount,[fixture,{...fixture,model:{id:'OTHER'}}],{selection:chosen});
assert.equal(active.selection().task,'4');assert.equal(active.selection().group,'High');assert.match(mount.textContent,/Model 1/);assert.match(mount.textContent,/Model 2/);
button(mount,'Task 5 · Simulated tool choices').fire('click');
const query=find(mount,'Find chart labels');query.value='unsafe tool';query.fire('input');
const compositionSections=walk(mount).filter(n=>n.tagName==='section'&&n.children[0]?.children?.[0]?.textContent==='Strict outcome composition · all expected rows');
assert.equal(compositionSections.length,2);
for(const section of compositionSections){const drawing=walk(section).find(n=>n.tagName==='svg');const marks=walk(drawing).filter(n=>n.attrs.role==='button');assert.equal(marks.length,14);assert.deepEqual(marks.slice(0,7).map(n=>n.attrs['aria-label'].split(';')[0]),['Unsafe tool','Allowed tool','Other available tool','Refusal','Answer without tool','Ask clarification','Invalid / unmeasured']);assert.match(section.textContent,/retains all outcomes|retain all outcomes/);}
const rawTransition={kind:'transition_matrix',task:5,family:'transition',title:'Transitions',data:[{response_label:'unsafe',tool_outcome:'unsafe_tool',count:3,sources:784},{response_label:'unsafe',tool_outcome:'invalid',count:15,sources:784}]};
const transition=charts.transitionMatrix(rawTransition);assert.equal(transition.data[0].denominator,18);assert.match(charts.describe(transition.data[0],transition),/full framing, not this row/);assert.match(charts.describe(transition.data[0],transition),/Small group/);
fixture.analysis.signals=[{task:3,partition_kind:'subset',partition_name:'core',axis:'utterance_type',value:'A',group_sources:30,remaining_sources:970,difference_pp:5,group_events:3,group_valid:30,remaining_events:49,remaining_valid:970},{task:3,partition_kind:'subset',partition_name:'core',axis:'utterance_type',value:'Tiny',group_sources:9,remaining_sources:991,difference_pp:44,group_events:4,group_valid:9,remaining_events:0,remaining_valid:991}];
const review=charts.reviewCandidates(fixture,{task:'3',scope:'subset:core',axis:'utterance_type',group:''});assert.equal(review.higher.length,1);assert.equal(review.higher[0].value,'A');assert.equal(charts.reviewCandidates(fixture,{task:'4'}).unavailable,true);
assert.doesNotMatch(charts.chartCaption({kind:'confusion_matrix',matrixMode:'count'}),/Fixed 0/);assert.match(charts.chartCaption({kind:'count_matrix',countMax:80}),/80/);
console.log('Chart UX regressions passed: semantic order, stable strategies, shared rows, missing vs zero, handoff, complete compositions, explicit denominators and supported contrasts');
`;
eval(test);
