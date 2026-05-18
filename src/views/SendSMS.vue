<template>
  <div class="animate-in">
    <div class="page-header">
      <h1 class="page-title">Send SMS</h1>
      <p class="page-subtitle">Compose and send messages via your Android device</p>
    </div>

    <!-- Not configured warning -->
    <div v-if="!store.isConfigured" class="not-configured card">
      <span style="font-size:32px">🔌</span>
      <div>
        <h3>Gateway Not Configured</h3>
        <p>Please configure your SMS Gateway credentials in Settings before sending messages.</p>
      </div>
      <router-link to="/settings" class="btn btn-primary">Go to Settings</router-link>
    </div>

    <div v-else class="send-layout">
      <!-- Compose Form -->
      <div class="card compose-card">
        <h3 class="section-title">✉️ Compose Message</h3>

        <form @submit.prevent="sendMessage" id="sms-form">
          <!-- Recipients -->
          <div class="form-group">
            <label class="form-label">Recipients</label>

            <!-- Phone input with add -->
            <div class="phone-input-row">
              <input
                id="phone-input"
                v-model="phoneInput"
                type="tel"
                class="form-control"
                placeholder="+1 234 567 8900"
                @keydown.enter.prevent="addPhone"
                @keydown.comma.prevent="addPhone"
                autocomplete="off"
              />
              <button type="button" class="btn btn-ghost" @click="addPhone" id="add-phone-btn">
                + Add
              </button>
              <button type="button" class="btn btn-ghost btn-contacts" @click="showContacts = true" id="import-contacts-btn" title="Import from contacts">
                👥 Contacts
              </button>
            </div>

            <!-- Tags -->
            <div v-if="phoneNumbers.length > 0" class="phone-tags">
              <span
                v-for="(num, i) in phoneNumbers"
                :key="i"
                class="phone-tag"
              >
                📱 {{ num }}
                <span class="remove-btn" @click="removePhone(i)">✕</span>
              </span>
            </div>

            <p v-if="phoneNumbers.length === 0" class="field-hint">
              Type a number and press Enter or click "+ Add". Supports multiple recipients.
            </p>
            <p v-else class="field-hint">{{ phoneNumbers.length }} recipient(s) added</p>
          </div>

          <!-- Message -->
          <div class="form-group">
            <label class="form-label" for="msg-input">
              Message
              <span class="char-count" :class="{ over: message.length > 160 }">
                {{ message.length }}/160
                <span v-if="message.length > 160"> ({{ Math.ceil(message.length / 153) }} parts)</span>
              </span>
            </label>
            <textarea
              id="msg-input"
              v-model="message"
              class="form-control"
              placeholder="Type your message here..."
              rows="5"
              required
            ></textarea>
          </div>

          <!-- Advanced Options -->
          <div class="advanced-toggle" @click="showAdvanced = !showAdvanced">
            <span>⚙️ Advanced Options</span>
            <span class="toggle-arrow">{{ showAdvanced ? '▲' : '▼' }}</span>
          </div>

          <transition name="fade">
            <div v-if="showAdvanced" class="advanced-opts">

              <!-- Row 1: SIM + Priority -->
              <div class="opts-grid">
                <div class="form-group">
                  <label class="form-label">SIM Card</label>
                  <select id="sim-select" v-model="simNumber" class="form-control">
                    <option :value="null">Auto (Default)</option>
                    <option :value="1">SIM 1</option>
                    <option :value="2">SIM 2</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">Priority</label>
                  <select id="priority-select" v-model.number="priority" class="form-control">
                    <option :value="0">Normal (0)</option>
                    <option :value="50">High (50)</option>
                    <option :value="100">Urgent — skip delays (100)</option>
                  </select>
                </div>
              </div>

              <!-- Row 2: TTL -->
              <div class="form-group">
                <label class="form-label">TTL (seconds) — auto-expire after this time if undelivered</label>
                <input
                  id="ttl-input"
                  v-model.number="ttl"
                  type="number"
                  class="form-control"
                  placeholder="e.g. 3600 = 1 hour, 86400 = 24 hours"
                  min="60"
                />
              </div>

              <!-- Row 3: Schedule Toggle -->
              <div class="form-group">
                <label class="toggle-label">
                  <div class="toggle-switch" :class="{ active: useSchedule }" @click="useSchedule = !useSchedule" id="schedule-toggle"></div>
                  <span>⏰ Schedule Message</span>
                </label>
              </div>

              <!-- Schedule Datetime Picker -->
              <transition name="fade">
                <div v-if="useSchedule" class="schedule-picker">
                  <div class="form-group" style="margin-bottom:0">
                    <label class="form-label" for="schedule-input">Send At (your local time)</label>
                    <input
                      id="schedule-input"
                      v-model="scheduleAt"
                      type="datetime-local"
                      class="form-control"
                      :min="minDateTime"
                    />
                  </div>
                  <p class="schedule-note">
                    ℹ️ Requires SMS Gateway app v1.41.0+ · Will be queued and sent at the specified time.
                  </p>
                  <div v-if="scheduleAt" class="schedule-preview">
                    <span>🕐</span>
                    <span>Scheduled for: <strong>{{ formatSchedulePreview(scheduleAt) }}</strong></span>
                    <span class="schedule-utc">(UTC: {{ toUtcPreview(scheduleAt) }})</span>
                  </div>
                </div>
              </transition>

              <!-- Row 4: Delivery Report -->
              <div class="form-group" style="margin-bottom:0; margin-top: var(--space-sm)">
                <label class="toggle-label">
                  <div class="toggle-switch" :class="{ active: withDeliveryReport }" @click="withDeliveryReport = !withDeliveryReport" id="delivery-toggle"></div>
                  <span>Request Delivery Report</span>
                </label>
              </div>

            </div>
          </transition>

          <!-- Send / Schedule Button -->
          <button
            type="submit"
            id="send-btn"
            :class="['btn', 'btn-lg', 'btn-block', useSchedule && scheduleAt ? 'btn-schedule' : 'btn-primary']"
            :disabled="isSending || phoneNumbers.length === 0 || !message.trim() || (useSchedule && !scheduleAt)"
            style="margin-top: 8px;"
          >
            <span v-if="isSending" class="spinner"></span>
            <span v-else>{{ useSchedule && scheduleAt ? '⏰' : '📤' }}</span>
            <span v-if="isSending">Sending...</span>
            <span v-else-if="useSchedule && scheduleAt">Schedule for {{ formatSchedulePreview(scheduleAt) }}</span>
            <span v-else>Send to {{ phoneNumbers.length || 0 }} recipient(s)</span>
          </button>
        </form>
      </div>

      <!-- Result Panel -->
      <div class="result-panel">
        <!-- Sending Tips -->
        <div class="card tips-card">
          <h3 class="section-title">💡 Tips</h3>
          <ul class="tips-list">
            <li>Use international format: <code>+1234567890</code></li>
            <li>Add multiple recipients for bulk SMS</li>
            <li>Messages over 160 chars are split automatically</li>
            <li>Enable delivery report to track message status</li>
          </ul>
        </div>

        <!-- Last Result -->
        <transition name="fade">
          <div v-if="lastResult" class="card result-card" :class="lastResult.success ? 'result-success' : 'result-error'">
            <div class="result-header">
              <span class="result-icon">{{ lastResult.success ? '✅' : '❌' }}</span>
              <h3>{{ lastResult.success ? 'Message Sent!' : 'Send Failed' }}</h3>
            </div>

            <div v-if="lastResult.success" class="result-details">
              <div class="result-row">
                <span class="result-key">Message ID</span>
                <code class="result-val">{{ lastResult.data.id }}</code>
              </div>
              <div class="result-row">
                <span class="result-key">State</span>
                <span :class="['badge', lastResult.data.state === 'Scheduled' ? 'badge-info' : 'badge-success']">
                  {{ lastResult.data.state }}
                </span>
              </div>
              <div v-if="lastResult.scheduledFor" class="result-row">
                <span class="result-key">Scheduled</span>
                <span class="result-scheduled">⏰ {{ lastResult.scheduledFor }}</span>
              </div>
              <div v-if="lastResult.data.recipients?.length > 0" class="result-row">
                <span class="result-key">Recipients</span>
                <div class="result-recipients">
                  <div
                    v-for="r in lastResult.data.recipients"
                    :key="r.phoneNumber"
                    class="recipient-status"
                  >
                    <span class="recipient-phone">{{ r.phoneNumber }}</span>
                    <span :class="['badge', r.state === 'Pending' ? 'badge-warning' : 'badge-success']">
                      {{ r.state }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="result-error-msg">
              <p>{{ lastResult.error }}</p>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>

  <!-- Contact Import Modal -->
  <ContactImportModal
    v-model="showContacts"
    @select="onContactsSelected"
  />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { store, addToHistory } from '../store/index.js'
import { sendMessage as apiSendMessage } from '../services/smsApi.js'
import { useToast } from '../composables/useToast.js'
import ContactImportModal from '../components/ContactImportModal.vue'

const route = useRoute()
const { success, error } = useToast()

const showContacts = ref(false)

function onContactsSelected(phones) {
  for (const phone of phones) {
    if (!phoneNumbers.value.includes(phone)) {
      phoneNumbers.value.push(phone)
    }
  }
}

const phoneInput = ref('')
const phoneNumbers = ref([])
const message = ref('')
const simNumber = ref(null)
const priority = ref(0)
const withDeliveryReport = ref(true)
const ttl = ref(null)
const useSchedule = ref(false)
const scheduleAt = ref('')   // datetime-local value (local time)
const showAdvanced = ref(false)
const isSending = ref(false)
const lastResult = ref(null)

// Pre-fill recipient when coming from Inbox "Reply" button (?to=+123456)
onMounted(() => {
  const to = route.query.to
  if (to && !phoneNumbers.value.includes(to)) {
    phoneNumbers.value.push(to)
    showAdvanced.value = false
  }
})

// Minimum datetime = now + 1 minute (for the datetime-local input min attr)
const minDateTime = computed(() => {
  const d = new Date(Date.now() + 60_000)
  // Format as YYYY-MM-DDTHH:mm (datetime-local format)
  return d.toISOString().slice(0, 16)
})

function formatSchedulePreview(localDt) {
  if (!localDt) return ''
  return new Date(localDt).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
}

function toUtcPreview(localDt) {
  if (!localDt) return ''
  return new Date(localDt).toISOString().replace('T', ' ').slice(0, 16) + ' UTC'
}

function addPhone() {
  const raw = phoneInput.value.trim().replace(/[,\s]+$/, '')
  if (!raw) return
  // Basic phone format cleanup
  const nums = raw.split(/[,\s]+/).map(n => n.trim()).filter(Boolean)
  for (const num of nums) {
    if (num && !phoneNumbers.value.includes(num)) {
      phoneNumbers.value.push(num)
    }
  }
  phoneInput.value = ''
}

function removePhone(index) {
  phoneNumbers.value.splice(index, 1)
}

async function sendMessage() {
  if (!store.apiClient || phoneNumbers.value.length === 0 || !message.value.trim()) return
  if (useSchedule.value && !scheduleAt.value) return

  isSending.value = true
  lastResult.value = null

  try {
    const payload = {
      message: message.value.trim(),
      phoneNumbers: phoneNumbers.value,
      withDeliveryReport: withDeliveryReport.value,
      priority: priority.value,
    }
    if (simNumber.value !== null) payload.simNumber = simNumber.value
    if (ttl.value) payload.ttl = ttl.value

    // if (store.config.mode === 'cloud' && store.config.cloud.deviceId) {
    //   payload.deviceId = store.config.cloud.deviceId
    // }

    // Convert local datetime to UTC ISO string for the API
    let scheduledFor = null
    if (useSchedule.value && scheduleAt.value) {
      const utcIso = new Date(scheduleAt.value).toISOString()
      payload.scheduleAt = utcIso
      scheduledFor = formatSchedulePreview(scheduleAt.value)
    }

    const data = await apiSendMessage(store.apiClient, payload)
    lastResult.value = { success: true, data, scheduledFor }
    addToHistory({
      ...data,
      message: message.value,
      phoneNumbers: phoneNumbers.value,
      scheduledFor,
    })

    if (scheduledFor) {
      success(`⏰ Message scheduled for ${scheduledFor}`)
    } else {
      success(`✉️ Message sent to ${phoneNumbers.value.length} recipient(s)!`)
    }

    // Reset form
    message.value = ''
    phoneNumbers.value = []
    scheduleAt.value = ''
    useSchedule.value = false
  } catch (err) {
    const errMsg = err.response?.data?.message || err.message || 'Failed to send message'
    lastResult.value = { success: false, error: errMsg }
    error(`❌ ${errMsg}`)
  } finally {
    isSending.value = false
  }
}
</script>

<style scoped>
.not-configured {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-xl);
  background: rgba(255, 179, 71, 0.05);
  border-color: rgba(255, 179, 71, 0.25);
}

