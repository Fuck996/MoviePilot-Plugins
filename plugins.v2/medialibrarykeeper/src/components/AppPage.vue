<script setup>
import { computed, getCurrentInstance, onMounted, ref } from 'vue'
import {
  createDefaultCleanupRule,
  createDefaultConfig,
  formatBytes,
  formatNumber,
  planItemFromMedia,
  readStatusCache,
  toEditableConfig,
  toPayloadConfig,
  unwrapResponse,
  writeStatusCache,
} from '../provider'

const props = defineProps({
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

const loading = ref(false)
const saving = ref(false)
const planning = ref(false)
const scanning = ref(false)
const ruleScanning = ref(false)
const executing = ref(false)
const fallbackToast = ref({
  show: false,
  text: '',
  color: 'success',
})
const activeTab = ref('overview')
const selectedMedia = ref([])
const selectedLibraryId = ref('')
const selectedMediaDetail = ref(null)
const detailDialog = ref(false)
const selectedPlanItem = ref(null)
const planTargetDialog = ref(false)
const planExpanded = ref(false)
const deleteSource = ref(false)
const searchText = ref('')
const watchFilter = ref('全部')
const typeFilter = ref('全部')
const mediaSort = ref('last_episode_added_at')
const sortDesc = ref(true)
const pageSize = ref(100)
const executeDialog = ref(false)
const executeConfirmed = ref(false)
const deletePlanDialog = ref(false)
const deletePlanConfirmed = ref(false)
const deletingPlan = ref(false)
const configDraft = ref(toEditableConfig())
const status = ref({
  config: createDefaultConfig(),
  summary: {},
  libraries: [],
  media: [],
  recommendations: [],
  pending_plan: null,
  history: [],
  capabilities: {},
  media_server_options: [],
  downloader_options: [],
})

const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`)
const summary = computed(() => status.value.summary || {})
const libraries = computed(() => status.value.libraries || [])
const mediaRows = computed(() => status.value.media || [])
const recommendationRows = computed(() => status.value.recommendations || [])
const pendingPlan = computed(() => status.value.pending_plan)
const pendingPlanItems = computed(() => pendingPlan.value?.items || [])
const pendingPlanStats = computed(() => pendingPlanItems.value.reduce((stats, item) => {
  if (item.type === 'movie') stats.movies += 1
  if (item.type === 'series') stats.series += 1
  stats.size += Number(item.size || 0)
  return stats
}, { movies: 0, series: 0, size: 0 }))
const historyRows = computed(() => status.value.history || [])
const capabilities = computed(() => status.value.capabilities || {})
const mediaServerOptions = computed(() => status.value.media_server_options || [])
const downloaderOptions = computed(() => status.value.downloader_options || [])
const selectedPlanItems = computed(() => selectedMedia.value.map(planItemFromMedia))

function resolveImageUrl(url) {
  if (!url || /^(https?:|data:|blob:|\/)/.test(url)) return url || ''
  const baseURL = props.api?.defaults?.baseURL || '/api/v1'
  return `${String(baseURL).replace(/\/$/, '')}/${String(url).replace(/^\//, '')}`
}
const selectedSize = computed(() => selectedMedia.value.reduce((sum, item) => sum + Number(item.size || 0), 0))
const planReady = computed(() => pendingPlan.value?.status === 'ready')
const planExecutable = computed(() => Number(pendingPlan.value?.ready_count || 0) > 0)
const planStatusText = computed(() => {
  if (planReady.value) return '可执行'
  if (planExecutable.value) return '部分可执行'
  return '需处理'
})
const planStatusColor = computed(() => {
  if (planReady.value) return 'success'
  if (planExecutable.value) return 'warning'
  return 'error'
})
const selectedLibrary = computed(() => libraries.value.find(item => item.id === selectedLibraryId.value))
const toast = getCurrentInstance()?.appContext.config.globalProperties?.$toast
const libraryOptions = computed(() => libraries.value.map(item => ({ title: item.server ? `${item.title} · ${item.server}` : item.title, value: item.id })))
const librarySwitchOptions = computed(() => [
  { title: '全部媒体库', value: '' },
  ...libraryOptions.value,
])
const sortOptions = [
  { title: '最后一集添加日期', value: 'last_episode_added_at' },
  { title: '最后观看日期', value: 'last_watched_at' },
  { title: '大小', value: 'size' },
  { title: '评分', value: 'rating' },
]
const scanCronOptions = [
  { title: '每 1 小时', value: '0 */1 * * *' },
  { title: '每 3 小时', value: '0 */3 * * *' },
  { title: '每 6 小时', value: '0 */6 * * *' },
  { title: '每 12 小时', value: '0 */12 * * *' },
  { title: '每天 03:00', value: '0 3 * * *' },
  { title: '每周一 03:00', value: '0 3 * * 1' },
]
const mediaWatchFilterOptions = ['全部', '已播放', '观看中', '未播放']
const cleanupWatchStateOptions = [
  { title: '不限制', value: 'any' },
  { title: '已看完', value: 'watched' },
  { title: '未看完', value: 'unwatched' },
]
const pageSizeOptions = [50, 100, 500, 1000]

const filteredMediaRows = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  return mediaRows.value.filter((item) => {
    if (selectedLibraryId.value && item.library_id !== selectedLibraryId.value) return false
    if (keyword) {
      const haystack = `${item.title || ''}${item.overview || ''}${item.path_preview || ''}`.toLowerCase()
      if (!haystack.includes(keyword)) return false
    }
    if (typeFilter.value === '电影' && item.type !== 'movie') return false
    if (typeFilter.value === '剧集' && item.type !== 'series') return false
    const watchState = resolveWatchState(item)
    if (watchFilter.value === '已播放' && watchState !== 'watched') return false
    if (watchFilter.value === '观看中' && watchState !== 'watching') return false
    if (watchFilter.value === '未播放' && watchState !== 'unwatched') return false
    return true
  })
})

const sortedMediaRows = computed(() => {
  const key = mediaSort.value
  const direction = sortDesc.value ? -1 : 1
  return [...filteredMediaRows.value].sort((left, right) => {
    const leftValue = sortValue(left, key)
    const rightValue = sortValue(right, key)
    if (leftValue === rightValue) {
      return String(left.title || '').localeCompare(String(right.title || ''), 'zh-CN')
    }
    return leftValue > rightValue ? direction : -direction
  })
})

const visibleMediaRows = computed(() => sortedMediaRows.value.slice(0, pageSize.value))

const libraryCards = computed(() => {
  const counts = mediaRows.value.reduce((acc, item) => {
    const key = item.library_id || 'unknown'
    acc[key] = acc[key] || { total: 0, movies: 0, series: 0, size: 0 }
    acc[key].total += 1
    acc[key].size += Number(item.size || 0)
    if (item.type === 'movie') acc[key].movies += 1
    if (item.type === 'series') acc[key].series += 1
    return acc
  }, {})
  return libraries.value.map(item => ({
    ...item,
    counts: counts[item.id] || { total: 0, movies: 0, series: 0, size: 0 },
  }))
})

const statCards = computed(() => [
  { label: '媒体库', value: formatNumber(summary.value.libraries), icon: 'mdi-folder-multiple-outline', color: 'primary' },
  { label: '电影', value: formatNumber(summary.value.movies), icon: 'mdi-movie-open-outline', color: 'info' },
  { label: '剧集', value: formatNumber(summary.value.series), icon: 'mdi-television-classic', color: 'success' },
  { label: '预计可释放', value: formatBytes(summary.value.estimated_reclaim_size), icon: 'mdi-harddisk-remove', color: 'warning' },
])

const capabilityLabels = {
  emby_scan: 'Emby 扫描',
  transfer_history_match: '整理记录匹配',
  storage_delete: '文件删除',
  ai_suggestions: 'AI 建议',
  notification: '通知推送',
}

const planHeaders = [
  { title: '媒体', key: 'title' },
  { title: '状态', key: 'status', width: 110 },
  { title: '预计释放', key: 'size', width: 120 },
  { title: '删除目标', key: 'target_count', width: 110 },
  { title: '说明', key: 'message' },
  { title: '操作', key: 'actions', width: 132, sortable: false },
]

function isSelected(item) {
  return selectedMedia.value.some(selected => selected.id === item.id)
}

function sortValue(item, key) {
  if (key === 'size') return Number(item.size || 0)
  if (key === 'rating') return Number(item.rating || 0)
  return String(item[key] || '')
}

function resolveWatchState(item) {
  return item.watch_state || (item.watched ? 'watched' : 'unwatched')
}

function watchStateColor(item) {
  const watchState = resolveWatchState(item)
  if (watchState === 'watched') return 'success'
  if (watchState === 'watching') return 'info'
  return 'warning'
}

function watchStateText(item) {
  const watchState = resolveWatchState(item)
  if (watchState === 'watched') return item.type === 'series' ? `已播放 ${item.progress}` : '已播放'
  if (watchState === 'watching') return item.type === 'series' ? `观看中 ${item.progress}` : '观看中'
  return item.type === 'series' ? `未播放 ${item.progress}` : '未播放'
}

function toggleSelected(item) {
  if (isSelected(item)) {
    selectedMedia.value = selectedMedia.value.filter(selected => selected.id !== item.id)
    return
  }
  selectedMedia.value = [...selectedMedia.value, item]
}

function openLibrary(library) {
  selectedLibraryId.value = library?.id || ''
  activeTab.value = 'library'
}

function addCleanupRule() {
  configDraft.value.cleanup_rules = [
    ...(configDraft.value.cleanup_rules || []),
    createDefaultCleanupRule(),
  ]
}

function removeCleanupRule(index) {
  const rules = [...(configDraft.value.cleanup_rules || [])]
  rules.splice(index, 1)
  configDraft.value.cleanup_rules = rules.length ? rules : [createDefaultCleanupRule()]
}

function addPathMapping() {
  configDraft.value.path_mappings = [
    ...(configDraft.value.path_mappings || []),
    { emby_path: '', mp_path: '' },
  ]
}

function removePathMapping(index) {
  const mappings = [...(configDraft.value.path_mappings || [])]
  mappings.splice(index, 1)
  configDraft.value.path_mappings = mappings
}

function openMediaDetail(item) {
  selectedMediaDetail.value = item
  detailDialog.value = true
}

function openPlanTargetDialog(item) {
  selectedPlanItem.value = item
  planTargetDialog.value = true
}

async function createSinglePlan(item) {
  selectedMedia.value = [item]
  detailDialog.value = false
  await createPlan()
}

async function loadStatus() {
  loading.value = true
  try {
    const response = await props.api.get(`${pluginBase.value}/status`)
    applyStatus(unwrapResponse(response))
  } catch (err) {
    showToast(err?.message || '加载媒体库管家状态失败', 'error')
  } finally {
    loading.value = false
  }
}

function loadCachedStatus() {
  const cached = readStatusCache(props.pluginId)
  if (cached) applyStatus(cached, { persist: false })
}

function applyStatus(data, options = {}) {
  if (!data) return
  status.value = data
  configDraft.value = toEditableConfig(status.value.config)
  deleteSource.value = Boolean(configDraft.value.default_delete_source)
  if (options.persist !== false) {
    writeStatusCache(props.pluginId, data)
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const response = await props.api.post(`${pluginBase.value}/config`, toPayloadConfig(configDraft.value))
    applyStatus(unwrapResponse(response))
    showToast('设置已保存')
  } catch (err) {
    showToast(err?.message || '保存设置失败', 'error')
  } finally {
    saving.value = false
  }
}

async function scanCleanupRules() {
  ruleScanning.value = true
  try {
    const configResponse = await props.api.post(`${pluginBase.value}/config`, toPayloadConfig(configDraft.value))
    if (configResponse?.success === false) {
      showToast(configResponse.message || '保存设置失败', 'error')
      return
    }
    const response = await props.api.post(`${pluginBase.value}/cleanup/scan`, {})
    if (response?.success === false) {
      showToast(response.message || '按规则扫描失败', 'error')
      return
    }
    applyStatus(unwrapResponse(response))
    const message = response?.message || '已按当前规则完成扫描识别'
    showToast(message, message.includes('已有') || message.includes('未命中') ? 'warning' : 'success')
    activeTab.value = 'plan'
    planExpanded.value = false
  } catch (err) {
    showToast(err?.message || '按规则扫描失败', 'error')
  } finally {
    ruleScanning.value = false
  }
}

async function scanLibrary() {
  scanning.value = true
  try {
    const response = await props.api.post(`${pluginBase.value}/scan`, {})
    if (response?.success === false) {
      showToast(response.message || '扫描媒体库失败', 'error')
      return
    }
    applyStatus(unwrapResponse(response))
    showToast('媒体库扫描完成')
    if (summary.value.disk_warning) {
      showToast('检测到磁盘容量低于阈值，请查看清理建议。', 'warning')
    }
    activeTab.value = 'overview'
  } catch (err) {
    showToast(err?.message || '扫描媒体库失败', 'error')
  } finally {
    scanning.value = false
  }
}

async function createPlan() {
  planning.value = true
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan`, {
      item_ids: selectedMedia.value.map(item => item.id),
      items: selectedPlanItems.value,
      delete_source: deleteSource.value,
    })
    if (response?.success === false) {
      showToast(response.message || '生成清理计划失败', 'error')
      return
    }
    const data = unwrapResponse(response)
    applyStatus(data?.status)
    showToast('清理计划已生成')
    activeTab.value = 'plan'
    planExpanded.value = false
  } catch (err) {
    showToast(err?.message || '生成清理计划失败', 'error')
  } finally {
    planning.value = false
  }
}

async function updatePlanItems(action, itemIds) {
  if (!pendingPlan.value?.id || !itemIds.length) return
  planning.value = true
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan/items`, {
      plan_id: pendingPlan.value.id,
      action,
      item_ids: itemIds,
    })
    if (response?.success === false) {
      showToast(response.message || '调整清理批次失败', 'error')
      return
    }
    const data = unwrapResponse(response)
    applyStatus(data?.status)
    showToast(action === 'remove' ? '已移出清理批次' : '已加入清理批次')
  } catch (err) {
    showToast(err?.message || '调整清理批次失败', 'error')
  } finally {
    planning.value = false
  }
}

