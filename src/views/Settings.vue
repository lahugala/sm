<template>
  <div class="animate-in">
    <div class="page-header">
      <h1 class="page-title">Settings</h1>
      <p class="page-subtitle">Configure your Android SMS Gateway connection</p>
    </div>

    <div class="settings-layout">
      <div class="settings-main">

        <!-- Mode Selector -->
        <div class="card settings-card">
          <h3 class="section-title">🔌 Active Mode</h3>
          <div class="mode-selector">
            <div class="mode-option" :class="{ active: form.mode === 'local' }" @click="form.mode = 'local'" id="mode-local">
              <div class="mode-option-icon">🏠</div>
              <div class="mode-option-info">
                <span class="mode-option-title">Local Mode</span>
                <span class="mode-option-desc">Direct LAN connection to device</span>
              </div>
              <div class="mode-radio" :class="{ selected: form.mode === 'local' }"></div>
            </div>
            <div class="mode-option" :class="{ active: form.mode === 'cloud' }" @click="form.mode = 'cloud'" id="mode-cloud">
              <div class="mode-option-icon">☁️</div>
              <div class="mode-option-info">
                <span class="mode-option-title">Cloud Mode</span>
                <span class="mode-option-desc">Via sms-gate.app relay server</span>
              </div>
              <div class="mode-radio" :class="{ selected: form.mode === 'cloud' }"></div>
            </div>
          </div>
          <p class="mode-hint" v-if="form.mode === 'local'">🏠 <strong>Local:</strong> Same Wi-Fi required. Fastest, supports Inbox.</p>
          <p class="mode-hint" v-else>☁️ <strong>Cloud:</strong> Works from anywhere via internet.</p>
        </div>

        <!-- Local Credentials -->
        <div class="card settings-card cred-card" :class="{ 'cred-active': form.mode === 'local' }">
          <div class="cred-card-header">
            <div class="cred-badge local-badge">🏠 Local</div>
            <span class="active-tag" v-if="form.mode === 'local'">● Active</span>
          </div>
          <h3 class="section-title">Local (LAN) Credentials</h3>

          <div class="form-group">
            <label class="form-label" for="local-url">Device URL</label>
            <input id="local-url" v-model="form.local.url" type="url" class="form-control" placeholder="http://192.168.0.100:8080" />
            <p class="field-hint">IP shown on SMS Gateway app home screen.</p>
          </div>
          <div class="credentials-grid">
            <div class="form-group">
              <label class="form-label" for="local-username">Username</label>
              <input id="local-username" v-model="form.local.username" type="text" class="form-control" placeholder="From app home screen" autocomplete="off" />
            </div>
            <div class="form-group">
              <label class="form-label" for="local-password">Password</label>
              <div class="password-wrapper">
                <input id="local-password" v-model="form.local.password" :type="showLocalPwd ? 'text' : 'password'" class="form-control" placeholder="From app home screen" autocomplete="off" />
                <button type="button" class="password-toggle" @click="showLocalPwd = !showLocalPwd">{{ showLocalPwd ? '🙈' : '👁' }}</button>
              </div>
            </div>
          </div>

          <transition name="fade">
            <div v-if="testResults.local" :class="['test-result', testResults.local.ok ? 'test-ok' : 'test-fail']">
              <div class="test-result-row">
                <span class="test-icon">{{ testResults.local.ok ? '✅' : '❌' }}</span>
                <div>
                  <div class="test-headline">{{ testResults.local.ok ? 'Connection successful!' : (testResults.local.hints?.headline || 'Connection failed') }}</div>
                  <div class="test-detail">{{ testResults.local.detail }}</div>
                </div>
              </div>
              <div v-if="testResults.local.ok && testResults.local.model" class="device-badge">
                <span class="device-badge-icon">📱</span>
                <span class="device-badge-label">Device</span>
                <span class="device-badge-model">{{ testResults.local.model }}</span>
              </div>
              <div v-if="testResults.local.ok" class="auto-saved-note">💾 Local credentials auto-saved</div>
              <ul v-if="!testResults.local.ok && testResults.local.hints?.steps" class="test-steps">
                <li v-for="(s, i) in testResults.local.hints.steps" :key="i">{{ s }}</li>
              </ul>
            </div>
          </transition>

          <div class="cred-actions">
            <button id="test-local-btn" class="btn btn-ghost" @click="testConnection('local')" :disabled="testing.local || !form.local.username || !form.local.password">
              <span v-if="testing.local" class="spinner"></span>
              <span v-else>🔌</span>
              {{ testing.local ? 'Testing...' : 'Test Local Connection' }}
            </button>
          </div>
        </div>

        <!-- Cloud Credentials -->
        <div class="card settings-card cred-card" :class="{ 'cred-active': form.mode === 'cloud' }">
          <div class="cred-card-header">
            <div class="cred-badge cloud-badge">☁️ Cloud</div>
            <span class="active-tag" v-if="form.mode === 'cloud'">● Active</span>
          </div>
          <h3 class="section-title">Cloud Credentials</h3>
          <p class="field-hint" style="margin-bottom: var(--space-md)">Your <strong>sms-gate.app</strong> account credentials — different from Local credentials.</p>

          <div class="credentials-grid">
            <div class="form-group">
              <label class="form-label" for="cloud-username">Username</label>
              <input id="cloud-username" v-model="form.cloud.username" type="text" class="form-control" placeholder="sms-gate.app username" autocomplete="off" />
            </div>
            <div class="form-group">
              <label class="form-label" for="cloud-password">Password</label>
              <div class="password-wrapper">
                <input id="cloud-password" v-model="form.cloud.password" :type="showCloudPwd ? 'text' : 'password'" class="form-control" placeholder="sms-gate.app password" autocomplete="off" />
                <button type="button" class="password-toggle" @click="showCloudPwd = !showCloudPwd">{{ showCloudPwd ? '🙈' : '👁' }}</button>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" for="cloud-device-id">Device ID</label>
              <input id="cloud-device-id" v-model="form.cloud.deviceId" type="text" class="form-control" placeholder="Device ID (optional)" autocomplete="off" />
            </div>
          </div>

          <transition name="fade">
            <div v-if="testResults.cloud" :class="['test-result', testResults.cloud.ok ? 'test-ok' : 'test-fail']">
              <div class="test-result-row">
                <span class="test-icon">{{ testResults.cloud.ok ? '✅' : '❌' }}</span>
                <div>
                  <div class="test-headline">{{ testResults.cloud.ok ? 'Cloud connection successful!' : (testResults.cloud.hints?.headline || 'Connection failed') }}</div>
                  <div class="test-detail">{{ testResults.cloud.detail }}</div>
                </div>
              </div>
              <div v-if="testResults.cloud.ok" class="auto-saved-note">💾 Cloud credentials auto-saved</div>
              <ul v-if="!testResults.cloud.ok && testResults.cloud.hints?.steps" class="test-steps">
                <li v-for="(s, i) in testResults.cloud.hints.steps" :key="i">{{ s }}</li>
              </ul>
            </div>
          </transition>

          <div class="cred-actions">
            <button id="test-cloud-btn" class="btn btn-ghost" @click="testConnection('cloud')" :disabled="testing.cloud || !form.cloud.username || !form.cloud.password">
              <span v-if="testing.cloud" class="spinner"></span>
              <span v-else>🔌</span>
              {{ testing.cloud ? 'Testing...' : 'Test Cloud Connection' }}
            </button>
          </div>
        </div>

        <!-- Default Message Settings -->
        <div class="card settings-card">
          <h3 class="section-title">⚙️ Default Message Settings</h3>
          <div class="form-group">
            <label class="form-label">Default SIM Card</label>
            <select id="default-sim" v-model="form.simNumber" class="form-control" style="max-width:200px">
              <option :value="null">Auto (Default)</option>
              <option :value="1">SIM 1</option>
              <option :value="2">SIM 2</option>
            </select>
          </div>
          <div class="form-group" style="margin-bottom:0">
            <label class="toggle-label">
              <div class="toggle-switch" :class="{ active: form.withDeliveryReport }" @click="form.withDeliveryReport = !form.withDeliveryReport" id="delivery-report-toggle"></div>
              <span>Request Delivery Report by Default</span>
            </label>
          </div>
        </div>

        <div class="save-row">
          <button id="save-settings-btn" class="btn btn-primary btn-lg" @click="saveSettings">💾 Save All Settings</button>
        </div>
      </div>

      <!-- Info Panel -->
      <div class="info-panel">
        <div class="card">
          <h3 class="section-title">🔑 Credential Differences</h3>
          <div class="cred-diff-list">
            <div class="cred-diff-item">
              <span style="font-size:24px">🏠</span>
              <div>
                <div class="cred-diff-title">Local credentials</div>
                <div class="cred-diff-desc">Auto-generated by the Android app. Shown on its home screen. Changes on reinstall.</div>
              </div>
            </div>
            <div class="cred-diff-item">
              <span style="font-size:24px">☁️</span>
              <div>
                <div class="cred-diff-title">Cloud credentials</div>
                <div class="cred-diff-desc">Your sms-gate.app account. Register once, works across devices.</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 class="section-title">📱 How to Set Up</h3>
          <ol class="setup-steps">
            <li>
              <div class="step-num">1</div>
              <div class="step-content">
                <span class="step-title">Download the App</span>
                <a href="https://github.com/capcom6/android-sms-gateway/releases/latest/download/app-release.apk" target="_blank" class="step-link">Download APK →</a>
              </div>
            </li>
            <li>
              <div class="step-num">2</div>
              <div class="step-content">
                <span class="step-title">Install &amp; open on Android</span>
                <span class="step-desc">Get Local username &amp; password from home screen</span>
              </div>
            </li>
            <li>
              <div class="step-num">3</div>
              <div class="step-content">
                <span class="step-title">For Cloud: register account</span>
                <a href="https://sms-gate.app" target="_blank" class="step-link">sms-gate.app →</a>
              </div>
            </li>
          </ol>
        </div>

        <div class="card">
          <h3 class="section-title">🔗 API Endpoints</h3>
          <div class="endpoint-list">
            <div class="endpoint-item">
              <span class="endpoint-method post">POST</span>
              <code class="endpoint-path">/message</code>
              <span class="endpoint-desc">Send SMS</span>
            </div>
            <div class="endpoint-item">
              <span class="endpoint-method get">GET</span>
              <code class="endpoint-path">/inbox</code>
              <span class="endpoint-desc">Read SMS (Local)</span>
            </div>
            <div class="endpoint-item">
              <span class="endpoint-method get">GET</span>
              <code class="endpoint-path">/health</code>
              <span class="endpoint-desc">Health check</span>
            </div>
          </div>
          <a href="https://docs.sms-gate.app" target="_blank" class="btn btn-ghost btn-sm" style="margin-top:var(--space-md);width:100%">📖 Full API Docs →</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { store, saveConfig } from '../store/index.js'
