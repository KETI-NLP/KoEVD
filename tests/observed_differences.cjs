/* Descriptive marginal pp must remain separate from paired and within-model effects. */
const fs=require('node:fs');
let test=fs.readFileSync('tests/detail_charts.cjs','utf8').split('const before=JSON.stringify(summary)')[0];
test+=String.raw`
const first={...summary,model:{id:'LEFT'}},second={...summary,model:{id:'RIGHT'}},make=(task,family,data)=>({task,family,kind:'rate_bars',title:'Measured group rates',scope_label:'Core',condition_label:'All conditions',data});
const left=make(3,'group',[{label:'A',...r(2,40)},{label:'Zero',...r(0,30)},{label:'Tiny',...r(4,9)},{label:'Missing',...r(2,50)}]),right=make(3,'group',[{label:'A',...r(3,50)},{label:'Zero',...r(0,30)},{label:'Tiny',...r(0,9)}]);
const rows=charts.observedDifferences([[left],[right]],[first,second]),a=rows.find(d=>d.group==='A');assert(Math.abs(a.difference_pp+1)<1e-10);assert.equal(a.left.denominator,40);assert.equal(a.right.denominator,50);assert.equal(a.paired_effect,false);assert.equal(a.comparison_kind,'observed_marginal_rates');assert.match(a.interpretation,/Model 1 has lower/);
assert.equal(rows.find(d=>d.group==='Zero').difference_pp,0);assert.equal(rows.find(d=>d.group==='Missing').difference_pp,null);assert.equal(rows.find(d=>d.group==='Tiny').limited_support,true);assert.equal(rows[0].group,'A','Adequate support must precede the larger tiny-group difference');
const swapped=charts.observedDifferences([[right],[left]],[second,first]).find(d=>d.group==='A');assert(Math.abs(a.difference_pp+swapped.difference_pp)<1e-10);assert.match(swapped.interpretation,/Model 2 has lower/);
const accuracy=charts.observedDifferences([[make(2,'variants',[{label:'Choose safest',...r(8,10)}])],[make(2,'variants',[{label:'Choose safest',...r(7,10)}])]], [first,second])[0];assert(Math.abs(accuracy.difference_pp-10)<1e-10);assert.match(accuracy.interpretation,/Model 1 has higher observed accuracy/);
const strategy=charts.observedDifferences([[make(4,'strategy',[{label:'a_evaluation',...r(8,10)}])],[make(4,'strategy',[{label:'a_evaluation',...r(7,10)}])]], [first,second])[0];assert.match(strategy.interpretation,/no quality preference/);
const historical=charts.observedDifferences([[make(1,'paper_summary',[{label:'Unsafe judgments',value:.4,numerator:null,denominator:null}])],[make(1,'paper_summary',[{label:'Unsafe judgments',value:.5,numerator:null,denominator:null}])]], [{...first,historical:true},{...second,historical:true}])[0];assert.equal(historical.left.denominator,null);assert.equal(historical.limited_support,true);assert.match(historical.interpretation,/no quality preference/);
assert.equal(charts.observedDifferences([[make(5,'paper_coverage',[{label:'Safe-Guided',...r(8,10)}])],[make(5,'paper_coverage',[{label:'Safe-Guided',...r(7,10)}])]], [first,second]).length,0);
const holder=new Element('div');ctx.window.KoEVDDetailCharts.mount(holder,[first,second]);assert.match(holder.textContent,/Between-model observed rate differences/);assert.match(holder.textContent,/Within-model group contrasts/);assert.match(holder.textContent,/not jointly valid paired effects/);assert.match(holder.textContent,/Different from the within-model/);
button(holder,'Task 5 · Simulated tool choices').fire('click');assert(walk(holder).filter(n=>n.tagName==='text').some(n=>n.textContent==='Valid 10/12 · 83.33%'),'Grouped framing bars must retain per-model valid/expected counts');
console.log('Observed difference journeys passed: signs, denominators, swaps, zero/missing, support order, historical/strategy limits and separate comparison kinds');
`;
eval(test);
