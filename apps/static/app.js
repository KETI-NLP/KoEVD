/* Local file bytes are only transferred to our disposable Web Worker, never HTTP. */
'use strict';
const el=id=>document.getElementById(id);
let worker=null, urls=[], generation=0, config=null;
function clearOutput(){el('report').hidden=true;el('report').removeAttribute('src');el('downloads').replaceChildren();for(const u of urls)URL.revokeObjectURL(u);urls=[];}
function reset(){generation++;if(worker)worker.terminate();worker=null;clearOutput();el('files').value='';el('analyze').disabled=false;el('status').textContent='파일 선택과 분석 결과를 지웠습니다.';}
el('clear').addEventListener('click',reset);
const configured=fetch('config.json').then(r=>{if(!r.ok)throw Error('설정 파일을 읽지 못했습니다.');return r.json();}).then(c=>{
  if(c.format!=='koevd-static-candidate-v1')throw Error('지원하지 않는 배포 설정입니다.');config=c;
  el('scope').textContent=c.synthetic_demo_enabled?'가상 CPU 데모 입력·참조입니다. 실제 추론·성능·GPU 증거가 아닙니다.':'고정 입력: '+c.indexes.map(i=>i.label).join(' / ');
  for(const b of c.baselines){const o=document.createElement('option');o.value=b.id;o.textContent=b.label;el('reference').append(o);}return c;
});
configured.catch(e=>{el('status').textContent=e.message;el('analyze').disabled=true;});
el('analyze').addEventListener('click',async()=>{
  const job=++generation;clearOutput();el('analyze').disabled=true;
  try{
    await configured;
    const selected=[...el('files').files],reference=el('reference').value;
    const count=selected.length+(reference?1:0),sum=selected.reduce((n,f)=>n+f.size,0);
    if(!selected.length||count>4||selected.some(f=>f.size>128*1024*1024)||sum>256*1024*1024)throw Error('결과 파일과 용량 한도를 확인하세요.');
    const resamples=Number(el('resamples').value),seed=Number(el('seed').value);
    if(!Number.isInteger(resamples)||resamples<0||resamples>10000||!Number.isSafeInteger(seed))throw Error('반복 수와 seed를 정수로 입력하세요.');
    el('status').textContent='브라우저 Python 환경 준비 중… 처음 실행 시 시간이 필요합니다.';
    const buffers=await Promise.all(selected.map(f=>f.arrayBuffer()));if(job!==generation)return;
    if(worker)worker.terminate();worker=new Worker('worker.js');
    worker.onerror=e=>{if(job!==generation)return;el('status').textContent='브라우저 분석 오류: '+e.message;el('analyze').disabled=false;worker.terminate();worker=null;};
    worker.onmessage=e=>{
      if(job!==generation)return;const m=e.data;
      if(m.progress){el('status').textContent=m.progress;return;}
      if(m.error){el('status').textContent='분석 거부: '+m.error;el('analyze').disabled=false;worker.terminate();worker=null;return;}
      for(const file of m.outputs){const blob=new Blob([file.bytes],{type:file.name.endsWith('.html')?'text/html;charset=utf-8':'application/octet-stream'});const u=URL.createObjectURL(blob);urls.push(u);const a=document.createElement('a');a.href=u;a.download=file.name;a.textContent=file.name;el('downloads').append(a);if(file.name==='report-v2.html'){el('report').src=u;el('report').hidden=false;}}
      el('status').textContent='분석 완료 · '+m.receipt.records.join(' + ')+'개 기록 · 공식 순위·공개 등록 없음';
      el('analyze').disabled=false;worker.terminate();worker=null;
    };
    worker.postMessage({buffers,reference,resamples,seed},buffers);
  }catch(e){if(job===generation){el('status').textContent=e.message;el('analyze').disabled=false;}}
});
window.addEventListener('pagehide',reset);
