/* Actual registration/navigation script, with synthetic public APIs and a renderer spy. */
const fs=require('node:fs');
let test=fs.readFileSync('tests/comparison_journey.cjs','utf8').split('(async()=>{')[0];
test=test.replace("scope:'summary',rank_admission", "analysis:{charts:[{}]},scope:'summary',rank_admission");
test+=String.raw`
(async()=>{
 const selected={task:'4',scope:'all:all',axis:'severity_band',group:'High',sort:'reported',query:'',cooccurrence:false};
 const renders=[];window.KoEVDDetailCharts={paperProfile:m=>({name:m.name}),mount(holder,summaries,options={}){renders.push({summaries,options});return {selection:()=>({...selected})};}};
 await tick();await tick();location.hash='#model=b';window.dispatchEvent({type:'hashchange'});await tick();await tick();
 assert(renders.some(r=>r.summaries.length===1));assert.equal(typeof renders.findLast(r=>r.summaries.length===1).options.onCompare,'function');renders.findLast(r=>r.summaries.length===1).options.onCompare();await tick();assert.equal(pending.length,1);resolvePair(pending.shift());await tick();await tick();
 const pair=renders.findLast(r=>r.summaries.length===2);assert.deepEqual(pair.options.selection,selected);
 // Rebuilding with another right model retains the active chart selection.
 node('public-pair-right').value='c';node('public-pair-right').fire('change');node('public-pair-build').fire('click');await tick();resolvePair(pending.shift());await tick();await tick();assert.deepEqual(renders.findLast(r=>r.summaries.length===2).options.selection,selected);
 await createdHome.paperDetail('Apertus 8B');await createdHome.paperCompare('Apertus 8B','GPT-5.4');assert.deepEqual(renders.findLast(r=>r.summaries.length===2).options.selection,selected);
 console.log('Detail-to-comparison handoff passed for registered, changed-pair and historical model flows');
})().catch(e=>{console.error(e);process.exitCode=1});`;
eval(test);
