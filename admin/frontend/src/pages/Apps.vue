<script setup>
import { h, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, Dialog, ListView, FormControl, LoadingText, ErrorMessage } from 'frappe-ui'

const router = useRouter()
const apps = ref([])
const loading = ref(true)
const error = ref('')

const showAdd = ref(false)
const addMode = ref('picker')
const registry = ref([])
const registrySearch = ref('')
const selectedApp = ref(null)
const manualName = ref('')
const manualRepo = ref('')
const manualBranch = ref('')
const addLoading = ref(false)
const addError = ref('')

const filteredRegistry = computed(() => {
  const q = registrySearch.value.toLowerCase()
  if (!q) return registry.value
  return registry.value.filter(a =>
    a.name.includes(q) ||
    (a.title || '').toLowerCase().includes(q) ||
    (a.description || '').toLowerCase().includes(q)
  )
})

const columns = [
  { label: 'Name', key: 'name', width: '150px' },
  { label: 'Repo', key: 'repo' },
  { label: 'Branch', key: 'branch', width: '100px' },
  { label: 'Commit', key: '_commit', width: '180px' },
  {
    label: 'Status', key: '_status', width: '100px',
    prefix: ({ row }) => h(Badge, { label: row._status, color: row._status === 'dirty' ? 'orange' : 'gray' }),
    getLabel: () => '',
  },
  { label: 'Version', key: 'installed_version', width: '100px' },
]

const rows = computed(() =>
  apps.value.map(a => ({
    ...a,
    _commit: a.is_cloned ? a.current_commit : 'not cloned',
    _status: a.uncommitted_changes ? 'dirty' : 'clean',
  }))
)

async function load() {
  try {
    const res = await fetch('/api/apps/')
    apps.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function loadRegistry() {
  try {
    const res = await fetch('/api/apps/registry')
    registry.value = await res.json()
  } catch { registry.value = [] }
}

function openAdd() {
  showAdd.value = true
  addMode.value = 'picker'
  addError.value = ''
  selectedApp.value = null
  registrySearch.value = ''
  if (!registry.value.length) loadRegistry()
}

async function doAdd(name, repo, branch) {
  addLoading.value = true
  addError.value = ''
  try {
    const res = await fetch('/api/apps/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, repo, branch }),
    })
    const d = await res.json()
    if (d.ok) { showAdd.value = false; router.push(`/tasks/${d.task_id}`) }
    else addError.value = d.error
  } catch (e) {
    addError.value = e.message
  } finally {
    addLoading.value = false
  }
}

const COLORS = ['#4f46e5','#0891b2','#059669','#d97706','#dc2626','#7c3aed']
function hashColor(name) {
  let h = 0
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) | 0
  return COLORS[Math.abs(h) % COLORS.length]
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <h3>Apps ({{ apps.length }})</h3>
      <Button variant="solid" @click="openAdd">Add App</Button>
    </div>

    <LoadingText v-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />

    <div v-else>
      <ListView
        :columns="columns"
        :rows="rows"
        row-key="name"
        :options="{ selectable: false, showTooltip: false }"
      />
    </div>

    <Dialog v-model="showAdd" :options="{ title: 'Add App', size: 'lg' }">
      <template #body-content>
        <div v-if="addMode === 'picker'">
          <FormControl type="text" v-model="registrySearch" placeholder="Search apps…" class="mb-3" />
          <div class="max-h-64 overflow-y-auto">
            <div v-if="!filteredRegistry.length" class="p-4">No apps found</div>
            <button
              v-for="a in filteredRegistry"
              :key="a.name"
              class="flex w-full items-center gap-3 px-3 py-2"
              :class="{ 'bg-blue-50': selectedApp?.name === a.name }"
              @click="selectedApp = a"
            >
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded font-bold text-white"
                   :style="{ background: hashColor(a.name) }">
                {{ (a.title || a.name)[0].toUpperCase() }}
              </div>
              <div class="text-left">
                <div>{{ a.title || a.name }}</div>
                <div>{{ a.description }}</div>
              </div>
            </button>
          </div>
          <ErrorMessage :message="addError" class="mt-2" />
          <div class="mt-4 flex justify-between">
            <Button variant="ghost" @click="addMode = 'manual'">Enter manually</Button>
            <div class="flex gap-2">
              <Button variant="ghost" @click="showAdd = false">Cancel</Button>
              <Button variant="solid" :loading="addLoading" :disabled="!selectedApp"
                @click="doAdd(selectedApp.name, selectedApp.repo, selectedApp.branch || '')">
                Add App
              </Button>
            </div>
          </div>
        </div>

        <div v-else>
          <div class="flex flex-col gap-3">
            <FormControl label="Name" type="text" v-model="manualName" placeholder="my_app" />
            <FormControl label="Repository URL" type="text" v-model="manualRepo" placeholder="https://github.com/org/repo" />
            <FormControl label="Branch" type="text" v-model="manualBranch" placeholder="main" description="Leave blank to use the repo default branch." />
          </div>
          <ErrorMessage :message="addError" class="mt-2" />
          <div class="mt-4 flex justify-between">
            <Button variant="ghost" @click="addMode = 'picker'">← Back to registry</Button>
            <div class="flex gap-2">
              <Button variant="ghost" @click="showAdd = false">Cancel</Button>
              <Button variant="solid" :loading="addLoading" @click="doAdd(manualName, manualRepo, manualBranch)">
                Add App
              </Button>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>
