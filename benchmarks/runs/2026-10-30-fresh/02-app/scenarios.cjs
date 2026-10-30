// Kịch bản Playwright cho 02-app. Viewport 390×844, trang đã mở index.html.
module.exports = async (page, pass, assert) => {
  const q = s => page.locator(s);
  const fresh = async () => { await page.reload(); await page.waitForSelector('#home-courts [data-test="court-pn"]'); };
  const active = id => page.$eval(id, el => el.hasAttribute('data-active'));

  // 1. Trạng thái rỗng tab Đã qua
  await fresh();
  assert.strictEqual(await q('[data-test="tab-past"]').getAttribute('aria-pressed'), 'true');
  assert.ok(await q('[data-test="past-empty"]').isVisible());
  assert.match(await q('[data-test="past-empty"]').innerText(), /Chưa có lượt đã qua/);
  pass('Lịch của tôi: tab Đã qua hiện trạng thái rỗng có nút Tìm sân');

  // 2. Nút Tiếp tục khoá khi chưa chọn khung, có lý do gắn với nút
  await q('#home-courts [data-test="court-pn"]').click();
  assert.strictEqual((await q('#detail-title').innerText()).trim(), 'Sân Phú Nhuận');
  const cont = q('[data-test="continue"]');
  assert.strictEqual(await cont.getAttribute('aria-disabled'), 'true');
  assert.strictEqual(await cont.getAttribute('aria-describedby'), 'detail-reason');
  assert.ok(await q('#detail-reason').isVisible());
  await cont.click({ force: true });
  assert.ok(!(await active('#s-book')), 'nút khoá không được chuyển màn');
  pass('Chi tiết sân: Tiếp tục khoá kèm lý do khi chưa chọn khung');

  // 3. Back về đúng màn vừa rời (Trang chủ, Tìm sân), Đặt sân → Chi tiết đúng sân
  await q('[data-test="detail-back"]').click();
  assert.ok(await active('#s-home'));
  await q('#list-courts [data-test="court-kh"]').click();
  assert.strictEqual((await q('#detail-title').innerText()).trim(), 'Sân Kỳ Hoà');
  await q('[data-test="detail-back"]').click();
  assert.ok(await active('#s-list'));
  await q('#list-courts [data-test="court-td"]').click();
  await q('[data-test="pick-slot-20"]').click();
  await q('[data-test="continue"]').click();
  assert.ok(await active('#s-book'));
  await q('[data-test="book-back"]').click();
  assert.ok(await active('#s-detail'));
  assert.strictEqual((await q('#detail-title').innerText()).trim(), 'Sân Tân Định');
  assert.strictEqual(await q('[data-test="pick-slot-20"]').getAttribute('aria-pressed'), 'true');
  pass('Back: Chi tiết về Trang chủ hoặc Tìm sân tuỳ nơi vào; Đặt sân về Chi tiết đúng sân, giữ khung đã chọn');

  // 4. Đường chính: Phú Nhuận 20:00 → Hủy giữ form → xác nhận → kết quả → Lịch có lượt mới
  await fresh();
  await q('#home-courts [data-test="court-pn"]').click();
  await q('[data-test="pick-slot-20"]').click();
  await q('[data-test="continue"]').click();
  assert.match(await q('[data-test="book-slot"]').innerText(), /20:00–21:00/);
  assert.match(await q('[data-test="book-total"]').innerText(), /120\.000 ₫/);
  await q('[data-test="book"]').click();
  assert.ok(await q('[data-test="confirm-sheet"]').isVisible());
  assert.match(await q('#confirm-kv').innerText(), /Sân Phú Nhuận[\s\S]*20:00–21:00[\s\S]*120\.000 ₫/);
  await q('[data-test="confirm-cancel"]').click();
  assert.ok(await q('[data-test="confirm-sheet"]').isHidden());
  assert.match(await q('[data-test="book-slot"]').innerText(), /20:00–21:00/);
  assert.strictEqual(await q('#bookings [data-test="booking"]').count(), 1);
  await q('[data-test="book"]').click();
  await q('[data-test="confirm-book"]').click();
  assert.ok(await q('[data-test="booking-result"]').isVisible());
  await q('[data-test="result-schedule"]').click();
  assert.ok(await active('#s-schedule'));
  assert.strictEqual(await q('[data-test="tab-upcoming"]').getAttribute('aria-pressed'), 'true');
  assert.strictEqual(await q('#bookings [data-test="booking"]').count(), 2);
  assert.match(await q('#bookings [data-new="true"]').innerText(), /20:00–21:00[\s\S]*Sân Phú Nhuận/);
  assert.match(await q('[data-test="hero-time"]').innerText(), /20:00–21:00/);
  assert.match(await q('#list-courts [data-test="court-pn"]').innerText(), /2 khung trống/);
  pass('Đặt Sân Phú Nhuận 20:00: Hủy giữ form, xác nhận → Đã đặt sân → Lịch của tôi có lượt mới, trang chủ và số khung cập nhật');

  // 5. Lỗi khung 19:00 vừa bị đặt → chọn khung khác → đặt thành công
  await fresh();
  await q('#list-courts [data-test="court-kh"]').click();
  await q('[data-test="pick-slot-19"]').click();
  await q('[data-test="continue"]').click();
  await q('[data-test="book"]').click();
  await q('[data-test="confirm-book"]').click();
  assert.ok(await q('#s-book [data-test="book-error"]').isVisible());
  assert.match(await q('#s-book [data-test="book-error"]').innerText(), /19:00 vừa có người đặt/);
  assert.ok(await q('[data-test="booking-result"]').isHidden());
  assert.strictEqual(await q('[data-test="book"]').getAttribute('aria-disabled'), 'true');
  assert.ok(await q('#book-reason').isVisible());
  assert.strictEqual(await q('[data-test="alt-19"]').count(), 0);
  await q('[data-test="alt-21"]').click();
  assert.strictEqual(await q('[data-test="book"]').getAttribute('aria-disabled'), 'false');
  assert.ok(await q('#s-book [data-test="book-error"]').isHidden());
  await q('[data-test="book"]').click();
  assert.match(await q('#confirm-kv').innerText(), /21:00–22:00/);
  await q('[data-test="confirm-book"]').click();
  assert.ok(await q('[data-test="booking-result"]').isVisible());
  assert.match(await q('#bookings [data-new="true"]').innerText(), /21:00–22:00[\s\S]*Sân Kỳ Hoà/);
  pass('Kỳ Hoà 19:00 vừa bị đặt: báo lỗi, nút Đặt sân khoá kèm lý do, chọn 21:00 từ gợi ý → đặt thành công');

  // 6. Đổi khung bằng sheet riêng, quay về đúng form
  await fresh();
  await q('#home-courts [data-test="court-pn"]').click();
  await q('[data-test="pick-slot-18"]').click();
  await q('[data-test="continue"]').click();
  await q('[data-test="book-slot"]').click();
  assert.ok(await q('[data-test="slot-sheet"]').isVisible());
  await q('[data-test="pick-sheet-slot-19"]').click({ force: true });
  assert.ok(await q('[data-test="slot-sheet"]').isVisible(), 'khung đã đặt không chọn được');
  await q('[data-test="pick-sheet-slot-21"]').click();
  assert.ok(await q('[data-test="slot-sheet"]').isHidden());
  assert.ok(await active('#s-book'));
  assert.match(await q('[data-test="book-slot"]').innerText(), /21:00–22:00/);
  pass('Khung giờ trong form mở sheet riêng, khung đã đặt không chọn được, chọn xong về đúng form');

  // 7. Tìm không ra → Xóa tìm kiếm khôi phục danh sách
  await q('[data-test="search"]').fill('Thủ Đức');
  assert.ok(await q('[data-test="list-empty"]').isVisible());
  await q('[data-test="clear-search"]').click();
  assert.strictEqual(await q('#list-courts [data-test^="court-"]').count(), 3);
  await q('[data-test="chip-q10"]').click();
  assert.strictEqual(await q('#list-courts [data-test^="court-"]').count(), 1);
  pass('Tìm sân: không có kết quả → Xóa tìm kiếm; lọc Quận 10 còn Sân Kỳ Hoà');
};
