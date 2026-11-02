#!/usr/bin/env python3
"""Ein Änderungsdatum je Seite (SEO/GEO 01.11.): letztes INHALTLICHES Änderungsdatum, erkannt am Inhalts-Hash, nicht an der Bauzeit.
Dasselbe Datum steht (1) sichtbar als "Stand: TT. Mon. JJJJ" unter der H1 (und im Haftungshinweis), (2) als dateModified im Article-Schema,
(3) als <lastmod> in sitemap.xml.

Ledger: tools/seiten-stand.json  {pfad: {"stand": "JJJJ-MM-TT", "hash": "<sha1>"}}.
Hash = sha1 des <main>-Inhalts ohne flüchtige Teile (Stand-Zeile, Stand im Haftungshinweis, vorgerenderte Termine inkl. Stand-Zeile, Skripte, Weiterlesen-Kartenraster, Linkziele <a href>; Linktext zählt). Reine Verlinkung bumpt das Datum nicht.
Ablauf: Hash gleich -> Datum bleibt; Hash anders -> Datum = heute. Erster Lauf (Seite nicht im Ledger): Datum = max(sichtbarer Stand,
bisheriger lastmod), Hash = aktuell.
Seiten, die tools/sitemap-fokus.py aus der Sitemap genommen hat, werden hier nicht mehr verfolgt (Ledger bleibt eingefroren, lastmod-Fingerabdruck greift erst wieder nach Aufnahme).
Aufruf im Repo-Root:  python3 tools/seiten-stand.py [--dry] [--rebase-hash (Hash nachziehen, Datum NICHT ändern: nur für technische Änderungen)] [--heute JJJJ-MM-TT] [--export <daten-datum.json des Generators>]
--export schreibt die Daten in die daten-datum.json des Generators (geaendert = Stand, wo er von veroeffentlicht abweicht)."""
import re, sys, os, json, glob, hashlib, datetime

MON = ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sep.", "Okt.", "Nov.", "Dez."]
HOST = "https://www.erstehilfekurse.online"
dry = "--dry" in sys.argv
rebase = "--rebase-hash" in sys.argv
heute = datetime.date.today().isoformat()
if "--heute" in sys.argv:
    heute = sys.argv[sys.argv.index("--heute") + 1]
export = sys.argv[sys.argv.index("--export") + 1] if "--export" in sys.argv else None
LEDGER = "tools/seiten-stand.json"
ledger = json.load(open(LEDGER, encoding="utf-8")) if os.path.exists(LEDGER) else {}


def de(iso):
    y, m, d = iso.split("-")
    return f"{int(d)}. {MON[int(m) - 1]} {y}"


def iso_de(txt):
    m = re.match(r"(\d{1,2})\. (\S+?) (\d{4})$", txt.strip())
    if not m or m.group(2) not in MON:
        return None
    return f"{m.group(3)}-{MON.index(m.group(2)) + 1:02d}-{int(m.group(1)):02d}"


KS = re.compile(r'(<p class="muted k-stand"[^>]*>)(.*?)(</p>)', re.S)
HIN = re.compile(r'(<aside class="note medizin-hinweis" role="note">.*?im Notfall an die 112\.)( Stand: [^<]*?\.)?(</aside>)', re.S)
TERM = re.compile(r'<div class="termine rv"[^>]*data-prerendered="1">.*?<p class="termine-stand">.*?</p></div>', re.S)

WL = re.compile(r'(Weiterlesen</h2></div>\s*<div class="grid g3">).*?(</div></section>)', re.S)


def inhalt_hash(t):
    i, j = t.find("<main"), t.find("</main>")
    m = t[i:j] if 0 <= i < j else t
    m = re.sub(r"<script.*?</script>", "", m, flags=re.S)
    m = KS.sub("", m)
    m = HIN.sub(r"\1\3", m)
    m = TERM.sub("", m)
    m = WL.sub(r"\1\2", m)  # Weiterlesen-Kartenraster zählt nicht (reine Verlinkung)
    m = re.sub(r"<a [^>]*>(.*?)</a>", r"\1", m, flags=re.S)  # Linkziele zählen nicht, Linktext schon
    m = re.sub(r"\s+", " ", m)
    return hashlib.sha1(m.encode("utf-8")).hexdigest()


