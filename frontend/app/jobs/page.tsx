'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { FaBriefcase, FaMapMarkerAlt, FaBuilding, FaExternalLinkAlt, FaTrash, FaEdit, FaRocket, FaTag } from 'react-icons/fa'
import Link from 'next/link'

interface Job {
  id: string
  title: string
  company: string
  location: string
  salary: string | null
  requirements: any
  skills: any
  description: string
  link: string
  source: string
  created_at: string
  posted_to_blogger: boolean
  sent_to_telegram: boolean
  sent_to_whatsapp: boolean
  blogger_url: string | null
  keyword?: string
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'wuzzuf' | 'indeed'>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  useEffect(() => {
    loadJobs()

    // Subscribe to real-time updates
    const subscription = supabase
      .channel('jobs-realtime')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'jobs' }, () => {
        loadJobs()
      })
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  const loadJobs = async () => {
    try {
      setLoading(true)
      let query = supabase
        .from('jobs')
        .select('*')
        .order('created_at', { ascending: false })

      if (filter !== 'all') {
        query = query.eq('source', filter)
      }

      const { data, error } = await query

      if (error) throw error
      setJobs(data || [])
    } catch (error) {
      console.error('Error loading jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const deleteJob = async (id: string) => {
    if (!confirm('Are you sure you want to delete this job?')) return

    try {
      const { error } = await supabase
        .from('jobs')
        .delete()
        .eq('id', id)

      if (error) throw error
      loadJobs()
    } catch (error) {
      console.error('Error deleting job:', error)
      alert('Failed to delete job')
    }
  }

  const filteredJobs = jobs.filter(job =>
    job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.location.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const totalPages = Math.ceil(filteredJobs.length / itemsPerPage)
  const paginatedJobs = filteredJobs.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
          <div>
            <Link href="/" className="text-2xl font-bold text-primary hover:text-secondary">
              ← TechFlow
            </Link>
            <h1 className="text-3xl font-bold text-gray-900 mt-2">Scraped Jobs</h1>
            <p className="text-gray-600 mt-1">Browse all scraped jobs from Wuzzuf and Indeed</p>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by title, company, or location..."
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Source Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source
              </label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="all">All Sources</option>
                <option value="wuzzuf">Wuzzuf Only</option>
                <option value="indeed">Indeed Only</option>
              </select>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            Showing {paginatedJobs.length} of {filteredJobs.length} jobs
          </div>
        </div>

        {/* Jobs List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading jobs...</p>
          </div>
        ) : paginatedJobs.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <FaBriefcase className="text-6xl text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600">Try adjusting your filters or start scraping new jobs</p>
            <Link
              href="/"
              className="inline-block mt-6 bg-primary hover:bg-secondary text-white font-bold py-2 px-6 rounded-lg transition duration-200"
            >
              Go to Dashboard
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {paginatedJobs.map((job) => (
              <div key={job.id} className="bg-white rounded-lg shadow hover:shadow-lg transition duration-200 p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">{job.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        job.source === 'wuzzuf' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        {job.source.toUpperCase()}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center">
                        <FaBuilding className="mr-2" />
                        {job.company}
                      </div>
                      <div className="flex items-center">
                        <FaMapMarkerAlt className="mr-2" />
                        {job.location}
                      </div>
                      {job.salary && (
                        <div className="font-semibold text-green-600">
                          {job.salary}
                        </div>
                      )}
                      <div className="text-gray-400">
                        {formatDate(job.created_at)}
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 text-xs">
                      {job.keyword && (
                        <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded flex items-center">
                          <FaTag className="mr-1" /> {job.keyword}
                        </span>
                      )}
                      {job.posted_to_blogger && (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                          ✓ Posted to Blogger
                        </span>
                      )}
                      {job.sent_to_telegram && (
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          ✓ Sent to Telegram
                        </span>
                      )}
                      {job.sent_to_whatsapp && (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                          ✓ Sent to WhatsApp
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col space-y-2 ml-4">
                    <a
                      href={job.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-primary hover:bg-secondary text-white px-4 py-2 rounded text-sm font-semibold flex items-center space-x-2 transition duration-200"
                    >
                      <span>View Job</span>
                      <FaExternalLinkAlt />
                    </a>
                    {job.blogger_url && (
                      <a
                        href={job.blogger_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold flex items-center space-x-2 transition duration-200"
                      >
                        <span>Blog Post</span>
                        <FaExternalLinkAlt />
                      </a>
                    )}
                    <button
                      onClick={() => deleteJob(job.id)}
                      className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded text-sm font-semibold flex items-center space-x-2 transition duration-200"
                    >
                      <FaTrash />
                      <span>Delete</span>
                    </button>
                  </div>
                </div>

                {job.description && (
                  <div className="mt-4 text-sm text-gray-600 line-clamp-2">
                    {job.description.substring(0, 200)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-8 flex justify-center items-center space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`px-4 py-2 border rounded-md ${
                  currentPage === page
                    ? 'bg-primary text-white border-primary'
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                {page}
              </button>
            ))}

            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
