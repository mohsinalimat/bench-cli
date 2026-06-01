<script setup>
import { ref } from 'vue'
import { Button, TextInput, ErrorMessage } from 'frappe-ui'

defineProps({
  benchName: { type: String, default: '' },
})

const emit = defineEmits(['authenticated'])

const password = ref('')
const error = ref('')
const loading = ref(false)

async function postLogin(value) {
  const response = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password: value }),
  })
  return response.json()
}

async function login() {
  if (!password.value) return
  loading.value = true
  error.value = ''
  try {
    const result = await postLogin(password.value)
    if (result.ok) emit('authenticated')
    else error.value = result.error || 'Login failed'
  } catch {
    error.value = 'Could not reach the server'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex h-screen items-center justify-center bg-surface-gray-2">
    <div class="w-full max-w-sm rounded-xl border border-outline-gray-2 bg-surface-white shadow-sm">

      <div class="border-b border-outline-gray-2 px-6 py-5">
        <p class="text-base font-semibold text-ink-gray-9">{{ benchName || 'Bench Admin' }}</p>
        <p class="mt-1 text-sm text-ink-gray-5">
          Enter the password configured in
          <code class="rounded bg-surface-gray-2 px-1 font-mono text-xs">bench.toml</code>
        </p>
      </div>

      <div class="flex flex-col gap-3 px-6 py-5">
        <TextInput
          v-model="password"
          type="password"
          placeholder="Password"
          @keydown.enter="login"
        />
        <ErrorMessage v-if="error" :message="error" />
        <Button variant="solid" theme="blue" :loading="loading" @click="login">
          Sign in
        </Button>
      </div>

    </div>
  </div>
</template>
