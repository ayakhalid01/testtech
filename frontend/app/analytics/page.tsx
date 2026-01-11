'use client';

import { useState, useEffect } from 'react';
import { FaChartBar, FaCheck, FaTimes, FaCopy, FaSearch, FaCalendar } from 'react-icons/fa';

interface ScrapingSummary {
  total_scraped: number;
  jobs_saved: number;
  duplicates_skipped: number;
  keywords_found: Record<string, number>;
  keywords_empty: string[];
  skip_reasons: Record<string, number>;
  sources: Record<string, number>;
  last_run: string;
}

interface ScrapingHistoryItem {
  id: number;
  timestamp: string;
  total_scraped: number;
  jobs_saved: number;
  duplicates: number;
  total_skipped: number;
  skip_reasons: Record<string, number>;
  keywords_found: Record<string, number>;
  sources: Record<string, number>;
  duration: number;
}

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<ScrapingSummary | null>(null);
  const [history, setHistory] = useState<ScrapingHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('today'); // today, week, month

  useEffect(() => {
    loadSummary();
    loadHistory();
  }, [timeRange]);

  const loadSummary = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/analytics/summary?range=${timeRange}`);
      const data = await response.json();
      console.log('Analytics data received:', data);
      setSummary(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/analytics/history?limit=20');
      const data = await response.json();
      setHistory(data.history || []);
      console.log('History loaded:', data.history?.length || 0, 'entries');
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#2D9763]"></div>
          </div>
        </div>
      </div>
    );
  }

  const successRate = summary 
    ? ((summary.jobs_saved / (summary.total_scraped || 1)) * 100).toFixed(1)
    : '0';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                <FaChartBar className="text-[#2D9763]" />
                تحليلات السكريب
              </h1>
              <p className="text-gray-600 mt-2">ملخص شامل لعمليات البحث والنتائج</p>
            </div>
            
            {/* Time Range Filter */}
            <div className="flex gap-2">
              <button
                onClick={() => setTimeRange('today')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  timeRange === 'today'
                    ? 'bg-[#2D9763] text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100'
                }`}
              >
                اليوم
              </button>
              <button
                onClick={() => setTimeRange('week')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  timeRange === 'week'
                    ? 'bg-[#2D9763] text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100'
                }`}
              >
                هذا الأسبوع
              </button>
              <button
                onClick={() => setTimeRange('month')}
                className={`px-4 py-2 rounded-lg transition-all ${
                  timeRange === 'month'
                    ? 'bg-[#2D9763] text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100'
                }`}
              >
                هذا الشهر
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Scraped */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">إجمالي الوظائف</p>
                <p className="text-3xl font-bold text-gray-800">{summary?.total_scraped || 0}</p>
              </div>
              <FaSearch className="text-4xl text-blue-500" />
            </div>
          </div>

          {/* Jobs Saved */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">تم الحفظ</p>
                <p className="text-3xl font-bold text-green-600">{summary?.jobs_saved || 0}</p>
              </div>
              <FaCheck className="text-4xl text-green-500" />
            </div>
          </div>

          {/* Duplicates */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">مكررة</p>
                <p className="text-3xl font-bold text-orange-600">{summary?.duplicates_skipped || 0}</p>
              </div>
              <FaCopy className="text-4xl text-orange-500" />
            </div>
          </div>

          {/* Success Rate */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">معدل النجاح</p>
                <p className="text-3xl font-bold text-purple-600">{successRate}%</p>
              </div>
              <FaChartBar className="text-4xl text-purple-500" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Keywords Performance */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <FaSearch className="text-[#2D9763]" />
              أداء الكلمات المفتاحية
            </h3>
            
            {/* Keywords with Jobs */}
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-gray-600 mb-2">✅ وجدت وظائف:</h4>
              <div className="space-y-2">
                {summary && Object.entries(summary.keywords_found || {}).map(([keyword, count]) => (
                  <div key={keyword} className="flex items-center justify-between bg-green-50 p-3 rounded-lg">
                    <span className="text-gray-700 font-medium">{keyword}</span>
                    <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                      {count}
                    </span>
                  </div>
                ))}
                {(!summary || Object.keys(summary.keywords_found || {}).length === 0) && (
                  <p className="text-gray-400 text-sm">لا توجد بيانات</p>
                )}
              </div>
            </div>

            {/* Keywords with No Jobs */}
            <div>
              <h4 className="text-sm font-semibold text-gray-600 mb-2">❌ لم تجد وظائف:</h4>
              <div className="flex flex-wrap gap-2">
                {summary?.keywords_empty?.map((keyword) => (
                  <span key={keyword} className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm">
                    {keyword}
                  </span>
                ))}
                {(!summary || !summary.keywords_empty || summary.keywords_empty.length === 0) && (
                  <p className="text-gray-400 text-sm">جميع الكلمات وجدت وظائف!</p>
                )}
              </div>
            </div>
          </div>

          {/* Skip Reasons */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <FaTimes className="text-orange-500" />
              أسباب التخطي
            </h3>
            <div className="space-y-2">
              {summary && Object.entries(summary.skip_reasons || {}).map(([reason, count]) => {
                const reasonLabels: Record<string, string> = {
                  'duplicate': 'مكررة',
                  'no_keyword': 'لا تحتوي على كلمة مفتاحية',
                  'not_egypt': 'خارج مصر',
                  'no_requirements': 'لا توجد متطلبات',
                  'no_link': 'بدون رابط',
                  'no_title': 'بدون عنوان',
                  'parse_error': 'خطأ في القراءة'
                };
                
                return (
                  <div key={reason} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                    <span className="text-gray-700">{reasonLabels[reason] || reason}</span>
                    <span className="bg-orange-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                      {count}
                    </span>
                  </div>
                );
              })}
              {(!summary || Object.keys(summary.skip_reasons || {}).length === 0) && (
                <p className="text-gray-400 text-sm">لا توجد وظائف تم تخطيها</p>
              )}
            </div>
          </div>
        </div>

        {/* Sources Breakdown */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <FaChartBar className="text-[#2D9763]" />
            توزيع المصادر
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {summary && Object.entries(summary.sources || {}).map(([source, count]) => {
              const total = summary.total_scraped || 1;
              const percentage = ((count / total) * 100).toFixed(1);
              
              return (
                <div key={source} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-700 font-semibold capitalize">{source}</span>
                    <span className="text-2xl font-bold text-[#2D9763]">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-[#2D9763] h-2 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{percentage}%</p>
                </div>
              );
            })}
            {(!summary || Object.keys(summary.sources || {}).length === 0) && (
              <p className="text-gray-400 text-sm">لا توجد بيانات</p>
            )}
          </div>
        </div>

        {/* Last Run Info */}
        {summary?.last_run && (
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-blue-700">
              <FaCalendar />
              <span className="font-semibold">آخر تشغيل:</span>
              <span>{new Date(summary.last_run).toLocaleString('ar-EG')}</span>
            </div>
          </div>
        )}

        {/* Scraping History */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-800">سجل عمليات الـ Scraping</h2>
          
          {history.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
              <p>لا توجد بيانات</p>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">التاريخ</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">الوظائف المحفوظة</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">متكررة</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">متجاهلة</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">الكلمات المفتاحية</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">المصادر</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">المدة</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {history.map((item) => (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(item.timestamp).toLocaleString('ar-EG', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            {item.jobs_saved}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                            {item.duplicates}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                            {item.total_skipped}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          <div className="flex flex-wrap gap-1">
                            {Object.entries(item.keywords_found).slice(0, 3).map(([keyword, count]) => (
                              <span key={keyword} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                                {keyword}: {count}
                              </span>
                            ))}
                            {Object.keys(item.keywords_found).length > 3 && (
                              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                                +{Object.keys(item.keywords_found).length - 3}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {Object.entries(item.sources).map(([source, count]) => (
                            <div key={source}>{source}: {count}</div>
                          ))}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.duration ? `${Math.round(item.duration)}s` : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
