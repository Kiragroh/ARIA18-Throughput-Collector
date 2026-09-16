const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try{
  const legacy=process.argv.includes('--legacy'),count=legacy?2:6;
  const page=await browser.newPage({viewport:{width:1440,height:1000},offline:true});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(path.resolve(process.argv[2])).href);
  await page.waitForFunction(n=>document.querySelector('#plot')?.data?.length===n,count);
  if(await page.locator('#sites tbody tr').count()!==count)throw Error('Site table');
  if(await page.locator('#checks tbody tr').count()!==count*(count-1)/2)throw Error('Pair checks');
  if(!legacy&&!await page.locator('#subtitle').textContent().then(t=>t.includes('SYNTHETISCHE')))throw Error('Demo label');
  if(legacy&&!await page.locator('#status').textContent().then(t=>t.includes('Nur deskriptiv')))throw Error('Legacy data not gated');
  if(await page.evaluate(()=>document.querySelector('#plot').data.some(t=>t.median.length!==4)))throw Error('Quarter boxes');
  await page.locator('#expand').click();
  await page.waitForFunction(n=>document.querySelector('#expanded-plot')?.data?.length===n,count);
  await page.locator('#close').click();
  await page.selectOption('#model','workflow');
  await page.selectOption('#metric','duration');
  const workflow=await page.evaluate(()=>document.querySelector('#plot').data[0].median[0]);
  await page.selectOption('#model','technical');
  const technical=await page.evaluate(()=>document.querySelector('#plot').data[0].median[0]);
  if(workflow===technical)throw Error('Model values stale');
  await page.selectOption('#granularity','month');
  if(await page.locator('#period option').count()!==12)throw Error('Month intervals');
  await page.selectOption('#view','line');
  if(await page.evaluate(()=>document.querySelector('#plot').data[0].y.length)!==12)throw Error('Month curve');
  for(const domain of ['population','flow','imaging']){
   await page.selectOption('#domain',domain);
   if(!await page.evaluate(()=>document.querySelector('#plot').data.some(t=>(t.y||[]).some(v=>v!=null))))throw Error('Empty domain '+domain);
  }
  await page.selectOption('#domain','throughput');await page.selectOption('#granularity','quarter');await page.selectOption('#view','box');
  fs.mkdirSync('.local/screenshots',{recursive:true});
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:1000});
   await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth,{},{timeout:5000}).catch(async()=>{
    const offenders=await page.evaluate(()=>[...document.querySelectorAll('header,main,section,label,select,.table-wrap,#plot,.modebar')].map(e=>({tag:e.tagName,id:e.id,cls:e.className,width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})).filter(e=>e.right>innerWidth));
    throw Error('Mobile overflow '+JSON.stringify(offenders));
   });
   for(const theme of ['light','dark']){
    await page.selectOption('#theme',theme);
    await page.locator('#plot-title').scrollIntoViewIfNeeded();
    if(!legacy)await page.screenshot({path:`.local/screenshots/multisite-${width}-${theme}.png`});
   }
  }
  if(errors.length)throw Error(errors.join('\n'));
  console.log(`MULTISITE_BROWSER_OK sites=${count} pairs=${count*(count-1)/2} models domains desktop/mobile offline legacy=${legacy}`);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
