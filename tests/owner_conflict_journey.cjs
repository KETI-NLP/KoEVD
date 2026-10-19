/* Shipped owner controls; concurrent writer is a synthetic owner API state. */
const fs=require('node:fs');
let source=fs.readFileSync('tests/comparison_journey.cjs','utf8').split('(async()=>{')[0];
source=source.replace('const workspace={',"let ownerItem={id:'a',owner:'SYNTHETIC-owner',version:2,head_revision:1,workflow:'registered',display:{display_name:'SYNTHETIC owner',description:''},publication:{status:'published',revision:1,scope:'summary'}};const expectedVersions=[];\nconst workspace={");
source=source.replace('api:async path=>{','api:async (path,options={})=>{');
source=source.replace("if(path==='/api/identity')return {json:async()=>({signed_in:false})};",`if(path==='/api/identity')return {json:async()=>({signed_in:true,subject:'SYNTHETIC-owner',username:'SYNTHETIC owner'})};
 if(path.startsWith('/api/submissions?'))return {json:async()=>({items:[ownerItem],next_cursor:null})};
 if(path==='/api/submissions/a')return {json:async()=>ownerItem};
 if(path.startsWith('/api/public/submissions?'))return {json:async()=>({items:pubs,next_cursor:null})};
 if(path==='/api/submissions/a/metadata'){const body=JSON.parse(options.body);expectedVersions.push(body.expected_version);if(body.expected_version!==ownerItem.version){const e=Error('Submission changed; reload before retrying');e.code='stale_version';throw e;}ownerItem={...ownerItem,version:ownerItem.version+1,display:{display_name:body.display_name,description:body.description}};return {json:async()=>ownerItem};}`);
source=source.replace('URLSearchParams,console};',"URLSearchParams,console,crypto:require('node:crypto').webcrypto};");
source+=`(async()=>{
 await tick();await tick();node('submission-list').children[0].fire('click');await tick();await tick();
 ownerItem={...ownerItem,version:3,display:{display_name:'SYNTHETIC concurrent change',description:'remote'}};
 node('submission-display-name').value='SYNTHETIC local draft';node('submission-description').value='local description';node('submission-reason').value='local reason';node('publication-consent').checked=true;node('publication-rights').value='old permission';
 node('submission-metadata-save').fire('click');await tick();await tick();
 assert.deepEqual(expectedVersions,[2]);assert.match(node('submission-status').textContent,/Reload selected registration/);assert.equal(node('submission-reload').hidden,false);assert.equal(node('submission-metadata-save').disabled,true);
 node('submission-reload').fire('click');await tick();await tick();
 assert.deepEqual(expectedVersions,[2],'reload must be a read, not an automatic write');assert.equal(node('submission-reload').hidden,true);assert.equal(node('submission-metadata-save').disabled,false);
 assert.equal(node('submission-display-name').value,'SYNTHETIC local draft');assert.equal(node('submission-description').value,'local description');assert.equal(node('submission-reason').value,'local reason');assert.equal(node('publication-consent').checked,false);assert.equal(node('publication-rights').value,'');
 node('submission-metadata-save').fire('click');await tick();await tick();assert.deepEqual(expectedVersions,[2,3]);assert.match(node('submission-status').textContent,/Display metadata saved/);
 ownerItem={...ownerItem,version:5};node('submission-metadata-save').fire('click');await tick();await tick();assert.equal(node('submission-reload').hidden,false);
 node('submissions-refresh').fire('click');await tick();await tick();assert.equal(node('submission-reload').hidden,true);assert.match(node('submission-status').textContent,/Latest registration state loaded/);
 node('submission-metadata-save').fire('click');await tick();await tick();assert.deepEqual(expectedVersions,[2,3,4,5]);
 console.log('Owner conflicts: explicit read recovery, list refresh updates selection, local draft retained, fresh consent and no write replay passed');
})().catch(e=>{console.error(e);process.exitCode=1});`;
eval(source);
