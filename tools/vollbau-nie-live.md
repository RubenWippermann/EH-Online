# Generator-Vollbau nie als Ganzes live (EHO, Stand 02.11.2026)

Der Live-Stand (Repo EH-Online) wird von mehreren Chats direkt gepflegt. Generator-Zweig (eho-gen-seo-20-10) und Live-Stand weichen in beide Richtungen ab:
Live hat z. B. das Head-Skript `className+=" js"`, der Generator-Output hat google-site-verification, og:image-Maße und
`role="region"` am Topbar, die Live fehlen (Details: Koordinator/seo/eho-generator-live-abweichung-02-11.md).
Eine Vollbau-Ausgabe, die als Ganzes nach `main` käme, würde Live-Änderungen zurückdrehen (und unbemerkt andere einführen).

Regel: Vor jedem Push `python3 tools/vor_push_pruefen.py` (Diff gegen origin/main). Abbruch bei mehr als 400 geänderten
Dateien (ohne `EHO_BULK_OK=<Grund>`) oder wenn eine geänderte Seite die Live-Kennung (Head-Skript `js`) verloren hat.
Massenänderungen laufen als Skript direkt auf dem Live-Stand (Beispiel `tools/live_aufraeumen.py`, mit Trockenlauf und Zählung).
Der Tageslauf (05:30) ist unkritisch: er patcht nur Termine-Block und Course-JSON-LD der 12 Kursseiten.

## Hinweiskasten auf Gesundheitsseiten (02.11.2026)
Der Kasten „… ersetzt keine ärztliche Untersuchung, Diagnose oder Behandlung … im Notfall 112“ steht auf ~3.400 Wissens- und den Medizin-Ratgeberseiten.
Quelle im Generator: `medizin_hinweis()` in build.py (Zeile ~603; Wissen: Aufruf im Wissens-Template). Ein Stand, der den Kasten nicht hat (z. B. Worktree eh-wt-meta, HEAD 3ba8e45f45),
darf nie über den Live-Stand gelegt werden. Sperre: `tools/vor_push_pruefen.py` zählt die Seiten mit Kasten in `wissen`/`ratgeber` (ref vs. HEAD) und bricht ab, wenn HEAD weniger hat.
