#!/usr/bin/env bash
# Fails if version.json build, index.html BUILD and engine.js?v= differ.
set -e; cd "$(dirname "$0")/.."
v=$(python3 -c "import json;print(json.load(open('version.json'))['build'])")
b=$(grep -o "const BUILD='[0-9]*'" index.html | grep -o '[0-9]\+')
e=$(grep -o 'engine.js?v=[0-9]*' index.html | grep -o '[0-9]\+$')
echo "version.json=$v BUILD=$b engine.js?v=$e"
[ -n "$v" ] && [ "$v" = "$b" ] && [ "$b" = "$e" ] || { echo "BUILD MISMATCH"; exit 1; }
echo OK
