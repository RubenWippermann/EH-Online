#!/usr/bin/env python3
"""IndexNow fuer erstehilfekurse.online. Im Repo (Wurzel = Webroot) ausfuehren.

Standard ist --dry-run: es wird nichts gesendet, nur gezaehlt und ausgegeben.
Echtes Senden nur mit --senden (api.indexnow.org).

  python3 tools/indexnow.py                  # Trockenlauf: geaenderte URLs seit letztem Ping-Stand bzw. HEAD~1
  python3 tools/indexnow.py --seit <rev>     # geaenderte Seiten seit <rev>
  python3 tools/indexnow.py --alle           # alle URLs der Sitemap
  python3 tools/indexnow.py --senden         # wirklich melden, danach Stand in tools/indexnow-stand.txt

Nur URLs, die in sitemap.xml stehen und zur Sitemap-Domain passen. Obergrenze 10.000 URLs je Aufruf.
Schluessel: die live liegende <key>.txt im Wurzelverzeichnis (32 Hex), wird nie neu erzeugt.
"""
import json, os, re, subprocess, sys, urllib.request
from urllib.parse import urlparse

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SITEMAP = os.path.join(ROOT, 'sitemap.xml')
STAND = os.path.join(ROOT, 'tools', 'indexnow-stand.txt')
ENDPOINT = 'https://api.indexnow.org/indexnow'
MAX_URLS = 10000


def sitemap_urls():
    text = open(SITEMAP, encoding='utf-8').read()
    return re.findall(r'<loc>([^<]+)</loc>', text)


def finde_schluessel():
    keys = [f[:-4] for f in os.listdir(ROOT) if re.fullmatch(r'[0-9a-f]{32}\.txt', f)]
    if len(keys) != 1:
        sys.exit(f'Erwartet genau eine <32-Hex>.txt im Wurzelverzeichnis, gefunden: {keys}')
    key = keys[0]
    if open(os.path.join(ROOT, key + '.txt'), encoding='utf-8').read().strip() != key:
        sys.exit('Inhalt der Schluesseldatei stimmt nicht mit dem Dateinamen ueberein.')
    return key


def git(*a):
    return subprocess.run(['git', '-C', ROOT, *a], capture_output=True, text=True, check=True).stdout


def datei_zu_url(f, host):
    if not f.endswith('.html'):
        return None
    if f == 'index.html':
        return f'https://{host}/'
    if f.endswith('/index.html'):
        return f'https://{host}/{f[:-len("index.html")]}'
    return f'https://{host}/{f}'


def main():
    a = sys.argv[1:]
    senden = '--senden' in a
    urls_sm = sitemap_urls()
    hosts = {urlparse(u).netloc for u in urls_sm}
    if len(hosts) != 1:
        sys.exit(f'Sitemap enthaelt mehrere Hosts: {hosts}')
    host = hosts.pop()
    if '--alle' in a:
        urls = urls_sm
        basis = 'alle'
    else:
        if '--seit' in a:
            basis = a[a.index('--seit') + 1]
        elif os.path.exists(STAND):
            basis = open(STAND).read().strip()
        else:
            basis = 'HEAD~1'
        dateien = git('diff', '--name-only', '--diff-filter=ACMR', basis, 'HEAD').splitlines()
        erlaubt = set(urls_sm)
        urls = [u for u in (datei_zu_url(f, host) for f in dateien) if u in erlaubt]
    urls = sorted(set(urls))
    fremd = [u for u in urls if urlparse(u).netloc != host]
    if fremd:
        sys.exit(f'Host-Pruefung fehlgeschlagen: {fremd[:3]}')
    if len(urls) > MAX_URLS:
        print(f'Warnung: {len(urls)} URLs, auf {MAX_URLS} gekuerzt (Rest im naechsten Aufruf).')
        urls = urls[:MAX_URLS]
    key = finde_schluessel()
    print(f'Host {host} | Basis {basis} | {len(urls)} URLs | {"SENDEN" if senden else "dry-run"}')
    if not senden:
        for u in urls[:5]:
            print('  ', u)
        return
    if not urls:
        print('Nichts zu melden.')
        return
    payload = json.dumps({'host': host, 'key': key, 'keyLocation': f'https://{host}/{key}.txt',
                          'urlList': urls}).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=payload, method='POST',
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f'IndexNow: HTTP {r.status}, {len(urls)} URLs gemeldet.')
    open(STAND, 'w').write(git('rev-parse', 'HEAD').strip() + '\n')


if __name__ == '__main__':
    main()
