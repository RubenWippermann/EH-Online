/* Inhouse-Anfrage: ?personen=N (aus dem Ersthelfer-Rechner) in das Feld "Teilnehmerzahl" uebernehmen.
   Nur ganze Zahlen 1-9999, kein Absenden, keine weiteren Parameter. */
(function () {
  'use strict';
  var m = /[?&]personen=(\d{1,4})(?:&|#|$)/.exec(location.search);
  var f = document.getElementById('f-personen');
  if (!m || !f || f.value) return;
  var n = parseInt(m[1], 10);
  if (n >= 1) f.value = String(n);
})();
