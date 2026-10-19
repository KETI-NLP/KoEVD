const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ui=require('../src/koevd_eval/assets/leaderboard.js'),data=JSON.parse(fs.readFileSync('src/koevd_eval/assets/paper_models.json','utf8'));
const model=data.models.find(m=>m.name==='Gemini 3.1 Pro');assert.equal(ui.paperValues(model).t1,null);
const rows=[{name:'Undefined',values:{t3:null}},{name:'Zero',values:{t3:0}},{name:'Higher',values:{t3:.2}}];
assert.deepEqual(ui.sortedRows(rows,'t3').map(r=>r.name),['Zero','Higher','Undefined']);
assert.deepEqual(ui.sortedRows(rows,'t3','descending').map(r=>r.name),['Higher','Zero','Undefined']);
assert.equal(ui.sortedRows(rows,'name','ascending','zero').length,1);
for(const [hash,path,expected] of [['','/','models'],['','/compare','compare'],['','/submit','submit'],['#paper-model=GPT-5.4','/','detail'],['#paper-compare=a&paper-right=b','/','compare'],['#model=a','/','detail'],['#left=a&right=b','/','compare']]){
 const nodes=new Map(),events={},node=id=>{if(!nodes.has(id))nodes.set(id,{hidden:false,addEventListener(){},focus(){}});return nodes.get(id)};
 const window={dispatchEvent(){},addEventListener(k,fn){events[k]=fn}},location={hash,pathname:path};
 vm.runInNewContext(fs.readFileSync('src/koevd_eval/assets/navigation.js','utf8'),{window,location,history:{pushState(){}},CustomEvent:class{},document:{getElementById:node,querySelectorAll:()=>[]}});
 for(const [id,page] of [['explore-page','models'],['detail-page','detail'],['compare-page','compare'],['submit-page','submit']])assert.equal(node(id).hidden,page!==expected,hash||path);
 window.KoEVDNavigation.show('submit');assert.equal(node('submit-page').hidden,false);assert.equal(node('explore-page').hidden,true);
}
console.log('Null ordering, paper projection and separate direct/back-navigation routes passed');
