/* Presentation only. Metric values, cohorts and rank eligibility stay server-owned. */
(function(root){'use strict';
const words={choose_best:'choose the safest response',choose_unsafe:'identify the unsafe response',rejected_vs_accepted:'accepted versus rejected',relative_harmfulness:'relative harmfulness',safe_guided:'safety-guided',tool_forced:'tool-forced',unsafe_induced:'unsafe-induced',core:'core sources',task5_overlap:'sources shared with Task 5',all:'all rows',overall:'all rows',event_on_valid:'unsafe event rate on valid outputs',observed_event_on_all:'observed unsafe events / all expected outputs',strategy_coverage:'strategy measurement coverage',accuracy_on_valid:'accuracy on valid answers',missed_risk_on_valid_unsafe:'missed risk among valid unsafe inputs',false_alarm_on_valid_safe:'false alarms among valid safe inputs'};
function name(id){return String(id).split('/').map(p=>words[p]||p.replace(/^task(\d+)$/,'Task $1').replaceAll('_',' ')).filter((p,i,a)=>i===0||p!==a[i-1]).join(' · ');}
function rate(task,key){const event=({1:'judgment errors',2:'answer errors',3:'classifier-labeled unsafe responses',5:'unsafe mock tool selections'})[task]||'events';if(key==='event_on_valid')return event+' / valid outputs';if(key==='observed_event_on_all')return 'observed '+event+' / all expected outputs';return name(key);}
function direction(value){return value==='higher'?'Higher is better':value==='lower'?'Lower is better':'Descriptive frequency; no better/worse direction';}
function focusKey(board,id,current=''){
  const p=board.publications.find(p=>p.submission_id===id);if(!p)return null;
  const target=p.duplicate_of||id,keys=[];
  for(const b of board.boards)if(b.rows.some(r=>r.entry_id===target))keys.push(b.metric_id+'|'+b.cohort_sha256);
  for(const r of board.excluded)if(r.entry_id===target)keys.push(r.metric_id+'|'+r.metric.cohort_sha256);
  return keys.find(k=>k.split('|')[0]===current.split('|')[0])||keys.find(k=>k.startsWith('task2/variant/choose_best/accuracy_on_valid|'))||keys[0]||null;
}
function matching(board,query){query=query.trim().toLocaleLowerCase();return board.publications.filter(p=>[p.submission_id,p.display?.display_name,p.model?.id,p.model?.revision].filter(Boolean).join(' ').toLocaleLowerCase().includes(query));}
// Aliases remain discoverable, while an original result occupies one table row.
function uniquePublications(items){
 const byId=new Map(items.map(p=>[p.submission_id,p])),groups=new Map();
 for(const p of items){const original=byId.get(p.duplicate_of)||p,key=original.artifact_sha256||p.artifact_sha256||original.submission_id;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(p);}
 return [...groups.entries()].map(([key,aliases])=>({key,aliases,publication:aliases.find(p=>!p.duplicate_of)||aliases[0]}));
}
function canonicalId(items,id){return uniquePublications(items).find(g=>g.aliases.some(p=>p.submission_id===id))?.publication.submission_id||id;}
function differentPublication(items,id){const groups=uniquePublications(items),current=groups.find(g=>g.aliases.some(p=>p.submission_id===id));return groups.find(g=>g!==current)?.publication||null;}
function subsetGuide(holder,doc){
  const el=(tag,text)=>{const n=doc.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
  const box=el('details');box.className='subset-guide';box.append(el('summary','Task 3/4 input sets: why the subset counts do not add up'));
  box.append(el('p','Canonical full protocol: core 2,000 + Task-5-linked 784 - shared 125 = union 2,659. Task 4 measures the same generated responses. Custom subsets can have different counts.'));
  const diagram=el('div');diagram.className='subset-diagram';diagram.setAttribute('role','group');diagram.setAttribute('aria-label','Overlapping source sets: core only 1,875; shared 125; Task-5-linked only 659');
  for(const [label,count] of [['Core only','1,875'],['Both sets','125'],['Task-5-linked only','659']]){const cell=el('div');cell.append(el('strong',count),el('span',label));diagram.append(cell);}box.append(diagram);
  box.append(el('p','Core = 1,875 + 125 = 2,000. Task-5-linked = 125 + 659 = 784. These subset rates are overlapping views; do not add their counts or percentages as disjoint groups. Missing/invalid measurements can reduce their valid denominators.'));
  holder.append(box);
}
const api={name,rate,direction,focusKey,matching,uniquePublications,canonicalId,differentPublication,subsetGuide};if(typeof module==='object'&&module.exports)module.exports=api;else root.KoEVDMetrics=api;
}(typeof window==='object'?window:globalThis));
