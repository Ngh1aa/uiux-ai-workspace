(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

  /* ---------- R1: chữ trồi lên từng dòng ---------- */
  const reveals = [...document.querySelectorAll('[data-reveal]')];
  const split = el => {
    const words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map(w => `<span class="w"><span>${w}</span></span>`).join(' ');
    const ws = [...el.querySelectorAll('.w')];
    let top = null, line = -1;
    ws.forEach(w => { if (w.offsetTop !== top) { top = w.offsetTop; line++; } w.style.setProperty('--line', line); });
  };
  if (!reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -15% 0px' });
    const start = () => reveals.forEach(el => { split(el); requestAnimationFrame(() => requestAnimationFrame(() => io.observe(el))); });
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(start);
  }

  /* ---------- Chữ ký: men lam chảy xuống thân cốc, bàn xoay quay theo cuộn ---------- */
  const cup = document.getElementById('cup');
  const glaze = document.getElementById('glaze');
  const spins = [...document.querySelectorAll('#cup .spin')];
  const hero = document.querySelector('.hero');
  const flood = document.querySelector('[data-flood]');
  let intro = reduce ? 1 : 0;
  const paint = () => {
    const vh = innerHeight;
    const y = scrollY;
    // men: 0 = đất mộc, 1 = men phủ hai phần ba thân cốc
    const g = reduce ? 1 : clamp(intro * 0.3 + y / (hero.offsetHeight * 0.7));
    cup.style.setProperty('--g', g.toFixed(3));
    glaze.setAttribute('transform', `translate(0 ${(40 + g * 260).toFixed(1)})`);
    spins.forEach((s, i) => s.setAttribute('stroke-dashoffset', reduce ? 0 : (-(y * (i ? 0.9 : 0.6)) - intro * 120).toFixed(1)));
    // men phủ section "Một buổi học": bắt đầu khi mép trên qua 85% màn
    if (!reduce) {
      const r = flood.getBoundingClientRect();
      flood.style.setProperty('--p', clamp((vh * 0.85 - r.top) / (vh * 0.8)).toFixed(3));
    }
  };
  let ticking = false;
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { ticking = false; paint(); }); } };
  if (!reduce) {
    // rót men lần đầu: 1,2 s, đường cong mềm
    const t0 = performance.now();
    const ease = t => 1 - Math.pow(1 - t, 3);
    const step = now => { intro = ease(clamp((now - t0) / 1200)); paint(); if (intro < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
  }
  paint();

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
