<template>
  <!-- Backdrop -->
  <teleport to="body">
    <transition name="modal">
      <div v-if="modelValue" class="modal-backdrop" @click.self="close" id="contact-import-modal">
        <div class="modal-box">

          <!-- Header -->
          <div class="modal-header">
            <div class="modal-title-row">
              <span style="font-size:22px">👥</span>
              <div>
                <h2 class="modal-title">Import Contacts</h2>
                <p class="modal-subtitle">Select recipients from CSV, vCard, or saved contacts</p>
              </div>
            </div>
            <button class="close-btn" @click="close" id="close-contact-modal">✕</button>
          </div>

          <!-- Tabs -->
          <div class="modal-tabs">
            <button class="tab-btn" :class="{ active: tab === 'saved' }"   @click="tab = 'saved'"   id="tab-saved">
              💾 Saved ({{ contactStore.total }})
            </button>
            <button class="tab-btn" :class="{ active: tab === 'import' }"  @click="tab = 'import'"  id="tab-import">
              📂 Import File
            </button>
          </div>

          <!-- ── TAB: Saved Contacts ── -->
          <div v-if="tab === 'saved'" class="modal-body">
            <div v-if="contactStore.total === 0" class="empty-contacts">
              <span style="font-size:40px">📋</span>
              <p>No saved contacts yet.</p>
              <p class="sub">Import a CSV or vCard file to save contacts for reuse.</p>
              <button class="btn btn-ghost" @click="tab = 'import'">📂 Import File</button>
            </div>

            <template v-else>
              <!-- Search bar -->
              <div class="contact-search-wrap">
                <span class="search-icon-sm">🔍</span>
                <input
                  v-model="savedSearch"
                  type="text"
                  class="form-control search-sm"
                  placeholder="Search name or number..."
                  id="contact-search-input"
                />
                <span class="contact-count-badge">{{ filteredSaved.length }} contacts</span>
              </div>

              <!-- Select all / clear row -->
              <div class="bulk-row">
                <label class="check-all-label">
                  <input type="checkbox" :checked="allSavedSelected" @change="toggleAllSaved" id="select-all-saved" />
                  <span>Select all visible</span>
                </label>
                <span class="selected-count" v-if="savedSelection.size > 0">
                  {{ savedSelection.size }} selected
                </span>
                <button v-if="contactStore.total > 0" class="btn-link danger" @click="confirmClearSaved">🗑 Clear all</button>
              </div>

              <!-- Contact list -->
              <div class="contact-list">
                <label
                  v-for="c in filteredSaved"
                  :key="c.id"
                  class="contact-row"
                  :class="{ selected: savedSelection.has(c.id) }"
                >
                  <input type="checkbox" :checked="savedSelection.has(c.id)" @change="toggleSaved(c.id)" />
                  <div class="contact-avatar">{{ avatarLetter(c.name || c.phone) }}</div>
                  <div class="contact-info">
                    <span class="contact-name">{{ c.name || '—' }}</span>
                    <span class="contact-phone">{{ c.phone }}</span>
                  </div>
                  <button class="del-contact" @click.prevent="removeContact(c.id)" title="Delete">✕</button>
                </label>
              </div>
            </template>
          </div>

          <!-- ── TAB: Import File ── -->
          <div v-if="tab === 'import'" class="modal-body">

            <!-- Drop zone -->
            <div
              class="drop-zone"
              :class="{ 'drag-over': isDragging, 'has-file': parsedContacts.length > 0 }"
              @dragover.prevent="isDragging = true"
              @dragleave="isDragging = false"
              @drop.prevent="onDrop"
              @click="fileInput.click()"
              id="file-drop-zone"
            >
              <input
                ref="fileInput"
                type="file"
                accept=".csv,.vcf,.vcard,text/csv,text/vcard"
                style="display:none"
                @change="onFileChange"
                id="contact-file-input"
              />
              <div v-if="parsedContacts.length === 0" class="drop-inner">
                <span style="font-size:42px">📂</span>
                <p class="drop-title">Drop a file here or click to browse</p>
                <p class="drop-hint">Supports <strong>CSV</strong> (.csv) and <strong>vCard</strong> (.vcf)</p>
                <div class="format-chips">
                  <span class="chip">CSV columns: name, phone</span>
                  <span class="chip">vCard 2.1 / 3.0 / 4.0</span>
                </div>
              </div>
              <div v-else class="drop-inner compact">
                <span style="font-size:28px">✅</span>
                <p class="drop-title">{{ fileName }} — {{ parsedContacts.length }} contacts parsed</p>
                <button class="btn-link" @click.stop="clearParsed">Change file</button>
              </div>
            </div>

            <!-- Parse error -->
            <div v-if="parseError" class="parse-error">⚠️ {{ parseError }}</div>

            <template v-if="parsedContacts.length > 0">
              <!-- Bulk row -->
              <div class="bulk-row">
                <label class="check-all-label">
                  <input type="checkbox" :checked="allParsedSelected" @change="toggleAllParsed" id="select-all-parsed" />
                  <span>Select all ({{ parsedContacts.length }})</span>
                </label>
                <span class="selected-count" v-if="parsedSelection.size > 0">
                  {{ parsedSelection.size }} selected
                </span>
              </div>

              <!-- Preview list -->
              <div class="contact-list preview-list">
                <label
                  v-for="(c, i) in parsedContacts"
                  :key="i"
                  class="contact-row"
                  :class="{ selected: parsedSelection.has(i), invalid: !c.phone }"
                >
                  <input type="checkbox" :checked="parsedSelection.has(i)" @change="toggleParsed(i)" :disabled="!c.phone" />
                  <div class="contact-avatar" :class="{ warn: !c.phone }">{{ c.phone ? avatarLetter(c.name || c.phone) : '!' }}</div>
                  <div class="contact-info">
                    <span class="contact-name">{{ c.name || '—' }}</span>
                    <span class="contact-phone" :class="{ 'no-phone': !c.phone }">{{ c.phone || 'No phone number' }}</span>
                  </div>
                </label>
              </div>

              <!-- Save to contacts toggle -->
              <label class="save-check">
                <input type="checkbox" v-model="saveToContacts" id="save-to-contacts-check" />
                <span>💾 Save imported contacts for future use</span>
              </label>
            </template>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="close">Cancel</button>
            <button
              class="btn btn-primary"
              @click="applySelection"
              :disabled="selectedPhones.length === 0"
              id="apply-contacts-btn"
            >
              ✉️ Add {{ selectedPhones.length || '' }} Recipient{{ selectedPhones.length !== 1 ? 's' : '' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { contactStore, addContacts, removeContact, clearContacts, parseCSV, parseVCard } from '../store/contacts.js'

const props = defineProps({ modelValue: Boolean })
const emit  = defineEmits(['update:modelValue', 'select'])

// ── Tab state ──────────────────────────────────────────────────────────
const tab         = ref('saved')
const savedSearch = ref('')

// ── Saved contacts selection ───────────────────────────────────────────
const savedSelection = ref(new Set())

const filteredSaved = computed(() => {
  const q = savedSearch.value.toLowerCase()
  return q
    ? contactStore.contacts.filter(c => c.name.toLowerCase().includes(q) || c.phone.includes(q))
    : contactStore.contacts
})

const allSavedSelected = computed(() =>
  filteredSaved.value.length > 0 && filteredSaved.value.every(c => savedSelection.value.has(c.id))
)

function toggleSaved(id) {
  const s = new Set(savedSelection.value)
  s.has(id) ? s.delete(id) : s.add(id)
  savedSelection.value = s
}

function toggleAllSaved() {
  if (allSavedSelected.value) {
    const s = new Set(savedSelection.value)
    filteredSaved.value.forEach(c => s.delete(c.id))
    savedSelection.value = s
  } else {
    const s = new Set(savedSelection.value)
    filteredSaved.value.forEach(c => s.add(c.id))
    savedSelection.value = s
  }
}

function confirmClearSaved() {
  if (confirm('Delete all saved contacts?')) {
    clearContacts()
    savedSelection.value = new Set()
  }
}

// ── File import ────────────────────────────────────────────────────────
const fileInput      = ref(null)
const isDragging     = ref(false)
const fileName       = ref('')
const parsedContacts = ref([])
const parseError     = ref('')
const parsedSelection = ref(new Set())
const saveToContacts  = ref(true)

function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) processFile(file)
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) processFile(file)
}

