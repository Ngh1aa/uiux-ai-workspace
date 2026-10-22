'use strict';
(async function () {
  const response = await fetch('cases.json');
  if (!response.ok) throw new Error('Không tải được dữ liệu ví dụ.');
  const data = await response.json();
  const params = new URLSearchParams(location.search);
  const own = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
  const caseKey = own(data.cases, params.get('case')) ? params.get('case') : 'healthcare';
  const variant = params.get('variant') === 'fragile' ? 'fragile' : 'considered';
  const brief = data.cases[caseKey];
  const esc = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const link = (key, value) => {
    const next = new URLSearchParams(params);
    next.set('case', caseKey); next.set('variant', variant); next.set(key, value);
    return '?' + next;
  };
  document.querySelector('#cases').innerHTML = Object.entries(data.cases).map(([key,item]) =>
    `<a href="${esc(link('case',key))}" ${key===caseKey?'aria-current="page"':''}>${esc(item.title)}</a>`).join('');
  document.querySelector('#variants').innerHTML = [['fragile','Cần sửa'],['considered','Có chủ đích']].map(([key,label]) =>
    `<a href="${esc(link('variant',key))}" ${key===variant?'aria-current="page"':''}>${label}</a>`).join('');
  const preview = document.querySelector('#preview');
  let value = brief.input_value;
  let reviewing = false;
  let recovered = false;
  let query = '';
  let selected = brief.options ? brief.options[0] : null;

  function factMarkup() {
    return brief.facts.map(([label,fact], index) =>
      `<div class="fact"><dt>${esc(label)}</dt><dd>${esc(index===1 && selected ? selected.label : fact)}</dd></div>`).join('');
  }
  function formMarkup() {
    return `<form novalidate>
      <label for="detail">${esc(brief.input_label)}</label>
      <input id="detail" name="detail" type="text" value="${esc(value)}" aria-describedby="feedback" maxlength="300">
      <div class="actions"><button type="submit">${esc(brief.next)}</button><button type="button" class="secondary" id="reset">Khôi phục ghi chú mẫu</button></div>
      <p id="feedback" class="feedback" role="status">${recovered?'Đã giữ thay đổi để bạn chỉnh sửa.':''}</p>
    </form>`;
  }
  function reviewMarkup() {
    return `<section class="review" aria-labelledby="review-title">
      <h3 id="review-title" tabindex="-1">Xem lại thông tin</h3>
      <p><strong>${esc(brief.input_label)}:</strong> ${esc(value)}</p>
      <div class="actions"><button type="button" id="back">Quay lại chỉnh sửa</button></div>
      <p class="feedback" role="status">Đang xem lại trong phiên. Chưa gửi yêu cầu.</p>
    </section>`;
  }
  function renderOptions() {
    const visible = brief.options.filter(item => item.label.toLocaleLowerCase('vi').includes(query.toLocaleLowerCase('vi')));
    document.querySelector('#options').innerHTML = visible.length
      ? visible.map(item => `<button type="button" class="option" data-option="${esc(item.id)}" aria-pressed="${selected.id===item.id}">${esc(item.label)}</button>`).join('')
      : '<p role="status">Chưa có lựa chọn phù hợp.</p><button type="button" class="secondary" id="clear-filter">Xóa bộ lọc</button>';
    document.querySelectorAll('[data-option]').forEach(button => button.addEventListener('click', () => {
      selected = brief.options.find(item => item.id===button.dataset.option);
      render(); document.querySelector(`[data-option="${selected.id}"]`).focus();
    }));
    const reset = document.querySelector('#clear-filter');
    if (reset) reset.addEventListener('click', () => {
      query = ''; document.querySelector('#catalog-filter').value = ''; renderOptions(); document.querySelector('#catalog-filter').focus();
    });
  }
  function render() {
    preview.className = variant;
    preview.innerHTML = `<h2>${esc(brief.title)}</h2><p class="task">${esc(brief.task)}</p>
      <div class="status" data-part="status"><strong>${esc(brief.status)}</strong><p>${esc(brief.owner)}</p></div>
      ${brief.options && !reviewing ? `<section class="catalog" aria-label="Chọn biến thể"><h3>So sánh biến thể</h3><label for="catalog-filter">Lọc màu hoặc kích thước</label><input id="catalog-filter" type="search" value="${esc(query)}"><div class="options" id="options"></div></section>` : ''}
      <section class="object" data-part="facts" aria-labelledby="object-title"><h3 id="object-title">${esc(brief.object)}</h3><dl class="facts">${factMarkup()}</dl></section>
      ${reviewing ? reviewMarkup() : formMarkup()}
      ${brief.help ? `<details><summary>${esc(brief.help.title)}</summary><p>${esc(brief.help.details)}</p></details>` : ''}`;
    if (reviewing) {
      document.querySelector('#back').addEventListener('click', () => {
        // Deliberate, labelled defect in the teaching variant; not production logic.
        if (variant === 'fragile') value = brief.input_value;
        reviewing = false; recovered = variant === 'considered'; render(); document.querySelector('#detail').focus();
      });
      document.querySelector('#review-title').focus();
      return;
    }
    if (brief.options) {
      renderOptions();
      document.querySelector('#catalog-filter').addEventListener('input', event => { query = event.target.value; renderOptions(); });
    }
    const input = document.querySelector('#detail');
    input.addEventListener('input', () => {
      value = input.value; input.removeAttribute('aria-invalid');
      document.querySelector('#feedback').textContent = '';
    });
    document.querySelector('form').addEventListener('submit', event => {
      event.preventDefault();
      if (!value.trim()) {
        const feedback = document.querySelector('#feedback');
        feedback.classList.add('error'); feedback.textContent = 'Nhập ghi chú trước khi xem lại.';
        input.setAttribute('aria-invalid','true'); input.focus(); return;
      }
      reviewing = true; render();
    });
    document.querySelector('#reset').addEventListener('click', () => {
      value = brief.input_value; recovered = false; render(); document.querySelector('#detail').focus();
    });
  }
  render();
  const targets = {status:'Trạng thái',facts:'Thông tin',recovery:'Phục hồi'};
  document.querySelector('#notes').innerHTML = `<h2>Đọc quyết định</h2><small>Phân tích do tác giả soạn · chưa phải user finding</small>
    ${brief.annotations.map(note=>`<article><h3>${esc(targets[note.target] || note.target)}</h3><p>${esc(note.observation)}</p><p><strong>Thay đổi:</strong> ${esc(note.change)}</p><p><strong>Đánh đổi:</strong> ${esc(note.trade_off)}</p></article>`).join('')}
    <article><h3>Kiểm tra lại</h3><p>${esc(brief.retest)}</p></article><article><h3>Không chuyển nguyên sang sản phẩm</h3><p>${esc(brief.do_not_transfer)}</p></article>`;
  document.querySelector('#show-notes').addEventListener('change', event => { document.querySelector('#notes').hidden = !event.target.checked; });
  document.querySelector('#cases [aria-current]').scrollIntoView({block:'nearest',inline:'nearest'});
  window.decisionLabReady = {caseKey,variant,evidenceClass:data.evidence_class};
}()).catch(error => { document.querySelector('#preview').textContent = error.message; });
