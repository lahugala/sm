<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-icon">
        <MessageSquare :size="22" stroke-width="2" />
      </div>
      <transition name="fade">
        <div v-if="!isCollapsed" class="logo-text">
          <span class="logo-title">SMSGate</span>
          <span class="logo-sub">Android Gateway</span>
        </div>
      </transition>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :title="isCollapsed ? item.label : ''"
      >
        <span class="nav-icon">
          <component :is="item.icon" :size="18" stroke-width="1.8" />
        </span>
        <transition name="fade">
          <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
        </transition>
        <transition name="fade">
          <span v-if="!isCollapsed && item.badge" class="nav-badge">{{ item.badge }}</span>
        </transition>
      </router-link>
    </nav>

    <!-- Connection Status -->
    <div class="sidebar-footer">
      <div class="connection-indicator" :class="connectionClass">
        <span class="connection-dot"></span>
        <transition name="fade">
          <div v-if="!isCollapsed" class="connection-info">
            <span class="connection-text">{{ connectionLabel }}</span>
            <span v-if="store.config.local?.deviceModel" class="connection-model">{{ store.config.local.deviceModel }}</span>
          </div>
        </transition>
      </div>

      <button class="collapse-btn" @click="isCollapsed = !isCollapsed" :title="isCollapsed ? 'Expand' : 'Collapse'">
        <ChevronLeft v-if="!isCollapsed" :size="14" />
        <ChevronRight v-else :size="14" />
      </button>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { store } from '../store/index.js'
import {
  LayoutDashboard, Send, Inbox, Clock, Settings,
  MessageSquare, ChevronLeft, ChevronRight, Code2
} from 'lucide-vue-next'

const isCollapsed = ref(false)

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/send',      label: 'Send SMS',  icon: Send },
  { path: '/inbox',     label: 'Inbox',     icon: Inbox },
  { path: '/history',   label: 'History',   icon: Clock },
  { path: '/api',       label: 'API Docs',  icon: Code2 },
  { path: '/settings',  label: 'Settings',  icon: Settings },
]

const connectionClass = computed(() => ({
  'status-connected': store.isConfigured,
  'status-disconnected': !store.isConfigured,
}))

const connectionLabel = computed(() =>
  store.isConfigured ? `${store.config.mode === 'local' ? 'Local' : 'Cloud'} Mode` : 'Not Configured'
)
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: var(--sidebar-width);
  background: linear-gradient(180deg, #0d1220 0%, #0a0d14 100%);
  border-right: 1px solid var(--clr-border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: width var(--transition-base);
  overflow: hidden;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed);
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-xl) var(--space-lg);
  border-bottom: 1px solid var(--clr-border);
  min-height: 80px;
  overflow: hidden;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(108, 99, 255, 0.4);
  animation: pulse-glow 3s ease-in-out infinite;
}

.logo-text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  white-space: nowrap;
}

.logo-title {
  font-size: 18px;
  font-weight: 800;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-sub {
  font-size: 11px;
  color: var(--clr-text-muted);
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: var(--space-lg) var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  overflow: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 11px var(--space-md);
  border-radius: var(--radius-md);
  color: var(--clr-text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-fast);
  position: relative;
  white-space: nowrap;
  overflow: hidden;
}

.nav-item:hover {
  background: rgba(108, 99, 255, 0.1);
  color: var(--clr-text-primary);
}

.nav-item.router-link-active {
  background: rgba(108, 99, 255, 0.15);
  color: var(--clr-accent-primary);
  border: 1px solid rgba(108, 99, 255, 0.2);
}

.nav-item.router-link-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--gradient-primary);
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  color: inherit;
}

.nav-label {
  font-size: 14px;
}

.nav-badge {
  margin-left: auto;
  background: var(--clr-accent-primary);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: var(--radius-full);
}

/* Footer */
.sidebar-footer {
  padding: var(--space-lg) var(--space-sm);
  border-top: 1px solid var(--clr-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm);
  overflow: hidden;
}

.connection-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  overflow: hidden;
}

.connection-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-connected .connection-dot {
  background: var(--clr-accent-success);
  box-shadow: 0 0 8px var(--clr-accent-success);
  animation: pulse-glow 2s ease-in-out infinite;
}

.status-disconnected .connection-dot {
  background: var(--clr-accent-danger);
}

.connection-text {
  font-size: 12px;
  color: var(--clr-text-muted);
  white-space: nowrap;
  overflow: hidden;
}

.connection-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.connection-model {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--clr-accent-success);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: transparent;
  border: 1px solid var(--clr-border);
  color: var(--clr-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: rgba(108, 99, 255, 0.1);
  color: var(--clr-accent-primary);
  border-color: var(--clr-border-hover);
}

/* Mobile */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    width: var(--sidebar-width);
  }
}
</style>
