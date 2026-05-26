<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Badge, Dialog, LoadingText, ErrorMessage } from 'frappe-ui'

const route = useRoute()
const router = useRouter()
const taskId = route.params.id

const task = ref(null)
const lines = ref([])
const loading = ref(true)
const error = ref('')
const streaming = ref(false)
const showKill = ref(false)
const actionLoading = ref('')
const actionError = ref('')
let es = null
const outputEl = ref(null)

const TASK_COLOR = { success: 'green', failed: 'red', running: 'blue', killed: 'gray' }

// Catppuccin Mocha palette for ANSI colors
const ANSI_FG = {
  '30': '#45475a', '31': '#f38ba8', '32': '#a6e3a1', '33': '#f9e2af',
  '34': '#89b4fa', '35': '#cba6f7', '36': '#89dceb', '37': '#cdd6f4',
  '90': '#585b70', '91': '#f38ba8', '92': '#a6e3a1', '93': '#f9e2af',
  '94': '#89b4fa', '95': '#cba6f7', '96': '#89dceb', '97': '#ffffff',
}

// Convert a plain text line (already \r-resolved) to safe HTML with ANSI colors.
function ansiToHtml(text) {
  let html = ''
  let openSpans = 0
  const parts = text.split(/(\x1b\[[0-9;]*[A-Za-z])/)
  for (const part of parts) {
    if (part.startsWith('\x1b[')) {
      const letter = part[part.length - 1]
      if (letter === 'm') {
        const codes = part.slice(2, -1).split(';')
        for (const code of codes) {
          if (code === '0' || code === '') {
            html += '</span>'.repeat(openSpans)
            openSpans = 0
          } else if (code === '1') {
            html += '<span style="font-weight:bold">'
            openSpans++
          } else if (ANSI_FG[code]) {
            html += `<span style="color:${ANSI_FG[code]}">`
            openSpans++
          }
        }
      }
      // non-SGR codes (cursor movement etc.) are silently dropped
    } else {
      html += part.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    }
  }
  return html + '</span>'.repeat(openSpans)
}

// Apply \r (carriage return) semantics: take the last non-empty segment after splitting on \r.
// This handles progress bars that overwrite the current line.
function applyCarriageReturns(raw) {
  const parts = raw.split('\r')
  for (let i = parts.length - 1; i >= 0; i--) {
    if (parts[i]) return parts[i]
  }
  return ''
}

function processRaw(raw) {
  return ansiToHtml(applyCarriageReturns(raw))
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
}

function fmtDuration(s) {
  if (s == null) return '—'
  if (s < 60) return `${Math.round(s)}s`
  if (s < 3600) return `${Math.round(s / 60)}m`
  return `${Math.round(s / 3600)}h`
}

function scrollBottom() {
  nextTick(() => {
    if (outputEl.value) outputEl.value.scrollTop = outputEl.value.scrollHeight
  })
}

async function load() {
  try {
    const res = await fetch(`/api/tasks/${taskId}`)
    if (!res.ok) throw new Error(`${res.status}`)
    const d = await res.json()
    task.value = d.task
    lines.value = d.output.map(processRaw)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function startStream() {
  streaming.value = true
  es = new EventSource(`/api/tasks/${taskId}/stream`)
  es.onmessage = (e) => {
    lines.value.push(processRaw(e.data))
    scrollBottom()
  }
  es.addEventListener('done', () => {
    streaming.value = false
    es.close()
    es = null
    load()
  })
  es.onerror = () => {
    streaming.value = false
    if (es) { es.close(); es = null }
  }
}

async function killTask() {
  showKill.value = false
  actionError.value = ''
  actionLoading.value = 'kill'
  try {
    const res = await fetch(`/api/tasks/${taskId}/kill`, { method: 'POST' })
    const d = await res.json()
    if (!d.ok) actionError.value = d.error
    else load()
  } catch (e) {
    actionError.value = e.message
  } finally {
    actionLoading.value = ''
  }
}

async function rerunTask() {
  actionError.value = ''
  actionLoading.value = 'rerun'
  try {
    const res = await fetch(`/api/tasks/${taskId}/rerun`, { method: 'POST' })
    const d = await res.json()
    if (d.ok) router.push(`/tasks/${d.task_id}`)
    else actionError.value = d.error
  } catch (e) {
    actionError.value = e.message
  } finally {
    actionLoading.value = ''
  }
}

onMounted(async () => {
  await load()
  if (task.value?.status === 'running') startStream()
})
onUnmounted(() => { if (es) { es.close(); es = null } })
</script>

<template>
  <div class="flex flex-col gap-4">
    <LoadingText v-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />

    <template v-else-if="task">
      <ErrorMessage :message="actionError" />

      <div class="flex flex-wrap items-center gap-4">
        <Badge :label="streaming ? 'running…' : task.status" :theme="TASK_COLOR[task.status] || 'gray'" />
        <code>{{ task.command }}</code>
        <code v-if="Object.keys(task.args).length">
          {{ Object.entries(task.args).map(([k,v]) => `${k}=${v}`).join(' ') }}
        </code>
        <span>{{ fmtDate(task.started_at) }}</span>
        <span v-if="task.duration_seconds != null">{{ fmtDuration(task.duration_seconds) }}</span>
        <Button v-if="task.status === 'running'" variant="outline" theme="red" size="sm"
          :loading="actionLoading === 'kill'" @click="showKill = true">Kill</Button>
        <Button v-else variant="outline" size="sm"
          :loading="actionLoading === 'rerun'" @click="rerunTask">Re-run</Button>
      </div>

      <div
        ref="outputEl"
        class="overflow-auto rounded-lg font-mono text-sm leading-5"
        style="background:#1e1e2e; color:#cdd6f4; padding:1rem; max-height:65vh; min-height:200px;"
      >
        <div v-if="!lines.length" style="color:#585b70;">No output yet…</div>
        <template v-else>
          <div
            v-for="(line, i) in lines"
            :key="i"
            class="whitespace-pre"
            v-html="line || '&nbsp;'"
          />
          <span v-if="streaming" style="color:#a6e3a1;" class="animate-pulse">█</span>
        </template>
      </div>
    </template>

    <Dialog v-model="showKill" :options="{ title: 'Kill Task', size: 'sm' }">
      <template #body-content>
        <p>Send SIGTERM to the running process?</p>
        <div class="mt-4 flex justify-end gap-2">
          <Button variant="ghost" @click="showKill = false">Cancel</Button>
          <Button variant="solid" theme="red" @click="killTask">Kill</Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>
