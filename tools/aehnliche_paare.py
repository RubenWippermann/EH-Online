#!/usr/bin/env python3
"""Findet nahezu doppelte indexierbare Seiten (Hauptinhalt, Wort-4-Shingles, dann difflib.SequenceMatcher.ratio).
Aufruf: python3 tools/aehnliche_paare.py [Ordner ...] [--min 0.85]   (Standard: wissen ratgeber kurse branchen)
Nur Lesen; schreibt eine Liste nach stdout (Paar, Ratio, Woerter)."""
import glob, html, os, re, sys, difflib, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
args = sys.argv[1:]
mn = float(args[args.index("--min") + 1]) if "--min" in args else 0.85
dirs = [a for a in args if not a.startswith("--") and not re.fullmatch(r"[0-9.]+", a)] or ["wissen", "ratgeber", "kurse", "branchen"]
docs = {}
for d in dirs:
    for f in glob.glob(os.path.join(ROOT, d, "*", "index.html")):
        t = open(f, encoding="utf-8", errors="ignore").read()
        if "noindex" in t[:6000] or "http-equiv=\"refresh\"" in t[:3000]:
            continue
        m = re.search(r"<main.*?</main>", t, re.S)
        s = re.sub(r"<script.*?</script>|<style.*?</style>", "", m.group(0) if m else t, flags=re.S)
        w = html.unescape(re.sub(r"<[^>]+>", " ", s)).lower().split()
        if len(w) > 60:
            docs[os.path.relpath(f, ROOT)[:-len("/index.html")]] = w
sh = {k: {tuple(w[i:i + 4]) for i in range(len(w) - 3)} for k, w in docs.items()}
inv = collections.defaultdict(list)
for k, s in sh.items():
    for x in s:
        inv[x].append(k)
cand = collections.Counter()
for x, ks in inv.items():
    if 2 <= len(ks) <= 6:
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                cand[(ks[i], ks[j])] += 1
out = []
for (a, b), c in cand.items():
    jac = c / len(sh[a] | sh[b])
    if jac < 0.25:
        continue
    r = difflib.SequenceMatcher(None, " ".join(docs[a]), " ".join(docs[b]), autojunk=False).ratio()
    if r >= mn:
        out.append((r, a, b, len(docs[a]), len(docs[b])))
for r, a, b, la, lb in sorted(out, reverse=True):
    print(f"{r:.3f}  {a}  ~  {b}   ({la}/{lb} Wörter)")
print(f"-- {len(out)} Paare >= {mn} in {len(docs)} Seiten")
