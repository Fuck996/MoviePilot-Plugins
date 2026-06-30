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
  navKey: {
    type: String,
    default: 'main',
  },
  hideTitle: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <AppPage :api="api" :plugin-id="pluginId" :nav-key="navKey" :hide-title="hideTitle" />
</template>
