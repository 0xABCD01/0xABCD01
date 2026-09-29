export const metadata = {
  title: 'CVE-2026-94545 lab',
  description: 'Local Next.js next/og test target for the CVE-2026-94545 nuclei templates'
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
