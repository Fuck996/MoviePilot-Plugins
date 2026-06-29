<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  createDefaultConfig,
  formatBytes,
  formatNumber,
  planItemFromMedia,
  toEditableConfig,
  toPayloadConfig,
  unwrapResponse,
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
const executing = ref(false)
const error = ref('')
const notice = ref('')
const activeTab = ref('overview')
const selectedMedia = ref([])
const selectedLibraryId = ref('')
const selectedMediaDetail = ref(null)
const detailDialog = ref(false)
const deleteSource = ref(false)
const searchText = ref('')
const watchFilter = ref('全部')
const typeFilter = ref('全部')
const executeDialog = ref(false)
const executeConfirmed = ref(false)
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
})

const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`)
const summary = computed(() => status.value.summary || {})
const libraries = computed(() => status.value.libraries || [])
const mediaRows = computed(() => status.value.media || [])
const recommendationRows = computed(() => status.value.recommendations || [])
const pendingPlan = computed(() => status.value.pending_plan)
const historyRows = computed(() => status.value.history || [])
const capabilities = computed(() => status.value.capabilities || {})
const mediaServerOptions = computed(() => status.value.media_server_options || [])
const selectedPlanItems = computed(() => selectedMedia.value.map(planItemFromMedia))
const selectedSize = computed(() => selectedMedia.value.reduce((sum, item) => sum + Number(item.size || 0), 0))
const planReady = computed(() => pendingPlan.value?.status === 'ready')
const selectedLibrary = computed(() => libraries.value.find(item => item.id === selectedLibraryId.value))

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
    if (watchFilter.value === '已看完' && !item.watched) return false
    if (watchFilter.value === '未看完' && item.watched) return false
    return true
  })
})

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
]

function isSelected(item) {
  return selectedMedia.value.some(selected => selected.id === item.id)
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

function clearLibraryFilter() {
  selectedLibraryId.value = ''
}

function openMediaDetail(item) {
  selectedMediaDetail.value = item
  detailDialog.value = true
}

async function createSinglePlan(item) {
  selectedMedia.value = [item]
  detailDialog.value = false
  await createPlan()
}

async function loadStatus() {
  loading.value = true
  error.value = ''
  try {
    const response = await props.api.get(`${pluginBase.value}/status`)
    applyStatus(unwrapResponse(response))
  } catch (err) {
    error.value = err?.message || '加载媒体库管家状态失败'
  } finally {
    loading.value = false
  }
}

function applyStatus(data) {
  if (!data) return
  status.value = data
  configDraft.value = toEditableConfig(status.value.config)
  deleteSource.value = Boolean(configDraft.value.default_delete_source)
}

async function saveConfig() {
  saving.value = true
  error.value = ''
  notice.value = ''
  try {
    const response = await props.api.post(`${pluginBase.value}/config`, toPayloadConfig(configDraft.value))
    applyStatus(unwrapResponse(response))
    notice.value = '设置已保存'
  } catch (err) {
    error.value = err?.message || '保存设置失败'
  } finally {
    saving.value = false
  }
}

async function scanLibrary() {
  scanning.value = true
  error.value = ''
  notice.value = ''
  try {
    const response = await props.api.post(`${pluginBase.value}/scan`, {})
    if (response?.success === false) {
      error.value = response.message || '扫描媒体库失败'
      return
    }
    applyStatus(unwrapResponse(response))
    notice.value = '媒体库扫描完成'
    activeTab.value = 'overview'
  } catch (err) {
    error.value = err?.message || '扫描媒体库失败'
  } finally {
    scanning.value = false
  }
}

async function createPlan() {
  planning.value = true
  error.value = ''
  notice.value = ''
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan`, {
      item_ids: selectedMedia.value.map(item => item.id),
      items: selectedPlanItems.value,
      delete_source: deleteSource.value,
    })
    if (response?.success === false) {
      error.value = response.message || '生成清理计划失败'
      return
    }
    const data = unwrapResponse(response)
    applyStatus(data?.status)
    notice.value = '清理计划已生成'
    activeTab.value = 'plan'
  } catch (err) {
    error.value = err?.message || '生成清理计划失败'
  } finally {
    planning.value = false
  }
}

function openExecuteDialog() {
  executeConfirmed.value = false
  executeDialog.value = true
}

