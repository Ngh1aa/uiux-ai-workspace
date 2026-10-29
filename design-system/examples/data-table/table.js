'use strict';
// One fixture owner; summary/detail/filter/sort use these same objects.
const orders = [
  { id: 'SO-101', customer: 'Nguyễn Thị Hường', date: '30/10/2026', status: 'pending', label: 'Chờ xác nhận', tone: 'warning', total: 960000 },
  { id: 'SO-102', customer: 'Trần Minh Anh', date: '29/10/2026', status: 'packing', label: 'Đang đóng gói', tone: 'info', total: 1200000 },
  { id: 'SO-103', customer: 'Lê Quỳnh Như', date: '28/10/2026', status: 'done', label: 'Đã giao', tone: 'success', total: 600000 },
];
const money = value => new Intl.NumberFormat('vi-VN').format(value);
const query = document.querySelector('#search');
const statusFilter = document.querySelector('#status');
const dialog = document.querySelector('#detail');
let descending = null;
function render() {
  document.querySelector('#total-count').textContent = String(orders.length);
  document.querySelector('#pending-count').textContent = String(orders.filter(order=>order.status!=='done').length);
  document.querySelector('#total-value').textContent = money(orders.reduce((sum,order)=>sum+order.total,0));
  const filtered = orders.filter(order => (statusFilter.value === 'all' || order.status === statusFilter.value)
    && `${order.id} ${order.customer}`.toLocaleLowerCase('vi').includes(query.value.trim().toLocaleLowerCase('vi')));
  if (descending !== null) filtered.sort((a, b) => descending ? b.total - a.total : a.total - b.total);
  document.querySelector('#rows').innerHTML = filtered.map(order => `<tr><th scope="row">${order.id}<small>${order.customer}</small></th><td>${order.date}</td><td><span class="ds-badge ds-badge--${order.tone}">${order.label}</span></td><td class="ds-table__num">${money(order.total)}</td><td><button type="button" data-order="${order.id}" aria-label="Mở đơn ${order.id}">Mở đơn</button></td></tr>`).join('');
  document.querySelector('#count').textContent = `${filtered.length} / ${orders.length} đơn hàng`;
  document.querySelector('#empty').hidden = filtered.length > 0;
}
document.querySelector('#filters').addEventListener('submit', event => event.preventDefault());
query.addEventListener('input', render);
statusFilter.addEventListener('change', render);
document.querySelector('#filters').addEventListener('reset', () => { query.value = ''; statusFilter.value = 'all'; render(); });
document.querySelector('#clear').addEventListener('click', () => { document.querySelector('#filters').reset(); query.focus(); });
document.querySelector('#sort').addEventListener('click', event => {
  descending = descending !== true;
  event.currentTarget.closest('th').setAttribute('aria-sort', descending ? 'descending' : 'ascending');
  render();
});
document.querySelector('#rows').addEventListener('click', event => {
  const button = event.target.closest('[data-order]');
  if (!button) return;
  const order = orders.find(item => item.id === button.dataset.order);
  document.querySelector('#detail-title').textContent = order.id;
  document.querySelector('#facts').innerHTML = [['Khách hàng', order.customer], ['Ngày giao', order.date], ['Trạng thái', order.label], ['Giá trị', `${money(order.total)} ₫`]].map(([label, value]) => `<div><dt>${label}</dt><dd>${value}</dd></div>`).join('');
  dialog.showModal();
});
document.querySelector('#close').addEventListener('click', () => dialog.close());
document.querySelector('#theme').addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme === 'dark' || (!document.documentElement.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'light' : 'dark';
});
render();
