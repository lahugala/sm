import axios from 'axios'

const LOCAL_API = 'http://192.168.1.131:8080'
const CLOUD_API = 'https://api.sms-gate.app/3rdparty/v1'

/**
 * Creates an Axios instance configured for the SMS Gateway API.
 *
 * ALL requests are routed through the Vite dev server proxy at /sms-proxy.
 * This avoids CORS issues for both Local (LAN) and Cloud modes.
 * The actual target URL is passed per-request via the X-Gateway-Url header.
 *
 * LOCAL  → proxy forwards to http://<phone-ip>:8080   (config.local.url)
 * CLOUD  → proxy forwards to https://api.sms-gate.app/3rdparty/v1
 *
 * Credentials are stored separately per mode:
 *   config.local.username / config.local.password
 *   config.cloud.username / config.cloud.password
 */
export function createApiClient(config) {
  const isLocal    = config.mode === 'local'
  const creds      = isLocal ? config.local : config.cloud
  const gatewayUrl = isLocal ? (config.local?.url || LOCAL_API) : CLOUD_API

  const client = axios.create({
    baseURL: '/sms-proxy',
    timeout: 15000,
    headers: {
      'Content-Type': 'application/json',
      'X-Gateway-Url': gatewayUrl,
    },
    auth: {
      username: creds?.username || '',
      password: creds?.password || '',
    },
  })

  client.isCloud = !isLocal

  return client
}

/**
 * Send an SMS message (single or bulk).
 * POST /message  (local)  |  POST /message  (cloud)
 *
 * Supported payload fields:
 *   message          – SMS text
 *   phoneNumbers     – array of E.164 numbers
 *   withDeliveryReport
 *   simNumber        – 1 | 2
 *   ttl              – seconds until expiry
 *   priority         – 0 (normal) … 100 (urgent, skips delays)
 *   scheduleAt       – UTC ISO string, e.g. "2026-05-17T08:00:00.000Z"
 */
export async function sendMessage(apiClient, { message, phoneNumbers, withDeliveryReport, simNumber, ttl, priority, scheduleAt, deviceId }) {
  const payload = {
    message,
    phoneNumbers: Array.isArray(phoneNumbers) ? phoneNumbers : [phoneNumbers],
  }

  if (withDeliveryReport !== undefined) payload.withDeliveryReport = withDeliveryReport
  if (simNumber !== undefined && simNumber !== null) payload.simNumber = simNumber
  if (ttl !== undefined && ttl !== null) payload.ttl = ttl
  if (priority !== undefined && priority !== 0) payload.priority = priority
  if (scheduleAt) payload.scheduleAt = scheduleAt
  if (deviceId) payload.deviceId = deviceId

  const endpoint = apiClient.isCloud ? '/messages' : '/message'
  const { data } = await apiClient.post(endpoint, payload)
  return data
}

/**
 * Get status of a specific message by ID.
 * GET /message/:id
 */
export async function getMessageStatus(apiClient, messageId) {
  const endpoint = apiClient.isCloud ? `/messages/${messageId}` : `/message/${messageId}`
  const { data } = await apiClient.get(endpoint)
  return data
}

/**
 * Fetch received (inbox) messages.
 * GET /inbox  — LOCAL MODE ONLY
 *
 * @param {object} params
 *   type   – 'SMS' | 'DATA_SMS' | 'MMS'  (default 'SMS')
 *   limit  – max results per page         (default 50)
 *   offset – pagination offset            (default 0)
 *   from   – filter by sender number
 *   to     – filter by recipient number
 * @returns { messages: [...], total: number }
 */
export async function getInbox(apiClient, params = {}) {
  const { data, headers } = await apiClient.get('/inbox', {
    params: {
      type: params.type || 'SMS',
      limit: params.limit || 50,
      offset: params.offset || 0,
      ...(params.from ? { from: params.from } : {}),
      ...(params.to ? { to: params.to } : {}),
    },
  })
  const total = parseInt(headers['x-total-count'] || '0', 10)
  return { messages: Array.isArray(data) ? data : [], total }
}

/**
 * Trigger a refresh of the inbox (re-reads messages from Android).
 * POST /inbox/refresh  — LOCAL MODE ONLY
 */
export async function refreshInbox(apiClient, { since, until } = {}) {
  const body = {}
  if (since) body.since = since
  if (until) body.until = until
  const { data } = await apiClient.post('/inbox/refresh', body)
  return data
}

/**
 * Health check / connectivity test.
 * Returns { ok, reason, detail } instead of a plain boolean
 * so callers can show specific troubleshooting hints.
 *
 * reason values:
 *   'ok'       – connected
 *   'auth'     – 401/403 wrong credentials
 *   'network'  – no route / device unreachable / CORS
 *   'not_found'– endpoint 404 (wrong URL path or port)
 *   'timeout'  – request timed out
 *   'unknown'  – other
 */
export async function checkHealth(apiClient) {
  // Try /health first; if that 404s, fall back to GET /messages
  const endpoints = ['/health', '/messages']

  for (const endpoint of endpoints) {
    try {
      const { data } = await apiClient.get(endpoint, { timeout: 8000 })
      // The /health endpoint returns { status: 'ok', model: 'CPH1823' }
      const model = data?.model ? ` — Device: ${data.model}` : ''
      return { ok: true, reason: 'ok', detail: `Connected${model}`, model: data?.model || null }
    } catch (err) {
      const status = err.response?.status

      // 401 / 403 — reached the device but wrong password
      if (status === 401 || status === 403) {
        return { ok: false, reason: 'auth', detail: 'Wrong username or password.' }
      }

      // 404 on /health — try next endpoint
      if (status === 404) continue

      // 2xx but unexpected — treat as ok
      if (status && status < 400) {
        return { ok: true, reason: 'ok', detail: `Reachable via ${endpoint}` }
      }

      // Network-level failure (CORS, unreachable, refused)
      if (!err.response) {
        const isTimeout = err.code === 'ECONNABORTED' || err.message?.includes('timeout')
        if (isTimeout) {
          return { ok: false, reason: 'timeout', detail: 'Request timed out. Device may be off or unreachable.' }
        }
        // CORS shows up as a Network Error with no response
        return {
          ok: false,
          reason: 'network',
          detail: err.message || 'Network error — device unreachable or CORS blocked.',
        }
      }

      // Any other HTTP error
      return { ok: false, reason: 'unknown', detail: `HTTP ${status}: ${err.message}` }
    }
  }

  // Both endpoints returned 404
  return { ok: false, reason: 'not_found', detail: 'No valid API endpoint found. Check the Device URL and port.' }
}
