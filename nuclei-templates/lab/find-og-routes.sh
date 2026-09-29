#!/usr/bin/env bash
# Find the OG image route of each target and aggregate a `paths` value for the
# templates.
#
# Two sources, because neither is complete on its own:
#   1. the front page - Next.js publishes the route in the og:image /
#      twitter:image meta tags, and the App Router flight payload repeats it
#   2. a direct probe of the usual suspects (/api/og, /og, ...) answered with
#      200 and an image content type
#
# Usage:
#   ./find-og-routes.sh -l targets.txt
#   ./find-og-routes.sh https://a.example https://b.example
#   ./find-og-routes.sh -l targets.txt --json routes.json --print-urls good.txt
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIST=""
JSON_OUT=""
URLS_OUT=""
TARGETS=()
MAX_TARGETS=500
TIMEOUT=10
SCHEME=""
PROBE_PATHS="/api/og,/og,/api/og-image,/api/twitter-image,/opengraph-image,/twitter-image,/api/image,/og-image"

while [ $# -gt 0 ]; do
  case "$1" in
    -l|--list)       LIST="${2:?--list needs a file}"; shift 2 ;;
    --json)          JSON_OUT="${2:?--json needs a path}"; shift 2 ;;
    --print-urls)    URLS_OUT="${2:?--print-urls needs a path}"; shift 2 ;;
    --probe-paths)   PROBE_PATHS="${2:?}"; shift 2 ;;
    --max)           MAX_TARGETS="${2:?}"; shift 2 ;;
    --timeout)       TIMEOUT="${2:?}"; shift 2 ;;
    --scheme)        SCHEME="${2:?}"; shift 2 ;;
    -h|--help)       sed -n '2,15p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)               TARGETS+=("$1"); shift ;;
  esac
done

if [ -n "$LIST" ]; then
  [ -f "$LIST" ] || { echo "no such file: $LIST" >&2; exit 1; }
  while IFS= read -r line; do
    [ -n "$line" ] && TARGETS+=("$line")
  done < "$LIST"
fi
[ "${#TARGETS[@]}" -gt 0 ] || { echo "no targets given (-l file, or URLs as arguments)" >&2; exit 2; }
command -v curl >/dev/null 2>&1 || { echo "curl is required" >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
CONFIRMED="$WORK/confirmed"   # per target: "<target> <route>"
MENTIONED="$WORK/mentioned"   # per target: "<target> <route>"
: > "$CONFIRMED"; : > "$MENTIONED"

looks_dynamic() {
  case "$1" in
    *.png|*.jpg|*.jpeg|*.webp|*.gif|*.avif|*.ico|*.svg) return 1 ;;
  esac
  printf '%s' "$1" | grep -qiE 'og|opengraph|twitter|image|render|card'
}

mentioned_routes() { # stdin: HTML -> candidate paths
  # read once: the two greps below must not compete for the same pipe (the
  # second one would see EOF)
  local page
  page="$(cat)"
  printf '%s' "$page" | grep -oiE '<meta[^>]+(og:image|twitter:image)[^>]*>' 2>/dev/null |
    grep -oiE 'content="[^"]+"' | sed 's/^content="//; s/"$//' |
    while IFS= read -r url; do
      path="${url#*://}"; case "$path" in *//*) continue ;; esac
      path="/${path#*/}"; path="${path%%\?*}"
      [ "${#path}" -gt 60 ] && continue
      looks_dynamic "$path" && printf '%s\n' "$path"
    done
  # no trailing quote in the pattern: the flight payload carries escaped quotes
  # (\"/api/og\"), which a strict "..." match would miss
  printf '%s' "$page" | grep -oE '"/(api/)?(og|og-image|opengraph-image|twitter-image|image|card)[a-z0-9/_.-]*' 2>/dev/null |
    tr -d '"' | sort -u
}

probe() { # base url + path -> "status content-type"
  curl -sS -m "$TIMEOUT" -o /dev/null -w '%{http_code} %{content_type}' \
    "${1}${2}?value=nuclei" 2>/dev/null || echo "000 -"
}

