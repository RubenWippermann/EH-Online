# Backup: Ortsseiten-Grunddaten + Rechtstexte

`build/` (Generator-Skripte, `build.py`/`data.py`/`staedte.json` u. a.) ist in diesem
Repo bewusst **nicht** versioniert. Genau das hat am 31.08./03.09. dazu geführt, dass
`staedte.json`, `orte_fakten.json`, `plz_cache.json` und `build/legal/` durch einen
fremden `git reset --hard` unwiederbringlich verloren gingen (siehe
`~/Claude/Koordinator/verteilbuch.md`, Abschnitt "HAUSWEITE REGEL: EH-Online-Repo").

Dieser Ordner ist **nur ein Backup**, kein Live-Pfad — `build.py` liest weiterhin aus
`build/staedte.json`, nicht von hier. Bei erneutem Verlust:

```bash
cp site/build-daten/staedte.json build/staedte.json
```

`staedte.json` wird aus dem offiziellen Destatis-Gemeindeverzeichnis erzeugt, siehe
`staedte_generieren.py` (ebenfalls hier gesichert). Neu erzeugen:

```bash
cd build/
curl -sL -o staedte_quelle_destatis.xlsx \
  "https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/Archiv/GVAuszugQ/AuszugGV1QAktuell.xlsx?__blob=publicationFile"
python3 staedte_generieren.py
```

Stand dieser Sicherung: 06.09.2026, 2.934 Gemeinden ≥5.000 EW (Destatis, Stand 31.03.2026).

## Rechtstexte (`legal/agb.html`, `legal/widerruf.html`)

Ebenfalls am 31.08./03.09. verloren gegangen, hat `build_legal()` seither hart
mit `KRITISCH: build/legal/agb.html fehlt` abgebrochen — und weil `build_sitemap()`
in `main()` danach läuft, blieb dadurch jeder vollständige Build (inkl. Sitemap)
blockiert. Am 06.09. aus dem LIVE `/agb/` bzw. `/widerruf/` zurückgewonnen (kein
neuer Text — nur der bereits freigegebene, unveränderte Inhalt aus dem
`<div class="prose legal">…</div>`-Block extrahiert, byte-identisch gegen den
Testbuild geprüft). Bei erneutem Verlust:

```bash
cp site/build-daten/legal/agb.html build/legal/agb.html
cp site/build-daten/legal/widerruf.html build/legal/widerruf.html
```

Falls auch die LIVE-Seiten selbst je verloren gehen sollten, bräuchte es echte
Rechtstext-Neufassung durch Ruben/Anwalt — das ist niemals eine Aufgabe für
diesen Chat, nur die technische Wiederherstellung aus einem bekannten,
bereits freigegebenen Stand.

## GitHub-Actions-Migration (`.github/workflows/termine.yml`)

Fertig vorbereiteter Workflow, analog zu EH-Worbis' `termine.yml`, um den
lokalen launchd-Job (`online.erstehilfekurse.termine`, hängt an diesem
einen Mac) durch einen robusteren täglichen GitHub-Actions-Lauf zu
ersetzen. Kann NICHT von hier aus scharf geschaltet werden — braucht zwei
Schritte, die nur Ruben machen kann (Details stehen als Kommentar oben in
der Workflow-Datei selbst):

1. `build/` (build.py, data.py, wissen_data.py, staedte.json, legal/) in
   ein neues Repo bringen — NICHT ins öffentliche EH-Online-Repo, weil
   data.py Geschäftsinternes enthält (Partner-Konditionen, AdSense-ID,
   Preisstruktur). Empfehlung: neues privates Repo (z. B.
   `RubenWippermann/EH-Online-Build`).
2. In diesem neuen Repo einen Secret `SITE_PUSH_TOKEN` anlegen
   (fine-grained PAT, "Contents: Read and write" nur auf EH-Online) und
   `TOKEN_ABLAUF` in der Workflow-Datei nachtragen.

Danach: Workflow-Datei aus `build-daten/.github/workflows/termine.yml`
in das neue Repo kopieren, und den launchd-Job deaktivieren
(`launchctl unload ~/Library/LaunchAgents/online.erstehilfekurse.termine.plist`),
damit nicht doppelt gebaut wird.
