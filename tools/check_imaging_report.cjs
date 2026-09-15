const { chromium } = require('playwright');
const { pathToFileURL } = require('url');

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(process.argv[2]).href);
    await page.locator('#imaging-table tbody tr').first().waitFor();
    const rows = await page.locator('#imaging-table tbody tr').count();
    if (rows < 1) throw Error('No image groups');
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 900 });
      for (const theme of ['light', 'dark']) {
        if ((await page.locator('html').getAttribute('data-theme') || 'light') !== theme) {
          await page.locator('#theme').click();
        }
        await page.waitForFunction(() => document.documentElement.scrollWidth <= innerWidth + 1);
        const table = page.locator('#imaging-table');
        await table.scrollIntoViewIfNeeded();
        if (!await table.isVisible()) throw Error('Image table hidden');
      }
    }
    for (const model of ['workflow', 'technical', 'activity']) {
      await page.selectOption('#model', model);
      await page.locator('#imaging-table tbody tr').first().waitFor();
    }
    if (errors.length) throw Error(errors.join('; '));
    console.log('IMAGING_BROWSER_OK groups=' + rows + ' desktop/mobile light/dark models');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exit(1); });
