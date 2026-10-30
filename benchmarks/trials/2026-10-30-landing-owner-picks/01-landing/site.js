(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

  /* ---------- Chữ trồi lên từng dòng (BCG) ---------- */
  const reveals = [...document.querySelectorAll('[data-reveal]')];
  const split = el => {
    const walk = node => [...node.childNodes].map(n => {
      if (n.nodeType === 3) return n.textContent.split(/(\s+)/).map(t => /^\s+$/.test(t) ? ' ' : t ? `<span class="w"><span>${t}</span></span>` : '').join('');
      return `<span class="w"><span>${n.outerHTML}</span></span>`;
    }).join('');
    el.innerHTML = walk(el);
    let top = null, line = -1;
    el.querySelectorAll('.w').forEach(w => { if (w.offsetTop !== top) { top = w.offsetTop; line++; } w.style.setProperty('--line', line); });
  };
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -12% 0px' });
  if (!reduce) {
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => {
      reveals.forEach(el => { split(el); requestAnimationFrame(() => requestAnimationFrame(() => io.observe(el))); });
    });
    /* Ảnh hiện từ dưới lên trong khung vòm */
    document.querySelectorAll('[data-unveil]').forEach(el => io.observe(el));
  } else {
    document.querySelectorAll('[data-unveil]').forEach(el => el.classList.add('in'));
  }

  /* ---------- Ảnh đầu trang nở ra tràn màn theo cuộn (DOD) ---------- */
  const grow = document.querySelector('[data-grow]');
  const paint = () => {
    const r = grow.getBoundingClientRect();
    const span = r.height - innerHeight;
    grow.style.setProperty('--p', clamp(-r.top / (span * 0.75)).toFixed(3));
  };
  let ticking = false;
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { ticking = false; paint(); }); } };
  if (!reduce) { addEventListener('scroll', onScroll, { passive: true }); addEventListener('resize', onScroll); paint(); }

  /* ---------- Cuộn mượt cho chuột có nấc (kiểu Lenis) ----------
   * Chỉ khi có chuột và không giảm chuyển động. Bàn phím, thanh cuộn, cảm ứng và vùng cuộn riêng
   * (sheet đặt chỗ) giữ cuộn gốc của trình duyệt. */
  if (!reduce && matchMedia('(pointer: fine)').matches) {
    let target = scrollY, cur = scrollY, raf = 0;
    const max = () => document.documentElement.scrollHeight - innerHeight;
    const loop = () => {
      cur += (target - cur) * 0.1;
      if (Math.abs(target - cur) < 0.5) { cur = target; raf = 0; } else raf = requestAnimationFrame(loop);
      scrollTo(0, cur);
    };
    const innerScroller = el => {
      for (let n = el; n && n !== document.body; n = n.parentElement) {
        if (n.scrollHeight > n.clientHeight && /(auto|scroll)/.test(getComputedStyle(n).overflowY)) return true;
      }
      return false;
    };
    addEventListener('wheel', e => {
      if (e.ctrlKey || document.querySelector('dialog[open]') || Math.abs(e.deltaX) > Math.abs(e.deltaY) || innerScroller(e.target)) return;
      e.preventDefault();
      if (!raf) target = cur = scrollY;
      const d = e.deltaMode === 1 ? e.deltaY * 40 : e.deltaMode === 2 ? e.deltaY * innerHeight : e.deltaY;
      target = clamp(target + d, 0, max());
      if (!raf) raf = requestAnimationFrame(loop);
    }, { passive: false });
    addEventListener('scroll', () => { if (!raf) target = cur = scrollY; }, { passive: true });
    const stop = () => { if (raf) { cancelAnimationFrame(raf); raf = 0; } };
    addEventListener('keydown', stop); addEventListener('pointerdown', stop);
  }

  /* ---------- Đặt chỗ ---------- */
  const CLASSES = [
    { name: 'Bàn xoay cơ bản', dur: '3 giờ', price: 450000, seats: 8 },
    { name: 'Nặn tay', dur: '2,5 giờ', price: 350000, seats: 10 },
    { name: 'Tráng men', dur: '2 giờ', price: 300000, seats: 8 }
  ];
  const SLOTS = [{ name: 'Ca sáng', time: '9:00' }, { name: 'Ca chiều', time: '14:00' }];
  const WD = ['Chủ nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy'];
  const days = [];
  for (const d = new Date(); days.length < 4;) {
    d.setDate(d.getDate() + 1);
    if (d.getDay() === 6 || d.getDay() === 0) days.push({ wd: WD[d.getDay()], dm: `${d.getDate()}/${d.getMonth() + 1}` });
  }
  const money = n => n.toLocaleString('vi-VN') + ' ₫';
  const dlg = document.getElementById('dat-cho');
  const $ = s => dlg.querySelector(s);
  const views = [...dlg.querySelectorAll('[data-view]')];
  const state = { cls: 0, day: -1, slot: -1, people: 1 };

  const radios = (group, items, render) => {
    const box = $(`[data-group="${group}"]`);
    box.innerHTML = items.map((it, i) => `<div class="opt"><input type="radio" name="${group}" id="${group}-${i}" value="${i}"><label for="${group}-${i}">${render(it)}</label></div>`).join('');
    box.addEventListener('change', e => { state[group] = +e.target.value; update(); });
  };
  radios('cls', CLASSES, c => `<b>${c.name}</b><span class="num">${c.dur}, ${money(c.price)}</span>`);
  radios('day', days, d => `<b>${d.wd}</b><span class="num">${d.dm}</span>`);
  radios('slot', SLOTS, s => `<b>${s.name}</b><span class="num">${s.time}</span>`);

  const nameIn = $('#f-name'), phoneIn = $('#f-phone');
  const go = $('[data-go-confirm]'), why = $('#why');
  const reason = () => {
    if (state.day < 0) return 'Chọn ngày học';
    if (state.slot < 0) return 'Chọn ca học';
    if (!nameIn.value.trim()) return 'Nhập họ tên';
    const digits = phoneIn.value.replace(/\D/g, '');
    if (!digits) return 'Nhập số điện thoại';
    if (digits.length !== 10) return 'Số điện thoại cần 10 chữ số';
    return '';
  };
  const rows = () => {
    const c = CLASSES[state.cls], d = days[state.day], s = SLOTS[state.slot];
    return [['Lớp', c.name], ['Ngày', `${d.wd} ${d.dm}`], ['Ca', `${s.name} ${s.time}`], ['Số người', `${state.people} người`], ['Tổng tiền', money(c.price * state.people)]];
  };
  const kv = list => list.map(([k, v]) => `<div><dt>${k}</dt><dd class="num">${v}</dd></div>`).join('');
  function update() {
    const c = CLASSES[state.cls];
    state.people = clamp(state.people, 1, c.seats);
    $('#people').value = state.people;
    $('#people').textContent = state.people;
    $('[data-step="-1"]').disabled = state.people <= 1;
    $('[data-step="1"]').disabled = state.people >= c.seats;
    $('[data-cap]').textContent = `Tối đa ${c.seats} người`;
    dlg.querySelectorAll('[data-total]').forEach(t => { t.textContent = money(c.price * state.people); });
    const r = reason();
    why.textContent = r;
    go.setAttribute('aria-disabled', r ? 'true' : 'false');
  }
  const show = name => {
    views.forEach(v => { v.hidden = v.dataset.view !== name; });
    dlg.scrollTop = 0;
    const first = dlg.querySelector(`[data-view="${name}"] h2`);
    if (first) { first.tabIndex = -1; first.focus({ preventScroll: true }); }
  };

  $('form').addEventListener('submit', e => e.preventDefault());
  dlg.addEventListener('input', e => { if (e.target === nameIn || e.target === phoneIn) update(); });
  dlg.querySelectorAll('[data-step]').forEach(b => b.addEventListener('click', () => { state.people += +b.dataset.step; update(); }));
  go.addEventListener('click', () => {
    if (go.getAttribute('aria-disabled') === 'true') { why.animate?.([{ opacity: .3 }, { opacity: 1 }], 240); return; }
    $('[data-summary="confirm"]').innerHTML = kv(rows().slice(0, 4).concat([['Họ tên', nameIn.value.trim()], ['Số điện thoại', phoneIn.value.trim()]]));
    show('confirm');
  });
  dlg.querySelectorAll('[data-back]').forEach(b => b.addEventListener('click', () => show('form')));
  $('[data-confirm-action]').addEventListener('click', () => {
    const now = new Date();
    const hm = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
    $('[data-summary="result"]').innerHTML = kv(rows().concat([['Đặt lúc', `${hm} ${now.getDate()}/${now.getMonth() + 1}`]]));
    const name = nameIn.value.trim();
    $('[data-person-name]').textContent = name;
    $('[data-person-phone]').textContent = phoneIn.value.trim();
    $('[data-initials]').textContent = name.split(/\s+/).slice(-2).map(w => w[0]).join('').toUpperCase();
    const c = CLASSES[state.cls], d = days[state.day], s = SLOTS[state.slot];
    document.querySelectorAll('[data-booked]').forEach(p => { p.textContent = `Đã đặt chỗ: ${c.name}, ${d.wd} ${d.dm}, ${s.time}`; });
    show('result');
  });

  const open = cls => {
    state.cls = cls; state.day = -1; state.slot = -1; state.people = 1;
    dlg.querySelectorAll('input[type=radio]').forEach(r => { r.checked = (r.name === 'cls' && +r.value === cls); });
    show('form');
    update();
    dlg.showModal();
  };
  document.querySelectorAll('[data-open-booking]').forEach(b => b.addEventListener('click', () => open(+(b.dataset.class || 0))));
  dlg.querySelectorAll('[data-close]').forEach(b => b.addEventListener('click', () => dlg.close()));
  dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
  update();
})();