import { createApiClient, checkHealth } from '../services/smsApi.js'
import { useToast } from '../composables/useToast.js'

const { success, error } = useToast()

const form = reactive({
  mode: store.config.mode,
  local: {
    username: store.config.local.username,
    password: store.config.local.password,
    url:      store.config.local.url,
  },
  cloud: {
    username: store.config.cloud.username,
    password: store.config.cloud.password,
    deviceId: store.config.cloud.deviceId,
  },
  simNumber:          store.config.simNumber,
  withDeliveryReport: store.config.withDeliveryReport,
})

const showLocalPwd = ref(false)
const showCloudPwd = ref(false)
const testing      = reactive({ local: false, cloud: false })
const testResults  = reactive({ local: null,  cloud: null  })

const REASON_HINTS = {
  auth:      { headline: 'Wrong username or password', steps: ['Open the SMS Gateway app', 'Copy the username & password exactly from the home screen — they are case-sensitive'] },
  network:   { headline: 'Device unreachable or CORS blocked', steps: ['Same Wi-Fi required for Local mode', 'Confirm SMS Gateway app is running', 'Check Device URL is correct', 'Try Cloud mode if Local keeps failing'] },
  timeout:   { headline: 'Request timed out', steps: ['SMS Gateway app must be open on phone', 'Check firewall isn\'t blocking port 8080'] },
  not_found: { headline: 'API endpoint not found (404)', steps: ['Default URL format: http://<phone-ip>:8080', 'Check the exact URL in the app home screen'] },
  unknown:   { headline: 'Unexpected error', steps: ['Open browser Console (F12) for details'] },
}

