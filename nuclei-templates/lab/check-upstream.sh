#!/usr/bin/env bash
# Verify that lab/app still behaves like the app published in
# https://github.com/EQSTLab/CVE-2026-94545 (the advisory's victim app).
#
# Compares the pieces that decide whether the templates apply:
#   * dependency versions (next / react / sharp)
#   * the OG route: request shapes and what reaches the SVG <title>
#   * the Node runtime pin
#
# Comments and formatting are normalised away, so only real behaviour shows up
# as a difference.
#
# Usage:  ./check-upstream.sh [-r <repo-url>] [-f <local app dir>]
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="https://github.com/EQSTLab/CVE-2026-94545.git"
LOCAL_APP="$LAB_DIR/app"

while [ $# -gt 0 ]; do
  case "$1" in
    -r) REPO="${2:?}"; shift 2 ;;
    -f) LOCAL_APP="${2:?}"; shift 2 ;;
    -h|--help) sed -n '2,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

command -v git >/dev/null 2>&1 || { echo "git is required" >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "cloning $REPO"
git clone --depth 1 -q "$REPO" "$WORK/upstream" || { echo "clone failed" >&2; exit 1; }
UPSTREAM_APP="$WORK/upstream/app"
[ -d "$UPSTREAM_APP" ] || { echo "no app/ directory in the upstream repository" >&2; exit 1; }

echo "upstream files:"
( cd "$WORK/upstream" && find app -type f | sed 's/^/  /' )

echo
python3 - "$UPSTREAM_APP" "$LOCAL_APP" <<'PY'
import json, os, re, sys

upstream_app, local_app = sys.argv[1], sys.argv[2]
problems = []

# ---------------------------------------------------------------- dependencies
def deps(path):
    with open(path, encoding='utf-8') as fh:
        return json.load(fh).get('dependencies', {})

try:
    up = deps(os.path.join(upstream_app, 'package.json'))
    loc = deps(os.path.join(local_app, 'package.json'))
    print('dependency versions (upstream -> lab)')
    for name in sorted(set(up) | set(loc)):
        mark = 'ok ' if up.get(name) == loc.get(name) else 'DIFF'
        if mark == 'DIFF':
            problems.append(f'{name}: upstream {up.get(name)} vs lab {loc.get(name)}')
        print(f"  {mark} {name:12} {up.get(name, '-'):10} {loc.get(name, '-')}")
except Exception as exc:  # noqa: BLE001
    problems.append(f'could not compare package.json: {exc}')
    print(f'  package.json comparison failed: {exc}')

# ------------------------------------------------------------------- OG route
def find_route(root):
    for dirpath, _dirs, files in os.walk(root):
        if dirpath.endswith(os.path.join('api', 'og')):
            for name in files:
                if name.startswith('route.'):
                    return os.path.join(dirpath, name)
    return None

def normalise(path):
    text = open(path, encoding='utf-8').read()
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)      # block comments
    text = re.sub(r'^\s*//.*$', '', text, flags=re.M)      # line comments
    text = re.sub(r'\s+', ' ', text)                       # all whitespace
    return text.strip()

up_route, loc_route = find_route(upstream_app), find_route(local_app)
print()
print('OG route')
if not up_route:
    problems.append('no route file found upstream')
    print('  no route found upstream')
else:
    print(f'  upstream: {os.path.relpath(up_route, upstream_app)}')
    print(f'  lab:      {os.path.relpath(loc_route, local_app) if loc_route else "MISSING"}')

    up_norm = normalise(up_route)
    loc_norm = normalise(loc_route) if loc_route else ''

    def token(name, text):
        return name in text

    checks = [
        ("runtime pinned to nodejs", "runtime = 'nodejs'" in up_norm, "runtime = 'nodejs'" in loc_norm),
        ("dynamic force-dynamic", "dynamic = 'force-dynamic'" in up_norm, "dynamic = 'force-dynamic'" in loc_norm),
        ("GET and POST exported", "POST = render" in up_norm, "POST = render" in loc_norm),
        ("POST body is the title text", "request.text()" in up_norm, "request.text()" in loc_norm),
        ("GET ?value= is the title text", "searchParams.get('value')" in up_norm, "searchParams.get('value')" in loc_norm),
        ("value placed in SVG <title>", "<title>{value}</title>" in up_norm, "<title>{value}</title>" in loc_norm),
    ]
    for label, up_ok, loc_ok in checks:
        mark = 'ok ' if (up_ok == loc_ok) else 'DIFF'
        if mark == 'DIFF':
            problems.append(f'route: {label} (upstream {up_ok}, lab {loc_ok})')
        print(f'  {mark} {label:32} upstream={str(up_ok):5} lab={str(loc_ok)}')

print()
if problems:
    print('RESULT: differences found')
    for item in problems:
        print(f'  - {item}')
    sys.exit(1)
print('RESULT: lab/app matches the upstream victim app on everything that matters')
PY
