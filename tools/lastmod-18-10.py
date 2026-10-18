#!/usr/bin/env python3
"""sitemap.xml: echtes Aenderungsdatum je URL = Datum (%cs) des letzten Commits der zugehoerigen Seitendatei.
Ein einziger `git log --name-only`-Durchlauf. Aendert nur <lastmod>; fehlende lastmod werden ergaenzt.
Idempotent. Im Repo-Root: python3 tools/lastmod-18-10.py [--dry]"""
import re, subprocess, sys, os
dry = '--dry' in sys.argv
HOST = 'https://www.erstehilfekurse.online'
out = subprocess.run(['git', 'log', '--name-only', '--format=@@%cs', '--no-renames', '-z'],
                     capture_output=True, text=True, check=True).stdout
# -z: Dateinamen NUL-getrennt; Datumszeilen beginnen mit @@
BULK = 300  # Commits, die >= BULK Dateien beruehren (Kopf/Fuss-Massenaenderungen), zaehlen nicht als inhaltliche Aenderung
commits = []  # neu -> alt: [datum, [dateien]]
for tok in out.split('\0'):
    for part in tok.split('\n'):
        if not part:
            continue
        if part.startswith('@@'):
            commits.append([part[2:], []])
        elif commits:
            commits[-1][1].append(part)
latest = {}
for d, fl in commits:                      # letzter nicht-massenhafter Commit
    if len(fl) < BULK:
        for f in fl:
            latest.setdefault(f, d)
for d, fl in reversed(commits):            # Rueckfall: aeltester Commit der Datei (Anlage)
    for f in fl:
        latest.setdefault(f, d)
t = open('sitemap.xml', encoding='utf-8').read()
chg = miss = add = 0
def fix(m):
    global chg, miss, add
    u = m.group(0)
    p = re.search(r'<loc>' + re.escape(HOST) + r'(/[^<]*)</loc>', u).group(1)
    f = (p.lstrip('/') + 'index.html') if p.endswith('/') else p.lstrip('/')
    d = latest.get(f)
    if not d:
        miss += 1
        return u
    if '<lastmod>' in u:
        n = re.sub(r'<lastmod>[^<]*</lastmod>', '<lastmod>' + d + '</lastmod>', u)
    else:
        n = u.replace('</loc>', '</loc><lastmod>' + d + '</lastmod>', 1); add += 1
    if n != u: chg += 1
    return n
new = re.sub(r'<url>.*?</url>', fix, t, flags=re.S)
print(f'URLs geaendert: {chg}, davon lastmod ergaenzt: {add}, ohne Git-Datum (unveraendert): {miss}')
if not dry and new != t:
    open('sitemap.xml', 'w', encoding='utf-8', newline='').write(new)
