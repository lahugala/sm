<template>
  <div class="animate-in">
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Overview of your SMS Gateway activity</p>
    </div>

    <!-- Configuration Warning -->
    <div v-if="!store.isConfigured" class="config-warning card">
      <div class="warning-icon"><AlertTriangle :size="28" class="icon-warning" /></div>
      <div class="warning-content">
        <h3>Gateway Not Configured</h3>
        <p>Set up your Android SMS Gateway credentials to start sending messages.</p>
      </div>
      <router-link to="/settings" class="btn btn-primary">Configure Now</router-link>
    </div>

    <!-- Stats Grid -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(108,99,255,0.15)"><Send :size="22" class="icon-primary" /></div>
        <div class="stat-value">{{ store.totalSent }}</div>
        <div class="stat-label">Total Messages Sent</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(0,229,160,0.15)"><Users :size="22" class="icon-success" /></div>
        <div class="stat-value">{{ store.totalRecipients }}</div>
        <div class="stat-label">Total Recipients</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(0,229,160,0.15)"><CheckCircle :size="22" class="icon-success" /></div>
        <div class="stat-value">{{ store.successCount }}</div>
        <div class="stat-label">Successful</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: rgba(255,94,122,0.15)"><XCircle :size="22" class="icon-danger" /></div>
        <div class="stat-value">{{ store.failedCount }}</div>
        <div class="stat-label">Failed</div>
      </div>
    </div>

    <!-- Two Columns -->
    <div class="dash-grid">
      <!-- Recent Messages -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Recent Messages</h3>
          <router-link to="/history" class="btn btn-ghost btn-sm">View All</router-link>
        </div>

        <div v-if="recentHistory.length === 0" class="empty-state">
          <div class="empty-icon"><InboxIcon :size="36" class="icon-muted" /></div>
          <p>No messages sent yet</p>
        </div>

        <div v-else class="recent-list">
          <div v-for="msg in recentHistory" :key="msg.id" class="recent-item">
            <div class="recent-meta">
              <span class="recent-phones">{{ msg.phoneNumbers.join(', ') }}</span>
              <span :class="['badge', statusBadge(msg.status)]">{{ msg.status }}</span>
            </div>
            <p class="recent-text">{{ truncate(msg.message, 80) }}</p>
            <span class="recent-time">{{ formatTime(msg.sentAt) }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Quick Actions</h3>
        </div>
        <div class="quick-actions">
          <router-link to="/send" class="quick-action-item" id="qa-send">
            <div class="qa-icon" style="background: rgba(108,99,255,0.15)"><Send :size="20" class="icon-primary" /></div>
            <div class="qa-info">
              <span class="qa-title">Send SMS</span>
              <span class="qa-desc">Single or bulk message</span>
            </div>
            <ChevronRight :size="16" class="qa-arrow" />
          </router-link>

          <router-link to="/history" class="quick-action-item" id="qa-history">
            <div class="qa-icon" style="background: rgba(79,195,247,0.15)"><Clock :size="20" class="icon-info" /></div>
            <div class="qa-info">
              <span class="qa-title">Message History</span>
              <span class="qa-desc">View sent messages</span>
            </div>
            <ChevronRight :size="16" class="qa-arrow" />
          </router-link>

          <router-link to="/settings" class="quick-action-item" id="qa-settings">
            <div class="qa-icon" style="background: rgba(0,229,160,0.15)"><SettingsIcon :size="20" class="icon-success" /></div>
            <div class="qa-info">
              <span class="qa-title">Settings</span>
              <span class="qa-desc">Configure gateway</span>
            </div>
            <ChevronRight :size="16" class="qa-arrow" />
          </router-link>
        </div>

        <!-- Mode info -->
        <div class="mode-info card" style="margin-top: 20px; background: rgba(108,99,255,0.05);">
          <div class="mode-info-header">
            <span class="mode-badge" :class="store.config.mode === 'local' ? 'badge-success' : 'badge-info'">
              <Wifi v-if="store.config.mode === 'local'" :size="12" style="display:inline;vertical-align:middle;margin-right:4px" />
              <Cloud v-else :size="12" style="display:inline;vertical-align:middle;margin-right:4px" />
              {{ store.config.mode === 'local' ? 'Local Mode' : 'Cloud Mode' }}
            </span>
          </div>
          <p v-if="store.config.mode === 'local'" class="mode-desc">
            Connected directly to your Android device on your local network.
          </p>
          <p v-else class="mode-desc">
            Using the SMS Gate cloud relay server for remote access.
          </p>
          <p class="mode-url">
            <span>API: </span>
            <code>{{ store.config.mode === 'local' ? store.config.local.url : 'api.sms-gate.app' }}</code>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { store } from '../store/index.js'
import {
  Send, Users, CheckCircle, XCircle, Clock,
  AlertTriangle, Inbox as InboxIcon, Settings as SettingsIcon,
  ChevronRight, Wifi, Cloud
} from 'lucide-vue-next'

const recentHistory = computed(() => store.history.slice(0, 5))

function statusBadge(status) {
  const map = {
    Sent: 'badge-success',
    Delivered: 'badge-success',
    Pending: 'badge-warning',
    Failed: 'badge-danger',
  }
  return map[status] || 'badge-info'
}

function truncate(str, len) {
  return str.length > len ? str.substring(0, len) + '...' : str
}

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}
</script>