async function executePlan() {
  if (!pendingPlan.value?.id || !executeConfirmed.value) return
  executing.value = true
  error.value = ''
  notice.value = ''
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/execute`, {
      plan_id: pendingPlan.value.id,
      confirm: true,
    })
    if (response?.success === false) {
      error.value = response.message || '执行清理计划失败'
      return
    }
    applyStatus(unwrapResponse(response))
    notice.value = '清理计划已执行'
    executeDialog.value = false
    selectedMedia.value = []
  } catch (err) {
    error.value = err?.message || '执行清理计划失败'
  } finally {
    executing.value = false
  }
}

defineExpose({
  loadStatus,
  saveConfig,
  scanLibrary,
  loading,
  saving,
  scanning,
})

onMounted(loadStatus)
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
      <VBtn prepend-icon="mdi-content-save" color="primary" variant="flat" :loading="saving" @click="saveConfig">
        保存设置
      </VBtn>
    </div>

    <VProgressLinear v-if="loading" indeterminate color="primary" rounded />
    <VAlert v-if="error" type="error" variant="tonal" density="comfortable">{{ error }}</VAlert>
    <VAlert v-if="notice" type="success" variant="tonal" density="comfortable">{{ notice }}</VAlert>
    <VAlert v-if="summary.disk_warning" type="warning" variant="tonal" density="comfortable">
      检测到磁盘容量低于阈值，请优先查看清理建议。
    </VAlert>

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
                <VImg v-if="library.image_url" :src="library.image_url" cover class="mlk-library-image" />
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
                  <div class="text-body-2 text-medium-emphasis">剩余 {{ formatBytes(disk.free) }} / {{ disk.free_percent }}%</div>
                </div>
                <VChip :color="disk.warning ? 'warning' : 'success'" variant="tonal">
                  {{ disk.warning ? '容量紧张' : '容量正常' }}
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
              <VTextField v-model="searchText" label="搜索名称、简介或路径" prepend-inner-icon="mdi-magnify" density="comfortable" hide-details clearable />
              <VSelect v-model="watchFilter" label="观看状态" :items="['全部', '已看完', '未看完']" density="comfortable" hide-details />
              <VSelect v-model="typeFilter" label="媒体类型" :items="['全部', '电影', '剧集']" density="comfortable" hide-details />
            </div>

            <div class="mlk-filter-row">
              <VChip
                :color="!selectedLibraryId ? 'primary' : undefined"
                :variant="!selectedLibraryId ? 'flat' : 'tonal'"
                @click="clearLibraryFilter"
              >
                全部媒体库
              </VChip>
              <VChip
                v-for="library in libraryCards"
                :key="library.id"
                :color="selectedLibraryId === library.id ? 'primary' : undefined"
                :variant="selectedLibraryId === library.id ? 'flat' : 'tonal'"
                @click="openLibrary(library)"
              >
                {{ library.title }}
              </VChip>
            </div>

            <VAlert v-if="selectedLibrary" type="info" variant="tonal" density="compact">
              当前入口：{{ selectedLibrary.title }}，共 {{ filteredMediaRows.length }} 个媒体条目。
            </VAlert>

            <div v-if="filteredMediaRows.length" class="mlk-media-grid">
              <VSheet
                v-for="item in filteredMediaRows"
                :key="item.id"
                border
                rounded
                class="mlk-media-card"
                @click="openMediaDetail(item)"
              >
                <div class="mlk-poster">
                  <VImg v-if="item.image_url" :src="item.image_url" cover />
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
                    <VChip size="small" :color="item.watched ? 'success' : 'warning'" variant="tonal">{{ item.progress }}</VChip>
                    <VChip size="small" variant="tonal">{{ formatBytes(item.size) }}</VChip>
                  </div>
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
                  <VImg v-if="item.image_url" :src="item.image_url" cover />
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
                <div class="text-subtitle-1 font-weight-medium">待生成计划</div>
                <div class="text-body-2 text-medium-emphasis">
                  已选择 {{ selectedMedia.length }} 项，当前 Emby 可见体积 {{ formatBytes(selectedSize) }}
                </div>
              </div>
              <VSpacer />
              <VSwitch v-model="deleteSource" color="error" hide-details inset label="同时删除源文件" />
              <VBtn color="primary" variant="flat" :loading="planning" :disabled="!selectedMedia.length" @click="createPlan">
                生成清理计划
              </VBtn>
            </VSheet>

            <VSheet v-if="pendingPlan" border rounded class="mlk-plan-detail">
              <div class="mlk-plan-title">
                <div>
                  <div class="text-subtitle-1 font-weight-medium">计划 {{ pendingPlan.id }}</div>
                  <div class="text-body-2 text-medium-emphasis">{{ pendingPlan.message }}</div>
                </div>
                <VChip :color="planReady ? 'success' : 'warning'" variant="tonal">{{ planReady ? '可执行' : '需处理' }}</VChip>
              </div>
              <VDataTable :headers="planHeaders" :items="pendingPlan.items || []" density="comfortable">
                <template #item.status="{ item }">
                  <VChip :color="item.status === 'ready' ? 'success' : 'warning'" variant="tonal" size="small">
                    {{ item.status === 'ready' ? '已匹配' : '未匹配' }}
                  </VChip>
                </template>
                <template #item.size="{ item }">{{ formatBytes(item.size) }}</template>
                <template #item.target_count="{ item }">{{ item.delete_targets?.length || 0 }}</template>
              </VDataTable>
              <div class="mlk-danger-actions">
                <div class="text-body-2 text-medium-emphasis">
                  预计释放 {{ formatBytes(pendingPlan.estimated_reclaim_size) }}
                </div>
                <VBtn
                  color="error"
                  variant="tonal"
                  prepend-icon="mdi-delete-alert-outline"
                  :disabled="!planReady"
                  @click="openExecuteDialog"
                >
                  执行清理计划
                </VBtn>
              </div>
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
            <div class="mlk-switch-grid">
              <VSwitch v-model="configDraft.enabled" color="primary" inset label="启用插件" />
              <VSwitch v-model="configDraft.show_sidebar_nav" color="primary" inset label="显示侧边栏入口" />
              <VSwitch v-model="configDraft.notify_enabled" color="primary" inset label="启用通知" />
              <VSwitch v-model="configDraft.disk_warning_enabled" color="warning" inset label="启用磁盘容量告警" />
            </div>
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
            <div class="mlk-form-grid">
              <VTextField v-model.number="configDraft.disk_warning_free_gb" type="number" min="0" label="剩余容量阈值 GB" />
              <VTextField v-model.number="configDraft.disk_warning_free_percent" type="number" min="0" label="剩余比例阈值 %" />
              <VTextField v-model="configDraft.scan_cron" label="扫描周期 Cron" />
            </div>
            <VTextarea
              v-model="configDraft.library_names"
              label="限定媒体库名称"
              hint="每行一个媒体库名称，留空表示全部媒体库。"
              persistent-hint
              auto-grow
              rows="3"
            />
            <VAlert type="info" variant="tonal" density="comfortable">
              磁盘容量会跟随 Emby 扫描到的电影文件和剧集分集路径自动识别，支持多个挂载磁盘，无需手动配置路径。
            </VAlert>
            <div class="mlk-switch-grid">
              <VSwitch v-model="configDraft.ai_suggestions" color="primary" inset label="允许 AI 参与清理建议排序" disabled />
              <VSwitch v-model="configDraft.default_delete_source" color="error" inset label="默认同时删除源文件" />
            </div>
          </div>
        </VWindowItem>
      </VWindow>
    </VSheet>

    <VDialog v-model="detailDialog" max-width="920">
      <VCard v-if="selectedMediaDetail">
        <div class="mlk-detail-layout">
          <div class="mlk-detail-poster">
            <VImg v-if="selectedMediaDetail.image_url" :src="selectedMediaDetail.image_url" cover />
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
              <VChip :color="selectedMediaDetail.watched ? 'success' : 'warning'" variant="tonal">{{ selectedMediaDetail.progress }}</VChip>
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
                <div class="text-caption text-medium-emphasis">首播/上映</div>
                <div>{{ selectedMediaDetail.premiere_date || '-' }}</div>
              </div>
              <div>
                <div class="text-caption text-medium-emphasis">集数</div>
                <div>{{ selectedMediaDetail.type === 'series' ? `${selectedMediaDetail.watched_episodes}/${selectedMediaDetail.total_episodes}` : '-' }}</div>
              </div>
              <div class="mlk-detail-wide">
                <div class="text-caption text-medium-emphasis">路径</div>
                <div>{{ selectedMediaDetail.path_preview || selectedMediaDetail.path || '-' }}</div>
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

    <VDialog v-model="executeDialog" max-width="640">
      <VCard>
        <VCardTitle>确认执行清理计划</VCardTitle>
        <VCardText>
          <div class="text-body-2">
            本次计划将删除 {{ pendingPlan?.items?.length || 0 }} 个媒体条目关联文件，预计释放
            {{ formatBytes(pendingPlan?.estimated_reclaim_size) }}。执行成功后会删除对应整理记录。
          </div>
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
.mlk-plan-title,
.mlk-danger-actions,
.mlk-disk-row,
.mlk-detail-head,
.mlk-detail-actions,
.mlk-chip-row,
.mlk-filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mlk-header,
.mlk-toolbar,
.mlk-plan-bar,
.mlk-filter-row {
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
.mlk-plan-detail,
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

.mlk-plan-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mlk-danger-actions,
.mlk-detail-actions {
  justify-content: flex-end;
}

.mlk-disk-row {
  justify-content: space-between;
}

.mlk-settings {
  max-width: 960px;
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
  .mlk-plan-bar > .v-btn {
    width: 100%;
  }

  .mlk-detail-layout {
    grid-template-columns: 1fr;
  }

  .mlk-detail-poster {
    min-height: 340px;
  }
}
</style>
