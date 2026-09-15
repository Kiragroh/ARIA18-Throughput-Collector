const { chromium } = require('playwright');
const { pathToFileURL } = require('url');
const path = require('path');
const fs = require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const out=path.resolve('.local/screenshots');fs.mkdirSync(out,{recursive:true});
 await page.goto(pathToFileURL(path.resolve(process.argv[2]||'.local/report/Standortanalyse.html')).href);
 await page.waitForFunction(()=>document.querySelector('#plot0')?.data?.length>1);
 for(const [name,width,height,dark] of [['desktop-light',1440,1000,false],['desktop-dark',1440,1000,true],['mobile-light',390,844,false],['mobile-dark',390,844,true]]){
  await page.setViewportSize({width,height});
  const current=await page.evaluate(()=>document.documentElement.dataset.theme==='dark');
  if(current!==dark)await page.locator('#theme').click();
  await page.waitForTimeout(700);
  const state=await page.evaluate(()=>({
   overflow:document.documentElement.scrollWidth>innerWidth,
   traces:document.querySelector('#plot0').data.length,
   line:document.querySelector('#plot0').data[0].line.color,
   boxes:document.querySelector('#plot0').querySelectorAll('path.box').length,
   quartiles:document.querySelector('#plot0').data[1].q1
  }));
  await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});
  if(state.overflow||state.line!==(dark?'#fff':'#000')||state.boxes===0)throw Error(name+': '+JSON.stringify(state));
 }
 await page.setViewportSize({width:1440,height:1000});
 const activity=await page.locator('#machines').innerText();
 await page.selectOption('#model','workflow');
 // Pooled KPIs may be suppressed for both models; compare the device table.
 if(await page.locator('#machines').innerText()===activity)throw Error('Model switch did not change device values');
 await page.selectOption('#granularity','month');
 if(await page.locator('#period option').count()!==12)throw Error('Month range missing');
 await page.selectOption('#period','5');
 if(!(await page.locator('#active').innerText()).includes('2025-06'))throw Error('Selected period missing');
 await page.locator('.chart button').first().click();
 await page.waitForFunction(()=>document.querySelector('#modal-plot').data?.length>1);
 if(!(await page.locator('#expanded').evaluate(e=>e.open)))throw Error('Fullscreen dialog missing');
 await page.screenshot({path:path.join(out,'expanded.png')});
 await page.locator('#close').click();
 await page.selectOption('#view','line');
 if(await page.locator('#plot0').evaluate(e=>e.data[1].type)!=='scatter')throw Error('Line mode missing');
 await browser.close();
 if(errors.length)throw Error(errors.join('\n'));
 console.log('BROWSER_OK desktop/mobile light/dark models period boxes lines expanded');
})().catch(e=>{console.error(e);process.exit(1)});
