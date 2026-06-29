<script setup>
import { onMounted, ref } from 'vue'
import { toEditableConfig, toPayloadConfig } from '../provider'

const props = defineProps({
  initialConfig: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['save', 'close'])
const config = ref(toEditableConfig())

function saveConfig() {
  emit('save', toPayloadConfig(config.value))
}

onMounted(() => {
  config.value = toEditableConfig(props.initialConfig)
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
      <div class="mlk-config-grid">
        <VTextField v-model.number="config.disk_warning_free_gb" type="number" label="剩余容量阈值 GB" />
        <VTextField v-model.number="config.disk_warning_free_percent" type="number" label="剩余比例阈值 %" />
        <VTextField v-model="config.scan_cron" label="扫描周期 Cron" />
      </div>
      <VTextarea
        v-model="config.library_names"
        label="限定媒体库名称"
        hint="留空表示全部媒体库。后续接入 Emby 后按行填写媒体库名称。"
        persistent-hint
        auto-grow
        rows="3"
      />
      <VSwitch v-model="config.ai_suggestions" color="primary" inset label="允许 AI 参与清理建议排序" />
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
