const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1600,height:1000}});
 await page.goto(pathToFileURL(path.resolve('.local/report/Standortanalyse.html')).href);
 await page.waitForFunction(()=>document.querySelector('#plot0')?.data?.length>1);
 const site=await page.locator('#subtitle').innerText();
 if(!/syntheti/i.test(site))throw Error('Only the synthetic report may be used');
 await page.locator('.chart button').first().click();
 await page.waitForFunction(()=>document.querySelector('#modal-plot')?.querySelectorAll('path.box').length>0);
 await page.evaluate(()=>Plotly.relayout('modal-plot',{width:1000,height:510,'font.size':16,'margin.b':100}));
 await page.locator('#modal-plot').evaluate(el=>{el.style.width='1000px';el.style.height='510px'});
 await page.locator('#modal-plot').screenshot({path:'kooperation/assets/boxplots-beispiel.png'});
 await browser.close();console.log('SYNTHETIC_CHART_CAPTURE_OK');
})().catch(e=>{console.error(e);process.exit(1)});
