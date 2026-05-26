<script setup>
import { h, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, Dialog, ListView, FormControl, LoadingText, ErrorMessage } from 'frappe-ui'

const router = useRouter()
const sites = ref([])
const registry = ref([])
const loading = ref(true)
const error = ref('')

const showCreate = ref(false)
const siteName = ref('')
const adminPassword = ref('')
const creating = ref(false)
const createError = ref('')

const logoMap = computed(() => Object.fromEntries(registry.value.map(a => [a.name, a.logo_url])))

const COLORS = ['#4f46e5', '#0891b2', '#059669', '#d97706', '#dc2626', '#7c3aed']
function hashColor(name) {
  let h = 0
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) | 0
  return COLORS[Math.abs(h) % COLORS.length]
}

function appLogoEl(appName) {
  const logo = logoMap.value[appName]
  return h('div', {
    class: 'flex h-5 w-5 shrink-0 items-center justify-center rounded overflow-hidden',
    style: logo ? {} : { background: hashColor(appName) },
  }, logo
    ? [h('img', { src: logo, alt: appName, class: 'h-full w-full object-contain' })]
    : [h('span', { class: 'text-[9px] font-bold text-white leading-none' }, appName[0].toUpperCase())]
  )
}

const columns = computed(() => [
  { label: 'Name', key: 'name', width: '200px' },
  {
    label: 'Status', key: '_status', width: '80px',
    prefix: ({ row }) => h(Badge, { label: row._status, theme: row._status === 'online' ? 'green' : 'gray' }),
    getLabel: () => '',
  },
  {
    label: 'Apps', key: '_apps',
    prefix: ({ row }) => h('div', { class: 'flex items-center gap-1 flex-wrap py-1' },
      row.installed_apps.map(app => appLogoEl(app))
    ),
    getLabel: () => '',
  },
  { label: 'Database', key: 'db_name', width: '150px' },
])

const rows = computed(() =>
  sites.value.map(s => ({
    ...s,
    _status: s.exists ? 'online' : 'offline',
  }))
)

async function load() {
  try {
    const res = await fetch('/api/sites/')
    sites.value = await res.json()
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

async function createSite() {
  if (!siteName.value.trim()) { createError.value = 'Site name is required.'; return }
  creating.value = true
  createError.value = ''
  try {
    const res = await fetch('/api/sites/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: siteName.value.trim(), admin_password: adminPassword.value.trim() }),
    })
    const d = await res.json()
    if (d.ok) { showCreate.value = false; router.push(`/tasks/${d.task_id}`) }
    else createError.value = d.error
  } catch (e) {
    createError.value = e.message
  } finally {
    creating.value = false
  }
}

function openCreate() {
  showCreate.value = true
  siteName.value = ''
  adminPassword.value = ''
  createError.value = ''
}

onMounted(() => { load(); loadRegistry() })
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex justify-end">
      <Button variant="solid" @click="openCreate">Create Site</Button>
    </div>

    <LoadingText v-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />

    <div v-else class="overflow-hidden">
      <ListView
        :columns="columns"
        :rows="rows"
        row-key="name"
        :options="{
          getRowRoute: (row) => `/sites/${row.name}`,
          selectable: false,
          showTooltip: false,
        }"
      />
    </div>

    <Dialog v-model="showCreate" :options="{ title: 'Create Site' }">
      <template #body-content>
        <div @pointerdown.stop class="flex flex-col gap-3">
          <FormControl label="Site Name" type="text" v-model="siteName" placeholder="mysite.localhost" @keyup.enter="createSite" />
          <FormControl label="Admin Password" type="password" v-model="adminPassword" placeholder="admin" description="Leave blank to use 'admin'" />
          <ErrorMessage :message="createError" />
          <div class="mt-1 flex justify-end gap-2">
            <Button variant="ghost" @click="showCreate = false">Cancel</Button>
            <Button variant="solid" :loading="creating" @click="createSite">Create Site</Button>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>
