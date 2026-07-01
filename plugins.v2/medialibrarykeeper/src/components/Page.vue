<script setup>
import AppPage from './AppPage.vue'

defineProps({
  api: {
    type: Object,
    default: () => ({}),
  },
  pluginId: {
    type: String,
    default: 'MediaLibraryKeeper',
  },
})
</script>

<template>
  <AppPage :api="api" :plugin-id="pluginId" hide-title />
</template>
