/* Numerical/DOM regressions across every archived model, not screenshot-only assertions. */
const fs=require('node:fs');
let code=fs.readFileSync('tests/detail_charts.cjs','utf8').split('const before=JSON.stringify(summary)')[0];
code+=String.raw`
let checked=0;
const fallbackHolder=new Element('div'),fallback=ctx.window.KoEVDDetailCharts.mount(fallbackHolder,[summary]);button(fallbackHolder,'Task 4 · Response strategies').fire('click');assert.equal(button(fallbackHolder,'Co-occurrence not supplied').disabled,true,'Unavailable co-occurrence must not be an inert active control');
const models=paper.models.map(m=>({...m,behavior:JSON.parse(fs.readFileSync('src/koevd_eval/assets/'+m.behavior_asset,'utf8')).tasks}));
for(const m of models){const s=charts.paperProfile(m);for(const task of ['4','5'])for(const cube of m.behavior[task]){
 const scope=cube.partition_kind+':'+cube.partition_name,st={task,scope,axis:'severity_band',strategy:'a_boundary setting',responseDenominator:'valid',cooccurrence:true,cooccurrenceMode:'conditional'};
 const q=charts.behaviorQuery(s,task,scope),tot=q.total;assert.equal(tot.expected,task==='4'?13552:784);
 for(const axis of ['utterance_type','topic','severity_band','explicitness']){
  const domain=charts.behaviorDomains([s],st,axis);
  for(const label of domain){const filter={[axis]:label},selected=cube.buckets.filter(b=>b.labels[axis].includes(label)),result=charts.behaviorQuery(s,task,scope,filter).total;assert.equal(result.expected,selected.reduce((n,b)=>n+b.rows,0));assert.equal(result.valid,selected.reduce((n,b)=>n+b.valid,0));checked++;}
 }
 const filters={topic:'Gender',severity_band:'High',explicitness:'Implicit'},manual=cube.buckets.filter(b=>Object.entries(filters).every(([a,v])=>b.labels[a].includes(v))),filtered=charts.behaviorQuery(s,task,scope,filters).total;assert.equal(filtered.expected,manual.reduce((n,b)=>n+b.rows,0));
 const specs=charts.behaviorCharts(s,st);for(const c of specs)for(const d of c.data)if(d.value!=null){assert(d.value>=0&&d.value<=1);if(d.numerator!=null)assert(Math.abs(d.value-d.numerator/d.denominator)<1e-12);}
 if(task==='5'){const composition=specs.find(c=>c.family==='composition');for(const frame of ['safe_guided','tool_forced','unsafe_induced'])assert.equal(composition.data.filter(d=>d.left===frame).reduce((n,d)=>n+d.count,0),784);const correspondence=specs.find(c=>c.family==='transition');assert.equal(correspondence.data.reduce((n,d)=>n+d.count,0),784);}
 else {const matrix=specs.find(c=>c.family==='behavior_cooccurrence');for(const d of matrix.data.filter(d=>d.left===d.right&&d.denominator))assert.equal(d.value,1);}
 }}
const m=models.find(m=>m.name==='GPT-5.4'),a=models.find(m=>m.name==='Apertus 8B');
const holder=new Element('div'),ui=ctx.window.KoEVDDetailCharts.mount(holder,[charts.paperProfile(m),charts.paperProfile(a)]);
const set=(label,value)=>{const n=find(holder,label);assert(n,label);n.value=value;n.fire('change');};
set('Analyze input by','severity_band');const severity=walk(holder).find(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Safe / unsafe by Input severity');const labels=walk(severity).filter(n=>n.attrs.role==='button').map(n=>n.attrs['aria-label'].split(';')[1]?.trim()||n.attrs['aria-label'].split(';')[0]);
assert.deepEqual([...new Set(labels)],['Benign','Low','Moderate','High','Extreme','HD/borderline']);
button(holder,'Task 4 · Response strategies').fire('click');assert.equal(ui.selection().scope,'all:all');assert.match(holder.textContent,/all 15 labels/);assert.match(holder.textContent,/strategy-eligible/);assert.match(holder.textContent,/excludes Unsafe marker/);
set('Filter Topic','Gender');set('Filter Input severity','High');set('Filter Explicitness','Implicit');set('Focus strategy','c_info providing');set('Co-occurrence view','conditional');assert.match(holder.textContent,/P\(column \| row\)/);assert.match(holder.textContent,/Same|Task 3 response classification/);
const task4View=ui.selection();assert.equal(task4View.filter_topic,'Gender');assert.equal(task4View.strategy,'c_info providing');
button(holder,'Task 5 · Simulated tool choices').fire('click');assert.equal(ui.selection().filter_topic,'','Task-specific filters must not leak');assert.equal(ui.selection().scope,'variant:tool_forced');assert.match(holder.textContent,/Seven outcomes/);assert.match(holder.textContent,/same input/i);set('Filter Topic','Gender');set('Response-group denominator','all');assert.match(holder.textContent,/all matched inputs/);
const transition=walk(holder).find(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Same-input correspondence · Task 3 label × Task 5 outcome');assert(walk(transition).some(n=>n.tagName==='rect'&&n.attrs.fill?.startsWith('rgba(23,100,116,')),'Allowed choices use teal, not risk red');assert(walk(transition).some(n=>n.tagName==='text'&&n.textContent.includes('/')),'Cell counts remain visible');
const framingPlot=walk(holder).find(n=>n.tagName==='svg'&&n.attrs['aria-label']==='Unsafe / valid · Tool risk category × framing'),framingCell=walk(framingPlot).find(n=>n.attrs.role==='button'&&n.attrs['aria-label'].includes('→ Safety-guided')&&!n.attrs['aria-label'].includes('N/A'));framingCell.fire('click');button(holder,'Apply this input condition').fire('click');assert.equal(ui.selection().scope,'variant:safe_guided');button(holder,'Back one condition').fire('click');assert.equal(ui.selection().scope,'variant:tool_forced');assert.equal(ui.selection().filter_topic,'Gender');
button(holder,'Task 4 · Response strategies').fire('click');assert.equal(ui.selection().strategy,'c_info providing');assert.equal(ui.selection().filter_severity_band,'High');
set('Filter Topic','Gender');button(holder,'Clear condition filters').fire('click');assert.equal(ui.selection().filter_topic,'');button(holder,'Back one condition').fire('click');assert.equal(ui.selection().filter_topic,'Gender');
console.log('Behavior charts passed: '+checked+' independently summed historical metadata groups, four-way AND, 15 strategies, directional co-inclusion, seven outcomes, same-input correspondence, semantic ordering and task-isolated recovery.');
`;
eval(code);