echo "target                                     confirmed route(s)"
echo "-------------------------------------------------------------------------------"
found_any=0
for target in "${TARGETS[@]:0:$MAX_TARGETS}"; do
  case "$target" in
    http://*|https://*) bases=("$target") ;;
    *) if [ -n "$SCHEME" ]; then bases=("$SCHEME://$target"); else bases=("https://$target" "http://$target"); fi ;;
  esac

  base=""
  html=""
  for u in "${bases[@]}"; do
    html="$(curl -sSLk -m "$TIMEOUT" -A 'Mozilla/5.0 (compatible; og-route-finder)' "$u" 2>/dev/null)" && [ -n "$html" ] && { base="$u"; break; }
  done

  candidates=""
  if [ -n "$html" ]; then
    mentioned="$(printf '%s' "$html" | mentioned_routes | grep -E '^/' | sort -u | head -6)"
    [ -n "$mentioned" ] && printf '%s %s\n' "$target" "$(printf '%s' "$mentioned" | paste -sd, -)" >> "$MENTIONED"
    candidates="$mentioned"
  else
    printf '%-42s %s\n' "$target" 'no response on https or http'
    continue
  fi

  # probe: extracted routes first, then the common names not already covered
  all="$( { printf '%s\n' "$candidates"; printf '%s\n' "$PROBE_PATHS" | tr ',' '\n'; } | grep -E '^/' | sort -u | head -12)"
  confirmed=""
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    read -r status ctype <<<"$(probe "${base%/}" "$path")"
    if [ "$status" = "200" ] && printf '%s' "$ctype" | grep -q '^image/'; then
      confirmed="$confirmed$path\n"
    fi
  done <<< "$all"

  if [ -n "$confirmed" ]; then
    found_any=1
    routes="$(printf "$confirmed" | sed '/^$/d' | sort -u | paste -sd, -)"
    printf '%s %s\n' "$target" "$routes" >> "$CONFIRMED"
    printf '%-42s %s\n' "$target" "$routes"
    [ -n "$URLS_OUT" ] && printf '%s\n' "$target" >> "$URLS_OUT"
  else
    printf '%-42s %s\n' "$target" '(no OG route answers as an image)'
  fi
done

echo
if [ "$found_any" = "1" ]; then
  echo "most common routes in this list:"
  awk '{n=split($2,a,","); for(i=1;i<=n;i++) print a[i]}' "$CONFIRMED" | sort | uniq -c | sort -rn | head -10 | sed 's/^/  /'
  suggestion="$(awk '{n=split($2,a,","); for(i=1;i<=n;i++) print a[i]}' "$CONFIRMED" | sort | uniq -c | sort -rn | awk '$1 >= 2 {print $2}' | head -8 | paste -sd, -)"
  [ -z "$suggestion" ] && suggestion="$(awk '{n=split($2,a,","); for(i=1;i<=n;i++) print a[i]}' "$CONFIRMED" | sort | uniq -c | sort -rn | head -3 | awk '{print $2}' | paste -sd, -)"
  echo
  echo "use them like this (trim the list to keep scans fast):"
  echo "  nuclei -l targets.txt    -t CVE-2026-94545.yaml     -var paths=$suggestion -stats"
  echo "  nuclei -l reachable.txt  -t CVE-2026-94545-rce.yaml -var paths=$suggestion"
  echo
  echo "the exploit needs a route that reads the request body (POST); a route that"
  echo "only renders through ?value= is detectable but cannot carry the 25 KB payload."
else
  echo "no OG route answered - static images, a CDN in front, auth, or no ImageResponse."
fi

if [ -s "$MENTIONED" ]; then
  echo
  echo "mentioned in the HTML but not confirmed by the probe (worth a look with -var paths=...):"
  sed 's/^/  /' "$MENTIONED" | head -10
fi

if [ -n "$JSON_OUT" ]; then
  python3 - "$CONFIRMED" "$JSON_OUT" "${suggestion:-}" <<'PY'
import json, sys
src, dst, suggestion = sys.argv[1], sys.argv[2], sys.argv[3]
targets = {}
for line in open(src):
    target, _, routes = line.strip().partition(" ")
    targets.setdefault(target, [])
    targets[target].extend(r for r in routes.split(",") if r)
json.dump({"suggestion": suggestion, "targets": targets}, open(dst, "w"), indent=2)
print(f"\nwritten: {dst}")
PY
fi
