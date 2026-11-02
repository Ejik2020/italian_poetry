/* Quarto renders all content. This file only controls presentation. */
(() => {
  'use strict';
  const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
  const body = document.body, reading = $('.reading');
  // Quarto's book template puts include-before-body inside <main>. Move the
  // global chrome out so it spans the viewport and stays sticky independently.
  body.prepend($('.edition-masthead'), $('.readingbar'), $('.mobile-shade'));
  body.append($('.font-control'));
  const book = /\/book\.html$/.test(location.pathname);
  body.classList.add(reading ? 'poet-page' : book ? 'book-page' : 'home-page');
  $(`.edition-masthead [data-section="${reading ? 'poets' : book ? 'book' : 'home'}"]`)?.setAttribute('aria-current', 'page');
  if (!reading) return;
  const storage = {
    get(k) {try {return localStorage.getItem(k);} catch {return null;}},
    set(k,v) {try {localStorage.setItem(k,v);} catch { /* Preferences are optional. */ }}
  };
  let mode = storage.get('edition-mode');
  if (!['parallel','translation','stacked'].includes(mode)) mode = 'parallel';
  const saved = Number(storage.get('edition-size') || 17);
  let size = Number.isFinite(saved) ? Math.max(16,Math.min(30,Math.round(saved))) : 17;
  let side = storage.get('edition-side') !== 'closed';
  const mobile = matchMedia('(max-width:760px)'), sidebar = $('#quarto-sidebar');
  const opener = $('.sidebar-switch'), shade = $('.mobile-shade');
  $('.readingbar').hidden = false;
  const head = $('.chapter-head'), block = $('#title-block-header');
  if (block) head.prepend(block);
  // These are display-name metadata, not replacements for biography text.
  const names = {'Монтале':'Eugenio Montale','Говони':'Corrado Govoni','Нове':'Aldo Nove','Пьерсанти':'Umberto Piersanti',"Д'Агостини":'Alessandro D’Agostini'};
  const match = $('.bio').textContent.match(/\(([A-Za-zÀ-ž][A-Za-zÀ-ž’' .-]+)\)/);
  const key = decodeURIComponent(location.pathname.split('/').pop()).replace(/\.html$/,'');
  if (match || names[key]) {
    const latin = document.createElement('p'); latin.className = 'latin'; latin.lang = 'it';
    latin.textContent = match ? match[1] : names[key]; head.insertBefore(latin,$('.bio'));
  }
  if (sidebar) {
    $$('#quarto-sidebar a.sidebar-item-text').forEach(a => {
      if (['index.html','book.html'].includes(decodeURIComponent(new URL(a.href).pathname.split('/').pop()))) a.closest('li')?.remove();
    });
    const heading = document.createElement('button'); heading.type = 'button';
    heading.className = 'sidebar-heading'; heading.textContent = '☰ Поэты';
    heading.setAttribute('aria-label','Свернуть список поэтов'); heading.setAttribute('aria-expanded','true');
    heading.setAttribute('aria-controls','quarto-sidebar'); sidebar.prepend(heading);
    heading.addEventListener('click',() => {
      if (mobile.matches) {closeDrawer();opener.focus();}
      else {side = false;storage.set('edition-side','closed');applySide();opener.focus();}
    });
  }
  function reflow() {reading.dataset.reflow = String(mode === 'parallel' && reading.clientWidth < size*39);}
  function setMode(value,persist=true) {
    mode=value;reading.dataset.mode=mode;
    $$('.reading-modes button').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
    if(persist) storage.set('edition-mode',mode);reflow();
  }
  function setFont(value,persist=true) {
    size=Math.max(16,Math.min(30,value));document.documentElement.style.setProperty('--font-size',size+'px');
    $('.font-control output').textContent=size;$('.font-down').disabled=size===16;$('.font-up').disabled=size===30;
    if(persist) storage.set('edition-size',String(size));reflow();
  }
  function closeDrawer() {
    body.classList.remove('sidebar-mobile-open');shade.hidden=true;
    opener.setAttribute('aria-expanded',String(!mobile.matches && side));
  }
  function applySide() {body.classList.toggle('sidebar-closed',!mobile.matches && !side);closeDrawer();reflow();}
  opener.addEventListener('click',() => {
    if(mobile.matches) {
      const open=body.classList.toggle('sidebar-mobile-open');shade.hidden=!open;opener.setAttribute('aria-expanded',String(open));
      if(open) $('.sidebar-heading')?.focus();
    } else {side=!side;storage.set('edition-side',side?'open':'closed');applySide();}
  });
  $('.edition-masthead [data-section="poets"]').addEventListener('click',e => {
    e.preventDefault();
    if(mobile.matches) {
      body.classList.add('sidebar-mobile-open');shade.hidden=false;opener.setAttribute('aria-expanded','true');
    } else {side=true;storage.set('edition-side','open');applySide();}
    $('.sidebar-heading')?.focus();
  });
  shade.addEventListener('click',closeDrawer);
  $$('.reading-modes button').forEach(b => b.addEventListener('click',() => setMode(b.dataset.mode)));
  $('.font-down').addEventListener('click',() => setFont(size-1));$('.font-up').addEventListener('click',() => setFont(size+1));
  document.addEventListener('keydown',e => {
    if(e.key==='Escape') {if(body.classList.contains('sidebar-mobile-open')){closeDrawer();opener.focus();}}
    if(e.key==='Tab' && mobile.matches && body.classList.contains('sidebar-mobile-open')) {
      const items=[...sidebar.querySelectorAll('button,a[href]')].filter(x => x.getClientRects().length);
      if(e.shiftKey && document.activeElement===items[0]) {items.at(-1).focus();e.preventDefault();}
      else if(!e.shiftKey && document.activeElement===items.at(-1)) {items[0].focus();e.preventDefault();}
    }
  });
  mobile.addEventListener('change',applySide);new ResizeObserver(reflow).observe(reading);
  setMode(mode,false);setFont(size,false);applySide();
})();
