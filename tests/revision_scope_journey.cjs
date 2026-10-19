/* Reuse the full shipped navigation/registration harness with owner API states. */
const fs=require('node:fs');
let source=fs.readFileSync('tests/comparison_journey.cjs','utf8').split('(async()=>{')[0];
source=source.replace("const workspace={", "let ownerItem={id:'a',owner:'SYNTHETIC-owner',version:2,head_revision:1,workflow:'registered',display:{display_name:'SYNTHETIC owner run'},publication:{status:'published',revision:1,scope:'summary'}};\nconst workspace={");
source=source.replace("({enabled:true})", "({enabled:true,self_reported_summaries_enabled:true})");
source=source.replace("if(path==='/api/identity')return {json:async()=>({signed_in:false})};", "if(path==='/api/identity')return {json:async()=>({signed_in:true,subject:'SYNTHETIC-owner',username:'SYNTHETIC owner'})};\n if(path.startsWith('/api/submissions?'))return {json:async()=>({items:[ownerItem],next_cursor:null})};\n if(path==='/api/submissions/a')return {json:async()=>ownerItem};\n if(path.startsWith('/api/public/submissions?'))return {json:async()=>({items:pubs,next_cursor:null})};");
source+=`(async()=>{
 await tick();await tick();
 const open=async()=>{node('submission-list').children[0].fire('click');await tick();await tick();};
 const walk=n=>[n,...n.children.flatMap(walk)];
 await open();assert.match(node('registration-progress').textContent,/public revision 1/);
 ownerItem={...ownerItem,head_revision:2,workflow:'draft',version:3};await open();
 assert.match(node('registration-progress').textContent,/revision 2 is private.*public revision 1/);
 assert.match(node('submission-next').textContent,/fresh reason, permission statement and consent/);
 assert.match(node('submission-original').textContent,/revision 2/);
 const ownerButtons=walk(node('submission-actions')).filter(n=>n.tagName==='button');
 assert(ownerButtons.some(n=>n.textContent==='Publish numerical summary'));assert(ownerButtons.some(n=>n.textContent==='Analyze saved result (revision 2)'));
 ownerButtons.find(n=>n.textContent==='Compare this result (public revision 1)').fire('click');await tick();await tick();
 assert.equal(node('public-pair-left').value,'a');assert.equal(pending.length,1,node('submission-status').textContent);resolvePair(pending.shift());await tick();await tick();
 assert.match(node('public-pair-results').textContent,/Public revisions: left 1/);
 ownerItem={...ownerItem,publication:{...ownerItem.publication,revision:2},workflow:'registered',version:4};pubs[0].revision=2;
 await open();assert.match(node('registration-progress').textContent,/Saved revision 2.*public revision 2/);assert.doesNotMatch(node('registration-progress').textContent,/is private/);
 assert(!walk(node('submission-actions')).some(n=>n.textContent==='Publish numerical summary'));
 walk(node('submission-actions')).find(n=>n.textContent==='Compare this result (public revision 2)').fire('click');await tick();await tick();resolvePair(pending.shift());await tick();await tick();
 assert.match(node('public-pair-results').textContent,/Public revisions: left 2/);
 console.log('Revision scope: private head/public revision distinction, explicit publication action, saved-original scope and public comparison revision passed');
})().catch(e=>{console.error(e);process.exitCode=1});`;
eval(source);
