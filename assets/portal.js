(function() {
    "use strict";
    function esc(s) {
        return String(s == null ? "" : s).replace(/[&<>"]/g, function(c) {
            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;"
            }[c];
        });
    }
    function initFinder() {
        var root = document.querySelector("[data-finder]");
        var dataEl = document.getElementById("finder-data");
        if (!root || !dataEl) return;
        var DATA;
        try {
            DATA = JSON.parse(dataEl.textContent);
        } catch (e) {
            return;
        }
        var result = root.querySelector("[data-result]");
        var tiles = root.querySelectorAll(".finder-tile");
        function show(anlassSlug) {
            var a = DATA.anlaesse[anlassSlug];
            if (!a) return;
            var k = DATA.kurse[a.kurs];
            if (!k) return;
            Array.prototype.forEach.call(tiles, function(t) {
                t.classList.toggle("sel", t.getAttribute("data-anlass") === anlassSlug);
            });
            result.hidden = false;
            result.innerHTML = '<div class="finder-card">' + '<span class="eyebrow">Empfehlung für „' + esc(a.name) + '"</span>' + "<h2>" + esc(k.name) + "</h2>" + "<p>" + esc(k.kurz) + "</p>" + '<dl class="k-meta">' + "<div><dt>Dauer</dt><dd>" + esc(k.dauer) + "</dd></div>" + "<div><dt>Gültig</dt><dd>" + esc(k.gueltig) + "</dd></div>" + "<div><dt>Wer zahlt</dt><dd>" + esc(k.wer_zahlt) + "</dd></div>" + "<div><dt>Preis</dt><dd>" + esc(k.preis) + "</dd></div></dl>" + '<div class="hero-actions">' + '<a class="btn primary" href="' + esc(k.url) + '">Zum Kurs &amp; zu den Terminen →</a>' + '<a class="btn ghost" href="/inhouse/#anfrage">Als Kurs vor Ort anfragen</a></div>' + '<p class="muted" style="font-size:.86rem;margin-top:12px">Nicht sicher? ' + '<a href="tel:+4955277488495">Ruf kurz an</a> — wir sortieren das in zwei Minuten.</p>' + "</div>";
            if (window.history && history.replaceState) {
                history.replaceState(null, "", "/kursfinder/?anlass=" + anlassSlug);
            }
            result.scrollIntoView({
                behavior: "smooth",
                block: "nearest"
            });
        }
        Array.prototype.forEach.call(tiles, function(t) {
            t.addEventListener("click", function() {
                show(t.getAttribute("data-anlass"));
            });
        });
        var m = /[?&]anlass=([a-z-]+)/.exec(location.search);
        if (m && DATA.anlaesse[m[1]]) show(m[1]);
    }
    function initErsthelfer() {
        var root = document.querySelector('[data-calc="ersthelfer"]');
        if (!root) return;
        var anz = root.querySelector("#c-anz");
        var out = root.querySelector("[data-out]");
        var API = "https://software-wippermann.de";
        var ORG_LEAD = "personal-paramedic";
        var QUELLE = "erstehilfekurse";
        var letztesErgebnis = null;
        function sendeLeadMail(e) {
            e.preventDefault();
            var form = e.target;
            var mail = form.querySelector('[name="email"]').value.trim();
            var hp = form.querySelector('[name="website"]');
            if (hp && hp.value) return;
            if (!mail || !letztesErgebnis) return;
            var btn = form.querySelector('button[type="submit"]');
            var status = form.querySelector(".calc-lead-status");
            btn.disabled = true;
            btn.textContent = "Wird gesendet …";
            fetch(API + "/api/lead", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    org: ORG_LEAD,
                    quelle: QUELLE,
                    email: mail,
                    website: "",
                    rechner: letztesErgebnis
                })
            }).then(function(r) {
                return r.json().catch(function() {
                    return {};
                });
            }).then(function(res) {
                if (res && res.ok) {
                    form.innerHTML = '<p class="calc-lead-status ok">Danke — das Ergebnis ist unterwegs zu dir.</p>';
                } else {
                    btn.disabled = false;
                    btn.textContent = "Ergebnis per Mail sichern";
                    if (status) status.textContent = "Das hat leider nicht geklappt. Bitte später erneut versuchen.";
                }
            }).catch(function() {
                btn.disabled = false;
                btn.textContent = "Ergebnis per Mail sichern";
                if (status) status.textContent = "Das hat leider nicht geklappt. Bitte später erneut versuchen.";
            });
        }
        function calc() {
            var n = parseInt(anz.value, 10);
            if (!n || n < 1) {
                out.innerHTML = "";
                letztesErgebnis = null;
                return;
            }
            var typ = (root.querySelector('input[name="c-typ"]:checked') || {}).value || "verwaltung";
            var zahl, regel;
            if (n <= 20) {
                zahl = 1;
                regel = "Bei 2 bis 20 anwesenden Versicherten genügt <b>ein:e Ersthelfer:in</b>.";
            } else {
                var quote = typ === "sonstige" ? .1 : .05;
                zahl = Math.ceil(n * quote);
                regel = "Bei über 20 Anwesenden: <b>" + quote * 100 + "&nbsp;%</b> von " + n + " = <b>" + zahl + "</b> (aufgerundet).";
            }
            letztesErgebnis = {
                anzahl: n,
                typ: typ,
                ergebnis: zahl
            };
            out.innerHTML = '<div class="calc-result"><b class="calc-big">' + zahl + "</b>" + "<span>" + (zahl === 1 ? "Ersthelfer:in" : "Ersthelfer:innen") + " erforderlich</span></div>" + "<p>" + regel + "</p>" + '<p class="muted" style="font-size:.86rem">Richtwert nach DGUV Vorschrift 1 § 26 Abs. 1. ' + "Plane Urlaub, Schicht und Krankheit ein, damit immer genug Ersthelfer:innen anwesend sind.</p>" + '<a class="btn primary" href="/inhouse/#anfrage" style="margin-top:8px">Ersthelfer ausbilden lassen →</a>' + '<form class="calc-lead-form" data-lead-form style="margin-top:14px">' + '<label for="c-lead-mail" style="font-size:.9rem">Ergebnis per Mail erhalten (optional)</label>' + '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:4px">' + '<input type="email" id="c-lead-mail" name="email" placeholder="deine@mail.de" style="flex:1;min-width:200px">' + '<input type="text" name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">' + '<button class="btn outline" type="submit">Ergebnis per Mail sichern</button>' + '</div><p class="calc-lead-status muted" style="font-size:.82rem;margin-top:4px"></p></form>';
            var leadForm = out.querySelector("[data-lead-form]");
            if (leadForm) leadForm.addEventListener("submit", sendeLeadMail);
        }
        anz.addEventListener("input", calc);
        Array.prototype.forEach.call(root.querySelectorAll('input[name="c-typ"]'), function(r) {
            r.addEventListener("change", calc);
        });
    }
    function initAuffrischung() {
        var root = document.querySelector('[data-calc="auffrischung"]');
        if (!root) return;
        var datum = root.querySelector("#c-datum");
        var out = root.querySelector("[data-out]");
        var MONTHS = [ "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember" ];
        function fmt(d) {
            return d.getDate() + ". " + MONTHS[d.getMonth()] + " " + d.getFullYear();
        }
        function calc() {
            if (!datum.value) {
                out.innerHTML = "";
                return;
            }
            var d = new Date(datum.value);
            if (isNaN(d.getTime())) {
                out.innerHTML = "";
                return;
            }
            var jahre = parseInt((root.querySelector('input[name="c-rolle"]:checked') || {}).value || "2", 10);
            var faellig = new Date(d.getTime());
            faellig.setFullYear(faellig.getFullYear() + jahre);
            var heute = new Date;
            heute.setHours(0, 0, 0, 0);
            var tage = Math.round((faellig - heute) / 864e5);
            var status, cls;
            if (tage < 0) {
                status = "Überfällig seit " + Math.abs(tage) + " Tagen — die Frist ist abgelaufen. " + "Jetzt ist in der Regel die komplette Erste-Hilfe-Ausbildung erneut nötig, nicht nur die Fortbildung.";
                cls = "err";
            } else if (tage <= 90) {
                status = "Bald fällig — in " + tage + " Tagen. Jetzt einen Fortbildungstermin sichern.";
                cls = "warn";
            } else {
                status = "Alles gut — noch " + tage + " Tage Zeit.";
                cls = "ok";
            }
            out.innerHTML = '<div class="calc-result"><b class="calc-big">' + fmt(faellig) + "</b>" + "<span>spätestens auffrischen (alle " + jahre + " Jahre)</span></div>" + '<p class="calc-status ' + cls + '">' + status + "</p>" + '<a class="btn primary" href="/kurse/erste-hilfe-fortbildung/" style="margin-top:8px">Fortbildungstermine ansehen →</a>';
        }
        datum.addEventListener("change", calc);
        datum.addEventListener("input", calc);
        Array.prototype.forEach.call(root.querySelectorAll('input[name="c-rolle"]'), function(r) {
            r.addEventListener("change", calc);
        });
    }
    function boot() {
        initFinder();
        initErsthelfer();
        initAuffrischung();
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
