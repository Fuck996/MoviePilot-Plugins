<script setup>
import { computed, onMounted, ref } from 'vue'
import { formatBytes, formatNumber, readStatusCache, unwrapResponse, writeStatusCache } from '../provider'

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
const statusText = computed(() => {
  if (summary.value.disk_warning) return '磁盘容量紧张，请查看清理建议'
  if (summary.value.last_scan_at) return `最近扫描：${summary.value.last_scan_at}`
  return '尚未扫描媒体库'
})

async function loadStatus() {
  loading.value = true
  try {
    const response = await props.api.get(`${pluginBase.value}/status`)
    applyStatus(unwrapResponse(response))
  } finally {
    loading.value = false
  }
}

function applyStatus(data, options = {}) {
  if (!data) return
  status.value = data
  if (options.persist !== false) {
    writeStatusCache(props.pluginId, data)
  }
}

function loadCachedStatus() {
  const cached = readStatusCache(props.pluginId)
  if (cached) applyStatus(cached, { persist: false })
}

onMounted(() => {
  loadCachedStatus()
  loadStatus()
})
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
    <VAlert :type="summary.disk_warning ? 'warning' : 'info'" variant="tonal" density="compact">
      {{ statusText }}
    </VAlert>
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