function processFile(file) {
  parseError.value     = ''
  parsedContacts.value = []
  parsedSelection.value = new Set()
  fileName.value = file.name

  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target.result
    let contacts = []
    try {
      if (file.name.toLowerCase().endsWith('.vcf') || file.type === 'text/vcard') {
        contacts = parseVCard(text)
      } else {
        contacts = parseCSV(text)
      }
      if (contacts.length === 0) {
        parseError.value = 'No valid contacts found. Check that the file has a phone number column.'
        return
      }
      parsedContacts.value = contacts
      // Auto-select all valid contacts
      parsedSelection.value = new Set(
        contacts.map((_, i) => i).filter(i => !!contacts[i].phone)
      )
    } catch (err) {
      parseError.value = `Failed to parse file: ${err.message}`
    }
  }
  reader.readAsText(file)
}

function clearParsed() {
  parsedContacts.value  = []
  parsedSelection.value = new Set()
  parseError.value      = ''
  fileName.value        = ''
  if (fileInput.value) fileInput.value.value = ''
}

const allParsedSelected = computed(() => {
  const valid = parsedContacts.value.filter(c => c.phone)
  return valid.length > 0 && valid.every((_, i) => parsedSelection.value.has(
    parsedContacts.value.indexOf(parsedContacts.value.filter(c => c.phone)[i])
  ))
})

