'use strict';
(async function () {
  const data = await fetch('study.json').then(response => {
    if (!response.ok) throw new Error('Study data unavailable');
    return response.json();
  });
  const params = new URLSearchParams(location.search);
  const owns = (object, key) => Object.prototype.hasOwnProperty.call(object, key);
  const caseKey = owns(data.cases, params.get('case')) ? params.get('case') : 'enterprise';
  const candidate = owns(data.directions, params.get('direction')) ? params.get('direction') : 'register';
  const brief = data.cases[caseKey];
  const direction = data.directions[candidate];
  const escape = value => String(value).replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
  const css = document.documentElement.style;
  for (const [viewport, prefix] of [['desktop',''],['mobile','mobile-']]) {
    const type = direction[viewport + '_typography'];
    const density = direction[viewport + '_density'];
    css.setProperty('--' + prefix + 'title', type.title.size_px + 'px');
    css.setProperty('--' + prefix + 'title-line', type.title.line_height);
    css.setProperty('--' + prefix + 'body', type.body.size_px + 'px');
    css.setProperty('--' + prefix + 'section', density.section_gap_px + 'px');
    css.setProperty('--' + prefix + 'group', density.group_gap_px + 'px');
    css.setProperty('--' + prefix + 'padding', density.object_padding_px + 'px');
    if (!prefix) {
      css.setProperty('--family', type.family);
      css.setProperty('--weight', type.title.weight);
      css.setProperty('--tracking', type.title_tracking_em + 'em');
      css.setProperty('--measure', type.reading_width_ch + 'ch');
    }
  }
  document.title = brief.title + ' · Direction study';
  document.body.className = candidate;
  const object = candidate === 'register'
    ? `<table class="matrix" aria-label="${escape(brief.object_title)}"><tbody>${brief.records.map(record => `<tr><th scope="row">${escape(record.title)}</th>${record.facts.map(([label,value]) => `<td><dl><dt>${escape(label)}</dt><dd>${escape(value)}</dd></dl></td>`).join('')}</tr>`).join('')}</tbody></table>`
    : `<div class="records">${brief.records.map(record => `<article class="record"><h3>${escape(record.title)}</h3><dl>${record.facts.map(([label,value]) => `<dt>${escape(label)}</dt><dd>${escape(value)}</dd>`).join('')}</dl></article>`).join('')}</div>`;
  document.querySelector('main').innerHTML = `<div class="intro"><p class="eyebrow">${escape(brief.category)}</p><h1>${escape(brief.title)}</h1><p class="lead">${escape(brief.lead)}</p><a class="action" href="#scope">${escape(brief.cta)}</a></div><section id="scope" class="object" aria-labelledby="object-title"><h2 id="object-title">${escape(brief.object_title)}</h2>${object}<p class="boundary">${escape(brief.boundary)}</p></section>`;
  window.studyReady = {caseKey,candidate};
}()).catch(() => {
  document.querySelector('main').textContent = 'The local study could not load. Check the local server and reload.';
});
