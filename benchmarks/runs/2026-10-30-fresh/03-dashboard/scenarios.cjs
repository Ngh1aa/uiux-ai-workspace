// Kịch bản Playwright cho 03-dashboard (viewport 1280×900). page đã mở index.html.
module.exports = async (page, pass, assert) => {
  const txt = async (sel) => (await page.textContent(sel)).trim();

  // 1. Trạng thái ban đầu đúng số liệu đề, mục nổi bật có chip
  assert.equal(await txt('[data-test="kpi-pending"]'), '14');
  assert.equal(await txt('[data-test="kpi-overdue"]'), '3');
  assert.equal(await txt('[data-test="kpi-urgent"]'), '1');
  assert.equal(await txt('[data-test="rev-total"]'), '18.550');
  assert.equal(await page.locator('[data-test="rev-chart"] li').count(), 7);
  assert.ok((await page.getAttribute('[data-test="stock-row-LC-012"]', 'class')).includes('is-urgent'));
  assert.ok((await txt('[data-test="next-order"]')).includes('#2041'));
  pass('Mở trang: 14 đơn chờ gửi, 3 quá hạn, 1 cần nhập gấp (LC-012), biểu đồ 7 cột, tổng 18.550, gửi trước #2041');

  // 2. Gửi đơn quá hạn → Hủy → không đổi, focus về nút mở
  await page.click('[data-test="send-open-2041"]');
  assert.ok(await page.isVisible('[data-test="send-dialog"]'));
  assert.equal(await txt('[data-test="send-order"]'), '#2041');
  await page.click('[data-test="send-cancel"]');
  assert.ok(!(await page.isVisible('[data-test="send-dialog"]')));
  assert.equal(await txt('[data-test="kpi-pending"]'), '14');
  assert.ok(await page.evaluate(() => document.activeElement?.dataset.test === 'send-open-2041'));
  pass('Gửi đơn #2041 → Hủy: hộp thoại đóng, số không đổi, focus về đúng nút vừa bấm');

  // 3. Gửi đơn → xác nhận → kết quả, số cập nhật
  await page.click('[data-test="send-open-2041"]');
  await page.click('[data-test="send-confirm"]');
  assert.ok(await page.isVisible('[data-test="result"]'));
  assert.ok((await txt('[data-test="result-text"]')).includes('#2041'));
  assert.equal(await txt('[data-test="kpi-pending"]'), '13');
  assert.equal(await txt('[data-test="kpi-overdue"]'), '2');
  assert.equal(await page.locator('[data-test="overdue-row-2041"]').count(), 0);
  assert.ok((await txt('[data-test="next-order"]')).includes('#2045'));
  pass('Gửi đơn #2041 → xác nhận → thẻ kết quả; đơn chờ gửi 13, quá hạn 2, gửi trước chuyển sang #2045');

  // 4. Hoàn tác về đúng trạng thái trước
  await page.click('[data-test="result-undo"]');
  assert.equal(await txt('[data-test="kpi-pending"]'), '14');
  assert.equal(await txt('[data-test="kpi-overdue"]'), '3');
  assert.equal(await page.locator('[data-test="overdue-row-2041"]').count(), 1);
  pass('Hoàn tác gửi đơn: #2041 trở lại, 14 và 3 như cũ');

  // 5. Ghi nhập hàng: nút khoá có lý do → nhập sai → lỗi → sửa → kết quả
  await page.click('[data-test="restock-open-LC-012"]');
  assert.ok(await page.isVisible('[data-test="restock-dialog"]'));
  assert.ok((await txt('[data-test="restock-product"]')).includes('LC-012'));
  assert.ok(await page.isDisabled('[data-test="restock-confirm"]'));
  assert.equal(await page.getAttribute('[data-test="restock-confirm"]', 'aria-describedby'), 'restock-reason');
  assert.ok(await page.isVisible('[data-test="restock-reason"]'));
  pass('Ghi nhập hàng LC-012: nút xác nhận khoá khi chưa nhập, lý do hiện và gắn aria-describedby');

  await page.fill('[data-test="restock-qty"]', '0');
  assert.ok(await page.isDisabled('[data-test="restock-confirm"]'));
  assert.equal(await page.getAttribute('[data-test="restock-qty"]', 'aria-invalid'), 'true');
  await page.fill('[data-test="restock-qty"]', '30');
  assert.ok(await page.isEnabled('[data-test="restock-confirm"]'));
  assert.ok((await txt('[data-test="restock-preview"]')).includes('36 cuộn'));
  await page.click('[data-test="restock-confirm"]');
  assert.ok(!(await page.isVisible('[data-test="restock-dialog"]')));
  assert.ok((await txt('[data-test="result-text"]')).includes('30 cuộn'));
  assert.ok((await txt('[data-test="left-LC-012"]')).startsWith('36'));
  assert.ok((await txt('[data-test="days-LC-012"]')).includes('12 ngày'));
  assert.ok(!(await page.getAttribute('[data-test="stock-row-LC-012"]', 'class')).includes('is-urgent'));
  assert.equal(await txt('[data-test="kpi-urgent"]'), '0');
  assert.equal(await txt('[data-test="kpi-low"]'), '3');
  pass('Nhập 0 → lỗi, nút khoá; sửa thành 30 → xác nhận → kết quả; LC-012 còn 36 cuộn, đủ bán 12 ngày, cần nhập gấp 0, sắp hết hàng 3');

  // 6. Esc đóng hộp thoại, không đổi dữ liệu
  await page.click('[data-test="restock-open-KM-035"]');
  await page.fill('[data-test="restock-qty"]', '5');
  await page.keyboard.press('Escape');
  assert.ok(!(await page.isVisible('[data-test="restock-dialog"]')));
  assert.ok((await txt('[data-test="left-KM-035"]')).startsWith('4'));
  pass('Ghi nhập hàng KM-035 → Esc: không ghi, còn 4 cây');

  // 7. Gửi hết đơn quá hạn → trạng thái rỗng
  for (const id of ['2041', '2045', '2047']) {
    await page.click(`[data-test="send-open-${id}"]`);
    await page.click('[data-test="send-confirm"]');
  }
  assert.ok(await page.isVisible('[data-test="overdue-empty"]'));
  assert.equal(await txt('[data-test="kpi-overdue"]'), '0');
  assert.equal(await txt('[data-test="kpi-pending"]'), '11');
  pass('Gửi cả 3 đơn quá hạn: danh sách rỗng có thông báo, quá hạn 0, đơn chờ gửi 11');

  // 8. Không cuộn ngang ở 390
  await page.setViewportSize({ width: 390, height: 844 });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  assert.ok(!overflow);
  pass('390px: không cuộn ngang');
};