async function addSelectedToPlan() {
  await updatePlanItems('add', selectedMedia.value.map(item => item.id))
}

async function removePlanItem(item) {
  await updatePlanItems('remove', [item.media_id])
}

function openExecuteDialog() {
  executeConfirmed.value = false
  executeDialog.value = true
}

function openDeletePlanDialog() {
  deletePlanConfirmed.value = false
  deletePlanDialog.value = true
}

async function deletePlan() {
  if (!pendingPlan.value?.id || !deletePlanConfirmed.value) return
  deletingPlan.value = true
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan/delete`, {
      plan_id: pendingPlan.value.id,
      confirm: true,
    })
    if (response?.success === false) {
      showToast(response.message || '删除清理批次失败', 'error')
      return
    }
    applyStatus(unwrapResponse(response))
    showToast(response?.message || '清理批次已删除')
    deletePlanDialog.value = false
    selectedMedia.value = []
  } catch (err) {
    showToast(err?.message || '删除清理批次失败', 'error')
  } finally {
    deletingPlan.value = false
  }
}

async function executePlan() {
  if (!pendingPlan.value?.id || !executeConfirmed.value) return
  executing.value = true
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/execute`, {
      plan_id: pendingPlan.value.id,
      confirm: true,
    })
    if (response?.success === false) {
      showToast(response.message || '执行清理计划失败', 'error')
      return
    }
    applyStatus(unwrapResponse(response))
    showToast('清理计划已执行')
    executeDialog.value = false
    selectedMedia.value = []
  } catch (err) {
    showToast(err?.message || '执行清理计划失败', 'error')
  } finally {
    executing.value = false
  }
}

