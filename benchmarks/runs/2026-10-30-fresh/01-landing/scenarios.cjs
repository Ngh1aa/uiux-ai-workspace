// Kịch bản Playwright cho 01-landing (viewport 390×844).
module.exports = async (page, pass, assert) => {
  const t = s => `[data-test="${s}"]`;
  const text = async s => (await page.textContent(t(s))).trim();

  // 1. Nút đầu trang mở luồng; nút khoá có lý do theo từng bước thiếu dữ liệu
  await page.click(t('book-top'));
  assert.ok(await page.isVisible(t('booking')), 'hộp đặt chỗ mở');
  assert.ok(await page.isDisabled(t('submit')), 'nút Đặt chỗ khoá khi chưa chọn gì');
  assert.equal(await text('reason'), 'Chọn lớp');
  assert.equal(await page.getAttribute(t('submit'), 'aria-describedby'), 'f-reason');
  await page.click(t('class-0'));
  assert.equal(await text('reason'), 'Chọn ngày');
  await page.click(t('date-0'));
  assert.equal(await text('reason'), 'Chọn ca');
  assert.match(await page.textContent(t('date-0')), /^(Thứ Bảy|Chủ nhật) \d{1,2}\/\d{1,2}$/);
  pass('Nút khoá kèm lý do: Chọn lớp → Chọn ngày → Chọn ca; ngày hiện thứ + ngày tháng');

  // 2. Ca hết chỗ bị khoá
  assert.equal(await text('slot-left-0'), 'Hết chỗ');
  assert.ok(await page.isDisabled(`${t('slot-0')} input`), 'ca hết chỗ không chọn được');
  pass('Bàn xoay cơ bản, ngày đầu, ca sáng hết chỗ: ô ca bị khoá, nhãn "Hết chỗ"');

  // 3. Nhánh lỗi: vượt số chỗ còn → giảm thì mở khoá; số điện thoại sai → sửa thì mở khoá
  await page.click(t('slot-1'));
  const leftText = await text('slot-left-1');
  const left = Number(leftText.match(/\d+/)[0]);
  for (let i = 1; i <= left; i++) await page.click(t('ppl-plus'));
  assert.equal(await text('ppl'), String(left + 1));
  assert.equal(await text('reason'), `Ca này còn ${left} chỗ`);
  await page.click(t('ppl-minus'));
  for (let i = left; i > 2; i--) await page.click(t('ppl-minus'));
  assert.equal(await text('ppl'), '2');
  assert.equal(await text('reason'), 'Nhập họ tên');
  await page.fill(t('name'), 'Lan Anh');
  await page.fill(t('phone'), '09123');
  await page.locator(t('phone')).blur();
  assert.ok(await page.isVisible(t('phone-error')), 'lỗi tại ô điện thoại');
  assert.equal(await text('reason'), 'Kiểm tra số điện thoại');
  assert.ok(await page.isDisabled(t('submit')));
  await page.fill(t('phone'), '0987 654 321');
  assert.ok(await page.isHidden(t('phone-error')), 'lỗi biến mất sau khi sửa');
  assert.ok(await page.isEnabled(t('submit')), 'nút mở khoá');
  assert.equal(await text('form-total'), '900.000 ₫');
  pass('Lỗi vượt chỗ và số điện thoại sai → sửa → nút mở khoá, tổng 2 × 450.000 ₫ = 900.000 ₫');

  // 4. Xác nhận → Hủy về form giữ dữ liệu
  await page.click(t('submit'));
  assert.ok(await page.isVisible(t('confirm')));
  assert.equal(await text('total'), '900.000 ₫');
  await page.click(t('cancel'));
  assert.ok(await page.isVisible(t('submit')), 'Hủy về đúng form');
  assert.equal(await page.inputValue(t('name')), 'Lan Anh');
  assert.equal(await text('ppl'), '2');
  pass('Xác nhận có Hủy: Hủy quay về form, giữ nguyên lớp, ngày, ca, số người, liên hệ');

  // 5. Sửa lựa chọn → xác nhận lại → kết quả; trang hiện lượt vừa đặt, số chỗ còn giảm
  await page.click(t('class-1'));
  await page.click(t('slot-1'));
  const leftBefore = Number((await text('slot-left-1')).match(/\d+/)[0]);
  await page.click(t('submit'));
  assert.equal(await text('total'), '700.000 ₫');
  await page.click(t('confirm-ok'));
  assert.ok(await page.isVisible(t('result')));
  const code = await text('code');
  assert.match(code, /^DN-\d{4}-01$/);
  await page.click(t('done'));
  assert.ok(await page.isHidden(t('booking')), 'Xong đóng hộp');
  assert.ok((await text('booked-top')).includes(code));
  assert.ok((await text('booked-bottom')).includes('700.000 ₫'));
  await page.click(t('book-bottom'));
  assert.ok(await page.isVisible(t('booking')), 'nút cuối trang mở cùng luồng');
  await page.click(t('class-1')); await page.click(t('date-0')); await page.click(t('slot-1'));
  assert.equal(Number((await text('slot-left-1')).match(/\d+/)[0]), leftBefore - 2);
  pass('Đổi sang Nặn tay → xác nhận 700.000 ₫ → kết quả có mã; thẻ trạng thái hiện ở đầu và cuối trang; số chỗ còn giảm 2');

  // 6. Đóng giữa chừng giữ bản nháp
  await page.fill(t('name'), 'Minh');
  await page.click(t('close'));
  assert.ok(await page.isHidden(t('booking')));
  await page.click(t('book-top'));
  assert.equal(await page.inputValue(t('name')), 'Minh');
  assert.ok(await page.isChecked(`${t('class-1')} input`));
  pass('Đóng hộp giữa chừng rồi mở lại: bản nháp còn nguyên');
};
