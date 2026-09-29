import { ImageResponse } from 'next/og'

// Sink: the request value is serialized straight into the SVG <title> element.
// Node runtime + sharp => native libvips/librsvg/libxml2 pipeline (vulnerable).
export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

async function render(request) {
  const url = new URL(request.url)
  const value = request.method === 'POST'
    ? await request.text()
    : (url.searchParams.get('value') ?? '')
  return new ImageResponse(
    <svg width="1200" height="630"><title>{value}</title></svg>,
    { width: 1200, height: 630 }
  )
}

export const GET = render
export const POST = render