async function testConnection(mode) {
  const creds = form[mode]
  if (!creds.username || !creds.password) return
  testing[mode]     = true
  testResults[mode] = null
  try {
    const tempConfig = { mode, local: { ...form.local }, cloud: { ...form.cloud } }
    const client     = createApiClient(tempConfig)
    const result     = await checkHealth(client)
    const hints      = !result.ok ? (REASON_HINTS[result.reason] || REASON_HINTS.unknown) : null
    testResults[mode] = { ok: result.ok, detail: result.detail, model: result.model || null, hints }
    if (result.ok) {
      const update = { mode: form.mode, [mode]: { ...form[mode] } }
      if (mode === 'local') update.local.deviceModel = result.model || null
      saveConfig(update)
      success(`✅ ${mode === 'local' ? '🏠 Local' : '☁️ Cloud'} connected — credentials saved!`)
    }
  } catch (err) {
    testResults[mode] = { ok: false, detail: err.message || 'Unexpected error', hints: REASON_HINTS.unknown }
  } finally {
    testing[mode] = false
  }
}

function saveSettings() {
  saveConfig({
    mode:               form.mode,
    local:              { ...form.local },
    cloud:              { ...form.cloud },
    simNumber:          form.simNumber,
    withDeliveryReport: form.withDeliveryReport,
  })
  success('✅ Settings saved!')
}
</script>

