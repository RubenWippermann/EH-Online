#!/usr/bin/env bash
# CSS-Quelle ist tools/styles.src.css (lesbar). assets/styles.css ist die minifizierte Auslieferung (esbuild, -6 KB gzip).
# Nach jeder CSS-Aenderung: in tools/styles.src.css aendern, dann dieses Skript ausfuehren. Aenderungen direkt in assets/styles.css gehen sonst verloren.
set -euo pipefail
cd "$(dirname "$0")/.."
esbuild tools/styles.src.css --minify --loader:.css=css --outfile=assets/styles.css
