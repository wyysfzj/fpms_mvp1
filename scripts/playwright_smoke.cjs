const fs = require('fs');
const os = require('os');
const path = require('path');
const repoRoot = path.resolve(__dirname, '..');

function loadPlaywright() {
  try {
    return require('playwright');
  } catch {}

  const npxRoot = path.join(os.homedir(), '.npm', '_npx');
  if (!fs.existsSync(npxRoot)) {
    throw new Error('Cannot find playwright package. Install it or run via npm exec playwright.');
  }

  const candidates = fs
    .readdirSync(npxRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(npxRoot, entry.name, 'node_modules', 'playwright'))
    .filter((pkgPath) => fs.existsSync(pkgPath));

  if (candidates.length === 0) {
    throw new Error('Cannot find cached playwright package under ~/.npm/_npx.');
  }

  candidates.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
  return require(candidates[0]);
}

const { chromium } = loadPlaywright();

const outDir = process.env.PLAYWRIGHT_SMOKE_OUTDIR
  ? path.resolve(process.env.PLAYWRIGHT_SMOKE_OUTDIR)
  : path.join(repoRoot, 'artifacts', 'playwright_smoke_latest');
const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5173';
const sampleUser = {
  username: process.env.PLAYWRIGHT_USERNAME || 'admin',
  password: process.env.PLAYWRIGHT_PASSWORD || 'admin123',
  source: 'samples/users.json',
};
const headless = process.env.PLAYWRIGHT_HEADFUL === '1' ? false : true;
const browserChannel = process.env.PLAYWRIGHT_CHANNEL || undefined;
const fallbackChromeHeadless = process.env.PLAYWRIGHT_FALLBACK_HEADLESS === '1';
const stepTimeoutMs = Number(process.env.PLAYWRIGHT_STEP_TIMEOUT_MS || 30000);
const perRouteSettledMs = Number(process.env.PLAYWRIGHT_SETTLE_MS || 1200);
const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

fs.mkdirSync(outDir, { recursive: true });

const results = [];
let stepNo = 0;

function screenshotName(title) {
  stepNo += 1;
  const safe = title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]+/g, '_');
  return `${String(stepNo).padStart(2, '0')}-${safe}.png`;
}

function formatError(error) {
  return error && error.message ? error.message : String(error);
}

async function checkHttpOk(url, label) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${label} preflight failed: ${response.status} ${response.statusText}`);
  }
}

async function runApiPreflight() {
  await checkHttpOk(`${baseUrl}/`, 'frontend');
  await checkHttpOk(apiBaseUrl.replace(/\/api\/v1$/, '/healthz'), 'backend health');

  const loginResponse = await fetch(`${apiBaseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: sampleUser.username,
      password: sampleUser.password,
    }),
  });
  if (!loginResponse.ok) {
    throw new Error(`backend login preflight failed: ${loginResponse.status} ${loginResponse.statusText}`);
  }

  const loginPayload = await loginResponse.json();
  const token = loginPayload.access_token;
  if (!token) {
    throw new Error('backend login preflight failed: missing access_token');
  }

  const casesResponse = await fetch(`${apiBaseUrl}/cases?page=1&page_size=1`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!casesResponse.ok) {
    const body = await casesResponse.text();
    throw new Error(`cases API preflight failed: ${casesResponse.status} ${body.slice(0, 240)}`);
  }
}

async function withTimeout(title, fn) {
  let timeoutId;
  try {
    return await Promise.race([
      fn(),
      new Promise((_, reject) => {
        timeoutId = setTimeout(() => reject(new Error(`step timeout after ${stepTimeoutMs}ms: ${title}`)), stepTimeoutMs);
      }),
    ]);
  } finally {
    clearTimeout(timeoutId);
  }
}

async function runStep(page, title, action) {
  const file = screenshotName(title);
  const filePath = path.join(outDir, file);
  const rec = { step: stepNo, title, screenshot: file, status: 'PASS', error: null, url: null };

  console.log(`[playwright-smoke] step ${rec.step}: ${title}`);

  try {
    await withTimeout(title, action);
    await page.waitForTimeout(500);
    rec.url = page.url();
  } catch (error) {
    rec.status = 'FAIL';
    rec.error = formatError(error);
    rec.url = page.url();
    console.error(`[playwright-smoke] step ${rec.step} failed: ${rec.error}`);
  }

  try {
    await page.screenshot({ path: filePath, fullPage: true });
  } catch (error) {
    rec.status = 'FAIL';
    rec.error = rec.error || `screenshot failed: ${formatError(error)}`;
  }

  results.push(rec);
  return rec.status === 'PASS';
}

