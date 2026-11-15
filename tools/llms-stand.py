#!/usr/bin/env python3
"""Setzt die Stand-Zeile in llms.txt und llms-full.txt maschinell.
Regel: Hat sich der Inhalt (ohne die Stand-Zeile) gegenüber HEAD geändert, steht heute drin; sonst bleibt die Zeile unverändert. Aufruf vor dem Commit: python3 tools/llms-stand.py [--dry]"""
import datetime, re, subprocess, sys
MON = ["Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.", "Sep.", "Okt.", "Nov.", "Dez."]
ZEILE = re.compile(r"^Stand: .*? \(letzte inhaltliche Änderung\)$", re.M)
def de(d): return f"{d.day}. {MON[d.month - 1]} {d.year}"
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout
dry = "--dry" in sys.argv
for f in ("llms.txt", "llms-full.txt"):
    t = open(f, encoding="utf-8").read()
    assert len(ZEILE.findall(t)) == 1, f
    kopf = ZEILE.sub("", t)
    alt = sh("git", "show", f"HEAD:{f}")
    geaendert = ZEILE.sub("", alt) != kopf
    if geaendert: d = datetime.date.today()
    else: d = None   # Inhalt unverändert: bestehende Stand-Zeile bleibt (sonst würde jeder Stand-Commit das Datum verschieben)
    neu = ZEILE.sub(f"Stand: {de(d)} (letzte inhaltliche Änderung)", t) if d else t
    print(f, "Inhalt geändert" if geaendert else "Inhalt unverändert", "->", de(d) if d else "bleibt", "(Änderung)" if neu != t else "(gleich)")
    if not dry and neu != t: open(f, "w", encoding="utf-8").write(neu)