sm = open("sitemap.xml", encoding="utf-8").read()
alt_lastmod = {}
for loc, lm in re.findall(r"<loc>" + re.escape(HOST) + r"([^<]*)</loc>(?:<lastmod>([^<]*)</lastmod>)?", sm):
    alt_lastmod[loc] = lm or None

neu_stand = {}
geaendert_n = neu_n = 0
for pfad in sorted(alt_lastmod):
    f = (pfad.lstrip("/") + "index.html") if pfad.endswith("/") else pfad.lstrip("/")
    if not os.path.exists(f):
        continue
    t = open(f, encoding="utf-8").read()
    h = inhalt_hash(t)
    e = ledger.get(pfad)
    if e is None:
        m = KS.search(t)
        sicht = None
        if m:
            mm = re.search(r"Stand: ([^·<]+)", m.group(2))
            sicht = iso_de(mm.group(1)) if mm else None
        kand = [d for d in (sicht, alt_lastmod[pfad]) if d]
        e = {"stand": max(kand) if kand else heute, "hash": h}
        neu_n += 1
    elif e["hash"] != h:
        if rebase:   # rein technische Änderung (z. B. Link-Umschreibung): Hash nachziehen, Datum behalten
            e = {**e, "hash": h}
        else:
            e = {**e, "stand": heute, "hash": h}
            geaendert_n += 1
    ledger[pfad] = e
    neu_stand[pfad] = e["stand"]
    # Seite angleichen: sichtbarer Stand, Haftungshinweis, dateModified
    o = t
    iso = e["stand"]
    t = KS.sub(lambda m: m.group(1) + re.sub(r"Stand: [^·<]*?(\s*)(?=·|$)", lambda q: "Stand: " + de(iso) + q.group(1), m.group(2), count=1) + m.group(3), t, count=1)
    t = HIN.sub(lambda m: m.group(1) + " Stand: " + de(iso) + "." + m.group(3), t)
    def ld(m):
        blk = m.group(0)
        if '"dateModified"' not in blk:
            return blk
        return re.sub(r'("dateModified":\s*")\d{4}-\d{2}-\d{2}(")', r"\g<1>" + iso + r"\g<2>", blk, count=1)
    t = re.sub(r'<script type="application/ld\+json">.*?</script>', ld, t, flags=re.S)
    if t != o and not dry:
        open(f, "w", encoding="utf-8").write(t)

# sitemap lastmod
def sub_lm(m):
    p = m.group(1)
    d = neu_stand.get(p)
    if not d:
        return m.group(0)
    if "<lastmod>" in m.group(0):
        return re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>" + d + "</lastmod>", m.group(0))
    return m.group(0).replace("</loc>", "</loc><lastmod>" + d + "</lastmod>", 1)
sm2 = re.sub(r"<url><loc>" + re.escape(HOST) + r"([^<]*)</loc>.*?</url>", sub_lm, sm, flags=re.S)
print(f"Seiten: {len(neu_stand)} | neu ins Ledger: {neu_n} | inhaltlich geändert (Datum = {heute}): {geaendert_n} | "
      f"lastmod geändert: {sum(1 for a, b in zip(re.findall(r'<lastmod>[^<]*', sm), re.findall(r'<lastmod>[^<]*', sm2)) if a != b)}"
      + (" (Trockenlauf)" if dry else ""))
if not dry:
    open("sitemap.xml", "w", encoding="utf-8", newline="").write(sm2)
    json.dump(ledger, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
if export and not dry:
    d = json.load(open(export, encoding="utf-8"))
    ver = d.setdefault("veroeffentlicht", {}); ger = d.setdefault("geaendert", {})
    n = 0
    for pfad, st in neu_stand.items():
        if pfad in ver and st != ver[pfad]:
            if ger.get(pfad) != st:
                ger[pfad] = st; n += 1
        elif pfad in ger and pfad in ver and st == ver[pfad]:
            del ger[pfad]; n += 1
    json.dump(d, open(export, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"daten-datum.json: {n} Einträge angeglichen")
