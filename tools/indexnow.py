#!/usr/bin/env python3
"""IndexNow-Ping fuer erstehilfekurse.online: meldet URLs bei api.indexnow.org (verteilt an Bing u. a.).

FEHLER bis 01.11.2026: SITEMAP zeigte auf ../site/sitemap.xml (existiert nicht) -> Lauf ohne Argumente
brach ab, Bing bekam nie einen Ping. Jetzt: Sitemap = <Repo-Wurzel>/sitemap.xml, Schluessel = die
32-stellige <hex>.txt in der Repo-Wurzel, Vorabpruefung der Schluesseldatei (live 200 und Inhalt = Schluessel),
Batches <= 10.000, Erfolg nur bei HTTP 200 oder 202.

Standard ist TROCKENLAUF (Anfrage bauen und zeigen, nichts senden). Senden nur mit --send.

Nutzung (Repo-Wurzel, nach dem Push, wenn die Seiten live sind):
    python3 tools/indexnow.py --git origin/main@{1}..origin/main --send   # alle seit dem letzten Stand geaenderten, indexierbaren Seiten
    python3 tools/indexnow.py --git HEAD~1..HEAD                          # Trockenlauf fuer den letzten Commit
    python3 tools/indexnow.py https://www.erstehilfekurse.online/wissen/herzinfarkt/ --send
    python3 tools/indexnow.py --sitemap --send                            # alle URLs der sitemap.xml (nur nach groesseren Umbauten)
noindex-Seiten werden bei --git nicht gemeldet. Rueckgabewert 0 = Erfolg (Trockenlauf: Anfrage gueltig).
"""
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HOST = "www.erstehilfekurse.online"
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH = 10000


def schluessel():
    dat = [p for p in glob.glob(os.path.join(ROOT, "*.txt")) if re.fullmatch(r"[0-9a-f]{32}", os.path.basename(p)[:-4])]
    if len(dat) != 1:
        sys.exit(f"Erwartet genau eine <32-hex>.txt in {ROOT}, gefunden: {len(dat)}")
    key = os.path.basename(dat[0])[:-4]
    if open(dat[0], encoding="utf-8").read().strip() != key:
        sys.exit("Schluesseldatei-Inhalt ist nicht gleich dem Dateinamen")
    return key


def urls_sitemap():
    return re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())


def urls_git(rng):
    out = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", rng], capture_output=True, text=True, check=True).stdout.split()
    urls = []
    for f in out:
        if f != "index.html" and not f.endswith("/index.html"):
            continue
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            continue
        if "noindex" in open(p, encoding="utf-8", errors="ignore").read(6000):
            continue
        urls.append(f"https://{HOST}/" + (f[:-len("index.html")] if f != "index.html" else ""))
    return urls


def pruefe_schluessel_live(key):
    loc = f"https://{HOST}/{key}.txt"
    try:
        with urllib.request.urlopen(loc, timeout=20) as r:
            ok = r.status == 200 and r.read().decode().strip() == key
    except Exception as e:
        sys.exit(f"Schluesseldatei nicht erreichbar ({loc}): {e}")
    if not ok:
        sys.exit(f"Schluesseldatei live falsch ({loc})")
    return loc


def main():
    args = sys.argv[1:]
    senden = "--send" in args
    args = [a for a in args if a != "--send"]
    if "--git" in args:
        i = args.index("--git"); urls = urls_git(args[i + 1]); del args[i:i + 2]
    elif "--sitemap" in args:
        args.remove("--sitemap"); urls = urls_sitemap()
    else:
        urls = []
    urls += args
    urls = list(dict.fromkeys(urls))
    fremd = [u for u in urls if not u.startswith(f"https://{HOST}/")]
    if fremd:
        sys.exit(f"URL(s) nicht auf {HOST}: {fremd[:3]}")
    if not urls:
        print("Keine URLs - nichts zu melden.")
        return
    key = schluessel()
    loc = pruefe_schluessel_live(key)
    print(f"Schluesseldatei live OK: {loc}")
    for n in range(0, len(urls), BATCH):
        teil = urls[n:n + BATCH]
        payload = {"host": HOST, "key": key, "keyLocation": loc, "urlList": teil}
        if not senden:
            print(f"TROCKENLAUF Batch {n // BATCH + 1}: {len(teil)} URLs, Beispiel: {teil[:3]} (mit --send senden)")
            continue
        req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), method="POST",
                                     headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        print(f"IndexNow Batch {n // BATCH + 1}: HTTP {code} ({len(teil)} URLs)")
        if code not in (200, 202):
            sys.exit(f"Fehler: HTTP {code} (200/202 erwartet; 403 = Schluessel, 422 = URL/Host, 429 = zu viele Anfragen)")


if __name__ == "__main__":
    main()
