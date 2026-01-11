'use client';

import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase';
import { updateTinyUrls } from '@/lib/api';
import { FaCopy, FaCheck, FaBriefcase, FaMapMarkerAlt, FaLink, FaSync } from 'react-icons/fa';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  requirements: string[];
  skills: string[];
  link: string;
  tiny_url: string;
  blogger_url: string;
  source: string;
  created_at: string;
  keyword?: string;
}

export default function SharePage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingUrls, setUpdatingUrls] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'wuzzuf' | 'indeed'>('all');

  const supabase = createClient();

  useEffect(() => {
    fetchJobs();
  }, [filter]);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      let query = supabase
        .from('jobs')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50);

      if (filter !== 'all') {
        query = query.eq('source', filter);
      }

      const { data, error } = await query;

      if (error) throw error;
      setJobs(data || []);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatJobText = (job: Job) => {
    const parts = [];
    
    // Title
    parts.push(`*${job.title}*`);
    parts.push('');
    
    // Location
    parts.push(`📍 *Location:* ${job.location}`);
    parts.push('');
    
    // Requirements or Skills
    if (job.requirements && job.requirements.length > 0) {
      parts.push('*Requirements:*');
      job.requirements.forEach((req: string) => {
        const cleanReq = req.replace('🔹 ', '').trim();
        parts.push(`🔹 ${cleanReq}`);
      });
      parts.push('');
    } else if (job.skills && job.skills.length > 0) {
      parts.push('*Skills:*');
      job.skills.forEach((skill: string) => {
        parts.push(`🔹 ${skill}`);
      });
      parts.push('');
    }
    
    // Apply link - use tiny_url if available (always has TinyURL now)
    // Falls back to blogger_url or original link if tiny_url not available
    const applyLink = job.tiny_url || job.blogger_url || job.link;
    
    parts.push(`🔗 *Apply Here:* ${applyLink}`);
    parts.push('');
    
    // Channels
    parts.push('⚡ WhatsApp Channel: https://tinyurl.com/3nyujz59');
    parts.push('💬 Telegram Channel: https://tinyurl.com/4p4wjvww');
    
    return parts.join('\n');
  };

  const copyToClipboard = async (job: Job) => {
    const text = formatJobText(job);
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(job.id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const copyAllJobs = async () => {
    const allTexts = jobs.map(job => formatJobText(job)).join('\n\n' + '─'.repeat(40) + '\n\n');
    try {
      await navigator.clipboard.writeText(allTexts);
      setCopiedId('all');
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('Failed to copy all:', error);
    }
  };

  const handleUpdateTinyUrls = async () => {
    setUpdatingUrls(true);
    try {
      const result = await updateTinyUrls();
      alert(`✅ Updated ${result.updated} TinyURLs!`);
      fetchJobs(); // Reload jobs
    } catch (error) {
      console.error('Error updating TinyURLs:', error);
      alert('❌ Error updating TinyURLs');
    } finally {
      setUpdatingUrls(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                <FaBriefcase className="text-[#2D9763]" />
                Share Jobs
              </h1>
              <p className="text-gray-600 mt-2">Copy formatted job posts to share on social media</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleUpdateTinyUrls}
                disabled={updatingUrls}
                className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-xl"
              >
                {updatingUrls ? (
                  <>
                    <FaSync className="text-lg animate-spin" />
                    Updating...
                  </>
                ) : (
                  <>
                    <FaSync className="text-lg" />
                    Update TinyURLs
                  </>
                )}
              </button>
              <button
                onClick={copyAllJobs}
                disabled={jobs.length === 0}
                className="bg-[#2D9763] text-white px-6 py-3 rounded-xl hover:bg-[#247a50] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg hover:shadow-xl"
              >
                {copiedId === 'all' ? (
                  <>
                    <FaCheck className="text-lg" />
                    Copied All!
                  </>
                ) : (
                  <>
                    <FaCopy className="text-lg" />
                    Copy All ({jobs.length})
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-3">
            <button
              onClick={() => setFilter('all')}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                filter === 'all'
                  ? 'bg-[#2D9763] text-white shadow-md'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All Jobs
            </button>
            <button
              onClick={() => setFilter('wuzzuf')}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                filter === 'wuzzuf'
                  ? 'bg-[#2D9763] text-white shadow-md'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Wuzzuf
            </button>
            <button
              onClick={() => setFilter('indeed')}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                filter === 'indeed'
                  ? 'bg-[#2D9763] text-white shadow-md'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Indeed
            </button>
          </div>
        </div>

        {/* Jobs List */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-[#2D9763]"></div>
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <FaBriefcase className="text-6xl text-gray-300 mx-auto mb-4" />
            <p className="text-xl text-gray-500">No jobs found</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all p-6 border-l-4 border-[#2D9763]"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">{job.title}</h2>
                    <div className="flex gap-4 text-gray-600 mb-3">
                      <span className="flex items-center gap-2">
                        <FaBriefcase className="text-[#2D9763]" />
                        {job.company}
                      </span>
                      <span className="flex items-center gap-2">
                        <FaMapMarkerAlt className="text-[#2D9763]" />
                        {job.location}
                      </span>
                    </div>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                      job.source === 'wuzzuf' 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-purple-100 text-purple-800'
                    }`}>
                      {job.source === 'wuzzuf' ? '🇪🇬 Wuzzuf' : '🌐 Indeed'}
                    </span>
                  </div>
                  <button
                    onClick={() => copyToClipboard(job)}
                    className="bg-gradient-to-r from-[#2D9763] to-[#247a50] text-white px-6 py-3 rounded-xl hover:shadow-xl transition-all flex items-center gap-2 ml-4"
                  >
                    {copiedId === job.id ? (
                      <>
                        <FaCheck className="text-lg" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <FaCopy className="text-lg" />
                        Copy
                      </>
                    )}
                  </button>
                </div>

                {/* Preview */}
                <div className="bg-gray-50 rounded-xl p-4 border-2 border-gray-200">
                  <pre className="whitespace-pre-wrap font-mono text-sm text-gray-700 leading-relaxed">
                    {formatJobText(job)}
                  </pre>
                </div>

                {/* Link Preview */}
                <div className="mt-4 flex gap-3">
                  {job.link && (
                    <a
                      href={job.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#2D9763] hover:text-[#247a50] flex items-center gap-2 text-sm font-medium"
                    >
                      <FaLink />
                      Original Listing
                    </a>
                  )}
                  {job.blogger_url && (
                    <a
                      href={job.blogger_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 flex items-center gap-2 text-sm font-medium"
                    >
                      <FaLink />
                      Blog Post
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
