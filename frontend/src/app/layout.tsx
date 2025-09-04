import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/lib/auth/AuthProvider'
import { QueryProvider } from '@/lib/providers/QueryProvider'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Klymate AI - Intelligent Climate Platform',
  description: 'AI-powered climate coaching and carbon footprint tracking platform',
  keywords: ['climate', 'AI', 'carbon footprint', 'sustainability', 'coaching'],
  authors: [{ name: 'Klymate AI Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#10b981',
  openGraph: {
    title: 'Klymate AI - Intelligent Climate Platform',
    description: 'AI-powered climate coaching and carbon footprint tracking platform',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Klymate AI - Intelligent Climate Platform',
    description: 'AI-powered climate coaching and carbon footprint tracking platform',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full antialiased`}>
        <QueryProvider>
          <AuthProvider>
            {children}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  style: {
                    background: '#10b981',
                  },
                },
                error: {
                  style: {
                    background: '#ef4444',
                  },
                },
              }}
            />
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  )
}