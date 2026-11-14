const { chromium } = require('playwright');
const SRC = process.argv[2], OUT = process.argv[3];
const CAST = [["samir_tired", "XABCDEFGH", [0, 1]], ["w1", "X", [0, 1]], ["w2", "X", [0, 1]], ["w3", "X", [0, 1]], ["w4", "X", [0, 1]], ["w5", "X", [0, 1]], ["ines", "X", [0, 1]]];
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 420, height: 920 } });
  for (const [name, mouths, blinks] of CAST) {
    await pg.goto('file://' + SRC + name + '.html');
    for (const m of mouths) for (const blink of blinks) {
      await pg.evaluate(([m, blink]) => {
        document.querySelector('.mouth').setAttribute('data-m', m);
        document.querySelectorAll('.lid').forEach(l => l.setAttribute('height', blink ? '36' : '0'));
      }, [m, blink]);
      await pg.locator('svg').first().screenshot({ path: `${OUT}${name}_${m}_${blink}.png`, omitBackground: true });
    }
  }
  await b.close();
})();
