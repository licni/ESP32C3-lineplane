// 版本流水號: r1 (2026-10-30) 補償功能說明書用的網頁截圖:用 tools/web_mock.py 的假伺服器 + Playwright Chromium,不用板子
// 用法:node tools/comp_manual_shots.js 假伺服器網址 輸出資料夾
//   假伺服器:python3 tools/web_mock.py 8765 → node tools/comp_manual_shots.js http://127.0.0.1:8765 docs/images/comp_manual
// 情境用 POST /mock/scenario 切換(姿態,飛行狀態,風格設定). 截圖寬 760px,2 倍解析度,淺色主題.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = process.argv[2] || 'http://127.0.0.1:8765';
const OUT = process.argv[3] || 'docs/images/comp_manual';
fs.mkdirSync(OUT, { recursive: true });

async function scenario(patch) {
  const r = await fetch(BASE + '/mock/scenario', { method: 'POST', body: JSON.stringify(patch) });
  if (!r.ok) throw new Error('scenario ' + r.status);
}

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 760, height: 1100 }, deviceScaleFactor: 2, colorScheme: 'light', locale: 'zh-TW' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  const shot = async (sel, name, opts = {}) => {
    const el = page.locator(sel).first();
    await el.waitFor({ state: 'visible' });
    await el.scrollIntoViewIfNeeded();
    await page.waitForTimeout(opts.wait || 600);
    await el.screenshot({ path: path.join(OUT, name + '.png') });
    console.log('  ' + name);
  };
  const open = async (tab) => {
    await page.goto(BASE + '/?r=' + Date.now() + '#tab-' + tab, { waitUntil: 'load' });   // 加亂數避免只換 hash 不重新載入
    await page.waitForSelector('#profSeg2 button', { state: 'attached', timeout: 10000 });
    await page.waitForTimeout(700);
    await page.addStyleTag({ content: 'header{position:static!important}' });   // 置頂標題列不要壓在長元素的截圖上
  };

  // 範例風格 B:側傾曲線拉成 45→+4,70→+8,90→+12;地上姿態 機頭 +25°,翼軸仰角 30°
  await scenario({ edit: 1, active: 1, profile: { 1: { sd1p: 4, sd2p: 8, sd3p: 12, compMode: 0 } },
                   status: { p: 25, r: 8, sd: 30, az: 150, state: 1, t: 0, lg: 0.55, gt: 0 } });
  console.log('角度補償頁(曲線方式)');
  await open('comp');
  await shot('#comp > .card:nth-of-type(1)', 'comp_mode_card');
  await shot('#curveMainCard .cvwrap', 'curve_main');
  await shot('#curveMainCard .cvside', 'curve_panel');
  // 側傾曲線:標題 + 說明 + 圖(用 clip 截卡片下半)
  await shot('#sdSvg', 'curve_side');
  // 第二段頁籤
  await page.click('#cvPhase button[data-ph="2"]');
  await page.waitForTimeout(500);
  await shot('#curveMainCard .cvwrap', 'curve_phase2');
  await page.click('#cvPhase button[data-ph="1"]');
  // 點選朝上第 2 點,面板顯示選取
  await page.evaluate(() => { const h = document.querySelector('#cvSvg .cv-hit[data-h="pt"][data-side="up"][data-i="2"]'); h.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, isPrimary: true, pointerId: 1, clientX: 0, clientY: 0 })); h.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1 })); });
  await page.waitForTimeout(500);
  await shot('#curveMainCard .cvwrap', 'curve_selected');
  // 全部點的數值
  await page.evaluate(() => { document.querySelector('#comp details.card').open = true; });
  await shot('#curveCard .side:nth-of-type(3)', 'curve_all_points_side');

  console.log('角度補償頁(曲線 + 回授)');
  await scenario({ profile: { 1: { compMode: 1 } } });
  await open('comp');
  await shot('#comp > .card:nth-of-type(1)', 'comp_mode_card_fb');
  console.log('角度補償頁(只回授)');
  await scenario({ profile: { 1: { compMode: 2 } } });
  await open('comp');
  await shot('#comp', 'comp_page_mode2', { wait: 800 });
  await scenario({ profile: { 1: { compMode: 1 } } });

  console.log('監看頁(地上)');
  await open('mon');
  await shot('#mon > .card:nth-of-type(1)', 'mon_attitude');
  await shot('#mon > .card:nth-of-type(2)', 'mon_h3', { wait: 900 });
  console.log('監看頁(飛行中)');
  await scenario({ status: { p: 30, r: 5, sd: 40, az: 200, state: 5, t: 52, lg: 2.4, gt: 6 } });
  await open('mon');
  await page.waitForTimeout(800);
  await shot('#fbar', 'mon_flying_bar');
  await shot('#mon > .card:nth-of-type(1) #compPreview', 'mon_comp_preview_flying');
  await scenario({ status: { p: 25, r: 8, sd: 30, az: 150, state: 1, t: 0, lg: 0.55, gt: 0 } });

  console.log('計時器頁');
  await open('prof');
  {   // 只截「起飛」那一組(標題到「起飛後不補償」)
    const box = await page.evaluate(() => {
      const h = document.querySelector('#profCards h3.grp'); const prms = [...document.querySelectorAll('#profCards .prm')];
      const last = prms.find(e => e.textContent.includes('起飛後不補償')); const a = h.getBoundingClientRect(), b = last.getBoundingClientRect();
      return { x: a.left - 4, y: a.top - 4 + window.scrollY, width: a.width + 8, height: b.bottom - a.top + 8 };
    });
    await page.screenshot({ path: path.join(OUT, 'prof_takeoff.png'), clip: box });
    console.log('  prof_takeoff');
  }

  console.log('紀錄頁');
  await open('log');
  await page.waitForTimeout(1500);
  // 游標放在第 42 秒那個拉起附近:點畫布(時間軸最新在右,3 分視窗)
  const cv = page.locator('#logCanvas');
  const box = await cv.boundingBox();
  await page.mouse.click(box.x + box.width * 0.55, box.y + box.height * 0.3);
  await page.waitForTimeout(700);
  await shot('#log > .card:nth-of-type(2)', 'log_chart');
  await shot('#log > .card:nth-of-type(3)', 'log_h3', { wait: 900 });
  await shot('#log > .card:nth-of-type(1)', 'log_stats');

  await browser.close();
  if (errors.length) { console.log('JS 例外:'); errors.forEach(e => console.log('  ' + e)); process.exit(1); }
  console.log('完成,輸出在', OUT);
})();