<style scoped>
.settings-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-xl);
  align-items: start;
}
.settings-main { display: flex; flex-direction: column; gap: var(--space-lg); }
.settings-card { padding: var(--space-xl); }
.section-title { font-size: 15px; font-weight: 700; color: var(--clr-text-primary); margin-bottom: var(--space-lg); }

/* Mode selector */
.mode-selector { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-sm); margin-bottom: var(--space-md); }
.mode-option {
  display: flex; align-items: center; gap: var(--space-md);
  padding: var(--space-md); border-radius: var(--radius-md);
  border: 1px solid var(--clr-border); cursor: pointer;
  transition: all var(--transition-fast);
}
.mode-option:hover { border-color: var(--clr-border-hover); }
.mode-option.active { border-color: var(--clr-accent-primary); background: rgba(108,99,255,0.07); }
.mode-option-icon { font-size: 22px; flex-shrink: 0; }
.mode-option-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.mode-option-title { font-size: 13px; font-weight: 700; color: var(--clr-text-primary); }
.mode-option-desc  { font-size: 11px; color: var(--clr-text-muted); }
.mode-radio { width: 16px; height: 16px; border-radius: 50%; border: 2px solid var(--clr-border); transition: all var(--transition-fast); flex-shrink: 0; }
.mode-radio.selected { border-color: var(--clr-accent-primary); background: var(--clr-accent-primary); }
.mode-hint { font-size: 12px; color: var(--clr-text-muted); padding: 6px 10px; background: rgba(108,99,255,0.05); border-radius: var(--radius-sm); }

/* Credential cards */
.cred-card { border-left: 3px solid var(--clr-border); transition: border-color var(--transition-fast); }
.cred-card.cred-active { border-left-color: var(--clr-accent-primary); }
.cred-card-header { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-sm); }
.cred-badge { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: var(--radius-full); }
.local-badge { background: rgba(0,229,160,0.12); color: var(--clr-accent-success); }
.cloud-badge { background: rgba(108,99,255,0.12); color: var(--clr-accent-primary); }
.active-tag  { font-size: 11px; color: var(--clr-accent-success); font-weight: 700; }

/* Credentials grid */
.credentials-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md); }
.password-wrapper { position: relative; }
.password-wrapper .form-control { padding-right: 44px; }
.password-toggle { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 16px; color: var(--clr-text-muted); }
.password-toggle:hover { color: var(--clr-text-primary); }

