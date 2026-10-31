// Render the Open Graph share cards (1200x630) that build.py writes to build/cards/ into docs/assets/og/.
// usage: node render_cards.js        (needs Playwright with Chromium; run after `python3 -I build.py`)
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const root = __dirname;
  const cards = path.join(root, 'build', 'cards');
  const out = path.join(root, 'docs', 'assets', 'og');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  for (const f of fs.readdirSync(cards).filter((f) => f.endsWith('.html'))) {
    await page.goto('file://' + path.join(cards, f));
    await page.evaluate(async () => { await document.fonts.ready; });
    await page.waitForTimeout(200);
    const dest = path.join(out, f.replace(/\.html$/, '.png'));
    await page.screenshot({ path: dest });
    console.log('card', path.relative(root, dest));
  }
  await browser.close();
})();
