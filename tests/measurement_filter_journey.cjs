/* Actual shipped tables; measurement declarations and APIs are synthetic. */
const fs=require('node:fs');
let source=fs.readFileSync('tests/comparison_journey.cjs','utf8').split('(async()=>{')[0];
source=source.replace("let pending=[],createdHome;",`const declaration=batch=>({status:'user_reported',conditions_sha256:'SYNTHETIC-batch-'+batch,conditions:{batch_size:batch,requested_dtype:'float32',observed_parameter_dtypes:['torch.float32']}});
for(const p of pubs)p.measurements={'3':declaration(2),'4':declaration(p.submission_id==='b'?4:2)};
let pending=[],createdHome;`);
source+=String.raw`(async()=>{
 await tick();await tick();createdHome.focusModel('a');
 const tab=t=>node('task-tabs').children.find(b=>b.dataset.task===t).fire('click');
 tab('4');assert.equal(node('measurement-controls').hidden,false);assert.match(node('home-results').textContent,/batch 2/);assert.match(node('home-results').textContent,/batch 4/);assert.equal(node('measurement-filter').options.length,3);
 node('measurement-filter').value='SYNTHETIC-batch-4';node('measurement-filter').fire('change');assert.match(node('home-status').textContent,/1\/2/);assert.doesNotMatch(node('home-results').textContent,/SYNTHETIC-a/);assert.match(node('home-results').textContent,/SYNTHETIC-b/);
 createdHome.render(board);assert.equal(node('measurement-filter').value,'SYNTHETIC-batch-4');assert.match(node('home-status').textContent,/1\/2/);
 tab('2');assert.equal(node('measurement-controls').hidden,true);assert.match(node('home-status').textContent,/2\/2/);
 tab('3');assert.equal(node('measurement-filter').value,'all');assert.match(node('home-status').textContent,/2\/2/);
 tab('4');assert.equal(node('measurement-filter').value,'SYNTHETIC-batch-4');createdHome.focusModel('a');assert.equal(node('measurement-filter').value,'all');assert.match(node('home-status').textContent,/2\/2/);
 delete pubs[0].measurements;createdHome.render(board);assert.match(node('home-results').textContent,/Measurement conditions unknown/);assert.equal(node('measurement-filter').options.length,3);
 node('measurement-filter').value='unknown';node('measurement-filter').fire('change');assert.match(node('home-status').textContent,/1\/2/);
 node('result-collection').value='paper';node('result-collection').fire('change');assert.equal(node('measurement-controls').hidden,true);assert.match(node('home-status').textContent,/12\/12/);
 console.log('Measurement display/filter: Task-specific declarations, unknowns, generation cohorts unchanged, unrelated tasks unaffected and focused-model recovery passed');
})().catch(e=>{console.error(e);process.exitCode=1});`;
eval(source);
