const repositories = [
  { name: 'uiux-ai-workspace', category: 'ai', discipline: 'AI design orchestration, rendered QA and evidence contracts', url: 'https://github.com/Ngh1aa/uiux-ai-workspace' },
  { name: 'skills_UIUX', category: 'ai', discipline: 'Routed UI/UX knowledge, research and verification skills', url: 'https://github.com/Ngh1aa/skills_UIUX' },
  { name: 'uiux-factory', category: 'ai', discipline: 'Earlier factory implementation and orchestration experiments', url: 'https://github.com/Ngh1aa/uiux-factory' },
  { name: 'bolt.diy', category: 'tooling', discipline: 'AI development tooling repository', url: 'https://github.com/Ngh1aa/bolt.diy' },
  { name: 'StudioOS', category: 'product', discipline: 'Creative-team workspace and project operating surface', url: 'https://github.com/Ngh1aa/StudioOS' },
  { name: 'FlowCRM', category: 'product', discipline: 'CRM dashboard, pipeline, customers, tasks and messaging', url: 'https://github.com/Ngh1aa/FlowCRM' },
  { name: 'HireFlow', category: 'product', discipline: 'Recruitment and candidate management workflow', url: 'https://github.com/Ngh1aa/HireFlow' },
  { name: 'QTSC', category: 'product', discipline: 'Product / interface study', url: 'https://github.com/Ngh1aa/QTSC' },
  { name: 'ui-feedback-tool', category: 'tooling', discipline: 'Interface feedback and review utility', url: 'https://github.com/Ngh1aa/ui-feedback-tool' },
  { name: 'Atelier', category: 'commerce', discipline: 'Editorial luxury-fashion commerce prototype', url: 'https://github.com/Ngh1aa/Atelier' },
  { name: 'LuxRoom', category: 'commerce', discipline: 'Luxury-minimal furniture commerce experience', url: 'https://github.com/Ngh1aa/LuxRoom' },
  { name: 'VioletMarketplace', category: 'commerce', discipline: 'Curated niche-fragrance marketplace prototype', url: 'https://github.com/Ngh1aa/VioletMarketplace' },
  { name: 'Capital', category: 'redesign', discipline: 'Building and leasing decision-support redesign', url: 'https://github.com/Ngh1aa/Capital' },
  { name: 'CapitalTowerRedesign', category: 'redesign', discipline: 'Capital Tower redesign study', url: 'https://github.com/Ngh1aa/CapitalTowerRedesign' },
  { name: 'RedesignVAS', category: 'redesign', discipline: 'VAS web experience redesign study', url: 'https://github.com/Ngh1aa/RedesignVAS' },
  { name: 'VasEducation', category: 'redesign', discipline: 'Education experience repository', url: 'https://github.com/Ngh1aa/VasEducation' },
  { name: 'Redesign-Vietbank-Website', category: 'redesign', discipline: 'Banking website redesign study', url: 'https://github.com/Ngh1aa/Redesign-Vietbank-Website' },
  { name: 'Veil', category: 'product', discipline: 'Interface / visual product experiment', url: 'https://github.com/Ngh1aa/Veil' }
];

const labels = {
  ai: 'AI / SYSTEMS',
  product: 'PRODUCT',
  commerce: 'COMMERCE',
  redesign: 'REDESIGN',
  tooling: 'TOOLING'
};

const list = document.querySelector('#repo-list');
const count = document.querySelector('#visible-count');
const searchInput = document.querySelector('#repo-search');
const filterButtons = [...document.querySelectorAll('.filter-button')];
const emptyState = document.querySelector('#empty-state');
const resetButton = document.querySelector('#reset-filter');

let activeFilter = 'all';
let searchTerm = '';

function normalize(value) {
  return value.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function matches(repo) {
  const filterMatch = activeFilter === 'all' || repo.category === activeFilter;
  const haystack = normalize(`${repo.name} ${repo.discipline} ${labels[repo.category]}`);
  return filterMatch && haystack.includes(normalize(searchTerm));
}

function render() {
  const visible = repositories.filter(matches);
  count.textContent = String(visible.length).padStart(2, '0');
  list.replaceChildren();

  visible.forEach((repo) => {
    const sourceIndex = repositories.indexOf(repo) + 1;
    const row = document.createElement('a');
    row.className = 'repo-row';
    row.href = repo.url;
    row.target = '_blank';
    row.rel = 'noreferrer';
    row.setAttribute('role', 'listitem');
    row.innerHTML = `
      <span class="repo-index">${String(sourceIndex).padStart(2, '0')}</span>
      <span class="repo-name">${repo.name}</span>
      <span class="repo-discipline">${repo.discipline}</span>
      <span class="repo-category">${labels[repo.category]}</span>
      <span class="repo-arrow" aria-hidden="true">↗</span>
    `;
    list.append(row);
  });

  emptyState.hidden = visible.length !== 0;
}

filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    activeFilter = button.dataset.filter;
    filterButtons.forEach((candidate) => {
      const selected = candidate === button;
      candidate.classList.toggle('is-active', selected);
      candidate.setAttribute('aria-pressed', String(selected));
    });
    render();
  });
});

searchInput.addEventListener('input', (event) => {
  searchTerm = event.currentTarget.value.trim();
  render();
});

resetButton.addEventListener('click', () => {
  activeFilter = 'all';
  searchTerm = '';
  searchInput.value = '';
  filterButtons.forEach((button) => {
    const selected = button.dataset.filter === 'all';
    button.classList.toggle('is-active', selected);
    button.setAttribute('aria-pressed', String(selected));
  });
  searchInput.focus();
  render();
});

render();
