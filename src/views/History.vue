<template>
  <div class="animate-in">
    <div class="page-header">
      <h1 class="page-title">Message History</h1>
      <p class="page-subtitle">All sent SMS messages and their delivery status</p>
    </div>

    <!-- Toolbar -->
    <div class="history-toolbar card" style="margin-bottom: var(--space-xl);">
      <div class="toolbar-left">
        <input
          id="search-input"
          v-model="searchQuery"
          type="text"
          class="form-control search-input"
          placeholder="🔍 Search messages or phone numbers..."
        />
        <select id="status-filter" v-model="statusFilter" class="form-control filter-select">
          <option value="">All Status</option>
          <option value="Sent">Sent</option>
          <option value="Delivered">Delivered</option>
          <option value="Pending">Pending</option>
          <option value="Failed">Failed</option>
        </select>
      </div>
      <div class="toolbar-right">
        <span class="msg-count">{{ filteredHistory.length }} message(s)</span>
        <button
          v-if="store.history.length > 0"
          id="clear-history-btn"
          class="btn btn-danger btn-sm"
          @click="confirmClear"
        >
          🗑 Clear All
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredHistory.length === 0" class="empty-state card">
      <div class="empty-icon">📭</div>
      <p v-if="store.history.length === 0">No messages sent yet. <router-link to="/send">Send your first SMS →</router-link></p>
      <p v-else>No messages match your search.</p>
    </div>

    <!-- Table -->
    <div v-else class="card" style="padding: 0;">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Recipients</th>
              <th>Message</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="msg in paginatedHistory" :key="msg.id">
              <td class="time-cell">
                <div class="time-date">{{ formatDate(msg.sentAt) }}</div>
                <div class="time-clock">{{ formatClock(msg.sentAt) }}</div>
              </td>
              <td>
                <div class="phone-list">
                  <span
                    v-for="(num, i) in msg.phoneNumbers"
                    :key="i"
                    class="phone-tag"
                  >
                    {{ num }}
                  </span>
                </div>
              </td>
              <td class="msg-cell">{{ truncate(msg.message, 70) }}</td>
              <td>
                <span :class="['badge', statusBadge(msg.status)]">{{ msg.status }}</span>
              </td>
              <td>
                <div style="display: flex; gap: var(--space-xs);">
                  <button
                    class="btn btn-ghost btn-sm btn-icon"
                    @click="viewDetail(msg)"
                    :id="`view-${msg.id}`"
                    title="View details"
                  >
                    👁
                  </button>
                  <button
                    v-if="store.isConfigured && msg.id"
                    class="btn btn-ghost btn-sm btn-icon"
                    :disabled="isRefreshing"
                    @click="refreshStatus(msg.id)"
                    title="Refresh status"
                  >
                    <span v-if="isRefreshing" class="spinner btn-spinner-sm"></span>
                    <span v-else>🔄</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button class="btn btn-ghost btn-sm" :disabled="currentPage <= 1" @click="currentPage--">◀ Prev</button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button class="btn btn-ghost btn-sm" :disabled="currentPage >= totalPages" @click="currentPage++">Next ▶</button>
      </div>
    </div>

    <!-- Detail Modal -->
    <transition name="fade">
      <div v-if="selectedMsg" class="modal-overlay" @click.self="selectedMsg = null">
        <div class="modal-card card animate-in">
          <div class="modal-header">
            <h3>Message Details</h3>
            <button class="btn btn-ghost btn-icon" @click="selectedMsg = null">✕</button>
          </div>

          <div class="detail-row">
            <span class="detail-key">ID</span>
            <code class="detail-val">{{ selectedMsg.id }}</code>
          </div>
          <div class="detail-row">
            <span class="detail-key">Sent At</span>
            <span class="detail-val">{{ new Date(selectedMsg.sentAt).toLocaleString() }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-key">Status</span>
            <div class="detail-status-wrapper">
              <span :class="['badge', statusBadge(selectedMsg.status)]">{{ selectedMsg.status }}</span>
              <button
                v-if="store.isConfigured && selectedMsg.id"
                class="btn btn-ghost btn-sm refresh-status-btn"
                :disabled="isRefreshing"
                @click="refreshStatus(selectedMsg.id)"
              >
                <span v-if="isRefreshing" class="spinner btn-spinner-sm"></span>
                <span v-else>🔄</span>
                <span>Refresh Status</span>
              </button>
            </div>
          </div>
          <div class="detail-row">
            <span class="detail-key">Recipients</span>
            <div class="detail-phones">
              <span v-for="(num, i) in selectedMsg.phoneNumbers" :key="i" class="phone-tag">{{ num }}</span>
            </div>
          </div>
          <div class="detail-row">
            <span class="detail-key">Message</span>
            <div class="detail-message">{{ selectedMsg.message }}</div>
          </div>

          <div v-if="selectedMsg.results?.length > 0">
            <div class="detail-row">
              <span class="detail-key">Per-Recipient</span>
            </div>
            <div class="recipient-details">
              <div v-for="r in selectedMsg.results" :key="r.phoneNumber" class="recipient-row">
                <span class="recipient-number">{{ r.phoneNumber }}</span>
                <span :class="['badge', r.state === 'Delivered' ? 'badge-success' : r.state === 'Failed' ? 'badge-danger' : 'badge-warning']">
                  {{ r.state }}
                </span>
                <span v-if="r.error" class="recipient-error">{{ r.error }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { store, clearHistory, refreshMessageStatus } from '../store/index.js'
import { useToast } from '../composables/useToast.js'

const { success, error } = useToast()

const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const perPage = 10
const selectedMsg = ref(null)
const isRefreshing = ref(false)

async function refreshStatus(id) {
  if (isRefreshing.value) return
  isRefreshing.value = true
  try {
    const res = await refreshMessageStatus(id)
    success(`Status updated: ${res.status}`)
    if (selectedMsg.value && selectedMsg.value.id === id) {
      selectedMsg.value.status = res.status
      selectedMsg.value.results = res.results
    }
  } catch (err) {
    const errMsg = err.response?.data?.message || err.message || 'Failed to update status'
    error(`❌ ${errMsg}`)
  } finally {
    isRefreshing.value = false
  }
}

const filteredHistory = computed(() => {
  let list = store.history
  if (statusFilter.value) list = list.filter(m => m.status === statusFilter.value)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(m =>
      m.message.toLowerCase().includes(q) ||
      m.phoneNumbers.some(p => p.includes(q))
    )
  }
  return list
})

const totalPages = computed(() => Math.ceil(filteredHistory.value.length / perPage))

const paginatedHistory = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredHistory.value.slice(start, start + perPage)
})

