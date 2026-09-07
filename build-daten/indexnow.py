"""IndexNow-Ping — versendet den in build.py geschriebenen Schlüssel NICHT nur als Datei,
sondern meldet geänderte URLs aktiv bei api.indexnow.org (Sammel-Endpunkt, verteilt an alle
teilnehmenden Suchmaschinen, kein Loop über einzelne Engines nötig).

FUND 07.09. (Rubens "Durchgang bis Null"): dieses Skript war dokumentiert (PFLICHT-DEPLOY-
SCHRITT in einem früheren Sitzungs-Log), aber nie im Repo/lokal vorhanden — die Schlüsseldatei
lag die ganze Zeit live (200), gesendet wurde nie etwas. Bis 07.09. wieder gebaut.

Nutzung:
    python3 indexnow.py                    # alle URLs aus sitemap.xml
    python3 indexnow.py <url1> <url2> ...   # nur die genannten URLs
"""
import json
import sys
import re
import os
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
HOST = "www.erstehilfekurse.online"
KEY = "6ee5c1615ef2f434e5d82d4c72b80fef"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAP = os.path.join(ROOT, "..", "site", "sitemap.xml")


def urls_aus_sitemap():
    text = open(SITEMAP, encoding="utf-8").read()
    return re.findall(r"<loc>([^<]+)</loc>", text)


def main():
    urls = sys.argv[1:] or urls_aus_sitemap()
    if not urls:
        print("Keine URLs — nichts zu melden.")
        return
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=payload, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"IndexNow: {resp.status} — {len(urls)} URLs gemeldet.")
    except urllib.error.HTTPError as e:
        print(f"IndexNow-Fehler: HTTP {e.code} — {e.read().decode(errors='replace')[:300]}")
        raise
    except Exception as e:
        print(f"IndexNow-Fehler: {e}")
        raise


if __name__ == "__main__":
    main()
