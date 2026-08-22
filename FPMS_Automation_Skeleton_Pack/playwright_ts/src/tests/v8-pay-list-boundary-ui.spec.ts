import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "@playwright/test";

const pageSource = readFileSync(
  resolve(process.cwd(), "../../frontend/src/modules/annuity/pages/PayListDetail.vue"),
  "utf8",
);

test("PayList detail declares four separate Simplified Chinese boundary sections", () => {
  expect(pageSource).toContain('<span class="form-card-title">内部导出</span>');
  expect(pageSource).toContain('<span class="form-card-title">官方工作簿</span>');
  expect(pageSource).toContain('<span class="form-card-title">支付记录</span>');
  expect(pageSource).toContain('<span class="form-card-title">官方凭证</span>');

  expect(pageSource).toContain("detail.internal_artifacts");
  expect(pageSource).toContain("detail.official_workbook");
  expect(pageSource).toContain("detail.payment");
  expect(pageSource).toContain("detail.official_evidence");
});

test("PayList detail gates absent official facts without consulting header status", () => {
  expect(pageSource).toContain('v-if="detail.official_workbook"');
  expect(pageSource).toContain("官方工作簿门禁尚未开放");
  expect(pageSource).toContain("当前没有内部导出产物");
  expect(pageSource).toContain("当前清单暂无支付记录");
  expect(pageSource).toContain("当前没有官方凭证");

  const officialWorkbookStart = pageSource.indexOf(
    '<span class="form-card-title">官方工作簿</span>',
  );
  const paymentStart = pageSource.indexOf('<span class="form-card-title">支付记录</span>');

  expect(officialWorkbookStart).toBeGreaterThanOrEqual(0);
  expect(paymentStart).toBeGreaterThan(officialWorkbookStart);

  const officialWorkbookSection = pageSource.slice(officialWorkbookStart, paymentStart);

  expect(officialWorkbookSection).not.toContain("detail.pay_list.status");
});
