<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { Button, Badge, Card, LoadingText, ErrorMessage, ListView } from 'frappe-ui'

const router = useRouter()
const data = ref(null)
const loading = ref(true)
const error = ref('')
const actionError = ref('')

async function load() {
  try {
    const res = await fetch('/api/dashboard')
    if (!res.ok) throw new Error(`${res.status}`)
    data.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function runTask(command, args = {}) {
  actionError.value = ''
  try {
    const res = await fetch('/api/tasks/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, ...args }),
    })
    const d = await res.json()
    if (d.ok) router.push(`/tasks/${d.task_id}`)
    else actionError.value = d.error
  } catch (e) {
    actionError.value = e.message
  }
}

function fmtDuration(s) {
  if (s == null) return '—'
  if (s < 60) return `${Math.round(s)}s`
  if (s < 3600) return `${Math.round(s / 60)}m`
  return `${Math.round(s / 3600)}h`
}

const TASK_COLOR = { success: 'green', failed: 'red', running: 'blue', killed: 'gray' }

const taskColumns = [
  { label: 'Command', key: 'command' },
  { label: 'Status', key: 'status', width: '100px' },
  { label: 'Duration', key: '_duration', width: '80px' },
]

const countdownDisplay = ref(10)
let countdown = 10
let timer

onMounted(() => {
  load()
  timer = setInterval(() => {
    countdown--
    countdownDisplay.value = countdown
    if (countdown <= 0) { countdown = 10; countdownDisplay.value = 10; load() }
  }, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <h3>Dashboard</h3>
      <span>Refreshing in {{ countdownDisplay }}s</span>
    </div>

    <LoadingText v-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />

    <template v-else-if="data">
      <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
        <RouterLink to="/apps">
          <Card :title="`${data.cloned_count} / ${data.apps.length}`" subtitle="Apps cloned" />
        </RouterLink>
        <RouterLink to="/sites">
          <Card :title="`${data.online_count} / ${data.sites.length}`" subtitle="Sites online" />
        </RouterLink>
        <RouterLink to="/processes">
          <Card :title="`${data.running_count} / ${data.processes.length}`" subtitle="Processes running" />
        </RouterLink>
        <RouterLink to="/tasks">
          <Card :title="String(data.recent_tasks.length)" subtitle="Recent tasks" />
        </RouterLink>
      </div>

      <Card title="Quick Actions">
        <div class="flex flex-wrap gap-2">
          <Button variant="outline" @click="runTask('build')">Build Assets</Button>
          <Button variant="outline" @click="runTask('update')">Update Bench</Button>
          <Button variant="outline" @click="runTask('reload-supervisor')">Reload Supervisor</Button>
        </div>
        <ErrorMessage :message="actionError" class="mt-2" />
      </Card>

      <Card title="Recent Tasks">
        <template #actions>
          <RouterLink to="/tasks">View all</RouterLink>
        </template>
        <ListView
          :columns="taskColumns"
          :rows="data.recent_tasks.map(t => ({ ...t, _duration: fmtDuration(t.duration_seconds) }))"
          row-key="task_id"
          :options="{
            getRowRoute: (row) => `/tasks/${row.task_id}`,
            selectable: false,
            showTooltip: false,
          }"
        >
          <template #cell="{ column, item }">
            <Badge v-if="column.key === 'status'" :label="item" :color="TASK_COLOR[item] || 'gray'" size="sm" />
            <span v-else>{{ item || '—' }}</span>
          </template>
        </ListView>
      </Card>
    </template>
  </div>
</template>