.not-configured h3 {
  color: var(--clr-accent-warning);
  margin-bottom: 4px;
}

.not-configured p {
  font-size: 13px;
  color: var(--clr-text-secondary);
}

.send-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: var(--space-xl);
  align-items: start;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--clr-text-primary);
  margin-bottom: var(--space-xl);
}

.phone-input-row {
  display: flex;
  gap: var(--space-sm);
}

.phone-input-row .form-control {
  flex: 1;
}

.btn-contacts {
  background: rgba(108, 99, 255, 0.1) !important;
  border-color: rgba(108, 99, 255, 0.3) !important;
  color: var(--clr-accent-primary) !important;
  white-space: nowrap;
}
.btn-contacts:hover {
  background: rgba(108, 99, 255, 0.2) !important;
}


.phone-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  margin-top: var(--space-sm);
}

.field-hint {
  font-size: 12px;
  color: var(--clr-text-muted);
  margin-top: var(--space-xs);
}

.char-count {
  float: right;
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--clr-text-muted);
}

.char-count.over {
  color: var(--clr-accent-warning);
}

.advanced-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-sm) var(--space-md);
  background: rgba(108, 99, 255, 0.06);
  border: 1px solid var(--clr-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 13px;
  color: var(--clr-text-secondary);
  margin-bottom: var(--space-md);
  transition: all var(--transition-fast);
}

