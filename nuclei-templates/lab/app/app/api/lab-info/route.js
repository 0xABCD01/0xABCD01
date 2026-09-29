import fs from 'node:fs'
import path from 'node:path'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

// Versions are read from disk instead of require() so the bundler never tries
// to resolve node_modules packages at build time.
function pkgVersion(name) {
  try {
    const file = path.join(process.cwd(), 'node_modules', name, 'package.json')
    return JSON.parse(fs.readFileSync(file, 'utf8')).version
  } catch (err) {
    return null
  }
}

// The OG renderer (and the satori build inside it) ships bundled inside next,
// so its version is recovered from the compiled entry: the pnpm path comment
// records which satori build Next packed.
function ogBundleInfo() {
  const rel = 'node_modules/next/dist/compiled/@vercel/og/index.node.js'
  const info = { og: pkgVersion('@vercel/og'), satori: null, escaping: null }
  try {
    const text = fs.readFileSync(path.join(process.cwd(), rel), 'utf8')
    const satori = text.match(/satori@([0-9][0-9.]*)/)
    if (satori) info.satori = satori[1]
    // 16.3.6 adds a second escape-html usage on the text serialization path
    info.escaping = (text.match(/require_escape_html\(\)/g) || []).length >= 2 ? 'html-escaped (patched)' : 'un-escaped (vulnerable)'
  } catch (err) {
    /* reported as null */
  }
  return info
}

export async function GET() {
  const info = {
    app: 'cve-2026-94545-lab',
    node: process.version,
    runtime: 'nodejs',
    rss: process.memoryUsage().rss,
    next: pkgVersion('next'),
    react: pkgVersion('react'),
    sharp: pkgVersion('sharp')
  }
  Object.assign(info, ogBundleInfo())

  try {
    const sharp = (await import('sharp')).default
    const versions = sharp?.versions || {}
    info.libvips = versions.vips ?? null
    info.librsvg = versions.rsvg ?? null
    info.libxml2 = versions.xml2 ?? versions.xml ?? null
    info.nativeVersions = versions
  } catch (err) {
    info.sharpError = String(err && err.message ? err.message : err)
  }

  return Response.json(info, { headers: { 'cache-control': 'no-store' } })
}
