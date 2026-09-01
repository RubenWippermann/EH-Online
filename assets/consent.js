/* erstehilfekurse.online — Cookie-Consent (essenziell vs. Marketing).
   Marketing-/Werbeskripte werden erst NACH ausdrücklicher Einwilligung geladen.
   Speicherung: localStorage + 1st-party-Cookie (12 Monate). */
(function () {
  'use strict';

  var KEY = 'ehk-consent';          // 'accept' | 'reject'
  var MAXAGE = 60 * 60 * 24 * 365;  // 12 Monate

  function get() {
    try { return localStorage.getItem(KEY); } catch (e) {}
    var m = /(?:^|;\s*)ehk_consent=([^;]+)/.exec(document.cookie);
    return m ? decodeURIComponent(m[1]) : null;
  }

  function set(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
    document.cookie = 'ehk_consent=' + encodeURIComponent(v) + ';max-age=' + MAXAGE +
      ';path=/;samesite=lax';
  }

  var banner = document.querySelector('[data-cc-banner]');

  function openBanner() { if (banner) { banner.hidden = false; document.body.classList.add('cc-open'); } }
  function closeBanner() { if (banner) { banner.hidden = true; document.body.classList.remove('cc-open'); } }

  /* Marketing freischalten. AdSense ist seit 31.08. anwaltlich freigegeben (AD_NETWORK_AKTIV) —
     das SDK-Skript wird deshalb hier NACH Opt-in nachgeladen, nie vorher, nie fest im <head>.
     Client-ID kommt aus dem bereits vorhandenen data-ad-client der Anzeigenplätze (network_ad_slot
     in build.py), nicht doppelt hier hinterlegt — kein Widerspruch möglich, falls sich die
     Publisher-ID mal ändert. Fund 01.09.: das SDK-Skript fehlte komplett, <ins>-Boxen standen
     leer/inert im HTML, obwohl AD_NETWORK_AKTIV=True war. */
  function enableMarketing() {
    document.documentElement.setAttribute('data-consent', 'marketing');
    var slots = document.querySelectorAll('[data-ad-consent]');
    Array.prototype.forEach.call(slots, function (el) {
      el.classList.add('consented');
    });
    if (slots.length && !document.querySelector('script[data-adsense-sdk]')) {
      var ins = document.querySelector('ins.adsbygoogle[data-ad-client]');
      var client = ins && ins.getAttribute('data-ad-client');
      if (client) {
        var s = document.createElement('script');
        s.async = true;
        s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + encodeURIComponent(client);
        s.crossOrigin = 'anonymous';
        s.setAttribute('data-adsense-sdk', '1');
        document.head.appendChild(s);
      }
    }
  }

  function apply(v) {
    if (v === 'accept') enableMarketing();
    else document.documentElement.setAttribute('data-consent', 'essential');
  }

  function choose(v) { set(v); apply(v); closeBanner(); }

  function boot() {
    if (banner) {
      var a = banner.querySelector('[data-cc="accept"]');
      var r = banner.querySelector('[data-cc="reject"]');
      if (a) a.addEventListener('click', function () { choose('accept'); });
      if (r) r.addEventListener('click', function () { choose('reject'); });
    }
    Array.prototype.forEach.call(document.querySelectorAll('[data-cookie-settings]'), function (b) {
      b.addEventListener('click', function (e) { e.preventDefault(); openBanner(); });
    });

    var cur = get();
    if (cur === 'accept' || cur === 'reject') { apply(cur); }
    else { openBanner(); }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
