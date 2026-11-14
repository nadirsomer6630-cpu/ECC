const { chromium } = require('playwright');
const jobs = require(process.argv[2]);
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 720, height: 920 } });
  let cur = null;
  for (const j of jobs) {
    if (j.html !== cur) { await pg.goto('file://' + j.html); cur = j.html; }
    await pg.evaluate((j) => {
      const set = (sel, deg, ox, oy) => { const g = document.querySelector(sel); if (g) g.setAttribute('transform', `rotate(${deg} ${ox} ${oy})`); };
      const sv = document.querySelector('svg'); sv.setAttribute('viewBox', '-150 0 700 900'); sv.setAttribute('width', '700');
      document.querySelector('.mouth').setAttribute('data-m', j.m);
      document.querySelectorAll('.lid').forEach(l => l.setAttribute('height', j.b ? '36' : '0'));
      set('.armL', j.armL, 99, 292); set('.armR', j.armR, 301, 292);
      set('.legL', j.legL, 168, 548); set('.legR', j.legR, 232, 548); set('.head', j.head, 200, 262);
    }, j);
    await pg.locator('svg').first().screenshot({ path: j.out, omitBackground: true });
  }
  await b.close();
})();
