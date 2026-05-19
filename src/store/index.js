import { reactive, computed } from 'vue'
import { createApiClient, getMessageStatus } from '../services/smsApi'

const DEFAULT_CONFIG = {
  mode: 'cloud',           // active mode: 'local' | 'cloud'

  // ── Local (LAN) credentials ──────────────────────────────────────
  local: {
    username: '',
    password: '',
    url: 'http://192.168.0.100:8080',
    deviceModel: null,     // populated after a successful test
  },

  // ── Cloud credentials ─────────────────────────────────────────────
  cloud: {
    username: 'H3VON6',
    password: 'cd6goxy1kx3nq2',
    deviceId: '_NU3lzBBnhlyr1C50BJzC',
  },

  // ── Shared message defaults ───────────────────────────────────────
  withDeliveryReport: true,
  simNumber: null,
}

const STORAGE_KEY = 'sms_gateway_config'
const HISTORY_KEY  = 'sms_gateway_history'

/**
 * Load config from localStorage, migrating the old flat format if needed.
 */
function loadConfig() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return structuredClone(DEFAULT_CONFIG)

    const saved = JSON.parse(raw)

    // ── Migration: old flat format had top-level username/password ──
    if (saved.username !== undefined || saved.password !== undefined) {
      const migrated = structuredClone(DEFAULT_CONFIG)
      migrated.mode = saved.mode || 'local'
      migrated.withDeliveryReport = saved.withDeliveryReport ?? true
      migrated.simNumber = saved.simNumber ?? null
      // Put old credentials into local (where most users configured them)
      migrated.local.username    = saved.username || ''
      migrated.local.password    = saved.password || ''
      migrated.local.url         = saved.localUrl  || DEFAULT_CONFIG.local.url
      migrated.local.deviceModel = saved.deviceModel || null
      // Persist the migrated format immediately
      localStorage.setItem(STORAGE_KEY, JSON.stringify(migrated))
      return migrated
    }

    // Merge over defaults to add any new keys added in future versions
    return {
      ...structuredClone(DEFAULT_CONFIG),
      ...saved,
      local: { ...structuredClone(DEFAULT_CONFIG.local), ...saved.local },
      cloud: { ...structuredClone(DEFAULT_CONFIG.cloud), ...saved.cloud },
    }
  } catch {
    return structuredClone(DEFAULT_CONFIG)
  }
}

// Load history
function loadHistory() {
  try {
    const saved = localStorage.getItem(HISTORY_KEY)
    return saved ? JSON.parse(saved) : []
  } catch {
    return []
  }
}

// ── Global reactive store ─────────────────────────────────────────────
export const store = reactive({
  config: loadConfig(),
  history: loadHistory(),
  apiClient: null,
  isConfigured: false,
  connectionStatus: 'unknown', // 'unknown' | 'connected' | 'error'

  get totalSent()       { return this.history.length },
  get totalRecipients() { return this.history.reduce((s, h) => s + (h.phoneNumbers?.length || 0), 0) },
  get successCount()    { return this.history.filter(h => h.status === 'Sent' || h.status === 'Delivered').length },
  get failedCount()     { return this.history.filter(h => h.status === 'Failed').length },
})

// ── Active-mode credential helpers ───────────────────────────────────
export function getActiveCreds() {
  return store.config.mode === 'local'
    ? store.config.local
    : store.config.cloud
}

/** Initialize API client from the active mode's stored credentials */
export function initClient() {
  const creds = getActiveCreds()
  if (creds.username && creds.password) {
    store.apiClient = createApiClient(store.config)
    store.isConfigured = true
    return true
  }
  store.apiClient   = null
  store.isConfigured = false
  return false
}

/** Merge partial updates into config, persist, and reinitialise the client */
export function saveConfig(updates) {
  // Support nested updates for local/cloud sub-objects
  if (updates.local)  store.config.local  = { ...store.config.local,  ...updates.local  }
  if (updates.cloud)  store.config.cloud  = { ...store.config.cloud,  ...updates.cloud  }

  // Top-level fields
  const { local: _l, cloud: _c, ...topLevel } = updates
  Object.assign(store.config, topLevel)

  localStorage.setItem(STORAGE_KEY, JSON.stringify(store.config))
  initClient()
}

// ── History helpers ───────────────────────────────────────────────────
export function addToHistory(entry) {
  const record = {
    id:           entry.id || crypto.randomUUID(),
    message:      entry.message,
    phoneNumbers: entry.phoneNumbers,
    status:       entry.state || 'Pending',
    sentAt:       new Date().toISOString(),
    results:      entry.recipients || [],
    scheduledFor: entry.scheduledFor || null,
  }
  store.history.unshift(record)
  if (store.history.length > 200) store.history.splice(200)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(store.history))
  return record
}

export function updateHistoryStatus(id, status, results) {
  const entry = store.history.find(h => h.id === id)
  if (entry) {
    entry.status = status
    if (results) entry.results = results
    localStorage.setItem(HISTORY_KEY, JSON.stringify(store.history))
  }
}

export async function refreshMessageStatus(id) {
  if (!store.apiClient || !store.isConfigured) {
    throw new Error('Gateway API is not configured')
  }
  const data = await getMessageStatus(store.apiClient, id)
  const status = data.state || data.status || 'Pending'
  const results = data.recipients || []
  updateHistoryStatus(id, status, results)
  return { status, results }
}

export function clearHistory() {
  store.history = []
  localStorage.removeItem(HISTORY_KEY)
}

// Initialize on import
initClient()