<style scoped>
.config-warning {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
  background: rgba(255, 179, 71, 0.05);
  border-color: rgba(255, 179, 71, 0.3);
  padding: var(--space-lg) var(--space-xl);
}

.warning-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

/* Icon color utilities */
.icon-primary { color: var(--clr-accent-primary); }
.icon-success { color: var(--clr-accent-success); }
.icon-danger  { color: var(--clr-accent-danger); }
.icon-warning { color: var(--clr-accent-warning); }
.icon-info    { color: #4fc3f7; }
.icon-muted   { color: var(--clr-text-muted); }


.warning-content {
  flex: 1;
}

.warning-content h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--clr-accent-warning);
  margin-bottom: 4px;
}

.warning-content p {
  font-size: 13px;
  color: var(--clr-text-secondary);
}

.dash-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--clr-text-primary);
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.recent-item {
  padding: var(--space-md);
  border-radius: var(--radius-md);
  background: rgba(108, 99, 255, 0.04);
  border: 1px solid var(--clr-border);
  transition: background var(--transition-fast);
}

.recent-item:hover {
  background: rgba(108, 99, 255, 0.08);
}

.recent-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.recent-phones {
  font-size: 13px;
  font-family: var(--font-mono);
  color: var(--clr-accent-secondary);
  font-weight: 500;
}

.recent-text {
  font-size: 13px;
  color: var(--clr-text-secondary);
  margin-bottom: 4px;
}

.recent-time {
  font-size: 11px;
  color: var(--clr-text-muted);
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.quick-action-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--clr-border);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.quick-action-item:hover {
  border-color: var(--clr-border-hover);
  background: rgba(108, 99, 255, 0.06);
}

.qa-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.qa-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.qa-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--clr-text-primary);
}

.qa-desc {
  font-size: 12px;
  color: var(--clr-text-muted);
}

.qa-arrow {
  color: var(--clr-text-muted);
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.mode-info {
  border-color: rgba(108, 99, 255, 0.1) !important;
}

.mode-info-header {
  margin-bottom: var(--space-sm);
}

.mode-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.mode-desc {
  font-size: 13px;
  color: var(--clr-text-secondary);
  margin-bottom: var(--space-sm);
}

.mode-url {
  font-size: 12px;
  color: var(--clr-text-muted);
}

.mode-url code {
  font-family: var(--font-mono);
  background: rgba(108, 99, 255, 0.1);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  color: var(--clr-accent-primary);
}

@media (max-width: 900px) {
  .dash-grid {
    grid-template-columns: 1fr;
  }
}
</style>
