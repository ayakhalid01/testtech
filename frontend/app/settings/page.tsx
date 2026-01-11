'use client'

import { useState, useEffect } from 'react'
import { getSettings, updateSettings } from '@/lib/api'
import { FaSave, FaKey, FaTelegram, FaWhatsapp, FaBlog, FaLink } from 'react-icons/fa'
import Link from 'next/link'

export default function SettingsPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [settings, setSettings] = useState<any>({
    scraper_config: {
      max_jobs: 6,
      sources: ['wuzzuf', 'indeed'],
      upload_to_blogger: false,
      send_to_telegram: false,
      send_to_whatsapp: false,
      use_tinyurl: true,
      use_selenium_skills: false
    },
    telegram_config: {
      bot_token: '',
      channel_id: '@techflow_channel',
      enabled: false
    },
    whatsapp_config: {
      api_token: '',
      phone_number_id: '',
      business_account_id: '',
      enabled: false
    },
    blogger_config: {
      blog_id: '6949685611084082756',
      blog_domain: 'https://careerjobst01.blogspot.com',
      enabled: false
    },
    tinyurl_config: {
      api_key: '',
      enabled: true
    },
    keywords: {
      keywords: []
    }
  })

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const data = await getSettings()
      setSettings(data)
    } catch (error) {
      console.error('Error loading settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (key: string) => {
    try {
      setSaving(true)
      await updateSettings(key, settings[key])
      alert('Settings saved successfully!')
    } catch (error: any) {
      console.error('Error saving settings:', error)
      alert('Failed to save settings: ' + (error.response?.data?.detail || error.message))
    } finally {
      setSaving(false)
    }
  }

  const updateSetting = (key: string, value: any) => {
    setSettings({ ...settings, [key]: value })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading settings...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <Link href="/" className="text-2xl font-bold text-primary hover:text-secondary">
            ← TechFlow
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-2">Settings</h1>
          <p className="text-gray-600 mt-1">Configure API keys and preferences</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Telegram Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <FaTelegram className="text-3xl text-blue-500 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Telegram Configuration</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bot Token
                </label>
                <input
                  type="password"
                  value={settings.telegram_config?.bot_token || ''}
                  onChange={(e) => updateSetting('telegram_config', {
                    ...settings.telegram_config,
                    bot_token: e.target.value
                  })}
                  placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Get from @BotFather on Telegram
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Channel ID
                </label>
                <input
                  type="text"
                  value={settings.telegram_config?.channel_id || ''}
                  onChange={(e) => updateSetting('telegram_config', {
                    ...settings.telegram_config,
                    channel_id: e.target.value
                  })}
                  placeholder="@your_channel"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.telegram_config?.enabled || false}
                  onChange={(e) => updateSetting('telegram_config', {
                    ...settings.telegram_config,
                    enabled: e.target.checked
                  })}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <span className="ml-2 text-gray-700">Enable Telegram Integration</span>
              </label>

              <button
                onClick={() => handleSave('telegram_config')}
                disabled={saving}
                className="bg-primary hover:bg-secondary text-white font-bold py-2 px-6 rounded-lg transition duration-200 flex items-center space-x-2"
              >
                <FaSave />
                <span>{saving ? 'Saving...' : 'Save Telegram Settings'}</span>
              </button>
            </div>
          </div>

          {/* WhatsApp Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <FaWhatsapp className="text-3xl text-green-500 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">WhatsApp Configuration</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Token
                </label>
                <input
                  type="password"
                  value={settings.whatsapp_config?.api_token || ''}
                  onChange={(e) => updateSetting('whatsapp_config', {
                    ...settings.whatsapp_config,
                    api_token: e.target.value
                  })}
                  placeholder="EAAxxxxxxxxxx"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <p className="text-xs text-gray-500 mt-1">
                  From Meta Business Suite
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number ID
                </label>
                <input
                  type="text"
                  value={settings.whatsapp_config?.phone_number_id || ''}
                  onChange={(e) => updateSetting('whatsapp_config', {
                    ...settings.whatsapp_config,
                    phone_number_id: e.target.value
                  })}
                  placeholder="915769064949083"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Account ID
                </label>
                <input
                  type="text"
                  value={settings.whatsapp_config?.business_account_id || ''}
                  onChange={(e) => updateSetting('whatsapp_config', {
                    ...settings.whatsapp_config,
                    business_account_id: e.target.value
                  })}
                  placeholder="1469839234118740"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.whatsapp_config?.enabled || false}
                  onChange={(e) => updateSetting('whatsapp_config', {
                    ...settings.whatsapp_config,
                    enabled: e.target.checked
                  })}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <span className="ml-2 text-gray-700">Enable WhatsApp Integration</span>
              </label>

              <button
                onClick={() => handleSave('whatsapp_config')}
                disabled={saving}
                className="bg-primary hover:bg-secondary text-white font-bold py-2 px-6 rounded-lg transition duration-200 flex items-center space-x-2"
              >
                <FaSave />
                <span>{saving ? 'Saving...' : 'Save WhatsApp Settings'}</span>
              </button>
            </div>
          </div>

          {/* Blogger Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <FaBlog className="text-3xl text-orange-500 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Blogger Configuration</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Blog ID
                </label>
                <input
                  type="text"
                  value={settings.blogger_config?.blog_id || ''}
                  onChange={(e) => updateSetting('blogger_config', {
                    ...settings.blogger_config,
                    blog_id: e.target.value
                  })}
                  placeholder="6949685611084082756"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Blog Domain
                </label>
                <input
                  type="text"
                  value={settings.blogger_config?.blog_domain || ''}
                  onChange={(e) => updateSetting('blogger_config', {
                    ...settings.blogger_config,
                    blog_domain: e.target.value
                  })}
                  placeholder="https://yourblog.blogspot.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.blogger_config?.enabled || false}
                  onChange={(e) => updateSetting('blogger_config', {
                    ...settings.blogger_config,
                    enabled: e.target.checked
                  })}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <span className="ml-2 text-gray-700">Enable Blogger Integration</span>
              </label>

              <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                <p className="text-sm text-blue-700">
                  <strong>Note:</strong> You need to configure OAuth2 credentials in the backend for Blogger API to work.
                  Place your client_secrets.json in the backend directory.
                </p>
              </div>

              <button
                onClick={() => handleSave('blogger_config')}
                disabled={saving}
                className="bg-primary hover:bg-secondary text-white font-bold py-2 px-6 rounded-lg transition duration-200 flex items-center space-x-2"
              >
                <FaSave />
                <span>{saving ? 'Saving...' : 'Save Blogger Settings'}</span>
              </button>
            </div>
          </div>

          {/* TinyURL Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <FaLink className="text-3xl text-purple-500 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">TinyURL Configuration</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={settings.tinyurl_config?.api_key || ''}
                  onChange={(e) => updateSetting('tinyurl_config', {
                    ...settings.tinyurl_config,
                    api_key: e.target.value
                  })}
                  placeholder="nRFavNgCA9lwoqmk0BxuxBe1TXGTb4s97jR2os6Aq8TfxWAGXNoVlr1qLe2D"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Get from tinyurl.com/app/settings/api
                </p>
              </div>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.tinyurl_config?.enabled || false}
                  onChange={(e) => updateSetting('tinyurl_config', {
                    ...settings.tinyurl_config,
                    enabled: e.target.checked
                  })}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
                <span className="ml-2 text-gray-700">Enable TinyURL Shortening</span>
              </label>

              <button
                onClick={() => handleSave('tinyurl_config')}
                disabled={saving}
                className="bg-primary hover:bg-secondary text-white font-bold py-2 px-6 rounded-lg transition duration-200 flex items-center space-x-2"
              >
                <FaSave />
                <span>{saving ? 'Saving...' : 'Save TinyURL Settings'}</span>
              </button>
            </div>
          </div>

          {/* Keywords Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <FaKey className="text-3xl text-red-500 mr-3" />
              <h2 className="text-2xl font-bold text-gray-900">Search Keywords</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Keywords (one per line)
                </label>
                <textarea
                  value={settings.keywords?.keywords?.join('\n') || ''}
                  onChange={(e) => updateSetting('keywords', {
                    keywords: e.target.value.split('\n').filter(k => k.trim())
                  })}
                  rows={10}
                  placeholder="Flutter&#10;Backend&#10;Frontend&#10;Full Stack&#10;..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">
                  These keywords will be used to search for jobs on Wuzzuf and Indeed
                </p>
              </div>

              <button
                onClick={() => handleSave('keywords')}
                disabled={saving}
                className="bg-primary hover:bg-secondary text-white font-bold py-2 px-6 rounded-lg transition duration-200 flex items-center space-x-2"
              >
                <FaSave />
                <span>{saving ? 'Saving...' : 'Save Keywords'}</span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
