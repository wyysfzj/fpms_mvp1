const fs = require('fs');
const path = require('path');
const { chromium } = require('/Users/cfcc/.npm/_npx/9833c18b2d85bc59/node_modules/playwright');

const outDir = path.resolve('artifacts/smoke_playwright_20260301');
const baseUrl = 'http://localhost:5173';
const sampleUser = {
  username: 'admin',
  password: 'admin123',
  source: 'samples/users.json',
};

const results = [];
let stepNo = 0;

function screenshotName(title) {
  stepNo += 1;
  const safe = title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]+/g, '_');
  return `${String(stepNo).padStart(2, '0')}-${safe}.png`;
}

async function runStep(page, title, action) {
  const file = screenshotName(title);
  const filePath = path.join(outDir, file);
  const rec = { step: stepNo, title, screenshot: file, status: 'PASS', error: null, url: null };

  try {
    await action();
    await page.waitForTimeout(600);
    rec.url = page.url();
  } catch (e) {
    rec.status = 'FAIL';
    rec.error = e && e.message ? e.message : String(e);
    rec.url = page.url();
  }

  try {
    await page.screenshot({ path: filePath, fullPage: true });
  } catch (e) {
    rec.status = 'FAIL';
    rec.error = rec.error || `screenshot failed: ${e && e.message ? e.message : String(e)}`;
  }

  results.push(rec);
  return rec.status === 'PASS';
}

(async () => {
  const browser = await chromium.launch({
    channel: 'chrome',
    headless: false,
    slowMo: 200,
  });

  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  await runStep(page, '首页', async () => {
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  });

  await runStep(page, '登录页', async () => {
    if (!page.url().includes('/login')) {
      await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' });
    }
  });

  await runStep(page, '登录-使用samples真实账号', async () => {
    const inputs = page.locator('input');
    await inputs.nth(0).fill(sampleUser.username);
    await inputs.nth(1).fill(sampleUser.password);

    const submit = page.getByRole('button', { name: /登\s*录/ });
    if (await submit.count()) {
      await submit.first().click();
    } else {
      await page.locator('button').first().click();
    }

    await page.waitForURL(/\/dashboard/, { timeout: 20000 });
  });

  const smokeRoutes = [
    { path: '/dashboard', name: '总览页' },
    { path: '/cases', name: '案件管理列表' },
    { path: '/documents', name: '中间文件列表' },
    { path: '/tasks/today', name: '今日任务提醒' },
    { path: '/fees/drafts', name: '费用草稿列表' },
    { path: '/billing/bills', name: '账单列表' },
    { path: '/billing/payments', name: '回款与核销列表' },
    { path: '/collections/dunning', name: '催款管理列表' },
    { path: '/commission/rules', name: '提成规则列表' },
    { path: '/consulting/cases/new', name: '顾问项目立案页' },
    { path: '/expenses', name: '支出管理列表' },
  ];

  for (const route of smokeRoutes) {
    await runStep(page, route.name, async () => {
      await page.goto(`${baseUrl}${route.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(1200);

      const bodyText = await page.locator('body').innerText();
      if (bodyText.includes('404') || bodyText.includes('Not Found') || bodyText.includes('权限不足')) {
        throw new Error(`page content indicates error: ${route.path}`);
      }
    });
  }

  await context.close();
  await browser.close();

  const jsonPath = path.join(outDir, 'smoke_results.json');
  fs.writeFileSync(jsonPath, JSON.stringify({
    executedAt: new Date().toISOString(),
    baseUrl,
    sampleData: {
      user: sampleUser,
      cases: ['CN-2025-0001', 'V3-001', 'CS-2025-CONS-001'],
      clients: ['C001', 'C-HW', 'C-BYD'],
      invoices: ['INV-2025-0001', 'INV-2025-0002'],
      payments: ['PAY-2026-0001', 'PAY-2026-0002'],
    },
    results,
  }, null, 2));

  const mdLines = [];
  mdLines.push('# FPMS Playwright Smoke Test Report');
  mdLines.push('');
  mdLines.push(`- 执行时间: ${new Date().toISOString()}`);
  mdLines.push(`- 前端地址: ${baseUrl}`);
  mdLines.push(`- 登录数据: ${sampleUser.username}/${sampleUser.password}（来源: ${sampleUser.source}）`);
  mdLines.push('');
  mdLines.push('| Step | Title | Status | URL | Screenshot | Error |');
  mdLines.push('|---|---|---|---|---|---|');
  for (const r of results) {
    mdLines.push(`| ${r.step} | ${r.title} | ${r.status} | ${r.url || ''} | ${r.screenshot} | ${r.error || ''} |`);
  }
  fs.writeFileSync(path.join(outDir, 'smoke_report.md'), mdLines.join('\n'));

  const failed = results.filter(r => r.status !== 'PASS').length;
  if (failed > 0) {
    process.exitCode = 2;
  }
})();
