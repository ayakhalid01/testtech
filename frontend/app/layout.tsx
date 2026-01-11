import '../styles/globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'
import { FaHome, FaBriefcase, FaCog, FaList, FaShareAlt, FaClock, FaChartBar } from 'react-icons/fa'

export const metadata: Metadata = {
  title: 'TechFlow - Job Scraper Dashboard',
  description: 'Automated job scraping from Wuzzuf and Indeed Egypt',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <nav className="bg-gradient-to-r from-[#2D9763] to-[#247a50] text-white shadow-lg">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">TechFlow Scraper</h1>
              <div className="flex gap-6">
                <Link href="/" className="flex items-center gap-2 hover:text-gray-200 transition-colors">
                  <FaHome /> Dashboard
                </Link>
                <Link href="/jobs" className="flex items-center gap-2 hover:text-gray-200 transition-colors">
                  <FaBriefcase /> Jobs
                </Link>
                <Link href="/analytics" className="flex items-center gap-2 hover:text-gray-200 transition-colors">
                  <FaChartBar /> Analytics
                </Link>
                <Link href="/share" className="flex items-center gap-2 hover:text-gray-200 transition-colors">
                  <FaShareAlt /> Share
                </Link>
                <Link href="/schedule" className="flex items-center gap-2 hover:text-gray-200 transition-colors">
                  <FaClock /> Schedule
                </Link>
                <Link href="/settings" className="flex items-center gap-2 hover:text-gray-200 transition-colors">
                  <FaCog /> Settings
                </Link>
                <Link href="/logs" className="flex items-center gap-2 hover:text-gray-200 transition-colors">
                  <FaList /> Logs
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  )
}