function statusBadge(status) {
  const map = { Sent: 'badge-success', Delivered: 'badge-success', Pending: 'badge-warning', Failed: 'badge-danger' }
  return map[status] || 'badge-info'
}

function truncate(str, len) {
  return str.length > len ? str.substring(0, len) + '…' : str
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString()
}

function formatClock(iso) {
  return new Date(iso).toLocaleTimeString()
}

function viewDetail(msg) {
  selectedMsg.value = msg
}

function confirmClear() {
  if (window.confirm('Clear all message history? This cannot be undone.')) {
    clearHistory()
    success('History cleared')
  }
}
</script>

<style scoped>
.history-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  gap: var(--space-sm);
  flex: 1;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.filter-select {
  width: 140px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.msg-count {
  font-size: 13px;
  color: var(--clr-text-muted);
}

.time-cell {
  white-space: nowrap;
}

.time-date {
  font-size: 13px;
  color: var(--clr-text-primary);
}

.time-clock {
  font-size: 12px;
  color: var(--clr-text-muted);
}

.phone-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.msg-cell {
  max-width: 300px;
  color: var(--clr-text-secondary);
  font-size: 13px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--clr-border);
}

.page-info {
  font-size: 13px;
  color: var(--clr-text-muted);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-xl);
}

.modal-card {
  width: 100%;
  max-width: 540px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 700;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-lg);
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--clr-border);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-key {
  font-size: 12px;
  color: var(--clr-text-muted);
  min-width: 90px;
  flex-shrink: 0;
  padding-top: 3px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-val {
  font-size: 13px;
  color: var(--clr-text-primary);
}

code.detail-val {
  font-family: var(--font-mono);
  background: rgba(108, 99, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--clr-accent-primary);
  font-size: 12px;
  word-break: break-all;
}

.detail-phones {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.detail-message {
  font-size: 14px;
  color: var(--clr-text-primary);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.recipient-details {
  padding: var(--space-sm) 0;
}

.recipient-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 6px 0;
  border-bottom: 1px solid var(--clr-border);
}

.recipient-row:last-child {
  border-bottom: none;
}

.recipient-number {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--clr-text-secondary);
  flex: 1;
}

.recipient-error {
  font-size: 12px;
  color: var(--clr-accent-danger);
}

.empty-state a {
  color: var(--clr-accent-primary);
  text-decoration: none;
}

.empty-state a:hover {
  text-decoration: underline;
}

.detail-status-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.refresh-status-btn {
  font-size: 11px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  height: auto;
  color: var(--clr-accent-primary);
  background: rgba(108, 99, 255, 0.05);
  border: 1px solid var(--clr-border);
}

.refresh-status-btn:hover:not(:disabled) {
  background: rgba(108, 99, 255, 0.12);
  border-color: var(--clr-border-hover);
}

.btn-spinner-sm {
  width: 12px;
  height: 12px;
  border-width: 1.5px;
  border-top-color: var(--clr-accent-primary);
}
</style>