function showToast(message, type = 'success') {
  const toastMethod = toast?.[type] || toast
  if (typeof toastMethod === 'function') {
    toastMethod(message)
    return
  }
  fallbackToast.value = {
    show: true,
    text: message,
    color: type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'success',
  }
}

defineExpose({
  loadStatus,
  saveConfig,
  scanLibrary,
  scanCleanupRules,
  loading,
  saving,
  scanning,
  ruleScanning,
})

onMounted(() => {
  loadCachedStatus()
  loadStatus()
})
</script>

<template>
  <div class="mlk-page">
    <div v-if="!hideTitle" class="mlk-header">
      <div>
        <div class="text-h5 font-weight-bold">媒体库管家</div>
        <div class="text-body-2 text-medium-emphasis">按 Emby 媒体库入口管理观看进度和空间释放</div>
      </div>
      <VSpacer />
      <VBtn prepend-icon="mdi-database-sync-outline" variant="tonal" :loading="scanning" @click="scanLibrary">
        立即扫描媒体库
      </VBtn>
    </div>

    <VProgressLinear v-if="loading" indeterminate color="primary" rounded />
    <div class="mlk-stats">
      <VSheet v-for="card in statCards" :key="card.label" border rounded class="mlk-stat-card">
        <VIcon :icon="card.icon" :color="card.color" size="28" />
        <div>
          <div class="text-caption text-medium-emphasis">{{ card.label }}</div>
          <div class="text-h6">{{ card.value }}</div>
        </div>
      </VSheet>
    </div>

    <VSheet border rounded class="mlk-panel">
      <VTabs v-model="activeTab" density="comfortable">
        <VTab value="overview">总览</VTab>
        <VTab value="library">媒体库</VTab>
        <VTab value="recommendations">清理建议</VTab>
        <VTab value="plan">清理计划</VTab>
        <VTab value="history">执行记录</VTab>
        <VTab value="settings">设置</VTab>
      </VTabs>
      <VDivider />

      <VWindow v-model="activeTab" :touch="false">
        <VWindowItem value="overview">
          <div class="mlk-section">
            <div v-if="libraryCards.length" class="mlk-library-grid">
              <VSheet
                v-for="library in libraryCards"
                :key="library.id"
                border
                rounded
                class="mlk-library-card"
                @click="openLibrary(library)"
              >
                <VImg v-if="library.image_url" :src="resolveImageUrl(library.image_url)" cover class="mlk-library-image" />
                <div v-else class="mlk-library-fallback">
                  <VIcon icon="mdi-folder-multiple-image" size="42" />
                </div>
                <div class="mlk-library-meta">
                  <div class="text-subtitle-1 font-weight-medium">{{ library.title }}</div>
                  <div class="text-caption text-medium-emphasis">{{ library.server }} · {{ library.type_label }}</div>
                  <div class="mlk-chip-row">
                    <VChip size="small" variant="tonal">{{ library.counts.movies }} 部电影</VChip>
                    <VChip size="small" variant="tonal">{{ library.counts.series }} 部剧集</VChip>
                    <VChip size="small" variant="tonal">{{ formatBytes(library.counts.size) }}</VChip>
                  </div>
                </div>
              </VSheet>
            </div>

            <div class="mlk-capability-grid">
              <VSheet v-for="(enabled, key) in capabilities" :key="key" border rounded class="mlk-capability">
                <VIcon :icon="enabled ? 'mdi-check-circle-outline' : 'mdi-progress-wrench'" :color="enabled ? 'success' : 'warning'" />
                <span>{{ capabilityLabels[key] || key }}</span>
              </VSheet>
            </div>

            <div class="mlk-disk-grid" v-if="summary.disk_status?.length">
              <VSheet v-for="disk in summary.disk_status" :key="disk.path" border rounded class="mlk-disk-row">
                <div>
                  <div class="text-subtitle-2">{{ disk.display_name || disk.mount_point || '未知卷' }}</div>
                  <div v-if="disk.unavailable" class="text-body-2 text-warning">
                    {{ disk.error || '路径不可访问' }}
                  </div>
                  <div v-else class="text-body-2 text-medium-emphasis">剩余 {{ formatBytes(disk.free) }} / {{ disk.free_percent }}%</div>
                </div>
                <VChip :color="disk.unavailable || disk.warning ? 'warning' : 'success'" variant="tonal">
                  {{ disk.unavailable ? '不可访问' : disk.warning ? '容量紧张' : '容量正常' }}
                </VChip>
              </VSheet>
            </div>

            <VEmptyState
              v-if="!mediaRows.length"
              icon="mdi-database-search-outline"
              title="尚未扫描媒体库"
              text="完成媒体服务器配置后，执行一次媒体库扫描即可查看电影、剧集、进度和清理候选。"
            />
          </div>
        </VWindowItem>

        <VWindowItem value="library">
          <div class="mlk-section">
            <div class="mlk-toolbar">
              <VSelect v-model="selectedLibraryId" label="媒体库" :items="librarySwitchOptions" density="comfortable" hide-details />
              <VTextField v-model="searchText" label="搜索名称、简介或路径" prepend-inner-icon="mdi-magnify" density="comfortable" hide-details clearable />
              <VSelect v-model="watchFilter" label="观看状态" :items="mediaWatchFilterOptions" density="comfortable" hide-details />
              <VSelect v-model="typeFilter" label="媒体类型" :items="['全部', '电影', '剧集']" density="comfortable" hide-details />
              <VSelect v-model="mediaSort" label="排序规则" :items="sortOptions" density="comfortable" hide-details />
              <VSelect v-model.number="pageSize" label="显示数量" :items="pageSizeOptions" density="comfortable" hide-details />
              <VBtn :prepend-icon="sortDesc ? 'mdi-sort-descending' : 'mdi-sort-ascending'" variant="tonal" @click="sortDesc = !sortDesc">
                {{ sortDesc ? '降序' : '升序' }}
              </VBtn>
            </div>

            <VAlert v-if="selectedLibrary" type="info" variant="tonal" density="compact">
              当前入口：{{ selectedLibrary.title }}，共 {{ filteredMediaRows.length }} 个媒体条目，显示 {{ visibleMediaRows.length }} 个。
            </VAlert>

            <div v-if="visibleMediaRows.length" class="mlk-media-grid">
              <VSheet
                v-for="item in visibleMediaRows"
                :key="item.id"
                border
                rounded
                class="mlk-media-card"
                @click="openMediaDetail(item)"
              >
                <div class="mlk-poster">
                  <VImg v-if="item.image_url" :src="resolveImageUrl(item.image_url)" cover />
                  <div v-else class="mlk-poster-fallback">
                    <VIcon :icon="item.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline'" size="44" />
                  </div>
                  <VBtn
                    class="mlk-select-btn"
                    :icon="isSelected(item) ? 'mdi-check-circle' : 'mdi-plus-circle-outline'"
                    :color="isSelected(item) ? 'success' : undefined"
                    variant="text"
                    @click.stop="toggleSelected(item)"
                  />
                </div>
                <div class="mlk-media-body">
                  <div class="mlk-media-title">{{ item.title }}</div>
                  <div class="text-caption text-medium-emphasis">{{ item.year || '未知年份' }} · {{ item.type_label }} · {{ item.library || item.server }}</div>
                  <div class="mlk-chip-row">
                    <VChip size="small" variant="tonal">{{ item.rating || '-' }} 分</VChip>
                    <VChip size="small" :color="watchStateColor(item)" variant="tonal">{{ watchStateText(item) }}</VChip>
                    <VChip size="small" variant="tonal">{{ formatBytes(item.size) }}</VChip>
                  </div>
                  <div class="text-caption text-medium-emphasis">末集 {{ item.last_episode_added_at || '-' }}</div>
                  <div class="text-caption text-medium-emphasis">观看 {{ item.last_watched_at || '-' }}</div>
                </div>
              </VSheet>
            </div>
            <VEmptyState v-else icon="mdi-folder-open-outline" title="没有匹配的媒体" text="调整媒体库入口、类型、观看状态或搜索关键词后再试。" />
          </div>
        </VWindowItem>

        <VWindowItem value="recommendations">
          <div class="mlk-section">
            <div v-if="recommendationRows.length" class="mlk-media-grid">
              <VSheet
                v-for="item in recommendationRows"
                :key="item.id"
                border
                rounded
                class="mlk-media-card"
                @click="openMediaDetail(item)"
              >
                <div class="mlk-poster">
                  <VImg v-if="item.image_url" :src="resolveImageUrl(item.image_url)" cover />
                  <div v-else class="mlk-poster-fallback">
                    <VIcon :icon="item.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline'" size="44" />
                  </div>
                </div>
                <div class="mlk-media-body">
                  <div class="mlk-media-title">{{ item.title }}</div>
                  <div class="text-caption text-medium-emphasis">{{ item.reason }}</div>
                  <div class="text-caption text-medium-emphasis">{{ item.message }}</div>
                  <div class="mlk-chip-row">
                    <VChip size="small" variant="tonal">{{ item.progress }}</VChip>
                    <VChip size="small" variant="tonal">{{ formatBytes(item.size) }}</VChip>
                  </div>
                </div>
              </VSheet>
            </div>
            <VEmptyState v-else icon="mdi-lightbulb-on-outline" title="暂无清理建议" text="扫描后会列出已看完、入库较久未观看和占用较大的候选。" />
          </div>
        </VWindowItem>

        <VWindowItem value="plan">
          <div class="mlk-section">
            <VSheet border rounded class="mlk-plan-bar">
              <div>
                <div class="text-subtitle-1 font-weight-medium">当前选择</div>
                <div class="text-body-2 text-medium-emphasis">
                  已选择 {{ selectedMedia.length }} 项，当前 Emby 可见体积 {{ formatBytes(selectedSize) }}
                </div>
              </div>
              <VSpacer />
              <VSwitch v-model="deleteSource" color="error" hide-details inset label="同时删除源文件" />
              <VBtn color="primary" variant="flat" :loading="planning" :disabled="!selectedMedia.length" @click="createPlan">
                生成新批次
              </VBtn>
              <VBtn variant="tonal" :loading="planning" :disabled="!pendingPlan || !selectedMedia.length" @click="addSelectedToPlan">
                加入当前批次
              </VBtn>
            </VSheet>

            <VSheet v-if="pendingPlan" border rounded class="mlk-plan-card">
              <div class="mlk-plan-summary">
                <div class="mlk-plan-main">
                  <div class="text-subtitle-1 font-weight-medium">批次 {{ pendingPlan.batch_id || pendingPlan.id }}</div>
                  <div class="text-caption text-medium-emphasis">{{ pendingPlan.source_label || '手动选择' }} · {{ pendingPlan.created_at }}</div>
                  <div class="text-body-2 text-medium-emphasis">{{ pendingPlan.message }}</div>
                  <div class="mlk-chip-row">
                    <VChip size="small" variant="tonal" color="info">电影 {{ pendingPlanStats.movies }}</VChip>
                    <VChip size="small" variant="tonal" color="success">剧集 {{ pendingPlanStats.series }}</VChip>
                    <VChip size="small" variant="tonal" color="primary">可执行 {{ pendingPlan.ready_count || 0 }}/{{ pendingPlanItems.length }}</VChip>
                    <VChip size="small" variant="tonal" color="warning">预计释放 {{ formatBytes(pendingPlan.estimated_reclaim_size || pendingPlanStats.size) }}</VChip>
                    <VChip :color="planStatusColor" size="small" variant="tonal">{{ planStatusText }}</VChip>
                  </div>
                </div>
                <div class="mlk-plan-actions">
                  <VTooltip :text="planExpanded ? '收起批次明细' : '展开批次明细'" location="top">
                    <template #activator="{ props: tooltipProps }">
                      <VBtn
                        v-bind="tooltipProps"
                        :icon="planExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down'"
                        variant="text"
                        @click="planExpanded = !planExpanded"
                      />
                    </template>
                  </VTooltip>
                  <VTooltip text="删除当前批次记录，不删除文件" location="top">
                    <template #activator="{ props: tooltipProps }">
                      <span v-bind="tooltipProps">
                        <VBtn
                          color="error"
                          variant="text"
                          prepend-icon="mdi-close-circle-outline"
                          :loading="deletingPlan"
                          @click="openDeletePlanDialog"
                        >
                          删除批次
                        </VBtn>
                      </span>
                    </template>
                  </VTooltip>
                  <VTooltip text="执行当前批次中已匹配的清理条目" location="top">
                    <template #activator="{ props: tooltipProps }">
                      <span v-bind="tooltipProps">
                        <VBtn
                          color="error"
                          variant="tonal"
                          prepend-icon="mdi-delete-alert-outline"
                          :disabled="!planExecutable"
                          @click="openExecuteDialog"
                        >
                          执行清理
                        </VBtn>
                      </span>
                    </template>
                  </VTooltip>
                </div>
              </div>
              <VExpandTransition>
                <div v-show="planExpanded" class="mlk-plan-detail">
                  <VDataTable :headers="planHeaders" :items="pendingPlanItems" density="comfortable">
                    <template #item.status="{ item }">
                      <VChip :color="item.status === 'ready' ? 'success' : 'warning'" variant="tonal" size="small">
                        {{ item.status === 'ready' ? '已匹配' : '未匹配' }}
                      </VChip>
                    </template>
                    <template #item.size="{ item }">{{ formatBytes(item.size) }}</template>
                    <template #item.target_count="{ item }">{{ item.delete_targets?.length || 0 }}</template>
                    <template #item.actions="{ item }">
                      <VTooltip text="查看删除目标" location="top">
                        <template #activator="{ props: tooltipProps }">
                          <span v-bind="tooltipProps">
                            <VBtn
                              icon="mdi-file-eye-outline"
                              variant="text"
                              :disabled="!item.delete_targets?.length"
                              @click="openPlanTargetDialog(item)"
                            />
                          </span>
                        </template>
                      </VTooltip>
                      <VTooltip text="从批次移除" location="top">
                        <template #activator="{ props: tooltipProps }">
                          <VBtn
                            v-bind="tooltipProps"
                            icon="mdi-minus-circle-outline"
                            variant="text"
                            color="error"
                            :loading="planning"
                            @click="removePlanItem(item)"
                          />
                        </template>
                      </VTooltip>
                    </template>
                  </VDataTable>
                </div>
              </VExpandTransition>
            </VSheet>
          </div>
        </VWindowItem>

        <VWindowItem value="history">
          <div class="mlk-section">
            <VDataTable
              :headers="[
                { title: '时间', key: 'created_at', width: 168 },
                { title: '结果', key: 'status', width: 110 },
                { title: '释放空间', key: 'reclaim_size', width: 120 },
                { title: '整理记录', key: 'deleted_records', width: 110 },
                { title: '说明', key: 'message' },
              ]"
              :items="historyRows"
              density="comfortable"
            >
              <template #item.status="{ item }">
                <VChip :color="item.status === 'success' ? 'success' : 'error'" variant="tonal" size="small">
                  {{ item.status === 'success' ? '成功' : '失败' }}
                </VChip>
              </template>
              <template #item.reclaim_size="{ item }">{{ formatBytes(item.reclaim_size) }}</template>
              <template #no-data>
                <VEmptyState icon="mdi-history" title="暂无执行记录" text="每次真实清理的结果都会保存在这里。" />
              </template>
            </VDataTable>
          </div>
        </VWindowItem>

        <VWindowItem value="settings">
          <div class="mlk-section mlk-settings">
            <div class="mlk-settings-group">
              <div class="text-subtitle-1 font-weight-medium">基础配置</div>
              <div class="mlk-switch-grid">
                <VSwitch v-model="configDraft.enabled" color="primary" inset label="启用插件" />
                <VSwitch v-model="configDraft.show_sidebar_nav" color="primary" inset label="显示侧边栏入口" />
                <VSwitch v-model="configDraft.notify_enabled" color="primary" inset label="启用通知" />
                <VSwitch v-model="configDraft.disk_warning_enabled" color="warning" inset label="启用磁盘容量告警" />
              </div>
              <div class="mlk-form-grid">
                <VSelect
                  v-model="configDraft.mediaservers"
                  label="媒体服务器"
                  :items="mediaServerOptions"
                  multiple
                  chips
                  clearable
                  hint="留空表示扫描所有 Emby 媒体服务器。"
                  persistent-hint
                />
                <VSelect
                  v-model="configDraft.downloaders"
                  label="下载器"
                  :items="downloaderOptions"
                  multiple
                  chips
                  clearable
                  hint="留空表示全部支持的下载器。"
                  persistent-hint
                />
              </div>
            </div>

            <div class="mlk-settings-group">
              <div class="text-subtitle-1 font-weight-medium">扫描与容量告警</div>
              <div class="mlk-form-grid">
                <VSelect v-model="configDraft.scan_cron" label="扫描周期" :items="scanCronOptions" />
                <VTextField v-model.number="configDraft.disk_warning_free_gb" type="number" min="0" label="剩余容量低于 GB" />
                <VTextField v-model.number="configDraft.disk_warning_free_percent" type="number" min="0" label="剩余比例低于 %" />
              </div>
              <VAlert type="info" variant="tonal" density="comfortable">
                磁盘容量会跟随 Emby 扫描到的电影文件和剧集分集路径自动识别，支持多个挂载磁盘。
              </VAlert>
            </div>

            <div class="mlk-settings-group">
              <div class="mlk-section-header">
                <div>
                  <div class="text-subtitle-1 font-weight-medium">目录映射</div>
                  <div class="text-caption text-medium-emphasis">将 Emby 容器路径转换为 MoviePilot 容器内可访问路径。</div>
                </div>
                <VBtn prepend-icon="mdi-plus" color="primary" variant="tonal" @click="addPathMapping">
                  添加映射
                </VBtn>
              </div>
              <VSheet
                v-for="(mapping, index) in configDraft.path_mappings"
                :key="`path-mapping-${index}`"
                border
                rounded
                class="mlk-path-mapping-row"
              >
                <VTextField v-model="mapping.emby_path" label="Emby 路径前缀" placeholder="/video" density="comfortable" hide-details />
                <VTextField v-model="mapping.mp_path" label="MP 路径前缀" placeholder="/media/video" density="comfortable" hide-details />
                <VBtn icon="mdi-delete-outline" color="error" variant="text" @click="removePathMapping(index)" />
              </VSheet>
              <VAlert v-if="!(configDraft.path_mappings || []).length" type="info" variant="tonal" density="comfortable">
                Emby 与 MoviePilot 挂载路径一致时无需配置。
              </VAlert>
            </div>

            <div class="mlk-settings-group">
              <div class="text-subtitle-1 font-weight-medium">删除行为</div>
              <div class="mlk-switch-grid">
                <VSwitch v-model="configDraft.ai_suggestions" color="primary" inset label="允许 AI 参与清理建议排序" disabled />
                <VSwitch v-model="configDraft.default_delete_source" color="error" inset label="默认同时删除源文件" />
                <VSwitch v-model="configDraft.delete_seed_tasks" color="warning" inset label="删除资源时同步删除保种任务" />
              </div>
            </div>

            <VDivider />

            <div class="mlk-settings-group">
              <div class="mlk-section-header">
                <div>
                  <div class="text-subtitle-1 font-weight-medium">清理计划</div>
                  <div class="text-caption text-medium-emphasis">先限定参与计划的媒体库，再配置多条条件组合；任意一组命中即进入待清理批次。</div>
                </div>
                <VBtn prepend-icon="mdi-plus" color="primary" variant="tonal" @click="addCleanupRule">
                  添加组合
                </VBtn>
              </div>
              <VSelect
                v-model="configDraft.cleanup_libraries"
                label="清理媒体库"
                :items="libraryOptions"
                multiple
                chips
                clearable
                hint="留空表示全部媒体库。"
                persistent-hint
              />
              <VSheet
                v-for="(rule, index) in configDraft.cleanup_rules"
                :key="rule.id || index"
                border
                rounded
                class="mlk-rule-row"
              >
                <div class="mlk-rule-title">组合 {{ index + 1 }}</div>
                <div class="mlk-rule-grid">
                  <VSelect
                    v-model="rule.operator"
                    label="组内关系"
                    :items="[
                      { title: '全部满足', value: 'and' },
                      { title: '任一满足', value: 'or' },
                    ]"
                    density="comfortable"
                    hide-details
                  />
                  <VSelect
                    v-model="rule.watch_state"
                    label="观看状态"
                    :items="cleanupWatchStateOptions"
                    density="comfortable"
                    hide-details
                  />
                  <VTextField v-model.number="rule.unwatched_days" type="number" min="0" label="未观看天数" density="comfortable" hide-details />
                  <VTextField v-model.number="rule.min_size_gb" type="number" min="0" label="大于 GB" density="comfortable" hide-details />
                  <VTextField v-model.number="rule.max_rating" type="number" min="0" step="0.1" label="评分低于/等于" density="comfortable" hide-details />
                  <VBtn icon="mdi-delete-outline" color="error" variant="text" :disabled="configDraft.cleanup_rules.length <= 1" @click="removeCleanupRule(index)" />
                </div>
              </VSheet>
              <div class="text-caption text-medium-emphasis">数字条件填 0 表示不启用；每条组合至少启用一个条件才会生效。</div>
            </div>

            <div class="mlk-settings-actions">
              <VBtn prepend-icon="mdi-playlist-search" color="secondary" variant="tonal" :loading="ruleScanning" @click="scanCleanupRules">
                立即按规则扫描
              </VBtn>
              <VBtn prepend-icon="mdi-content-save" color="primary" variant="flat" :loading="saving" @click="saveConfig">
                保存设置
              </VBtn>
            </div>
          </div>
        </VWindowItem>
      </VWindow>
    </VSheet>

    <VDialog v-model="detailDialog" max-width="920">
      <VCard v-if="selectedMediaDetail">
        <div class="mlk-detail-layout">
          <div class="mlk-detail-poster">
            <VImg v-if="selectedMediaDetail.image_url" :src="resolveImageUrl(selectedMediaDetail.image_url)" cover />
            <div v-else class="mlk-poster-fallback">
              <VIcon :icon="selectedMediaDetail.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline'" size="54" />
            </div>
          </div>
          <div class="mlk-detail-content">
            <div class="mlk-detail-head">
              <div>
                <div class="text-h6 font-weight-bold">{{ selectedMediaDetail.title }}</div>
                <div class="text-body-2 text-medium-emphasis">
                  {{ selectedMediaDetail.year || '未知年份' }} · {{ selectedMediaDetail.type_label }} · {{ selectedMediaDetail.library || selectedMediaDetail.server }}
                </div>
              </div>
              <VBtn icon="mdi-close" variant="text" @click="detailDialog = false" />
            </div>
            <div class="mlk-chip-row">
              <VChip color="primary" variant="tonal">{{ selectedMediaDetail.rating || '-' }} 分</VChip>
              <VChip :color="watchStateColor(selectedMediaDetail)" variant="tonal">{{ watchStateText(selectedMediaDetail) }}</VChip>
              <VChip variant="tonal">{{ formatBytes(selectedMediaDetail.size) }}</VChip>
            </div>
            <p class="mlk-overview">
              {{ selectedMediaDetail.overview || '暂无简介。' }}
            </p>
            <div class="mlk-detail-grid">
              <div>
                <div class="text-caption text-medium-emphasis">服务器</div>
                <div>{{ selectedMediaDetail.server }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">入库时间</div>
                <div>{{ selectedMediaDetail.added_at || '-' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">最后一集添加</div>
                <div>{{ selectedMediaDetail.last_episode_added_at || '-' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">最后观看</div>
                <div>{{ selectedMediaDetail.last_watched_at || '-' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">首播/上映</div>
                <div>{{ selectedMediaDetail.premiere_date || '-' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">集数</div>
                <div>{{ selectedMediaDetail.type === 'series' ? `${selectedMediaDetail.watched_episodes}/${selectedMediaDetail.total_episodes}` : '-' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">所属卷</div>
                <div>{{ selectedMediaDetail.volume_name || '-' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">卷剩余</div>
                <div>{{ selectedMediaDetail.volume_free_percent !== null && selectedMediaDetail.volume_free_percent !== undefined ? `${selectedMediaDetail.volume_free_percent}%` : '-' }}</div>
              </div>
              <div class="mlk-detail-wide">
                <div class="text-caption text-medium-emphasis">路径</div>
                <div>{{ selectedMediaDetail.path_preview || selectedMediaDetail.path || '-' }}</div>
              </div>
              <div class="mlk-detail-wide" v-if="selectedMediaDetail.emby_path_preview">
                <div class="text-caption text-medium-emphasis">Emby 原路径</div>
                <div>{{ selectedMediaDetail.emby_path_preview }}</div>
              </div>
              <div class="mlk-detail-wide" v-if="selectedMediaDetail.genres?.length">
                <div class="text-caption text-medium-emphasis">类型</div>
                <div class="mlk-chip-row">
                  <VChip v-for="genre in selectedMediaDetail.genres" :key="genre" size="small" variant="tonal">{{ genre }}</VChip>
                </div>
              </div>
            </div>
            <VDivider />
            <div class="mlk-detail-actions">
              <VSwitch v-model="deleteSource" color="error" hide-details inset label="同时删除源文件" />
              <VSpacer />
              <VBtn variant="tonal" :color="isSelected(selectedMediaDetail) ? 'success' : 'primary'" @click="toggleSelected(selectedMediaDetail)">
                {{ isSelected(selectedMediaDetail) ? '移出清理选择' : '加入清理选择' }}
              </VBtn>
              <VBtn color="primary" variant="flat" :loading="planning" @click="createSinglePlan(selectedMediaDetail)">
                为此项生成计划
              </VBtn>
            </div>
          </div>
        </div>
      </VCard>
    </VDialog>

    <VDialog v-model="planTargetDialog" max-width="820">
      <VCard v-if="selectedPlanItem">
        <VCardTitle>审核删除目标</VCardTitle>
        <VCardText>
          <div class="text-subtitle-2 mb-3">{{ selectedPlanItem.title }}</div>
          <div v-if="selectedPlanItem.delete_targets?.length" class="mlk-target-list">
            <VSheet v-for="target in selectedPlanItem.delete_targets" :key="`${target.kind}-${target.path}`" border rounded class="mlk-target-row">
              <div class="mlk-target-head">
                <VChip :color="target.kind === 'src' ? 'error' : 'primary'" variant="tonal" size="small">
                  {{ target.kind_label || (target.kind === 'src' ? '源文件' : '媒体库文件') }}
                </VChip>
                <VChip v-if="target.match_source === 'directory_mapping'" color="info" variant="tonal" size="small">
                  目录映射
                </VChip>
              </div>
              <div class="text-body-2">{{ target.path_preview || target.path }}</div>
              <div v-if="target.directory_mapping" class="text-caption text-medium-emphasis">
                {{ target.directory_mapping.name || '未命名目录配置' }} / {{ target.directory_mapping.transfer_type || '未知整理方式' }}
              </div>
            </VSheet>
          </div>
          <VEmptyState v-else icon="mdi-file-search-outline" title="没有可审核的删除目标" />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn variant="text" @click="planTargetDialog = false">关闭</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="executeDialog" max-width="640">
      <VCard>
        <VCardTitle>确认执行清理计划</VCardTitle>
        <VCardText>
          <div class="text-body-2">
            本次计划将删除 {{ pendingPlan?.ready_count || 0 }} 个已匹配媒体条目关联文件，预计释放
            {{ formatBytes(pendingPlan?.estimated_reclaim_size) }}。执行成功后会删除对应整理记录。
          </div>
          <VAlert v-if="pendingPlan && (pendingPlan.ready_count || 0) < pendingPlanItems.length" type="info" variant="tonal" density="comfortable" class="mt-4">
            批次中还有 {{ pendingPlanItems.length - (pendingPlan.ready_count || 0) }} 个未匹配条目，本次不会执行这些条目。
          </VAlert>
          <VAlert type="warning" variant="tonal" density="comfortable" class="mt-4">
            这是不可逆操作；请确认媒体库文件和源文件范围都符合预期。
          </VAlert>
          <VCheckbox v-model="executeConfirmed" color="error" label="我已确认删除范围，允许执行清理" hide-details class="mt-2" />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn variant="text" @click="executeDialog = false">取消</VBtn>
          <VBtn color="error" variant="flat" :loading="executing" :disabled="!executeConfirmed" @click="executePlan">
            确认删除
          </VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VDialog v-model="deletePlanDialog" max-width="560">
      <VCard>
        <VCardTitle>删除当前清理批次</VCardTitle>
        <VCardText>
          <div class="text-body-2">
            将删除批次 {{ pendingPlan?.batch_id || pendingPlan?.id }} 的待处理记录，不会删除媒体文件、源文件或整理记录。
          </div>
          <VCheckbox v-model="deletePlanConfirmed" color="error" label="我确认只删除当前批次记录" hide-details class="mt-4" />
        </VCardText>
        <VCardActions>
          <VSpacer />
          <VBtn variant="text" @click="deletePlanDialog = false">取消</VBtn>
          <VBtn color="error" variant="flat" :loading="deletingPlan" :disabled="!deletePlanConfirmed" @click="deletePlan">
            删除批次
          </VBtn>
        </VCardActions>
      </VCard>
    </VDialog>

    <VSnackbar v-model="fallbackToast.show" :color="fallbackToast.color" location="bottom right" timeout="3200">
      {{ fallbackToast.text }}
    </VSnackbar>
  </div>
</template>

<style scoped>
.mlk-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.mlk-header,
.mlk-toolbar,
.mlk-plan-bar,
.mlk-plan-summary,
.mlk-plan-actions,
.mlk-section-header,
.mlk-disk-row,
.mlk-detail-head,
.mlk-detail-actions,
.mlk-chip-row,
.mlk-settings-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mlk-header,
.mlk-toolbar,
.mlk-plan-bar,
.mlk-plan-summary,
.mlk-plan-actions {
  flex-wrap: wrap;
}

.mlk-stats,
.mlk-capability-grid,
.mlk-form-grid,
.mlk-switch-grid,
.mlk-disk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 12px;
}

.mlk-library-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 14px;
}

.mlk-media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 14px;
}

.mlk-stat-card,
.mlk-capability,
.mlk-plan-bar,
.mlk-plan-card,
.mlk-disk-row {
  padding: 16px;
}

.mlk-stat-card,
.mlk-capability {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mlk-panel {
  overflow: hidden;
}

.mlk-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.mlk-toolbar > * {
  min-width: 180px;
  flex: 1 1 180px;
}

.mlk-library-card,
.mlk-media-card {
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.16s ease, transform 0.16s ease;
}

.mlk-library-card:hover,
.mlk-media-card:hover {
  border-color: rgb(var(--v-theme-primary));
  transform: translateY(-2px);
}

.mlk-library-image,
.mlk-library-fallback {
  height: 126px;
}

.mlk-library-fallback,
.mlk-poster-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: rgba(var(--v-theme-surface-variant), 0.55);
}

.mlk-library-meta,
.mlk-media-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}

.mlk-chip-row {
  flex-wrap: wrap;
  gap: 6px;
}

.mlk-poster {
  position: relative;
  aspect-ratio: 2 / 3;
  background: rgba(var(--v-theme-surface-variant), 0.55);
}

.mlk-select-btn {
  position: absolute;
  top: 4px;
  right: 4px;
}

.mlk-media-title {
  min-height: 40px;
  font-weight: 600;
  line-height: 1.25;
}

.mlk-plan-card,
.mlk-plan-detail,
.mlk-plan-main {
  display: flex;
  flex-direction: column;
}

.mlk-plan-card {
  gap: 12px;
}

.mlk-plan-summary {
  justify-content: space-between;
}

.mlk-plan-main {
  flex: 1 1 320px;
  min-width: 0;
  gap: 8px;
}

.mlk-plan-actions {
  justify-content: flex-end;
}

.mlk-plan-detail {
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.mlk-target-list,
.mlk-target-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mlk-target-row {
  padding: 12px;
}

.mlk-target-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.mlk-detail-actions {
  justify-content: flex-end;
}

.mlk-disk-row {
  justify-content: space-between;
}

.mlk-settings {
  max-width: 1200px;
}

.mlk-settings-group,
.mlk-rule-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mlk-section-header {
  justify-content: space-between;
  align-items: flex-start;
}

.mlk-rule-row {
  padding: 14px;
}

.mlk-rule-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.72);
}

.mlk-rule-grid {
  display: grid;
  grid-template-columns: minmax(132px, 0.9fr) minmax(132px, 0.9fr) minmax(126px, 0.8fr) minmax(112px, 0.7fr) minmax(140px, 0.9fr) 44px;
  gap: 10px;
  align-items: start;
}

.mlk-path-mapping-row {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(180px, 1fr) 44px;
  gap: 10px;
  align-items: start;
  padding: 14px;
}

.mlk-settings-actions {
  justify-content: flex-end;
}

.mlk-detail-layout {
  display: grid;
  grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
  min-height: 520px;
}

.mlk-detail-poster {
  min-height: 520px;
  background: rgba(var(--v-theme-surface-variant), 0.55);
}

.mlk-detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
}

.mlk-detail-head {
  align-items: flex-start;
  justify-content: space-between;
}

.mlk-overview {
  margin: 0;
  color: rgba(var(--v-theme-on-surface), 0.82);
  line-height: 1.7;
  white-space: pre-wrap;
}

.mlk-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.mlk-detail-wide {
  grid-column: 1 / -1;
}

@media (max-width: 720px) {
  .mlk-page {
    padding: 12px;
  }

  .mlk-header > .v-btn,
  .mlk-plan-bar > .v-btn,
  .mlk-plan-actions {
    width: 100%;
  }

  .mlk-plan-actions {
    justify-content: stretch;
  }

  .mlk-plan-actions span,
  .mlk-plan-actions .v-btn:not(.v-btn--icon) {
    flex: 1 1 auto;
  }

  .mlk-section-header {
    flex-direction: column;
  }

  .mlk-section-header > .v-btn {
    width: 100%;
  }

  .mlk-rule-grid {
    grid-template-columns: 1fr;
  }

  .mlk-detail-layout {
    grid-template-columns: 1fr;
  }

  .mlk-detail-poster {
    min-height: 340px;
  }
}
</style>
