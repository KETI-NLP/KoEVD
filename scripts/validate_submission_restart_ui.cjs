/* CSS + actual local HTTP restart; all account/model/permission data SYNTHETIC. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
function arg(k,d){const i=process.argv.indexOf(k);return i<0?d:process.argv[i+1];}
const origin=arg('--origin','http://127.0.0.1:8770'),out=path.resolve(arg('--output-dir','generated/submission-web-layout-20261008'));
const fixture=path.resolve(arg('--fixture-dir','generated/space-demo-20261008'));fs.mkdirSync(out,{recursive:true});let browser;
async function main(){
 browser=await chromium.launch({headless:true,executablePath:arg('--browser-executable',process.env.KOEVD_TEST_BROWSER)});
 const context=await browser.newContext({viewport:{width:1440,height:1050}}),errors=[],external=[];
 await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();external.push(new URL(r.request().url()).origin);return r.abort();});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto(origin+'/');await page.locator('#status').filter({hasText:'Private session ready'}).waitFor();
 const entries=(await(await context.request.get(origin+'/api/public/submissions')).json()).items;assert.equal(entries.length,1);const published=entries[0];assert.equal(published.scope,'responses');
 assert.equal((await context.request.get(origin+'/api/submissions/'+published.submission_id)).status(),401);
 const popupPromise=context.waitForEvent('page');await page.locator('#hf-signin').click();const popup=await popupPromise;await popup.waitForURL(origin+'/SYNTHETIC/authorize*');await popup.locator('a[data-code="SYNTHETIC-author"]').click();await popup.waitForURL(origin+'/auth/done');await popup.close();await page.locator('#identity-refresh').click();await page.locator('#submission-controls:not([hidden])').waitFor();
 const states=(await(await context.request.get(origin+'/api/submissions')).json()).items;const withdrawn=states.find(s=>s.workflow==='withdrawn');assert(withdrawn);
 assert.equal((await context.request.get(origin+'/api/public/submissions/'+withdrawn.id)).status(),404);
 const original=await(await context.request.get(origin+'/api/submissions/'+published.submission_id+'/result')).json();assert.equal(original.content_sha256,JSON.parse(fs.readFileSync(path.join(fixture,'SYNTHETIC-B.json'),'utf8')).content_sha256);
 await page.locator('[data-public-id="'+published.submission_id+'"]').click();await page.locator('#public-metrics table').waitFor();
 const metric=page.locator('#public-metrics td').nth(1);assert.equal(await metric.evaluate(n=>getComputedStyle(n).whiteSpace),'nowrap');
 await page.locator('#public-metrics').screenshot({path:path.join(out,'metrics-desktop.png')});
 await page.setViewportSize({width:390,height:844});await page.locator('#public-metrics').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'metrics-mobile.png')});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify({scope:'final CSS and actual local HTTP restart with SYNTHETIC identity/model/permissions; no actual HF/GPU/deployment',published_projection_restored:true,withdrawal_restored:true,new_login_same_subject_original_preserved:true,numeric_columns_do_not_wrap:true,mobile_document_no_overflow:true,browser_errors:errors,external_requests:external,screenshots:['metrics-desktop.png','metrics-mobile.png']},null,2));console.log(JSON.stringify({restart_verified:true,layout_verified:true,browser_errors:0,external_requests:0,scope:'SYNTHETIC local candidate'}));
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();});
