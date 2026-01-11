'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { getLogs, stopScraping, getScrapingStatus } from '@/lib/api'
import { FaInfoCircle, FaExclamationTriangle, FaTimesCircle, FaFilter, FaTrash, FaStop } from 'react-icons/fa'
import Link from 'next/link'

interface Log {
  id: string
  timestamp: string
  level: 'info' | 'warning' | 'error'
  message: string
  metadata: any
}

export default function LogsPage() {
  const [logs, setLogs] = useState<Log[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'info' | 'warning' | 'error'>('all')
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [isRunning, setIsRunning] = useState(false)
  const [currentProgress, setCurrentProgress] = useState(0)

  useEffect(() => {
    loadLogs()
    checkScrapingStatus()

    // Subscribe to real-time updates
    const subscription = supabase
      .channel('logs-realtime')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'scraping_logs' }, (payload) => {
        const newLog = payload.new as Log
        setLogs(prev => [newLog, ...prev])
        
        // Extract progress from metadata
        if (newLog.metadata?.progress) {
          setCurrentProgress(newLog.metadata.progress)
        }
      })
      .subscribe()

    // Auto-refresh every 3 seconds
    let interval: NodeJS.Timeout
    if (autoRefresh) {
      interval = setInterval(() => {
        loadLogs()
        checkScrapingStatus()
      }, 3000)
    }

    return () => {
      subscription.unsubscribe()
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, filter])

  const checkScrapingStatus = async () => {
    try {
      const status = await getScrapingStatus()
      setIsRunning(status.is_active)
    } catch (error) {
      // Ignore errors
    }
  }

  const handleStopScraping = async () => {
    if (!confirm('⚠️ Are you sure you want to stop the current scraping process?')) {
      return
    }

    try {
      const result = await stopScraping()
      alert('✅ ' + result.message)
      setIsRunning(false)
      setCurrentProgress(0)
    } catch (error: any) {
      console.error('Error stopping scraping:', error)
      alert('❌ Error stopping scraping: ' + error.message)
    }
  }

  const loadLogs = async () => {
    try {
      setLoading(true)
      const params = filter !== 'all' ? { level: filter, limit: 200 } : { limit: 200 }
      const data = await getLogs(params)
      setLogs(data.logs || [])
    } catch (error) {
      console.error('Error loading logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const clearLogs = async () => {
    if (!confirm('Are you sure you want to clear all logs? This cannot be undone.')) return

    try {
      const { error } = await supabase
        .from('scraping_logs')
        .delete()
        .neq('id', '00000000-0000-0000-0000-000000000000') // Delete all

      if (error) throw error
      setLogs([])
      alert('All logs cleared successfully')
    } catch (error) {
      console.error('Error clearing logs:', error)
      alert('Failed to clear logs')
    }
  }

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'info':
        return <FaInfoCircle className="text-blue-500" />
      case 'warning':
        return <FaExclamationTriangle className="text-yellow-500" />
      case 'error':
        return <FaTimesCircle className="text-red-500" />
      default:
        return <FaInfoCircle className="text-gray-500" />
    }
  }

  const getLogBgColor = (level: string) => {
    switch (level) {
      case 'info':
        return 'bg-blue-50 border-l-4 border-blue-500'
      case 'warning':
        return 'bg-yellow-50 border-l-4 border-yellow-500'
      case 'error':
        return 'bg-red-50 border-l-4 border-red-500'
      default:
        return 'bg-gray-50 border-l-4 border-gray-500'
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <Link href="/" className="text-2xl font-bold text-primary hover:text-secondary">
            ← TechFlow
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-2">Scraping Logs</h1>
          <p className="text-gray-600 mt-1">View real-time scraping logs and history</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Progress Bar - Always show when scraping is active */}
        {isRunning && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6 border-l-4 border-primary">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-xl font-bold text-gray-800 flex items-center">
                  <span className="animate-pulse mr-2">🔄</span> Scraping In Progress
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {currentProgress > 0 
                    ? `Processing jobs... ${currentProgress}% complete`
                    : 'Initializing scraper...'
                  }
                </p>
              </div>
              <span className="text-3xl font-bold text-primary">{currentProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden shadow-inner">
              <div
                className="bg-gradient-to-r from-primary via-green-500 to-secondary h-6 transition-all duration-500 ease-out flex items-center justify-center text-white text-xs font-semibold"
                style={{ width: `${Math.max(currentProgress, 5)}%` }}
              >
                {currentProgress > 10 && `${currentProgress}%`}
              </div>
            </div>
            <button
              onClick={handleStopScraping}
              className="mt-4 w-full bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg flex items-center justify-center space-x-2 transition duration-200 font-semibold shadow-md hover:shadow-lg"
            >
              <FaStop /> <span>⛔ Stop Scraping Now</span>
            </button>
          </div>
        )}

        {/* Controls */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <FaFilter className="text-gray-600 mr-2" />
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value as any)}
                  className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="all">All Levels</option>
                  <option value="info">Info Only</option>
                  <option value="warning">Warnings Only</option>
                  <option value="error">Errors Only</option>
                </select>
              </div>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <span className="ml-2 text-gray-700">Auto-refresh (3s)</span>
              </label>

              <div className="text-sm text-gray-600">
                {logs.length} log{logs.length !== 1 ? 's' : ''}
              </div>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={loadLogs}
                className="bg-primary hover:bg-secondary text-white font-bold py-2 px-4 rounded-lg transition duration-200"
              >
                Refresh Now
              </button>
              <button
                onClick={clearLogs}
                className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition duration-200 flex items-center space-x-2"
              >
                <FaTrash />
                <span>Clear All</span>
              </button>
            </div>
          </div>
        </div>

        {/* Logs */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading logs...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <FaInfoCircle className="text-6xl text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No logs found</h3>
            <p className="text-gray-600">Start scraping to see logs appear here</p>
          </div>
        ) : (
          <div className="space-y-2">
            {logs.map((log) => (
              <div key={log.id} className={`${getLogBgColor(log.level)} rounded-lg p-4`}>
                <div className="flex items-start">
                  <div className="flex-shrink-0 mt-1">
                    {getLogIcon(log.level)}
                  </div>
                  <div className="ml-3 flex-1">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          log.level === 'info' 
                            ? 'bg-blue-100 text-blue-800' 
                            : log.level === 'warning'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {log.level.toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500">
                          {formatTime(log.timestamp)}
                        </span>
                      </div>
                    </div>
                    <p className="mt-2 text-sm text-gray-900 font-medium">
                      {log.message}
                    </p>
                    {log.metadata && Object.keys(log.metadata).length > 0 && (
                      <details className="mt-2">
                        <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-900">
                          View metadata
                        </summary>
                        <pre className="mt-2 text-xs bg-gray-900 text-green-400 p-3 rounded overflow-x-auto">
                          {JSON.stringify(log.metadata, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
