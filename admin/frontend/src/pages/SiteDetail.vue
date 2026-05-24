<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Badge, Dialog, FormControl, Breadcrumbs, LoadingText, ErrorMessage } from 'frappe-ui'

const route = useRoute()
const router = useRouter()
const siteName = route.params.name

const site = ref(null)
const installable = ref([])
const loading = ref(true)
const error = ref('')

const actionLoading = ref('')
const actionError = ref('')

const showInstall = ref(false)
const selectedInstallApp = ref('')
const installLoading = ref(false)
const installError = ref('')

const showDrop = ref(false)
const showUninstall = ref(false)
const uninstallTarget = ref('')

async function load() {
  try {
    const res = await fetch(`/api/sites/${siteName}`)
    if (!res.ok) throw new Error(`${res.status}`)
    const d = await res.json()
    site.value = d.site
    installable.value = d.installable_apps
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function doAction(path, body = {}) {
  actionError.value = ''
  actionLoading.value = path
  try {
    const res = await fetch(`/api/sites/${siteName}/${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const d = await res.json()
    if (d.ok) router.push(`/tasks/${d.task_id}`)
    else actionError.value = d.error
  } catch (e) {
    actionError.value = e.message
  } finally {
    actionLoading.value = ''
  }
}

async function installApp() {
  if (!selectedInstallApp.value) return
  installLoading.value = true
  installError.value = ''
  try {
    const res = await fetch(`/api/sites/${siteName}/install-app`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app: selectedInstallApp.value }),
    })
    const d = await res.json()
    if (d.ok) { showInstall.value = false; router.push(`/tasks/${d.task_id}`) }
    else installError.value = d.error
  } catch (e) {
    installError.value = e.message
  } finally {
    installLoading.value = false
  }
}

function confirmUninstall(app) {
  uninstallTarget.value = app
  showUninstall.value = true
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-4">
    <Breadcrumbs :items="[{ label: 'Sites', route: '/sites' }, { label: siteName }]" />

    <LoadingText v-if="loading" />
    <ErrorMessage v-else-if="error" :message="error" />

    <template v-else-if="site">
      <ErrorMessage :message="actionError" />

      <div class="flex items-center gap-4">
        <Badge :label="site.exists ? 'online' : 'offline'" :color="site.exists ? 'green' : 'gray'" />
        <span>{{ site.db_name || '—' }}</span>
        <span>{{ site.db_host || '—' }}</span>
        <div class="flex gap-2">
          <Button variant="outline" :loading="actionLoading === 'backup'" @click="doAction('backup')">Backup</Button>
          <Button v-if="installable.length" variant="outline" @click="showInstall = true">Install App</Button>
        </div>
      </div>

      <div>
        <h4>Installed Apps</h4>
        <ListView
          :columns="[{ label: 'App', key: 'name' }, { label: '', key: '_action', width: '100px' }]"
          :rows="site.installed_apps.map(a => ({ name: a, _action: a }))"
          row-key="name"
          :options="{ selectable: false, showTooltip: false }"
        >
          <template #cell="{ column, item }">
            <Button v-if="column.key === '_action'" variant="ghost" theme="red" size="sm" @click="confirmUninstall(item)">Uninstall</Button>
            <span v-else>{{ item }}</span>
          </template>
        </ListView>
      </div>

      <div>
        <h4>site_config.json</h4>
        <pre class="overflow-x-auto font-mono">{{ JSON.stringify(site.site_config, null, 2) }}</pre>
      </div>

      <div class="mt-4">
        <h4>Danger Zone</h4>
        <div class="flex items-center justify-between">
          <span>Permanently delete this site and all its data.</span>
          <Button variant="solid" theme="red" @click="showDrop = true">Drop Site</Button>
        </div>
      </div>
    </template>

    <Dialog v-model="showInstall" :options="{ title: 'Install App' }">
      <template #body-content>
        <FormControl
          label="App to install"
          type="select"
          v-model="selectedInstallApp"
          :options="[{ label: 'Select an app…', value: '' }, ...installable.map(a => ({ label: a, value: a }))]"
        />
        <ErrorMessage :message="installError" class="mt-2" />
        <div class="mt-4 flex justify-end gap-2">
          <Button variant="ghost" @click="showInstall = false">Cancel</Button>
          <Button variant="solid" :loading="installLoading" :disabled="!selectedInstallApp" @click="installApp">Install</Button>
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showDrop" :options="{ title: 'Drop Site', size: 'sm' }">
      <template #body-content>
        <p>Are you sure you want to permanently drop <strong>{{ siteName }}</strong>? All data will be lost.</p>
        <div class="mt-4 flex justify-end gap-2">
          <Button variant="ghost" @click="showDrop = false">Cancel</Button>
          <Button variant="solid" theme="red" :loading="actionLoading === 'drop'" @click="showDrop = false; doAction('drop')">Drop Site</Button>
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showUninstall" :options="{ title: 'Uninstall App', size: 'sm' }">
      <template #body-content>
        <p>Uninstall <strong>{{ uninstallTarget }}</strong> from {{ siteName }}?</p>
        <div class="mt-4 flex justify-end gap-2">
          <Button variant="ghost" @click="showUninstall = false">Cancel</Button>
          <Button variant="solid" theme="red" @click="showUninstall = false; doAction('uninstall-app', { app: uninstallTarget })">Uninstall</Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>
