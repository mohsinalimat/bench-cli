<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ListView, TabButtons, LoadingText, ErrorMessage } from 'frappe-ui'

const router = useRouter()
const queries = ref([])
const loading = ref(true)
const error = ref('')
const limit = ref(50)

function fmtDate(iso) {
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' })
}

const tabs = [
  { label: 'Binary Logs', value: 'binlogs' },
  { label: 'Slow Queries', value: 'slow-queries' },
]

const columns = [
  { label: 'Time', key: '_time', width: '150px' },
  { label: 'Query Time', key: '_query_time', width: '100px' },
  { label: 'Rows', key: '_rows', width: '80px' },
  { label: 'SQL', key: 'sql' },
]

const rows = computed(() =>
  queries.value.map(q => ({
    ...q,
    _time: fmtDate(q.timestamp),
    _query_time: `${q.query_time.toFixed(3)}s`,
    _rows: `${q.rows_sent}/${q.rows_examined}`,
  }))
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`/api/database/slow-queries?limit=${limit.value}`)
    if (!res.ok) throw new Error(await res.text())
    queries.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center gap-4">
      <h3>Database</h3>
      <TabButtons
        :buttons="tabs"
        modelValue="slow-queries"
        @update:modelValue="v => router.push(v === 'binlogs' ? '/database/binlogs' : '/database/slow-queries')"
      />
    </div>

    <LoadingText v-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />

    <div v-else>
      <ListView
        :columns="columns"
        :rows="rows"
        row-key="_time"
        :options="{ selectable: false, showTooltip: false }"
      />
    </div>
  </div>
</template>
