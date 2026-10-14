/* Synthetic client-review example. All screens share this renderer and state. */
(() => {
  'use strict';
  const services = {
    consultation: { name: 'Tư vấn thiết kế', detail: '30 phút · Trực tuyến', icon: '↗' },
    portfolio: { name: 'Review portfolio', detail: '45 phút · Trực tuyến', icon: '▤' }
  };
  const slots = ['09:00', '10:30', '13:00', '14:30', '16:00', '17:30'];
  const storageKey = 'uiux-mobile-appointment-demo.v1';
  const app = document.querySelector('#app');
  let bookings = [];
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (Array.isArray(saved)) bookings = saved.filter(item => item && Object.hasOwn(services, item.service)
      && slots.includes(item.slot) && typeof item.id === 'string' && /^[a-z0-9-]+$/.test(item.id));
  } catch { /* Invalid/unavailable local demo storage starts with an empty state. */ }

  function current() {
    const query = new URLSearchParams(location.search);
    return {
      screen: ['home', 'bookings', 'confirm'].includes(query.get('screen')) ? query.get('screen') : 'home',
      state: ['ready', 'offline', 'empty'].includes(query.get('state')) ? query.get('state') : 'ready',
      service: Object.hasOwn(services, query.get('service')) ? query.get('service') : 'consultation',
      slot: slots.includes(query.get('slot')) ? query.get('slot') : slots[0]
    };
  }
  function navigate(update, replace = false, focusSelector = 'h1') {
    const state = { ...current(), ...update };
    const url = new URL(location.href);
    for (const [key, value] of Object.entries(state)) url.searchParams.set(key, value);
    history[replace ? 'replaceState' : 'pushState']({}, '', url);
    render(focusSelector);
  }
  function persist() {
    try { localStorage.setItem(storageKey, JSON.stringify(bookings)); }
    catch { document.querySelector('#announcement').textContent = 'Lịch demo chỉ được giữ trong phiên này.'; }
  }
  function render(focusSelector = 'h1') {
    const { screen, state, service, slot } = current();
    const selected = services[service];
    const header = '<div class="eyebrow"><span>STUDIO / LỊCH HẸN</span><span class="badge">DEMO</span></div>';
    const offline = state === 'offline'
      ? '<div class="banner" role="status">Bạn đang mất kết nối. Lựa chọn vẫn được giữ.<button type="button" data-action="recover">Thử kết nối lại</button></div>' : '';
    if (screen === 'home') {
      app.innerHTML = `${header}<h1 tabindex="-1">Dành thời gian<br>cho ý tưởng của bạn.</h1>
        <p class="intro">Chọn một buổi trao đổi cùng studio.<br>Lịch hẹn rõ ràng, bắt đầu dễ dàng.</p>${offline}
        <h2>Chọn buổi hẹn</h2>${Object.entries(services).map(([id, item]) =>
          `<button class="service" data-service="${id}" aria-pressed="${id === service}"><span class="service-icon" aria-hidden="true">${item.icon}</span><span><strong>${item.name}</strong><small>${item.detail}</small></span></button>`).join('')}
        <h2>Thời gian phù hợp</h2><div class="date-card"><span class="date-number">16</span><div><strong>Tháng 10, 2026</strong><p>Ngày mẫu của bản demo</p></div></div>
        <div class="slots" aria-label="Chọn giờ">${slots.map(time => `<button class="slot" data-slot="${time}" aria-pressed="${time === slot}">${time}</button>`).join('')}</div>
        <button class="primary" data-action="continue" ${state === 'offline' ? 'disabled' : ''}>Tiếp tục · ${slot}</button>`;
    } else if (screen === 'confirm') {
      app.innerHTML = `${header}<button class="back" data-screen="home">← Quay lại</button>
        <h1 tabindex="-1">Xác nhận<br>buổi hẹn.</h1><p class="intro">Kiểm tra lựa chọn trước khi lưu vào lịch demo.</p>${offline}
        <div class="summary"><dl><dt>Buổi hẹn</dt><dd>${selected.name}</dd><dt>Thời gian</dt><dd>${slot} · 16 tháng 10, 2026</dd><dt>Hình thức</dt><dd>${selected.detail}</dd></dl></div>
        <button class="primary" data-action="book" ${state === 'offline' ? 'disabled' : ''}>Xác nhận lịch demo</button>
        <p class="intro">Không gửi yêu cầu đặt lịch thật.</p>`;
    } else {
      const visible = state === 'empty' ? [] : bookings;
      app.innerHTML = `${header}<h1 tabindex="-1">Lịch của tôi.</h1><p class="intro">Những buổi hẹn bạn đã lưu trong bản demo.</p>${offline}
        ${visible.length ? visible.map(item => `<article class="booking"><strong>${services[item.service].name}</strong><small>${item.slot} · 16 tháng 10, 2026</small><small>Đã lưu trong demo · Trực tuyến</small><button data-cancel="${item.id}">Hủy lịch demo</button></article>`).join('')
          : '<div class="empty" data-empty="true"><span class="empty-mark" aria-hidden="true">▤</span><h2>Chưa có lịch hẹn</h2><p>Khi bạn chọn một buổi hẹn,<br>lịch demo sẽ xuất hiện tại đây.</p><button class="primary" data-screen="home">Chọn buổi hẹn</button></div>'}`;
    }
    app.dataset.screen = screen;
    app.dataset.state = state;
    document.querySelector('#scenario').value = state;
    document.querySelector('#booking-count').textContent = bookings.length ? `(${bookings.length})` : '';
    document.querySelectorAll('.tab-bar [data-screen]').forEach(button => {
      if (button.dataset.screen === screen) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    app.querySelector(focusSelector)?.focus({ preventScroll: true });
  }
  document.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button || button.disabled) return;
    if (button.id === 'reset-demo') {
      bookings = []; persist(); navigate({ screen: 'home', state: 'ready', service: 'consultation', slot: slots[0] });
      document.querySelector('#announcement').textContent = 'Đã đặt lại bản demo.';
    } else if (button.dataset.screen) navigate({ screen: button.dataset.screen, state: 'ready' });
    else if (button.dataset.service) navigate({ service: button.dataset.service }, false, `[data-service="${button.dataset.service}"]`);
    else if (button.dataset.slot) navigate({ slot: button.dataset.slot }, false, `[data-slot="${button.dataset.slot}"]`);
    else if (button.dataset.cancel) {
      bookings = bookings.filter(item => item.id !== button.dataset.cancel); persist(); render();
      document.querySelector('#announcement').textContent = 'Đã hủy lịch demo.';
    } else if (button.dataset.action === 'recover') navigate({ state: 'ready' });
    else if (button.dataset.action === 'continue') navigate({ screen: 'confirm' });
    else if (button.dataset.action === 'book' && current().state !== 'offline') {
      const { service, slot } = current();
      const id = `${service}-${slot.replace(':', '-')}`;
      if (!bookings.some(item => item.id === id)) bookings.push({ id, service, slot });
      persist(); navigate({ screen: 'bookings', state: 'ready' });
      document.querySelector('#announcement').textContent = 'Đã lưu lịch demo.';
    }
  });
  document.querySelector('#scenario').addEventListener('change', event => navigate({
    state: event.target.value, ...(event.target.value === 'empty' ? { screen: 'bookings' } : {})
  }));
  window.addEventListener('popstate', () => render());
  render();
})();
