# Backup: Ortsseiten-Grunddaten

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
