import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Drone Delivery System',
  description: 'Parrot Anafi 드론 배송 시스템',
  manifest: '/manifest.json',
  themeColor: '#2962FF',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
      </head>
      <body>{children}</body>
    </html>
  )
}
