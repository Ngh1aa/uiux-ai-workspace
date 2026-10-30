'use strict';
/* Kịch bản hành vi cho đề 05-native. Mỗi khung data-screen là một app độc lập có trạng thái riêng. */
module.exports = async (page, pass, assert) => {
  const S = (screen, test) => `[data-screen="${screen}"] [data-test="${test}"]`;
  const text = async sel => ((await page.textContent(sel)) || '').replace(/\s+/g, ' ').trim();
  const visible = sel => page.isVisible(sel);
  const gone = async sel => !(await page.$(sel)) || !(await page.isVisible(sel));

  for (const [P, label] of [['iOS', 'iOS'], ['Android', 'Android']]) {
    /* 1. Hôm nay → bài tập → nộp ảnh (Hủy rồi nộp thật) → kết quả → Back, số bài cập nhật */
    const home = `${P} Hôm nay`;
    assert.equal(await text(S(home, 'todo-count')), '2');
    await page.click(S(home, 'hw-cay-dua'));
    assert.equal(await text(S(home, 'hw-title')), 'Tập đọc: Cây dừa');
    await page.click(S(home, 'submit-photo'));
    assert.ok(await visible(S(home, 'pick-cancel')));
    await page.click(S(home, 'pick-cancel'));
    assert.ok(await gone(S(home, 'pick-cancel')));
    assert.ok(await visible(S(home, 'submit-photo')));
    await page.click(S(home, 'submit-photo'));
    await page.click(S(home, 'pick-camera'));
    assert.match(await text(S(home, 'result')), /Đã nộp ảnh bài làm/);
    assert.ok(await gone(S(home, 'submit-photo')));
    assert.match(await text(`[data-screen="${home}"]`), /Đã nộp/);
    await page.click(S(home, 'back'));
    assert.equal(await text(S(home, 'todo-count')), '1');
    assert.ok(!(await page.$(S(home, 'hw-cay-dua'))), 'bài đã nộp rời danh sách chưa nộp');
    pass(`${label}: Hôm nay → Tập đọc: Cây dừa → Nộp ảnh (Hủy, rồi Chụp ảnh) → kết quả Đã nộp → Back về Hôm nay, bài chưa nộp 2 → 1`);

    /* 2. Mở đúng đối tượng: bài Toán */
    await page.click(S(home, 'hw-bai-14'));
    assert.equal(await text(S(home, 'hw-title')), 'Bài 14: Phép cộng có nhớ');
    await page.click(S(home, 'back'));
    assert.equal(await text(S(home, 'todo-count')), '1');
    pass(`${label}: dòng Bài 14 mở đúng bài Toán, Back về Hôm nay giữ số đã cập nhật`);

    /* 3. Xin nghỉ: lỗi ngày đã qua tại trường ngày, nút khoá có lý do → chọn lại → gửi → kết quả */
    const form = `${P} Xin nghỉ`;
    assert.ok(await visible(S(form, 'date-error')));
    assert.match(await text(S(form, 'date-error')), /Thứ Ba 21\/10 đã qua/);
    assert.equal(await page.getAttribute(S(form, 'send'), 'aria-disabled'), 'true');
    const why = await page.getAttribute(S(form, 'send'), 'aria-describedby');
    assert.match(await text(`[data-screen="${form}"] #${why}`), /Ngày nghỉ đã qua/);
    await page.click(S(form, 'send'));
    assert.ok(await visible(S(form, 'form')), 'nút khoá không gửi đơn');
    await page.click(S(form, 'day-24-10'));
    assert.ok(await gone(S(form, 'date-error')));
    assert.equal(await page.getAttribute(S(form, 'send'), 'aria-disabled'), null);
    await page.click(S(form, 'send'));
    assert.ok(await gone(S(form, 'form')));
    assert.match(await text(S(form, 'result')), /Đã gửi đơn nghỉ cả ngày thứ Sáu 24\/10/);
    assert.match(await text(S(form, 'leave-l2')), /Nghỉ cả ngày thứ Sáu 24\/10.*Đã gửi/);
    pass(`${label}: Xin nghỉ chọn thứ Ba 21/10 → lỗi tại trường ngày, Gửi đơn khoá kèm lý do → chọn thứ Sáu 24/10 → gửi → kết quả và đơn mới trong danh sách`);

    /* 4. Form mới: khoá theo từng lý do, đóng form về đúng màn */
    await page.click(S(form, 'new-leave'));
    assert.match(await text(S(form, 'submit-why')), /Chưa chọn ngày nghỉ/);
    await page.click(S(form, 'day-23-10'));
    assert.match(await text(S(form, 'submit-why')), /Chưa nhập lý do/);
    await page.fill(S(form, 'reason'), 'Bị sốt');
    assert.ok(await gone(S(form, 'submit-why')));
    await page.click(S(form, 'form-cancel'));
    assert.ok(await gone(S(form, 'form')));
    assert.ok(await visible(S(form, 'todo-count')), 'đóng form quay về Hôm nay');
    pass(`${label}: form trống khoá Gửi đơn với lý do Chưa chọn ngày nghỉ, rồi Chưa nhập lý do; đóng form về Hôm nay`);

    /* 5. Hủy đơn: hộp xác nhận có Hủy → giữ đơn; xác nhận → kết quả, trạng thái Đã hủy */
    const cancel = `${P} Hủy đơn`;
    assert.ok(await visible(S(cancel, 'confirm')));
    assert.match(await text(S(cancel, 'confirm')), /Nghỉ cả ngày thứ Hai 27\/10.*Đi khám răng/);
    await page.click(S(cancel, 'confirm-dismiss'));
    assert.ok(await gone(S(cancel, 'confirm')));
    assert.match(await text(S(cancel, 'leave-status')), /Đã gửi/);
    await page.click(S(cancel, 'cancel-leave'));
    await page.click(S(cancel, 'confirm-cancel'));
    assert.match(await text(S(cancel, 'result')), /Đã hủy đơn nghỉ cả ngày thứ Hai 27\/10/);
    assert.match(await text(S(cancel, 'leave-l1')), /Đã hủy/);
    await page.click(S(cancel, 'leave-l1'));
    assert.ok(!(await page.$(S(cancel, 'cancel-leave'))), 'đơn đã hủy không còn nút Hủy đơn');
    await page.click(S(cancel, 'back'));
    assert.ok(await visible(S(cancel, 'todo-count')));
    pass(`${label}: Hủy đơn → hộp xác nhận, bấm Hủy giữ đơn Đã gửi → Hủy đơn lần nữa → xác nhận → kết quả, đơn chuyển Đã hủy, Back về Hôm nay`);

    /* 6. Thanh tab: viên đang chọn đổi theo tab */
    const hw = `${P} Chi tiết bài tập`;
    await page.click(S(hw, 'back'));
    await page.click(S(hw, 'tab-leaves'));
    assert.equal(await page.getAttribute(S(hw, 'tab-leaves'), 'aria-current'), 'page');
    assert.equal(await page.getAttribute(S(hw, 'tab-today'), 'aria-current'), null);
    assert.ok(await visible(S(hw, 'leave-l1')));
    await page.click(S(hw, 'tab-hwlist'));
    assert.ok(await visible(S(hw, 'hw-cay-dua')) && await visible(S(hw, 'hw-bai-14')));
    pass(`${label}: Chi tiết bài tập Back về Hôm nay; tab Đơn nghỉ và Bài tập chuyển viên đang chọn và hiện đúng danh sách`);
  }
};
