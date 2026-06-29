<script setup>
import { computed, onMounted, ref } from 'vue'
import { toEditableConfig, toPayloadConfig, unwrapResponse } from '../provider'

const props = defineProps({
  api: {
    type: Object,
    default: () => ({}),
  },
  pluginId: {
    type: String,
    default: 'MediaLibraryKeeper',
  },
  initialConfig: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['save', 'close'])
const config = ref(toEditableConfig())
const loadingOptions = ref(false)
const mediaServerOptions = ref([])
const downloaderOptions = ref([])
const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`)

function saveConfig() {
  emit('save', toPayloadConfig(config.value))
}

async function loadMediaServerOptions() {
  if (!props.api?.get) return
  loadingOptions.value = true
  try {
    const response = await props.api.get(`${pluginBase.value}/status`)
    const status = unwrapResponse(response) || {}
    mediaServerOptions.value = status.media_server_options || []
    downloaderOptions.value = status.downloader_options || []
  } finally {
    loadingOptions.value = false
  }
}

onMounted(async () => {
  config.value = toEditableConfig(props.initialConfig)
  await loadMediaServerOptions()
})
</script>

<template>
  <div class="mlk-config">
    <VToolbar density="comfortable" color="transparent">
      <div class="text-h6 ms-3">媒体库管家配置</div>
      <VSpacer />
      <VBtn icon="mdi-content-save" variant="text" color="primary" @click="saveConfig" />
      <VBtn icon="mdi-close" variant="text" @click="emit('close')" />
    </VToolbar>
    <VDivider />

    <div class="mlk-config-body">
      <VSwitch v-model="config.enabled" color="primary" inset label="启用插件" />
      <VSwitch v-model="config.show_sidebar_nav" color="primary" inset label="显示侧边栏入口" />
      <VSwitch v-model="config.notify_enabled" color="primary" inset label="启用通知" />
      <VSelect
        v-model="config.mediaservers"
        label="媒体服务器"
        :items="mediaServerOptions"
        multiple
        chips
        clearable
        :loading="loadingOptions"
        :disabled="!mediaServerOptions.length"
        hint="自动读取 MoviePilot 已配置的媒体服务器；留空表示扫描所有 Emby。"
        persistent-hint
      />
      <VSelect
        v-model="config.downloaders"
        label="下载器"
        :items="downloaderOptions"
        multiple
        chips
        clearable
        :loading="loadingOptions"
        :disabled="!downloaderOptions.length"
        hint="自动读取 MoviePilot 已启用的 QB / Transmission；留空表示全部支持的下载器。"
        persistent-hint
      />
      <VSwitch v-model="config.ai_suggestions" color="primary" inset label="允许 AI 参与清理建议排序" disabled />
      <VSwitch v-model="config.default_delete_source" color="error" inset label="默认同时删除源文件" />
      <VSwitch v-model="config.delete_seed_tasks" color="warning" inset label="删除资源时同步删除保种任务" />
    </div>
  </div>
</template>

<style scoped>
.mlk-config-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
}

</style>
