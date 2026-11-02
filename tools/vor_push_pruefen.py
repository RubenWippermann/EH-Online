#!/usr/bin/env python3
"""Sperre gegen Generator-Vollbau-Ausgabe im Push-Weg (siehe tools/vollbau-nie-live.md).
Vergleicht HEAD mit dem Live-Stand (origin/main bzw. ersten Argument) und bricht ab (Rueckgabewert 1), wenn
 a) mehr als MAX_DATEIEN Dateien geaendert sind (Standard 400; mit EHO_BULK_OK=<Grund> freigegeben, z. B. fuer live_aufraeumen.py), oder
 b) eine geaenderte Seite eine Live-Kennung verloren hat, die nur der Live-Stand traegt (Generator kennt sie nicht).
Aufruf (Repo-Wurzel):  python3 tools/vor_push_pruefen.py [live-ref]"""
import os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
MAX_DATEIEN = 400
KENNUNGEN = ['document.documentElement.className+=" js"']   # Live-Kennung, die der Generator-Vollbau nicht ausgibt (gemessen 02.11.)


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, check=True).stdout


dateien = git("diff", "--name-only", f"{ref}..HEAD").split("\n")
dateien = [d for d in dateien if d]
fehler = []
if len(dateien) > MAX_DATEIEN and not os.environ.get("EHO_BULK_OK"):
    fehler.append(f"{len(dateien)} geaenderte Dateien > {MAX_DATEIEN}: wirkt wie ein Vollbau/Massenlauf. Mit EHO_BULK_OK=<Grund> nur freigeben, wenn ein Skript mit Zaehlung dahinter steht (z. B. tools/live_aufraeumen.py).")
if not fehler:
    # alle alten Fassungen in einem Aufruf lesen (git cat-file --batch), nicht pro Datei ein Prozess
    seiten = [d for d in dateien if d.endswith("index.html")]
    p = subprocess.Popen(["git", "-C", ROOT, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    ein = "".join(f"{ref}:{d}\n" for d in seiten).encode()
    out, _ = p.communicate(ein)
    pos = 0
    for d in seiten:
        ende = out.index(b"\n", pos)
        kopf = out[pos:ende].split()
        if len(kopf) == 2 and kopf[1] == b"missing":
            pos = ende + 1
            continue
        n = int(kopf[2])
        alt = out[ende + 1:ende + 1 + n].decode("utf-8", "ignore")[:12000]
        pos = ende + 1 + n + 1
        neu = open(os.path.join(ROOT, d), encoding="utf-8", errors="ignore").read()[:12000]
        for k in KENNUNGEN:
            if k in alt and k not in neu:
                fehler.append(f"{d}: Live-Kennung verloren: {k}")
                break
        if len(fehler) > 20:
            break
if fehler:
    print("PUSH-SPERRE:\n  " + "\n  ".join(fehler[:20]))
    sys.exit(1)
print(f"ok: {len(dateien)} Dateien gegen {ref} geprueft, keine verlorene Live-Kennung")