.advanced-toggle:hover {
  border-color: var(--clr-border-hover);
  color: var(--clr-text-primary);
}

.toggle-arrow {
  font-size: 11px;
}

.advanced-opts {
  padding: var(--space-md);
  background: rgba(108, 99, 255, 0.04);
  border: 1px solid var(--clr-border);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
}

.opts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  cursor: pointer;
  font-size: 13px;
  color: var(--clr-text-secondary);
}

.toggle-switch {
  width: 40px;
  height: 22px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--clr-border);
  position: relative;
  transition: background var(--transition-fast);
  flex-shrink: 0;
}

.toggle-switch::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  top: 2px;
  left: 2px;
  transition: left var(--transition-fast);
}

.toggle-switch.active {
  background: var(--clr-accent-primary);
  border-color: var(--clr-accent-primary);
}

.toggle-switch.active::after {
  left: 20px;
}

/* Result panel */
.result-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.tips-card {
  padding: var(--space-lg) var(--space-xl);
}

.tips-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.tips-list li {
  font-size: 13px;
  color: var(--clr-text-secondary);
  padding-left: 16px;
  position: relative;
}

.tips-list li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--clr-accent-primary);
}

.tips-list code {
  font-family: var(--font-mono);
  background: rgba(108, 99, 255, 0.1);
  padding: 1px 6px;
  border-radius: 4px;
  color: var(--clr-accent-primary);
  font-size: 12px;
}

