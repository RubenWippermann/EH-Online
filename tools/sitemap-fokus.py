#!/usr/bin/env python3
"""Sitemap-Fokus (BL-Entscheidung 02.11., Stufe 1): Wissensseiten stehen nur mit >= 350 Prosa-Wörtern in sitemap.xml.
Alles andere (Ratgeber, Kurse, Hubs, Orte, Rechtsseiten, Start) bleibt unangetastet. Dünnere Wissensseiten bleiben erreichbar,
indexierbar (kein noindex) und im Hub verlinkt, fliegen nur aus der Sitemap. Reversibel: Schwelle 0 setzt alle wieder ein.
Seiten mit noindex oder Canonical auf einen anderen Slug (Alias) kommen nie hinein. lastmod aus tools/seiten-stand.json (inhaltlicher Stand);
Seiten außerhalb der Sitemap werden von tools/seiten-stand.py nicht mehr verfolgt (Ledger eingefroren) und beim Wiederaufnehmen
mit ihrem Ledger-Stand eingetragen.
Aufruf im Repo-Root: python3 tools/sitemap-fokus.py [--dry] [--min N]"""
import re, sys, glob, json, html
HOST = "https://www.erstehilfekurse.online"
dry = "--dry" in sys.argv
mn = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 350
sm = open("sitemap.xml", encoding="utf-8").read()
ledger = json.load(open("tools/seiten-stand.json", encoding="utf-8"))
ok = set()
for f in glob.glob("wissen/*/index.html"):
    slug = f.split("/")[1]
    t = open(f, encoding="utf-8", errors="ignore").read()
    if re.search(r'<meta[^>]+robots[^>]+noindex', t):
        continue
    c = re.search(r'rel="canonical" href="([^"]+)"', t)
    if not c or c.group(1) != f"{HOST}/wissen/{slug}/":
        continue
    pr = re.search(r'<div class="prose rv">(.*?)</div>\s*<aside', t, re.S)
    if pr and len(html.unescape(re.sub(r"<[^>]+>", " ", pr.group(1))).split()) >= mn:
        ok.add(f"/wissen/{slug}/")
urls = re.findall(r"<url>.*?</url>", sm, flags=re.S)
vorher = len(urls)
keep, raus = [], 0
have = set()
for u in urls:
    p = re.search(r"<loc>" + re.escape(HOST) + r"([^<]*)</loc>", u).group(1)
    have.add(p)
    if p.startswith("/wissen/") and p != "/wissen/" and p not in ok:
        raus += 1
        continue
    keep.append(u)
neu = 0
for p in sorted(ok - have):
    d = ledger.get(p, {}).get("stand")
    keep.append(f"<url><loc>{HOST}{p}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "<changefreq>monthly</changefreq><priority>0.70</priority></url>")
    neu += 1
head = sm[:sm.index("<url>")]
out = head + "".join(keep) + "</urlset>"
w = sum(1 for u in keep if "/wissen/" in u and "<loc>" + HOST + "/wissen/</loc>" not in u)
print(f"Sitemap vorher {vorher} -> nachher {len(keep)} | Wissen entfernt {raus}, neu aufgenommen {neu}, Wissen in Sitemap {w} | Schwelle {mn} Wörter" + (" (Trockenlauf)" if dry else ""))
if not dry:
    open("sitemap.xml", "w", encoding="utf-8", newline="").write(out)
