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
const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`)

function saveConfig() {
  emit('save', toPayloadConfig(config.value))
}

async function loadMediaServerOptions() {
  if (!props.api?.get) return
  loadingOptions.value = true
  try {
    const response = await props.api.get(`${pluginBase.value}/status`)
    mediaServerOptions.value = unwrapResponse(response)?.media_server_options || []
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
      <VSwitch v-model="config.disk_warning_enabled" color="warning" inset label="启用磁盘容量告警" />
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
      <div class="mlk-config-grid">
        <VTextField v-model.number="config.disk_warning_free_gb" type="number" min="0" label="剩余容量阈值 GB" />
        <VTextField v-model.number="config.disk_warning_free_percent" type="number" min="0" label="剩余比例阈值 %" />
        <VTextField v-model="config.scan_cron" label="扫描周期 Cron" />
      </div>
      <VTextarea
        v-model="config.library_names"
        label="限定媒体库名称"
        hint="每行一个媒体库名称，留空表示全部媒体库。"
        persistent-hint
        auto-grow
        rows="3"
      />
      <VAlert type="info" variant="tonal" density="comfortable">
        磁盘容量会跟随 Emby 扫描到的媒体路径自动识别，支持多个挂载磁盘，无需手动配置路径。
      </VAlert>
      <VSwitch v-model="config.ai_suggestions" color="primary" inset label="允许 AI 参与清理建议排序" disabled />
      <VSwitch v-model="config.default_delete_source" color="error" inset label="默认同时删除源文件" />
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

.mlk-config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
</style>