async function gotoAndCheck(page, routePath) {
  await page.goto(`${baseUrl}${routePath}`, { waitUntil: 'domcontentloaded', timeout: stepTimeoutMs });
  await page.waitForTimeout(perRouteSettledMs);

  const bodyText = await page.locator('body').innerText();
  if (bodyText.includes('404') || bodyText.includes('Not Found') || bodyText.includes('权限不足')) {
    throw new Error(`page content indicates error: ${routePath}`);
  }
}

async function main() {
  await runApiPreflight();

  let browser;
  let launchedHeadless = headless;
  let launchedChannel = browserChannel || null;
  try {
    browser = await chromium.launch({
      headless,
      ...(browserChannel ? { channel: browserChannel } : {}),
    });
  } catch (error) {
    const message = formatError(error);
    const canFallbackToChrome = !browserChannel && message.includes("Executable doesn't exist");
    if (!canFallbackToChrome) {
      throw error;
    }

    console.warn(
      `[playwright-smoke] bundled browser missing, retrying with local Chrome channel (${fallbackChromeHeadless ? 'headless' : 'headed'})`,
    );
    launchedHeadless = fallbackChromeHeadless;
    launchedChannel = 'chrome';
    browser = await chromium.launch({
      headless: fallbackChromeHeadless,
      channel: 'chrome',
    });
  }

  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const pageErrors = [];

  page.on('pageerror', (error) => {
    pageErrors.push(formatError(error));
  });

  try {
    await runStep(page, '首页', async () => {
      await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: stepTimeoutMs });
    });

    await runStep(page, '登录页', async () => {
      if (!page.url().includes('/login')) {
        await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded', timeout: stepTimeoutMs });
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

      await page.waitForURL(/\/dashboard/, { timeout: stepTimeoutMs });
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
        await gotoAndCheck(page, route.path);
      });
    }
  } finally {
    await context.close();
    await browser.close();
  }

  const jsonPath = path.join(outDir, 'smoke_results.json');
  fs.writeFileSync(
    jsonPath,
    JSON.stringify(
      {
        executedAt: new Date().toISOString(),
        baseUrl,
        headless: launchedHeadless,
        browserChannel: launchedChannel,
        sampleData: {
          user: sampleUser,
        },
        pageErrors,
        results,
      },
      null,
      2,
    ),
  );

  const mdLines = [];
  mdLines.push('# FPMS Playwright Smoke Test Report');
  mdLines.push('');
  mdLines.push(`- 执行时间: ${new Date().toISOString()}`);
  mdLines.push(`- 前端地址: ${baseUrl}`);
  mdLines.push(`- 无头模式: ${launchedHeadless ? '是' : '否'}`);
  mdLines.push(`- 浏览器通道: ${launchedChannel || 'bundled'}`);
  mdLines.push(`- 登录数据: ${sampleUser.username}/${sampleUser.password}（来源: ${sampleUser.source}）`);
  mdLines.push('');
  if (pageErrors.length) {
    mdLines.push('## Page Errors');
    mdLines.push('');
    for (const error of pageErrors) {
      mdLines.push(`- ${error}`);
    }
    mdLines.push('');
  }
  mdLines.push('| Step | Title | Status | URL | Screenshot | Error |');
  mdLines.push('|---|---|---|---|---|---|');
  for (const r of results) {
    mdLines.push(`| ${r.step} | ${r.title} | ${r.status} | ${r.url || ''} | ${r.screenshot} | ${r.error || ''} |`);
  }
  fs.writeFileSync(path.join(outDir, 'smoke_report.md'), mdLines.join('\n'));

  const failed = results.filter((record) => record.status !== 'PASS').length;
  if (failed > 0) {
    process.exitCode = 2;
  }
}

main().catch((error) => {
  console.error(`[playwright-smoke] fatal: ${formatError(error)}`);
  process.exitCode = 1;
});