/* Test results */
.test-result { margin-top: var(--space-md); border-radius: var(--radius-md); padding: var(--space-md); font-size: 13px; }
.test-ok   { background: rgba(0,229,160,0.06); border: 1px solid rgba(0,229,160,0.25); }
.test-fail { background: rgba(255,94,122,0.06); border: 1px solid rgba(255,94,122,0.25); }
.test-result-row { display: flex; align-items: flex-start; gap: var(--space-sm); }
.test-icon     { font-size: 18px; flex-shrink: 0; }
.test-headline { font-weight: 700; color: var(--clr-text-primary); font-size: 13px; }
.test-detail   { font-size: 12px; color: var(--clr-text-secondary); margin-top: 2px; }
.test-steps    { margin: var(--space-sm) 0 0 var(--space-lg); display: flex; flex-direction: column; gap: 4px; }
.test-steps li { font-size: 12px; color: var(--clr-text-secondary); }
.device-badge  { display: flex; align-items: center; gap: var(--space-sm); margin-top: var(--space-sm); padding: 6px 12px; background: rgba(0,229,160,0.08); border-radius: var(--radius-sm); font-size: 13px; }
.device-badge-icon  { font-size: 16px; }
.device-badge-label { color: var(--clr-text-muted); font-size: 11px; }
.device-badge-model { font-weight: 700; color: var(--clr-accent-success); font-family: var(--font-mono); }
.auto-saved-note { font-size: 11px; color: var(--clr-text-muted); margin-top: var(--space-xs); }

.cred-actions { margin-top: var(--space-md); display: flex; }
.save-row     { display: flex; justify-content: flex-end; }

/* Toggle */
.toggle-label  { display: flex; align-items: center; gap: var(--space-md); cursor: pointer; font-size: 13px; color: var(--clr-text-secondary); }
.toggle-switch { width: 40px; height: 22px; border-radius: var(--radius-full); background: rgba(255,255,255,0.1); border: 1px solid var(--clr-border); position: relative; transition: background var(--transition-fast); flex-shrink: 0; }
.toggle-switch::after { content: ''; position: absolute; width: 16px; height: 16px; border-radius: 50%; background: #fff; top: 2px; left: 2px; transition: left var(--transition-fast); }
.toggle-switch.active { background: var(--clr-accent-primary); border-color: var(--clr-accent-primary); }
.toggle-switch.active::after { left: 20px; }

/* Info panel */
.info-panel { display: flex; flex-direction: column; gap: var(--space-lg); }
.info-panel .card { padding: var(--space-lg) var(--space-xl); }

/* Cred diff */
.cred-diff-list { display: flex; flex-direction: column; gap: var(--space-md); }
.cred-diff-item { display: flex; align-items: flex-start; gap: var(--space-md); }
.cred-diff-title { font-size: 13px; font-weight: 700; color: var(--clr-text-primary); margin-bottom: 2px; }
.cred-diff-desc  { font-size: 12px; color: var(--clr-text-secondary); line-height: 1.5; }

/* Setup steps */
.setup-steps { list-style: none; display: flex; flex-direction: column; gap: var(--space-md); }
.setup-steps li { display: flex; align-items: flex-start; gap: var(--space-md); }
.step-num { width: 24px; height: 24px; border-radius: 50%; background: var(--gradient-primary); color: #fff; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.step-content { display: flex; flex-direction: column; gap: 2px; }
.step-title { font-size: 13px; font-weight: 600; color: var(--clr-text-primary); }
.step-desc  { font-size: 12px; color: var(--clr-text-secondary); }
.step-link  { font-size: 12px; color: var(--clr-accent-primary); text-decoration: none; }
.step-link:hover { text-decoration: underline; }

/* Endpoints */
.endpoint-list { display: flex; flex-direction: column; gap: var(--space-sm); }
.endpoint-item { display: flex; align-items: center; gap: var(--space-sm); font-size: 12px; }
.endpoint-method { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: var(--radius-sm); font-family: var(--font-mono); }
.endpoint-method.post { background: rgba(108,99,255,0.15); color: var(--clr-accent-primary); }
.endpoint-method.get  { background: rgba(0,229,160,0.15);  color: var(--clr-accent-success); }
.endpoint-path { font-family: var(--font-mono); color: var(--clr-text-secondary); }
.endpoint-desc { color: var(--clr-text-muted); }

.field-hint { font-size: 12px; color: var(--clr-text-muted); margin-top: var(--space-xs); }
.btn-sm { padding: 6px 14px; font-size: 13px; }
.btn-lg { padding: 12px 28px; font-size: 15px; }

@media (max-width: 900px) {
  .settings-layout    { grid-template-columns: 1fr; }
  .credentials-grid   { grid-template-columns: 1fr; }
  .mode-selector      { grid-template-columns: 1fr; }
}
</style>
