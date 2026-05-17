import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Views
import SendSMS from './views/SendSMS.vue'
import History from './views/History.vue'
import Settings from './views/Settings.vue'
import Dashboard from './views/Dashboard.vue'
import Inbox from './views/Inbox.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard, meta: { title: 'Dashboard' } },
  { path: '/send', component: SendSMS, meta: { title: 'Send SMS' } },
  { path: '/inbox', component: Inbox, meta: { title: 'Inbox' } },
  { path: '/history', component: History, meta: { title: 'Message History' } },
  { path: '/settings', component: Settings, meta: { title: 'Settings' } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'SMS Gateway'} - Android SMS Sender`
})

const app = createApp(App)
app.use(router)

// Global error handler — logs component errors to console so blank pages are diagnosable
app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', info, err)
}

app.mount('#app')