.result-card {
  padding: var(--space-lg);
}

.result-success {
  border-color: rgba(0, 229, 160, 0.3);
  background: rgba(0, 229, 160, 0.05);
}

.result-error {
  border-color: rgba(255, 94, 122, 0.3);
  background: rgba(255, 94, 122, 0.05);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.result-header h3 {
  font-size: 15px;
  font-weight: 700;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.result-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md);
}

.result-key {
  font-size: 12px;
  color: var(--clr-text-muted);
  min-width: 90px;
  flex-shrink: 0;
  padding-top: 2px;
}

.result-val {
  font-family: var(--font-mono);
  font-size: 12px;
  background: rgba(108, 99, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--clr-accent-primary);
  word-break: break-all;
}

.result-recipients {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recipient-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.recipient-phone {
  font-family: var(--font-mono);
  color: var(--clr-text-secondary);
}

.result-error-msg p {
  font-size: 13px;
  color: var(--clr-accent-danger);
}

@media (max-width: 900px) {
  .send-layout {
    grid-template-columns: 1fr;
  }
}

/* Schedule picker */
.schedule-picker {
  background: rgba(255, 179, 71, 0.05);
  border: 1px solid rgba(255, 179, 71, 0.2);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  margin-top: calc(-1 * var(--space-sm));
  margin-bottom: var(--space-sm);
}

.schedule-note {
  font-size: 11px;
  color: var(--clr-text-muted);
  line-height: 1.5;
}

.schedule-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  padding: 6px 10px;
  background: rgba(255, 179, 71, 0.12);
  border: 1px solid rgba(255, 179, 71, 0.3);
  border-radius: var(--radius-sm);
  color: var(--clr-accent-warning);
}

.schedule-preview strong {
  font-weight: 700;
}

.schedule-utc {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--clr-text-muted);
  margin-left: auto;
}

/* Schedule (amber) send button */
.btn-schedule {
  background: linear-gradient(135deg, #ff9800, #ff6f00);
  color: #fff;
  border: none;
  box-shadow: 0 4px 20px rgba(255, 152, 0, 0.35);
  transition: all var(--transition-fast);
}

.btn-schedule:hover:not(:disabled) {
  box-shadow: 0 6px 28px rgba(255, 152, 0, 0.5);
  transform: translateY(-1px);
}

/* Result scheduled time */
.result-scheduled {
  font-size: 13px;
  color: var(--clr-accent-warning);
  font-weight: 600;
}

/* badge-info for Scheduled state */
:deep(.badge-info) {
  background: rgba(100, 180, 255, 0.15);
  color: #64b4ff;
}
</style>
