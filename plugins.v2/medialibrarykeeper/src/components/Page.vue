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
  show_switch: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['close', 'switch'])
</script>

<template>
  <AppPage :api="api" :plugin-id="pluginId" hide-title />
  <VBtn
    v-if="show_switch"
    class="mlk-page-settings-fab"
    icon="mdi-cog"
    color="primary"
    variant="flat"
    size="large"
    @click="emit('switch')"
  />
</template>

<style scoped>
.mlk-page-settings-fab {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 20;
}
</style>
