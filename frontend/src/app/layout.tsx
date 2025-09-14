import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/lib/auth/AuthProvider'
import { QueryProvider } from '@/lib/providers/QueryProvider'
import { ThemeProvider } from '@/lib/theme/ThemeProvider'
import AppNavigation from '@/components/navigation/AppNavigation'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Klymate AI - Intelligent Climate Platform',
  description: 'AI-powered climate coaching and carbon footprint tracking platform',
  keywords: ['climate', 'AI', 'carbon footprint', 'sustainability', 'coaching'],
  authors: [{ name: 'Klymate AI Team' }],
  metadataBase: new URL('http://localhost:3000'),
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
            <ThemeProvider>
              {children}
              <AppNavigation />
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
                      background: 'var(--color-primary)',
                    },
                  },
                  error: {
                    style: {
                      background: '#ef4444',
                    },
                  },
                }}
              />
            </ThemeProvider>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  )
}