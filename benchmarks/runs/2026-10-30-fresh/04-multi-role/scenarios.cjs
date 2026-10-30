'use strict';
// Kịch bản hành vi cho 04-multi-role (viewport 1280×800). Mỗi khung data-screen là một phiên app riêng.
module.exports = async (page, pass, assert) => {
  const R = '#s-reception', D = '#s-doctor', O = '#s-owner', X = '#s-denied';
  const t = (f, k) => `${f} [data-test="${k}"]`;
  const vis = (s) => page.isVisible(s);
  const txt = (s) => page.textContent(s);

  // 1. Xung đột khi xếp khách vãng lai vào khung đã có người → chọn khung khác → đặt → kết quả, lịch cập nhật
  assert.ok(await vis(t(R, 'conflict')), 'Khối xung đột hiển thị');
  assert.match(await txt(t(R, 'conflict')), /Ghế 1 lúc 9:30 đã có Lâm Gia Bảo/);
  assert.ok(await page.isDisabled(t(R, 'book-submit')), 'Đặt lịch khoá khi trùng');
  assert.equal((await txt(t(R, 'book-reason'))).trim(), 'Khung đã có người, chọn khung khác');
  assert.ok((await page.getAttribute(t(R, 'book-submit'), 'aria-describedby')).length > 0);
  pass('Xếp khách vãng lai vào Ghế 1 9:30 đã có người: hiện xung đột, nút Đặt lịch khoá có lý do');
  const pending0 = await txt(t(R, 'count-pending'));
  await page.click(`${t(R, 'alt-slot')} >> nth=0`);
  assert.ok(!(await vis(t(R, 'conflict'))), 'Hết xung đột sau khi chọn khung khác');
  assert.ok(await page.isEnabled(t(R, 'book-submit')));
  await page.click(t(R, 'book-submit'));
  assert.ok(await vis(t(R, 'booking-result')));
  assert.match(await txt(t(R, 'booking-result')), /Ngô Thanh Tâm/);
  assert.match(await txt(t(R, 'booking-result')), /9:30/);
  assert.notEqual(await txt(t(R, 'count-pending')), pending0, 'Số Chưa đến cập nhật');
  assert.match(await txt(t(R, 'schedule')), /Ngô Thanh Tâm/);
  pass('Chọn khung trống gợi ý → Đặt lịch → thẻ kết quả, lưới lịch và số Chưa đến cập nhật');

  // 2. Nút khoá khi thiếu tên, mở lại khi nhập
  await page.click(t(R, 'book-again'));
  assert.ok(await page.isDisabled(t(R, 'book-submit')));
  assert.equal((await txt(t(R, 'book-reason'))).trim(), 'Nhập họ tên bệnh nhân');
  await page.fill(t(R, 'f-name'), 'Phạm Minh Khoa');
  assert.ok(await page.isEnabled(t(R, 'book-submit')));
  await page.click(t(R, 'booking-cancel'));
  assert.ok(await vis(t(R, 'upcoming')));
  pass('Form trống: Đặt lịch khoá với lý do "Nhập họ tên bệnh nhân"; Hủy về danh sách Sắp đến');

  // 3. Bàn phím: Tab tới ô Trống, Enter mở form, gõ tên, Enter gửi
  await page.focus(t(R, 'search'));
  await page.keyboard.press('Tab'); // Đặt lịch
  assert.equal(await page.evaluate(() => document.activeElement.dataset.test), 'book');
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(() => document.activeElement.dataset.test), 'f-name', 'Focus vào ô họ tên');
  await page.keyboard.type('Lê Văn Hải');
  await page.keyboard.press('Enter');
  assert.ok(await vis(t(R, 'booking-result')));
  assert.equal(await page.evaluate(() => document.activeElement.textContent.trim()), 'Đã đặt lịch');
  await page.keyboard.press('Escape');
  assert.ok(await vis(t(R, 'upcoming')));
  pass('Chỉ bàn phím: Tab tới Đặt lịch, Enter, gõ tên, Enter đặt; Esc đóng thẻ kết quả');

  // 4. Mở đúng lượt và Back về đúng chỗ
  await page.click(t(R, 'row-a3'));
  assert.match(await txt(t(R, 'appt-detail')), /Hồ Ngọc Mai/);
  await page.click(t(R, 'arrive'));
  assert.match(await txt(t(R, 'detail-status')), /Đã đến/);
  await page.click(t(R, 'detail-back'));
  assert.ok(await vis(t(R, 'upcoming')));
  assert.equal(await page.evaluate(() => document.activeElement.dataset.test), 'row-a4', 'Focus về dòng đầu Sắp đến');
  assert.ok(!(await txt(t(R, 'upcoming'))).includes('Hồ Ngọc Mai'), 'Hồ Ngọc Mai rời Sắp đến');
  pass('Dòng Hồ Ngọc Mai mở đúng lượt → Xác nhận đến → Quay lại về Sắp đến, danh sách cập nhật');

  // 5. Bác sĩ: dị ứng tách biệt, Bắt đầu khám khoá tới khi gọi
  assert.match(await txt(t(D, 'allergy')), /Penicillin/);
  assert.equal(await page.getAttribute(t(D, 'allergy'), 'role'), 'alert');
  assert.ok(await page.isDisabled(t(D, 'start')));
  assert.match(await txt(t(D, 'start-reason')), /Gọi bệnh nhân trước/);
  await page.click(t(D, 'call'));
  assert.ok(await page.isEnabled(t(D, 'start')));
  await page.click(t(D, 'start'));
  assert.match(await txt(t(D, 'patient-status')), /Đang khám/);
  await page.fill(t(D, 'note'), 'Bé hợp tác, cầm máu tốt');
  await page.click(t(D, 'save-note'));
  assert.match(await txt(t(D, 'note-status')), /Đã lưu ghi chú/);
  pass('Bác sĩ: dị ứng Penicillin riêng khối; Bắt đầu khám khoá có lý do → Gọi bệnh nhân → Bắt đầu khám → Lưu ghi chú');

  // 6. Chủ: trạng thái rỗng Ghế 3
  assert.match(await txt(t(O, 'chair3-empty')), /Chưa đủ 7 ngày dữ liệu/);
  assert.match(await txt(t(O, 'month')), /186\.200\.000 đ/);
  assert.ok(!(await vis(t(O, 'nav-next'))), 'Chủ không thấy Bệnh nhân tiếp theo');
  pass('Chủ phòng khám: doanh thu tháng, Ghế 3 trạng thái rỗng, điều hướng ẩn mục của bác sĩ');

  // 7. Không có quyền → Quay lại về Lịch hôm nay
  assert.ok(await vis(t(X, 'denied')));
  assert.ok(!(await vis(t(X, 'nav-revenue'))), 'Lễ tân không có mục Doanh thu');
  await page.click(t(X, 'denied-back'));
  assert.equal(await page.getAttribute(t(X, 'main'), 'data-view'), 'schedule');
  assert.equal(await page.getAttribute(t(X, 'nav-schedule'), 'aria-current'), 'page');
  pass('Lễ tân mở Doanh thu: trạng thái không có quyền → Quay lại về Lịch hôm nay');

  // 8. Đổi vai trò bằng menu tài khoản, có bàn phím
  await page.focus(t(X, 'account'));
  await page.keyboard.press('Enter');
  assert.ok(await vis(t(X, 'role-owner')));
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  assert.equal(await page.getAttribute(t(X, 'main'), 'data-view'), 'revenue');
  assert.ok(await vis(t(X, 'nav-revenue')));
  assert.ok(!(await vis(t(X, 'book'))));
  await page.click(t(X, 'account'));
  await page.keyboard.press('Escape');
  assert.ok(!(await vis(t(X, 'role-owner'))));
  pass('Đổi vai trò bằng menu tài khoản (bàn phím): sang Chủ phòng khám mở Doanh thu, ẩn Đặt lịch; Esc đóng menu');
};
