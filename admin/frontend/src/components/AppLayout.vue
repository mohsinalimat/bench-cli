<script setup>
import { computed } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { Button } from 'frappe-ui'

const router = useRouter()
const route = useRoute()

const navItems = [
  { label: 'Dashboard', to: '/' },
  { label: 'Apps', to: '/apps' },
  { label: 'Sites', to: '/sites' },
  { label: 'Processes', to: '/processes' },
  { label: 'Logs', to: '/logs' },
  { label: 'Database', to: '/database/binlogs' },
  { label: 'Tasks', to: '/tasks' },
]

function isActive(to) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}
</script>

<template>
  <div class="flex h-screen flex-col">
    <header class="flex shrink-0 items-center justify-between border-b px-4 py-2">
      <span class="font-semibold">Bench</span>
      <nav class="flex items-center gap-1">
        <Button
          v-for="item in navItems"
          :key="item.to"
          :variant="isActive(item.to) ? 'subtle' : 'ghost'"
          :label="item.label"
          size="sm"
          @click="router.push(item.to)"
        />
      </nav>
    </header>
    <main class="flex-1 overflow-auto p-6">
      <RouterView />
    </main>
  </div>
</template>
