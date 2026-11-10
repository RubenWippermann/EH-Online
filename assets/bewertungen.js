/* Stimmen unserer Teilnehmenden: ein GET je Seitenaufruf (kein Browser-Speicher, BL/Jurist 05.11.), nur freigegebene Bewertungen der eigenen
   Firma (Personal Paramedic e.K. = org personal-paramedic). Ohne Daten/Fehler/Timeout bleibt der Block
   ausgeblendet (hidden). Kein JSON-LD: Eigenbewertungen der Betreiberfirma sind fuer Rich Results nicht zulaessig. */
(function () {
  'use strict';
  var root = document.querySelector('[data-bewertungen]');
  if (!root) return;
  var ORG = 'personal-paramedic', API = 'https://software-wippermann.de';
  var section = root.closest('section') || root;

  function show(list) {
    if (!list || !list.length) return;
    var frag = document.createDocumentFragment();
    list.slice(0, 6).forEach(function (b) {
      if (!b || !b.text) return;
      var fig = document.createElement('figure'); fig.className = 'card';
      var st = document.createElement('div');
      st.setAttribute('role', 'img');
      st.setAttribute('aria-label', Math.max(1, Math.min(5, +b.sterne || 5)) + ' von 5 Sternen');
      st.style.cssText = 'color:var(--brand);font-size:1.05rem;letter-spacing:.08em';
      st.textContent = '★★★★★'.slice(0, Math.max(1, Math.min(5, +b.sterne || 5)));
      var q = document.createElement('blockquote');
      q.style.cssText = 'margin:12px 0 14px;font-size:1rem;color:var(--ink-2)';
      q.textContent = String(b.text).length > 400 ? String(b.text).slice(0, 397).replace(/\s+\S*$/, '') + ' …' : String(b.text);
      var cap = document.createElement('figcaption'); cap.className = 'muted'; cap.style.fontSize = '.87rem';
      cap.textContent = (b.name && String(b.name).trim()) || 'Teilnehmer:in';
      fig.appendChild(st); fig.appendChild(q); fig.appendChild(cap); frag.appendChild(fig);
    });
    if (!frag.childNodes.length) return;
    root.appendChild(frag);
    section.hidden = false;
  }

  var ctl = window.AbortController ? new AbortController() : null;
  var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 6000);
  fetch(API + '/api/bewertungen?org=' + encodeURIComponent(ORG), ctl ? { signal: ctl.signal } : {})
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      var l = (d && d.bewertungen) || [];
      show(l);
    })
    .catch(function () {})
    .then(function () { clearTimeout(timer); });
})();
