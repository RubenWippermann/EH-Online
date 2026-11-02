# Generator-Vollbau nie als Ganzes live (EHO, Stand 02.11.2026)

Der Live-Stand (Repo EH-Online) wird von mehreren Chats direkt gepflegt. Der Generator (Zweig eho-gen-seo-20-10)
kennt diese Änderungen nicht; sein Vollbau gibt z. B. keine `js`-Klasse im Head, keine google-site-verification,
keine og:image-Maße, kein `role="region"` am Topbar aus (Details: Koordinator/seo/eho-generator-live-abweichung-02-11.md).
Eine Vollbau-Ausgabe, die als Ganzes nach `main` käme, würde diese Änderungen zurückdrehen.

Regel: Vor jedem Push `python3 tools/vor_push_pruefen.py` (Diff gegen origin/main). Abbruch bei mehr als 400 geänderten
Dateien (ohne `EHO_BULK_OK=<Grund>`) oder wenn eine geänderte Seite eine Live-Kennung verloren hat.
Massenänderungen laufen als Skript direkt auf dem Live-Stand (Beispiel `tools/live_aufraeumen.py`, mit Trockenlauf und Zählung).
Der Tageslauf (05:30) ist unkritisch: er patcht nur Termine-Block und Course-JSON-LD der 12 Kursseiten.
