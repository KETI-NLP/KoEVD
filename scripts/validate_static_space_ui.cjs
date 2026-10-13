/* Isolated headless browser + read-only localhost static server. No user session. */
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
function arg(n,f){const i=process.argv.indexOf(n);return i<0?f:process.argv[i+1];}
const root=path.resolve(arg('--space',null)),out=path.resolve(arg('--output',null));
const files=JSON.parse(arg('--files','[]')).map(x=>path.resolve(x));
const expected=path.resolve(arg('--expected',null));
const resamples=arg('--resamples','100'),reference=arg('--reference','');
fs.mkdirSync(out,{recursive:true});
let browser,server;const requests=[],errors=[];
async function main(){
  server=http.createServer((req,res)=>{
    requests.push({method:req.method,url:req.url,bodyBytes:Number(req.headers['content-length']||0)});
    if(req.method!=='GET'){res.writeHead(405);return res.end();}
    const p=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]==='/'?'/index.html':req.url.split('?')[0]));
    if(!p.startsWith(root+path.sep)){res.writeHead(403);return res.end();}
    if(!fs.existsSync(p)||!fs.statSync(p).isFile()){res.writeHead(404);return res.end();}
    const types={'.html':'text/html','.js':'application/javascript','.json':'application/json','.css':'text/css','.wasm':'application/wasm'};
    res.writeHead(200,{'Content-Type':types[path.extname(p)]||'application/octet-stream'});fs.createReadStream(p).pipe(res);
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const origin='http://127.0.0.1:'+server.address().port;
  browser=await chromium.launch({headless:true,executablePath:arg('--browser-executable',process.env.KOEVD_TEST_BROWSER)});
  const context=await browser.newContext({acceptDownloads:true,viewport:{width:1440,height:1050}});
  const external=[];await context.route('**/*',async route=>{const u=route.request().url();if(u.startsWith(origin+'/'))await route.continue();else{external.push(u);await route.abort();}});
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.goto(origin);await page.locator('#scope').filter({hasText:/./}).waitFor();
  await page.locator('#files').setInputFiles(files);await page.locator('#resamples').fill(resamples);
  if(reference)await page.locator('#reference').selectOption(reference);
  const began=performance.now();await page.locator('#analyze').click();
  await page.waitForFunction(()=>document.getElementById('status').textContent.includes('분석 완료')||document.getElementById('status').textContent.startsWith('분석 거부:'),null,{timeout:600000});
  const status=await page.locator('#status').textContent();console.log(status);
  assert(status.startsWith('분석 완료'),status);
  const elapsed=(performance.now()-began)/1000;
  const downloadNames=['profile-v2.json','cases-v2.jsonl','metrics-v2.csv','report-v2.md','report-v2.html'];
  for(const name of downloadNames){const p=page.waitForEvent('download');await page.getByRole('link',{name,exact:true}).click();const d=await p;await d.saveAs(path.join(out,name));assert.equal(d.suggestedFilename(),name);}
  const got=JSON.parse(fs.readFileSync(path.join(out,'profile-v2.json'),'utf8'));
  assert.deepEqual(got,JSON.parse(fs.readFileSync(expected,'utf8')));
  const frame=page.frameLocator('#report');await frame.locator('#tab-overview[aria-selected="true"]').waitFor();
  for(const tab of ['task1','task2','task3','task4','task5','comparison','cases','method']){await frame.locator('#tab-'+tab).click();assert((await frame.locator('#view h1').textContent()).length>3);}
  await frame.locator('#tab-comparison').click();
  await page.screenshot({path:path.join(out,'desktop-comparison.png')});
  await frame.locator('#tab-cases').click();await frame.locator('.case-card summary').first().click();
  assert.equal(await frame.locator('img,object').count(),0);
  assert.equal(await frame.locator('body').evaluate(()=>Boolean(globalThis.__KOEVD_INJECTED__)),false);
  await page.screenshot({path:path.join(out,'desktop-cases.png')});
  await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'mobile.png')});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.locator('#clear').click();assert(await page.locator('#report').isHidden());assert.equal(await page.locator('#downloads a').count(),0);
  assert.equal(external.length,0);assert.equal(errors.length,0);assert(requests.every(r=>r.method==='GET'&&r.bodyBytes===0));
  fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify({scope:'actual browser Python analysis, not new inference/identity/storage/publication',browser:browser.version(),status,seconds:elapsed,profile_exact:true,records:got.runs.map(r=>r.tasks),requests,external,errors,cleared:true},null,2));
  console.log(JSON.stringify({seconds:elapsed,profile_exact:true,files:downloadNames.length,requests:requests.length,external:external.length,errors:errors.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({error:String(e),errors,requests},null,2));}).finally(async()=>{if(browser)await browser.close();if(server)await new Promise(r=>server.close(r));});
