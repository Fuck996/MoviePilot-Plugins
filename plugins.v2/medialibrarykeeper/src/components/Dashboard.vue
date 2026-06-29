<script setup>
import { computed, onMounted, ref } from 'vue'
import { formatBytes, formatNumber, unwrapResponse } from '../provider'

const props = defineProps({
  api: {
    type: Object,
    default: () => ({}),
  },
  pluginId: {
    type: String,
    default: 'MediaLibraryKeeper',
  },
  config: {
    type: Object,
    default: () => ({ attrs: {} }),
  },
  refreshInterval: {
    type: Number,
    default: 0,
  },
})

const loading = ref(false)
const status = ref({ summary: {} })

const summary = computed(() => status.value.summary || {})
const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`)
const cardTitle = computed(() => props.config?.attrs?.title || '媒体库管家')
const cardSubtitle = computed(() => props.config?.attrs?.subtitle || '空间风险与清理建议')

async function loadStatus() {
  loading.value = true
  try {
    const response = await props.api.get(`${pluginBase.value}/status`)
    status.value = unwrapResponse(response) || status.value
  } finally {
    loading.value = false
  }
}

onMounted(loadStatus)
</script>

<template>
  <VSheet border rounded class="mlk-dashboard">
    <div class="mlk-dashboard-head">
      <div>
        <div class="text-subtitle-1 font-weight-medium">{{ cardTitle }}</div>
        <div class="text-caption text-medium-emphasis">{{ cardSubtitle }}</div>
      </div>
      <VProgressCircular v-if="loading" indeterminate size="20" width="2" />
    </div>
    <div class="mlk-dashboard-grid">
      <div>
        <div class="text-caption text-medium-emphasis">媒体库</div>
        <div class="text-h6">{{ formatNumber(summary.libraries) }}</div>
      </div>
      <div>
        <div class="text-caption text-medium-emphasis">剧集</div>
        <div class="text-h6">{{ formatNumber(summary.series) }}</div>
      </div>
      <div>
        <div class="text-caption text-medium-emphasis">预计释放</div>
        <div class="text-h6">{{ formatBytes(summary.estimated_reclaim_size) }}</div>
      </div>
    </div>
    <VAlert type="info" variant="tonal" density="compact">等待接入 Emby 扫描</VAlert>
  </VSheet>
</template>

<style scoped>
.mlk-dashboard {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  min-height: 180px;
}

.mlk-dashboard-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.mlk-dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
</style>
