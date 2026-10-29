window.icon = name => `<svg class="icon" aria-hidden="true"><use href="../../../../design-system/components/icons.svg#ds-i-${name}"/></svg>`;
window.escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
window.money = value => new Intl.NumberFormat('vi-VN').format(value) + ' ₫';
document.querySelectorAll('[data-icon]').forEach(el => el.innerHTML = icon(el.dataset.icon));
document.querySelectorAll('[data-theme-toggle]').forEach(button => button.addEventListener('click', () => {const dark = document.documentElement.dataset.theme === 'dark' || (!document.documentElement.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);document.documentElement.dataset.theme = dark ? 'light' : 'dark';button.setAttribute('aria-pressed', String(!dark));}));
window.focusHeading = root => {const heading=root.querySelector('h1,h2');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}};
