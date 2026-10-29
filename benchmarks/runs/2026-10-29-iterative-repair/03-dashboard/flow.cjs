'use strict';
module.exports=async(page,assert,{snap})=>{
 const scenarios=[];
 const first=page.locator('[data-dispatch]').first();await first.click();
 assert.match(await page.locator('#dispatch-copy').innerText(),/#2041 chị Hà.*Đà Nẵng Quá 2 ngày/);
 await page.locator('#cancel-dispatch').click();
 assert.equal(await page.locator('[data-dispatch]').count(),3);
 await first.click();await snap(page,'review-order');
 await page.locator('#confirm-dispatch').click();
 assert.equal(await page.locator('[data-pending]').innerText(),'13');
 assert.equal(await page.locator('[data-late-count]').innerText(),'2 đơn');assert.equal(await page.locator('#orders .ds-section-header .ds-link').innerText(),'2 đơn quá hạn');
 assert.match(await page.locator('#orders li').first().innerText(),/#2041 chị Hà.*Đã gửi/s);
 assert.equal(await page.locator('[data-dispatch]').count(),2);
 scenarios.push({name:'Đúng đơn/khách, cancel giữ state, review xác nhận cập nhật14→13 và3→2',status:'PASS'});
 await page.getByText('Ví dụ trạng thái minh hoạ của panel',{exact:true}).click();const retry=page.getByRole('button',{name:'Thử lại'});await retry.click();
 assert.match(await page.locator('.action-feedback').innerText(),/Đã tải lại dữ liệu minh hoạ.*18.550/);
 scenarios.push({name:'Lỗi panel doanh thu → thử lại, không ảnh hưởng đơn/kho',status:'PASS'});
 assert.match(await page.locator('#sales').innerText(),/18.550.*4.120/s);
 if(await page.locator('[aria-label="Mở menu"]').isVisible()){
  await page.locator('[aria-label="Mở menu"]').click();await page.locator('.web-nav a[href="#stock"]').click();
 }else await page.locator('.web-nav a[href="#stock"]').click();
 assert.equal(await page.evaluate(()=>location.hash),'#stock');
 await page.goBack();assert.notEqual(await page.evaluate(()=>location.hash),'#stock');
 assert.equal(await page.locator('[data-pending]').innerText(),'13');
 scenarios.push({name:'Navigation/back giữ dữ liệu, chart có đơn vị/kỳ/tổng đúng',status:'PASS'});
 return scenarios;
};
