#!/usr/bin/env node
// One-shot HTTP request used by nuclei-shim.mjs.
//
// The nuclei JavaScript protocol blocks inside http.Client calls while Go does
// the I/O; Node cannot block, so the shim runs this file through spawnSync and
// reads the result back synchronously.
//
// stdin : JSON { method, url, headers, body, timeoutMs }
// stdout: JSON { ok, status, contentType, headers, bodyFile, bytes, error }
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

async function main() {
  const chunks = []
  for await (const chunk of process.stdin) chunks.push(chunk)
  const req = JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}')

  const bodyFile = path.join(os.tmpdir(), `shim-body-${process.pid}-${Date.now()}.bin`)
  const result = { ok: false, status: 0, contentType: '', headers: {}, bodyFile, bytes: 0, error: '' }

  try {
    const init = {
      method: req.method || 'GET',
      headers: req.headers || {},
      redirect: 'follow',
      signal: AbortSignal.timeout(req.timeoutMs || 60000)
    }
    if (req.body !== undefined && req.body !== null && init.method !== 'GET') {
      init.body = req.body
    }

    const response = await fetch(req.url, init)
    const buffer = Buffer.from(await response.arrayBuffer())
    fs.writeFileSync(bodyFile, buffer)

    result.ok = true
    result.status = response.status
    result.contentType = response.headers.get('content-type') || ''
    result.headers = Object.fromEntries(response.headers.entries())
    result.bytes = buffer.length
  } catch (err) {
    result.error = String(err && err.message ? err.message : err)
    fs.writeFileSync(bodyFile, Buffer.alloc(0))
  }

  process.stdout.write(JSON.stringify(result))
}

main()
