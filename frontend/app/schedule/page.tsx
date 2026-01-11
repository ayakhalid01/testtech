'use client';

import { useState, useEffect } from 'react';
import { FaClock, FaSave, FaPlay, FaStop } from 'react-icons/fa';
import { getSchedule, saveSchedule, getLogs, stopScraping, getScrapingStatus } from '@/lib/api';

export default function SchedulePage() {
  const [schedule, setSchedule] = useState({
    enabled: false,
    time: '10:00',
    frequency: 'daily',
    max_jobs: 6,
    sources: ['wuzzuf', 'indeed'],
    upload_to_blogger: false,
    send_to_telegram: false,
    send_to_whatsapp: false
  });

  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [lastRun, setLastRun] = useState<string | null>(null);
  const [nextRun, setNextRun] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [testRunning, setTestRunning] = useState(false);

  // تحميل الإعدادات المحفوظة عند فتح الصفحة
  useEffect(() => {
    const loadSchedule = async () => {
      try {
        // تحميل من API (database)
        const scheduleData = await getSchedule();
        setSchedule(scheduleData);
        localStorage.setItem('schedule', JSON.stringify(scheduleData));

        // استخدام next_run من API
        if (scheduleData.next_run) {
          setNextRun(scheduleData.next_run);
        }

        // جلب آخر تشغيل من logs
        const logsData = await getLogs({ limit: 1 });
        if (logsData.logs && logsData.logs.length > 0) {
          setLastRun(logsData.logs[0].timestamp);
        }
      } catch (error) {
        console.error('Error loading schedule:', error);
        // تحميل من localStorage في حالة فشل API
        const savedSchedule = localStorage.getItem('schedule');
        if (savedSchedule) {
          setSchedule(JSON.parse(savedSchedule));
        }
      } finally {
        setLoading(false);
      }
    };

    loadSchedule();
  }, []);

  // حفظ التغييرات في localStorage تلقائياً
  useEffect(() => {
    if (!loading) {
      localStorage.setItem('schedule', JSON.stringify(schedule));
    }
  }, [schedule, loading]);

  // حساب الموعد القادم
  const calculateNextRun = () => {
    if (!schedule.enabled || !schedule.time) {
      setNextRun(null);
      return;
    }

    const now = new Date();
    const [hours, minutes] = schedule.time.split(':').map(Number);
    const next = new Date();
    next.setHours(hours, minutes, 0, 0);

    // إذا كان الوقت فات اليوم، حدد الموعد القادم حسب التكرار
    if (next <= now) {
      if (schedule.frequency === 'hourly') {
        // إذا hourly، خد الساعة الجاية
        next.setHours(now.getHours() + 1, 0, 0, 0);
      } else if (schedule.frequency === 'daily') {
        next.setDate(next.getDate() + 1);
      } else if (schedule.frequency === 'weekly') {
        next.setDate(next.getDate() + 7);
      }
    }

    console.log('Next run calculated:', next.toISOString());
    setNextRun(next.toISOString());
  };

  // تشغيل تجريبي
  const handleTestRun = async () => {
    setTestRunning(true);
    setIsRunning(true);
    
    try {
      // قراءة API key من البيئة
      const apiKey = 'sb_secret_r5OjjpYY-BXcI-6yL_xk7g_lVlok325';
      
      console.log('Starting test scrape with config:', {
        max_jobs: schedule.max_jobs,
        sources: schedule.sources
      });

      const response = await fetch('http://localhost:8000/api/scrape', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify({
          max_jobs: schedule.max_jobs,
          sources: schedule.sources,
          upload_to_blogger: schedule.upload_to_blogger,
          send_to_telegram: schedule.send_to_telegram,
          send_to_whatsapp: schedule.send_to_whatsapp,
          use_selenium_skills: false
        })
      });

      const data = await response.json();
      console.log('Response:', data);
      
      if (response.ok) {
        alert('✅ Test scrape started! Check Logs page for real-time updates.');
        // تحديث آخر تشغيل
        setLastRun(new Date().toISOString());
        
        // إعادة تحميل بعد 5 ثواني
        setTimeout(() => {
          setIsRunning(false);
        }, 5000);
      } else {
        setIsRunning(false);
        alert('❌ Failed: ' + (data.detail || data.message || 'Unknown error'));
      }
    } catch (error: any) {
      setIsRunning(false);
      console.error('Error starting test run:', error);
      alert('❌ Error: Backend not available. Make sure server is running on port 8000\n\nDetails: ' + error.message);
    } finally {
      setTestRunning(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // حفظ في database عبر API
      const response = await saveSchedule(schedule);
      
      // تحديث next_run من response
      if (response && response.data) {
        const updatedSchedule = response.data;
        setSchedule(updatedSchedule);
        if (updatedSchedule.next_run) {
          setNextRun(updatedSchedule.next_run);
        }
        localStorage.setItem('schedule', JSON.stringify(updatedSchedule));
      } else {
        localStorage.setItem('schedule', JSON.stringify(schedule));
      }

      alert('✅ Schedule saved successfully!');
    } catch (error) {
      console.error('Error saving schedule:', error);
      alert('❌ Error saving schedule');
    } finally {
      setSaving(false);
    }
  };

  const toggleSchedule = async () => {
    const newSchedule = { ...schedule, enabled: !schedule.enabled };
    setSchedule(newSchedule);
    
    // حفظ مباشرة عند التفعيل/التعطيل
    localStorage.setItem('schedule', JSON.stringify(newSchedule));
    
    try {
      // حفظ في database عبر API
      await saveSchedule(newSchedule);
    } catch (error) {
      console.error('Error saving schedule state:', error);
    }
  };

  const handleStopScraping = async () => {
    if (!confirm('⚠️ Are you sure you want to stop the current scraping process?')) {
      return;
    }

    try {
      const result = await stopScraping();
      alert('✅ ' + result.message);
      setIsRunning(false);
      setTestRunning(false);
    } catch (error: any) {
      console.error('Error stopping scraping:', error);
      alert('❌ Error stopping scraping: ' + error.message);
    }
  };

  const handleResetSchedule = async () => {
    if (!confirm('⚠️ Are you sure you want to reset schedule to default settings?')) {
      return;
    }

    const defaultSchedule = {
      enabled: false,
      time: '10:00',
      frequency: 'daily',
      max_jobs: 6,
      sources: ['wuzzuf', 'indeed'],
      upload_to_blogger: false,
      send_to_telegram: false,
      send_to_whatsapp: false
    };

    setSchedule(defaultSchedule);
    localStorage.setItem('schedule', JSON.stringify(defaultSchedule));

    try {
      await saveSchedule(defaultSchedule);
      alert('✅ Schedule reset successfully!');
    } catch (error) {
      console.error('Error resetting schedule:', error);
      alert('❌ Error resetting schedule');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-[#2D9763] mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading schedule...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                <FaClock className="text-[#2D9763]" />
                Scraping Schedule
              </h1>
              <p className="text-gray-600 mt-2">Automate job scraping on a schedule</p>
            </div>
            <button
              onClick={toggleSchedule}
              className={`px-6 py-3 rounded-xl transition-all flex items-center gap-2 shadow-lg ${
                schedule.enabled
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {schedule.enabled ? (
                <>
                  <FaStop /> Disable
                </>
              ) : (
                <>
                  <FaPlay /> Enable
                </>
              )}
            </button>
          </div>

          {/* Status Badge */}
          <div className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${
            schedule.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}>
            {schedule.enabled ? '✅ Schedule Active' : '⏸️ Schedule Paused'}
          </div>
        </div>

        {/* Status Information */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Last Run */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">آخر تشغيل</h3>
            {lastRun ? (
              <div>
                <p className="text-2xl font-bold text-gray-800">
                  {new Date(lastRun).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {new Date(lastRun).toLocaleDateString('ar-EG')}
                </p>
              </div>
            ) : (
              <p className="text-lg text-gray-400">لم يتم التشغيل بعد</p>
            )}
          </div>

          {/* Next Run */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">الموعد القادم</h3>
            {schedule.enabled && nextRun ? (
              <div>
                <p className="text-2xl font-bold text-[#2D9763]">
                  {new Date(nextRun).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {new Date(nextRun).toLocaleDateString('ar-EG')}
                </p>
              </div>
            ) : (
              <p className="text-lg text-gray-400">غير مفعّل</p>
            )}
          </div>

          {/* Status */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">الحالة الحالية</h3>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                isRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
              }`}></div>
              <p className="text-lg font-bold text-gray-800">
                {isRunning ? 'جاري التشغيل...' : 'في انتظار الموعد'}
              </p>
            </div>
            <div className="mt-4 space-y-2">
              <button
                onClick={handleTestRun}
                disabled={testRunning || isRunning}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {testRunning ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                    جاري التشغيل...
                  </>
                ) : (
                  <>
                    <FaPlay className="text-sm" />
                    تشغيل تجريبي
                  </>
                )}
              </button>
              
              {isRunning && (
                <button
                  onClick={handleStopScraping}
                  className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  <FaStop className="text-sm" />
                  إيقاف الآن
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Schedule Settings */}
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Schedule Settings</h2>

          {/* Time */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scraping Time
            </label>
            <input
              type="time"
              value={schedule.time}
              onChange={(e) => setSchedule({ ...schedule, time: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#2D9763] focus:outline-none"
            />
            <p className="text-sm text-gray-500 mt-1">
              Jobs will be scraped daily at this time (server timezone)
            </p>
          </div>

          {/* Frequency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Frequency
            </label>
            <select
              value={schedule.frequency}
              onChange={(e) => setSchedule({ ...schedule, frequency: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#2D9763] focus:outline-none"
            >
              <option value="hourly">Every Hour</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>

          {/* Max Jobs */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Jobs per Run
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={schedule.max_jobs}
              onChange={(e) => setSchedule({ ...schedule, max_jobs: parseInt(e.target.value) })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-[#2D9763] focus:outline-none"
            />
          </div>

          {/* Sources */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Sources
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={schedule.sources.includes('wuzzuf')}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSchedule({ ...schedule, sources: [...schedule.sources, 'wuzzuf'] });
                    } else {
                      setSchedule({ ...schedule, sources: schedule.sources.filter(s => s !== 'wuzzuf') });
                    }
                  }}
                  className="w-5 h-5 text-[#2D9763] rounded focus:ring-[#2D9763]"
                />
                <span className="text-gray-700">Wuzzuf</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={schedule.sources.includes('indeed')}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSchedule({ ...schedule, sources: [...schedule.sources, 'indeed'] });
                    } else {
                      setSchedule({ ...schedule, sources: schedule.sources.filter(s => s !== 'indeed') });
                    }
                  }}
                  className="w-5 h-5 text-[#2D9763] rounded focus:ring-[#2D9763]"
                />
                <span className="text-gray-700">Indeed</span>
              </label>
            </div>
          </div>

          {/* Actions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Automated Actions
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={schedule.upload_to_blogger}
                  onChange={(e) => setSchedule({ ...schedule, upload_to_blogger: e.target.checked })}
                  className="w-5 h-5 text-[#2D9763] rounded focus:ring-[#2D9763]"
                />
                <span className="text-gray-700">Upload to Blogger</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={schedule.send_to_telegram}
                  onChange={(e) => setSchedule({ ...schedule, send_to_telegram: e.target.checked })}
                  className="w-5 h-5 text-[#2D9763] rounded focus:ring-[#2D9763]"
                />
                <span className="text-gray-700">Send to Telegram</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={schedule.send_to_whatsapp}
                  onChange={(e) => setSchedule({ ...schedule, send_to_whatsapp: e.target.checked })}
                  className="w-5 h-5 text-[#2D9763] rounded focus:ring-[#2D9763]"
                />
                <span className="text-gray-700">Send to WhatsApp</span>
              </label>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex gap-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 bg-gradient-to-r from-[#2D9763] to-[#247a50] text-white px-6 py-4 rounded-xl hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg font-semibold"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                  Saving...
                </>
              ) : (
                <>
                  <FaSave />
                  Save Schedule
                </>
              )}
            </button>

            <button
              onClick={handleResetSchedule}
              className="bg-red-600 hover:bg-red-700 text-white px-6 py-4 rounded-xl transition-all flex items-center gap-2 text-lg font-semibold"
            >
              🗑️ Reset
            </button>
          </div>
        </div>

        {/* Info Card */}
        <div className="mt-8 bg-blue-50 border-2 border-blue-200 rounded-2xl p-6">
          <h3 className="text-lg font-bold text-blue-900 mb-2">ℹ️ How it works</h3>
          <ul className="space-y-2 text-blue-800">
            <li>• Schedule runs automatically at the specified time</li>
            <li>• Jobs are scraped from selected sources</li>
            <li>• Results are saved to database</li>
            <li>• Automated actions (Blogger, Telegram, WhatsApp) are executed if enabled</li>
            <li>• You can view logs in the Logs page</li>
          </ul>
        </div>

        {/* Next Runs */}
        {schedule.enabled && (
          <div className="mt-8 bg-green-50 border-2 border-green-200 rounded-2xl p-6">
            <h3 className="text-lg font-bold text-green-900 mb-2">📅 Next Scheduled Runs</h3>
            <div className="space-y-2 text-green-800">
              <div className="flex justify-between">
                <span>Today</span>
                <span className="font-semibold">{schedule.time}</span>
              </div>
              <div className="flex justify-between">
                <span>Tomorrow</span>
                <span className="font-semibold">{schedule.time}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
