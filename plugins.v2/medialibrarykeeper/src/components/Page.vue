<script setup>
import { ref } from 'vue'
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

const emit = defineEmits(['close'])
const pageRef = ref(null)
</script>

<template>
  <div>
    <VToolbar density="comfortable" class="mlk-sticky-toolbar">
      <div class="text-h6 ms-3">媒体库管家</div>
      <VSpacer />
      <VBtn icon="mdi-database-sync-outline" variant="text" :loading="pageRef?.scanning" @click="pageRef?.scanLibrary?.()" />
      <VBtn icon="mdi-close" variant="text" @click="emit('close')" />
    </VToolbar>
    <VDivider />
    <AppPage ref="pageRef" :api="api" :plugin-id="pluginId" hide-title />
  </div>
</template>

<style scoped>
.mlk-sticky-toolbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgb(var(--v-theme-surface));
}
</style>
