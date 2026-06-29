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
  media: [],
  recommendations: [],
  pending_plan: null,
  history: [],
  capabilities: {},
  media_server_options: [],
})

const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`)
const summary = computed(() => status.value.summary || {})
const mediaRows = computed(() => status.value.media || [])
const recommendationRows = computed(() => status.value.recommendations || [])
const pendingPlan = computed(() => status.value.pending_plan)
const historyRows = computed(() => status.value.history || [])
const capabilities = computed(() => status.value.capabilities || {})
const mediaServerOptions = computed(() => status.value.media_server_options || [])
const selectedPlanItems = computed(() => selectedMedia.value.map(planItemFromMedia))
const selectedSize = computed(() => selectedMedia.value.reduce((sum, item) => sum + Number(item.size || 0), 0))
const planReady = computed(() => pendingPlan.value?.status === 'ready')

const filteredMediaRows = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  return mediaRows.value.filter((item) => {
    if (keyword && !`${item.title || ''}${item.path_preview || ''}`.toLowerCase().includes(keyword)) return false
    if (typeFilter.value === '电影' && item.type !== 'movie') return false
    if (typeFilter.value === '剧集' && item.type !== 'series') return false
    if (watchFilter.value === '已看完' && !item.watched) return false
    if (watchFilter.value === '未看完' && item.watched) return false
    return true
  })
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

const mediaHeaders = [
  { title: '媒体', key: 'title', minWidth: 260 },
  { title: '类型', key: 'type_label', width: 92 },
  { title: '评分', key: 'rating', width: 80 },
  { title: '进度', key: 'progress', width: 110 },
  { title: '体积', key: 'size', width: 110 },
  { title: '入库时间', key: 'added_at', width: 168 },
]

const planHeaders = [
  { title: '媒体', key: 'title' },
  { title: '状态', key: 'status', width: 110 },
  { title: '预计释放', key: 'size', width: 120 },
  { title: '删除目标', key: 'target_count', width: 110 },
  { title: '说明', key: 'message' },
]

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
    activeTab.value = 'library'
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
        <div class="text-body-2 text-medium-emphasis">Emby 媒体库整理、观看进度和空间释放</div>
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
            <div class="mlk-capability-grid">
              <VSheet v-for="(enabled, key) in capabilities" :key="key" border rounded class="mlk-capability">
                <VIcon :icon="enabled ? 'mdi-check-circle-outline' : 'mdi-progress-wrench'" :color="enabled ? 'success' : 'warning'" />
                <span>{{ capabilityLabels[key] || key }}</span>
              </VSheet>
            </div>
            <div class="mlk-disk-grid" v-if="summary.disk_status?.length">
              <VSheet v-for="disk in summary.disk_status" :key="disk.path" border rounded class="mlk-disk-row">
                <div>
                  <div class="text-subtitle-2">{{ disk.path }}</div>
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
              <VTextField v-model="searchText" label="搜索名称或路径" prepend-inner-icon="mdi-magnify" density="comfortable" hide-details clearable />
              <VSelect v-model="watchFilter" label="观看状态" :items="['全部', '已看完', '未看完']" density="comfortable" hide-details />
              <VSelect v-model="typeFilter" label="媒体类型" :items="['全部', '电影', '剧集']" density="comfortable" hide-details />
            </div>
            <VDataTable
              v-model="selectedMedia"
              :headers="mediaHeaders"
              :items="filteredMediaRows"
              item-value="id"
              show-select
              return-object
              density="comfortable"
              class="mlk-table"
            >
              <template #item.title="{ item }">
                <div class="mlk-media-cell">
                  <VAvatar rounded size="46" color="surface-variant">
                    <VImg v-if="item.image_url" :src="item.image_url" cover />
                    <VIcon v-else :icon="item.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline'" />
                  </VAvatar>
                  <div>
                    <div class="font-weight-medium">{{ item.title }}</div>
                    <div class="text-caption text-medium-emphasis">{{ item.path_preview || item.server }}</div>
                  </div>
                </div>
              </template>
              <template #item.rating="{ item }">{{ item.rating || '-' }}</template>
              <template #item.size="{ item }">{{ formatBytes(item.size) }}</template>
              <template #no-data>
                <VEmptyState icon="mdi-folder-open-outline" title="暂无媒体库数据" text="请先执行媒体库扫描。" />
              </template>
            </VDataTable>
          </div>
        </VWindowItem>

        <VWindowItem value="recommendations">
          <div class="mlk-section">
            <VDataTable
              :headers="[
                { title: '建议类型', key: 'reason', width: 130 },
                { title: '媒体', key: 'title' },
                { title: '进度', key: 'progress', width: 100 },
                { title: '预计释放', key: 'size', width: 120 },
                { title: '说明', key: 'message' },
              ]"
              :items="recommendationRows"
              density="comfortable"
            >
              <template #item.size="{ item }">{{ formatBytes(item.size) }}</template>
              <template #no-data>
                <VEmptyState icon="mdi-lightbulb-on-outline" title="暂无清理建议" text="扫描后会列出已看完、入库较久未观看和占用较大的候选。 " />
              </template>
            </VDataTable>
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
            <VTextarea
              v-model="configDraft.storage_paths"
              label="磁盘容量检查路径"
              hint="每行一个路径；留空时会尝试使用 MoviePilot 的 LIBRARY_PATH / DOWNLOAD_PATH。"
              persistent-hint
              auto-grow
              rows="3"
            />
            <div class="mlk-switch-grid">
              <VSwitch v-model="configDraft.ai_suggestions" color="primary" inset label="允许 AI 参与清理建议排序" disabled />
              <VSwitch v-model="configDraft.default_delete_source" color="error" inset label="默认同时删除源文件" />
            </div>
          </div>
        </VWindowItem>
      </VWindow>
    </VSheet>

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
.mlk-media-cell,
.mlk-disk-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mlk-header,
.mlk-toolbar,
.mlk-plan-bar {
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

.mlk-plan-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mlk-danger-actions {
  justify-content: flex-end;
}

.mlk-disk-row {
  justify-content: space-between;
}

.mlk-settings {
  max-width: 960px;
}

@media (max-width: 720px) {
  .mlk-page {
    padding: 12px;
  }

  .mlk-header > .v-btn,
  .mlk-plan-bar > .v-btn {
    width: 100%;
  }
}
</style>