function toggleParsed(i) {
  const s = new Set(parsedSelection.value)
  s.has(i) ? s.delete(i) : s.add(i)
  parsedSelection.value = s
}

function toggleAllParsed() {
  const validIdxs = parsedContacts.value.map((c, i) => c.phone ? i : -1).filter(i => i !== -1)
  if (validIdxs.every(i => parsedSelection.value.has(i))) {
    parsedSelection.value = new Set()
  } else {
    parsedSelection.value = new Set(validIdxs)
  }
}

// ── Combined selected phones ───────────────────────────────────────────
const selectedPhones = computed(() => {
  const phones = []
  if (tab.value === 'saved') {
    savedSelection.value.forEach(id => {
      const c = contactStore.contacts.find(x => x.id === id)
      if (c) phones.push(c.phone)
    })
  } else {
    parsedSelection.value.forEach(i => {
      const c = parsedContacts.value[i]
      if (c?.phone) phones.push(c.phone)
    })
  }
  return [...new Set(phones)]   // deduplicate
})

// ── Apply / close ──────────────────────────────────────────────────────
function applySelection() {
  if (tab.value === 'import' && saveToContacts.value && parsedContacts.value.length > 0) {
    addContacts(parsedContacts.value.filter((_, i) => parsedSelection.value.has(i)))
  }
  emit('select', selectedPhones.value)
  close()
}

function close() {
  emit('update:modelValue', false)
}

// Reset state when closed
watch(() => props.modelValue, (open) => {
  if (!open) {
    clearParsed()
    savedSearch.value    = ''
    savedSelection.value = new Set()
    tab.value = contactStore.total > 0 ? 'saved' : 'import'
  } else {
    tab.value = contactStore.total > 0 ? 'saved' : 'import'
  }
})

// ── Helpers ────────────────────────────────────────────────────────────
function avatarLetter(str) {
  return (str || '?').trim()[0].toUpperCase()
}
</script>

<style scoped>
/* Backdrop */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
}

.modal-box {
  background: var(--clr-surface);
  border: 1px solid var(--clr-border-hover);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 580px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6);
  overflow: hidden;
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--clr-border);
  flex-shrink: 0;
}
.modal-title-row { display: flex; align-items: center; gap: var(--space-md); }
.modal-title { font-size: 17px; font-weight: 800; color: var(--clr-text-primary); margin: 0; }
.modal-subtitle { font-size: 12px; color: var(--clr-text-muted); margin: 0; }

.close-btn {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--clr-border);
  color: var(--clr-text-muted);
  width: 30px; height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 13px;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}
.close-btn:hover { background: rgba(255,94,122,0.15); color: var(--clr-accent-danger); border-color: rgba(255,94,122,0.3); }

/* Tabs */
.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--clr-border);
  flex-shrink: 0;
}
.tab-btn {
  flex: 1;
  padding: 12px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 13px;
  font-weight: 600;
  color: var(--clr-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.tab-btn:hover { color: var(--clr-text-primary); background: rgba(108,99,255,0.04); }
.tab-btn.active { color: var(--clr-accent-primary); border-bottom-color: var(--clr-accent-primary); background: rgba(108,99,255,0.05); }

/* Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg) var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* Empty saved */
.empty-contacts {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xl);
  text-align: center;
  color: var(--clr-text-secondary);
  font-size: 13px;
}
.empty-contacts .sub { font-size: 12px; color: var(--clr-text-muted); }

/* Search */
.contact-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}
.search-icon-sm {
  position: absolute;
  left: 10px;
  font-size: 13px;
  pointer-events: none;
}
.search-sm { padding-left: 32px !important; }
.contact-count-badge {
  flex-shrink: 0;
  font-size: 11px;
  color: var(--clr-text-muted);
  white-space: nowrap;
}

