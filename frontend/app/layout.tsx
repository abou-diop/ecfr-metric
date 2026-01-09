import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ECFR Metrics Dashboard',
  description: 'Analyze and visualize Electronic Code of Federal Regulations metrics',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
