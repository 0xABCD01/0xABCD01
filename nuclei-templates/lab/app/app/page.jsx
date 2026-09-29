export const dynamic = 'force-dynamic'

const endpoints = [
  ['POST /api/og', 'body text becomes the SVG <title>', 'the sink used by both templates'],
  ['GET /api/og?value=', 'query value becomes the SVG <title>', 'second request shape'],
  ['GET /api/lab-info', 'version metadata of this instance', 'confirm next/satori/libvips'],
  ['/lab', 'interactive console', 'paste a payload, see the PNG size']
]

export default function Page() {
  return (
    <main style={{ fontFamily: 'ui-sans-serif,system-ui,sans-serif', maxWidth: 860, margin: '60px auto', padding: '0 24px', lineHeight: 1.6 }}>
      <p style={{ letterSpacing: 2, fontSize: 12, color: '#888', margin: 0 }}>LOCAL TEST TARGET</p>
      <h1 style={{ margin: '6px 0 4px' }}>CVE-2026-94545 lab instance</h1>
      <p style={{ marginTop: 0, color: '#555' }}>
        Next.js <code>next/og</code> Satori SVG injection → native librsvg/libxml2 memory corruption → RCE.
        This server is the <em>affected product</em> used by the nuclei templates in the parent directory.
      </p>

      <h2 style={{ fontSize: 18, marginTop: 34 }}>Endpoints</h2>
      <table style={{ borderCollapse: 'collapse' }}>
        <tbody>
          {endpoints.map(([route, what, why]) => (
            <tr key={route}>
              <td style={{ padding: '6px 16px 6px 0', verticalAlign: 'top' }}><code>{route}</code></td>
              <td style={{ padding: '6px 16px 6px 0', verticalAlign: 'top', color: '#555' }}>{what}</td>
              <td style={{ padding: '6px 0', verticalAlign: 'top', color: '#999' }}>{why}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 style={{ fontSize: 18, marginTop: 34 }}>Quick check from a shell</h2>
      <pre style={{ background: '#f5f5f5', padding: 14, borderRadius: 6, overflowX: 'auto' }}>
{`# what build is this?
curl -s http://127.0.0.1:3000/api/lab-info | python3 -m json.tool

# the innocent request shape both templates use
curl -s -o /dev/null -w 'HTTP %{http_code}  %{size_download} bytes\\n' \\
  "http://127.0.0.1:3000/api/og?value=hello"`}
      </pre>

      <p style={{ color: '#777', fontSize: 14 }}>
        Run the automated template checks with <code>lab/run-tests.sh</code>; open the{' '}
        <a href="/lab">test console</a> to drive <code>/api/og</code> from the browser.
      </p>
    </main>
  )
}