/* Bulk row */
.bulk-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: 4px 0;
}
.check-all-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--clr-text-secondary);
  cursor: pointer;
}
.selected-count {
  font-size: 12px;
  font-weight: 700;
  color: var(--clr-accent-primary);
}
.btn-link {
  background: none;
  border: none;
  font-size: 12px;
  cursor: pointer;
  color: var(--clr-text-muted);
  margin-left: auto;
  padding: 2px 4px;
  border-radius: 3px;
  transition: color var(--transition-fast);
}
.btn-link:hover { color: var(--clr-text-primary); }
.btn-link.danger:hover { color: var(--clr-accent-danger); }

/* Contact list */
.contact-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
  border: 1px solid var(--clr-border);
  border-radius: var(--radius-md);
}

.contact-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 8px 12px;
  cursor: pointer;
  transition: background var(--transition-fast);
  border-bottom: 1px solid var(--clr-border);
}
.contact-row:last-child { border-bottom: none; }
.contact-row:hover { background: rgba(108,99,255,0.05); }
.contact-row.selected { background: rgba(108,99,255,0.08); }
.contact-row.invalid { opacity: 0.5; }

.contact-avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.contact-avatar.warn { background: rgba(255,179,71,0.3); color: var(--clr-accent-warning); }

.contact-info { flex: 1; display: flex; flex-direction: column; gap: 1px; overflow: hidden; }
.contact-name  { font-size: 13px; font-weight: 600; color: var(--clr-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.contact-phone { font-size: 11px; font-family: var(--font-mono); color: var(--clr-text-muted); }
.contact-phone.no-phone { color: var(--clr-accent-danger); }

.del-contact {
  background: none;
  border: none;
  color: var(--clr-text-muted);
  cursor: pointer;
  font-size: 12px;
  padding: 3px 6px;
  border-radius: 3px;
  opacity: 0;
  transition: all var(--transition-fast);
}
.contact-row:hover .del-contact { opacity: 1; }
.del-contact:hover { color: var(--clr-accent-danger); background: rgba(255,94,122,0.1); }

/* Drop zone */
.drop-zone {
  border: 2px dashed var(--clr-border-hover);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: center;
}
.drop-zone:hover, .drop-zone.drag-over {
  border-color: var(--clr-accent-primary);
  background: rgba(108,99,255,0.05);
}
.drop-zone.has-file {
  border-color: var(--clr-accent-success);
  border-style: solid;
  background: rgba(0,229,160,0.04);
}
.drop-inner { padding: var(--space-xl); display: flex; flex-direction: column; align-items: center; gap: var(--space-sm); }
.drop-inner.compact { padding: var(--space-lg); }
.drop-title { font-size: 14px; font-weight: 700; color: var(--clr-text-primary); margin: 0; }
.drop-hint  { font-size: 12px; color: var(--clr-text-muted); margin: 0; }
.format-chips { display: flex; gap: var(--space-sm); flex-wrap: wrap; justify-content: center; margin-top: 4px; }
.chip {
  font-size: 11px; padding: 3px 10px;
  background: rgba(108,99,255,0.1);
  border: 1px solid rgba(108,99,255,0.2);
  border-radius: var(--radius-full);
  color: var(--clr-accent-primary);
}

.parse-error {
  font-size: 12px;
  color: var(--clr-accent-danger);
  background: rgba(255,94,122,0.07);
  border: 1px solid rgba(255,94,122,0.2);
  border-radius: var(--radius-sm);
  padding: var(--space-sm) var(--space-md);
}

/* Preview list */
.preview-list { max-height: 260px; overflow-y: auto; }

/* Save to contacts */
.save-check {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 13px;
  color: var(--clr-text-secondary);
  cursor: pointer;
  padding: var(--space-sm) 0;
}

/* Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  border-top: 1px solid var(--clr-border);
  flex-shrink: 0;
}

/* Transition */
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-box, .modal-leave-to .modal-box { transform: scale(0.95) translateY(10px); }
</style>
