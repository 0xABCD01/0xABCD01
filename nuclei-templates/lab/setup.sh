#!/usr/bin/env bash
# Build the local CVE-2026-94545 test lab: Node 24.20.0 runtime + two copies of
# the next/og app (vulnerable 16.3.5, patched 16.3.6) + harness dependencies.
#
# Needs: bash, curl, tar, npm (any recent node) on PATH.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_VERSION="24.20.0"
NODE_TARBALL="https://registry.npmjs.org/node-linux-x64/-/node-linux-x64-${NODE_VERSION}.tgz"
VULN_NEXT="16.3.5"
PATCHED_NEXT="16.3.6"
RUNTIME="$LAB_DIR/.runtime/node"

log() { printf '\033[1;34m[setup]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[setup] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- node runtime
if [ -x "$RUNTIME/bin/node" ]; then
  log "node runtime present: $("$RUNTIME/bin/node" --version)"
else
  log "fetching official Node ${NODE_VERSION} linux-x64 from the npm registry"
  mkdir -p "$LAB_DIR/.runtime"
  tmp="$(mktemp -d)"
  curl -fsSL -o "$tmp/node.tgz" "$NODE_TARBALL" || die "download failed: $NODE_TARBALL"
  tar -xzf "$tmp/node.tgz" -C "$tmp"
  rm -rf "$RUNTIME"
  mv "$tmp/package" "$RUNTIME"
  rm -rf "$tmp"
fi

NODE_BIN="$RUNTIME/bin/node"
NODE_ACTUAL="$("$NODE_BIN" --version)"
[ "$NODE_ACTUAL" = "v${NODE_VERSION}" ] || die "runtime is $NODE_ACTUAL, expected v${NODE_VERSION}"

# The ROP chain inside the template is pinned to the offsets of this exact
# build; a PIE binary would invalidate every gadget address.
if command -v python3 >/dev/null 2>&1; then
  etype="$(python3 -c "
import struct, sys
with open(sys.argv[1], 'rb') as fh:
    head = fh.read(64)
print(struct.unpack('<H', head[16:18])[0])
" "$NODE_BIN")"
  [ "$etype" = "2" ] || die "node binary is not ET_EXEC (non-PIE); got e_type=$etype"
  log "node binary verified: ET_EXEC (non-PIE), $(( $(wc -c < "$NODE_BIN") )) bytes"
else
  log "python3 not found - skipping the non-PIE check"
fi

# ---------------------------------------------------------------- applications
command -v npm >/dev/null 2>&1 || die "npm not found on PATH (needed to install the app dependencies)"

build_variant() {
  local name="$1" next_version="$2" dir="$LAB_DIR/run/$1"

  # Re-sync the app sources every time so edits under lab/app always land in the
  # built variants (setup.sh is the only thing that writes to run/).
  local rebuild=0
  if [ ! -d "$dir/node_modules" ] || ! diff -r -q --exclude=node_modules --exclude=.next "$LAB_DIR/app" "$dir" >/dev/null 2>&1; then
    rebuild=1
  fi

  if [ "$rebuild" = "0" ]; then
    log "variant '$name' (next $next_version) is up to date"
    return 0
  fi

  log "building variant '$name' (next $next_version) in lab/run/$name"
  rm -rf "$dir"
  mkdir -p "$LAB_DIR/run"
  cp -r "$LAB_DIR/app" "$dir"
  sed -i.bak "s/\"next\": \"[^\"]*\"/\"next\": \"$next_version\"/" "$dir/package.json"
  rm -f "$dir/package.json.bak"

  ( cd "$dir" \
    && npm install --no-audit --no-fund --silent \
    && NEXT_TELEMETRY_DISABLED=1 "$NODE_BIN" ./node_modules/next/dist/bin/next build >/dev/null )
}

build_variant vulnerable "$VULN_NEXT"
build_variant patched "$PATCHED_NEXT"

# ---------------------------------------------------------------- harness deps
if [ ! -d "$LAB_DIR/tools/node_modules/yaml" ]; then
  log "installing harness dependencies (yaml)"
  ( cd "$LAB_DIR/tools" && npm install --no-audit --no-fund --silent )
fi

# ---------------------------------------------------------------- version report
log "installed stack:"
for variant in vulnerable patched; do
  ( cd "$LAB_DIR/run/$variant" && VARIANT="$variant" "$NODE_BIN" -e '
      const fs = require("fs"), path = require("path");
      const read = (name) => JSON.parse(fs.readFileSync(path.join("node_modules", name, "package.json"), "utf8")).version;
      const sharp = require("sharp");
      const v = sharp.versions || {};
      console.log("  " + process.env.VARIANT.padEnd(11) +
        " next=" + read("next") +
        " satori=" + (() => {
          try {
            const m = fs.readFileSync("node_modules/next/dist/compiled/@vercel/og/index.node.js", "utf8").match(/satori@([0-9][0-9.]*)/);
            if (m) return m[1];
          } catch (e) {}
          return "?";
        })() +
        " sharp=" + read("sharp") +
        " libvips=" + (v.vips || "?") +
        " librsvg=" + (v.rsvg || "?") +
        " libxml2=" + (v.xml2 || v.xml || "?") +
        " node=" + process.version);
  ' )
done

cat <<EOF

Lab built.

  ./start.sh        start vulnerable (:3000), patched (:3001) and the OOB listener
  ./run-tests.sh    run both nuclei templates against both builds
  ./stop.sh         stop everything

EOF
