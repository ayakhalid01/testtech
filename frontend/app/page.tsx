'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { getStats, startScraping } from '@/lib/api'
import { FaBriefcase, FaRocket, FaCheck, FaPaperPlane } from 'react-icons/fa'

interface ScrapingLog {
  id: string
  timestamp: string
  level: string
  message: string
  metadata: any
}

export default function Home() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [scraping, setScraping] = useState(false)
  const [showLogs, setShowLogs] = useState(false)
  const [scrapingLogs, setScrapingLogs] = useState<ScrapingLog[]>([])
  
  const [config, setConfig] = useState({
    max_jobs: 6,
    sources: ['wuzzuf', 'indeed'],
    upload_to_blogger: false,
    send_to_telegram: false,
    send_to_whatsapp: false,
    use_tinyurl: true,
    use_selenium_skills: false
  })

  useEffect(() => {
    loadStats()
    
    // Subscribe to real-time updates for stats
    const statsSubscription = supabase
      .channel('jobs-channel')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'jobs' }, () => {
        loadStats()
      })
      .subscribe()

    // Subscribe to real-time logs when scraping
    const logsSubscription = supabase
      .channel('logs-channel')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'scraping_logs' }, (payload) => {
        if (scraping) {
          setScrapingLogs(prev => [...prev, payload.new as ScrapingLog])
        }
      })
      .subscribe()

    return () => {
      statsSubscription.unsubscribe()
      logsSubscription.unsubscribe()
    }
  }, [scraping])

  const loadStats = async () => {
    try {
      const data = await getStats()
      setStats(data)
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const handleStartScraping = async () => {
    setScraping(true)
    setShowLogs(true)
    setScrapingLogs([])
    
    try {
      const result = await startScraping(config)
      
      // Add success log
      setScrapingLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        level: 'info',
        message: result.message,
        metadata: {}
      }])
      
    } catch (error: any) {
      // Add error log
      setScrapingLogs(prev => [...prev, {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        level: 'error',
        message: 'Error: ' + (error.response?.data?.detail || error.message),
        metadata: {}
      }])
    } finally {
      setTimeout(() => {
        setScraping(false)
        loadStats()
      }, 2000)
    }
  }

  const toggleSource = (source: string) => {
    setConfig(prev => ({
      ...prev,
      sources: prev.sources.includes(source)
        ? prev.sources.filter(s => s !== source)
        : [...prev.sources, source]
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-primary">TechFlow Job Scraper</h1>
          <p className="text-gray-600 mt-1">Automated job scraping from Wuzzuf and Indeed Egypt</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Jobs</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.total_jobs || 0}</p>
              </div>
              <FaBriefcase className="text-4xl text-primary opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Wuzzuf Jobs</p>
                <p className="text-3xl font-bold text-blue-600">{stats?.wuzzuf_jobs || 0}</p>
              </div>
              <FaBriefcase className="text-4xl text-blue-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Indeed Jobs</p>
                <p className="text-3xl font-bold text-orange-600">{stats?.indeed_jobs || 0}</p>
              </div>
              <FaBriefcase className="text-4xl text-orange-600 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Posted to Blogger</p>
                <p className="text-3xl font-bold text-green-600">{stats?.posted_to_blogger || 0}</p>
              </div>
              <FaCheck className="text-4xl text-green-600 opacity-20" />
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Control Panel</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Jobs to Scrape
                </label>
                <input
                  type="number"
                  value={config.max_jobs}
                  onChange={(e) => setConfig({...config, max_jobs: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  min="1"
                  max="50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Sources
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.sources.includes('wuzzuf')}
                      onChange={() => toggleSource('wuzzuf')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <span className="ml-2 text-gray-700">Wuzzuf</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.sources.includes('indeed')}
                      onChange={() => toggleSource('indeed')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <span className="ml-2 text-gray-700">Indeed Egypt</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Actions
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.upload_to_blogger}
                      onChange={(e) => setConfig({...config, upload_to_blogger: e.target.checked})}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <span className="ml-2 text-gray-700">Upload to Blogger</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.send_to_telegram}
                      onChange={(e) => setConfig({...config, send_to_telegram: e.target.checked})}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <span className="ml-2 text-gray-700">Send to Telegram</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.send_to_whatsapp}
                      onChange={(e) => setConfig({...config, send_to_whatsapp: e.target.checked})}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <span className="ml-2 text-gray-700">Send to WhatsApp</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.use_tinyurl}
                      onChange={(e) => setConfig({...config, use_tinyurl: e.target.checked})}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <span className="ml-2 text-gray-700">Use TinyURL</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={config.use_selenium_skills}
                      onChange={(e) => setConfig({...config, use_selenium_skills: e.target.checked})}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <span className="ml-2 text-gray-700">Use Selenium for Skills</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6">
            <button
              onClick={handleStartScraping}
              disabled={scraping || config.sources.length === 0}
              className="w-full bg-primary hover:bg-secondary text-white font-bold py-3 px-6 rounded-lg transition duration-200 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {scraping ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Scraping...</span>
                </>
              ) : (
                <>
                  <FaRocket />
                  <span>Start Scraping Now</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <a
            href="/jobs"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition duration-200"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-2">View Jobs</h3>
            <p className="text-gray-600 text-sm">Browse all scraped jobs</p>
          </a>

          <a
            href="/settings"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition duration-200"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-2">Settings</h3>
            <p className="text-gray-600 text-sm">Configure API keys and preferences</p>
          </a>

          <a
            href="/logs"
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition duration-200"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-2">Logs</h3>
            <p className="text-gray-600 text-sm">View scraping logs and history</p>
          </a>
        </div>
      </main>

      {/* Scraping Logs Modal */}
      {showLogs && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] flex flex-col">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-2xl font-bold text-gray-900">
                {scraping ? '🔄 Scraping in Progress...' : '✅ Scraping Complete'}
              </h3>
              <button
                onClick={() => setShowLogs(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
              <div className="space-y-3">
                {scrapingLogs.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-gray-600">Initializing scraper...</p>
                  </div>
                ) : (
                  scrapingLogs.map((log, index) => (
                    <div
                      key={log.id || index}
                      className={`p-4 rounded-lg border-l-4 ${
                        log.level === 'error'
                          ? 'bg-red-50 border-red-500'
                          : log.level === 'warning'
                          ? 'bg-yellow-50 border-yellow-500'
                          : 'bg-blue-50 border-blue-500'
                      }`}
                    >
                      <div className="flex items-start">
                        <span className={`px-2 py-1 rounded text-xs font-semibold mr-3 ${
                          log.level === 'error'
                            ? 'bg-red-100 text-red-800'
                            : log.level === 'warning'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {log.level.toUpperCase()}
                        </span>
                        <div className="flex-1">
                          <p className="text-sm text-gray-900 font-medium">{log.message}</p>
                          {log.metadata && Object.keys(log.metadata).length > 0 && (
                            <pre className="mt-2 text-xs text-gray-600 overflow-x-auto">
                              {JSON.stringify(log.metadata, null, 2)}
                            </pre>
                          )}
                        </div>
                        <span className="text-xs text-gray-500 ml-3">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {scraping && (
                <div className="mt-6 text-center">
                  <div className="inline-flex items-center space-x-2 bg-primary text-white px-6 py-3 rounded-lg">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span className="font-semibold">Processing jobs...</span>
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-100">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  {scrapingLogs.length} log entries
                </div>
                <button
                  onClick={() => {
                    setShowLogs(false)
                    setScrapingLogs([])
                  }}
                  className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-lg transition duration-200"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
