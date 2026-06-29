<script setup>
import { computed, onMounted, ref } from 'vue'
import {
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
const scaning = ref(false)
const error = ref('')
const notice = ref('')
const activeTab = ref('overview')
const selectedMedia = ref([])
const deleteSource = ref(false)
const configDraft = ref(toEditableConfig())
const status = ref({
  config: cloneConfig(),
  summary: {},
  media: [],
  recommendations: [],
  pending_plan: null,
  history: [],
  capabilities: {},
})

const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`)
const summary = computed(() => status.value.summary || {})
const mediaRows = computed(() => status.value.media || [])
const recommendationRows = computed(() => status.value.recommendations || [])
const pendingPlan = computed(() => status.value.pending_plan)
const historyRows = computed(() => status.value.history || [])
const capabilities = computed(() => status.value.capabilities || {})
const selectedPlanItems = computed(() => selectedMedia.value.map(planItemFromMedia))
const selectedSize = computed(() => selectedMedia.value.reduce((sum, item) => sum + Number(item.size || 0), 0))

const statCards = computed(() => [
  { label: '媒体库', value: formatNumber(summary.value.libraries), icon: 'mdi-folder-multiple-outline', color: 'primary' },
  { label: '电影', value: formatNumber(summary.value.movies), icon: 'mdi-movie-open-outline', color: 'info' },
  { label: '剧集', value: formatNumber(summary.value.series), icon: 'mdi-television-classic', color: 'success' },
  { label: '预计可释放', value: formatBytes(summary.value.estimated_reclaim_size), icon: 'mdi-harddisk-remove', color: 'warning' },
])

async function loadStatus() {
  loading.value = true
  error.value = ''
  try {
    const response = await props.api.get(`${pluginBase.value}/status`)
    const data = unwrapResponse(response)
    status.value = data || status.value
    configDraft.value = toEditableConfig(status.value.config)
    deleteSource.value = Boolean(configDraft.value.default_delete_source)
  } catch (err) {
    error.value = err?.message || '加载媒体库管家状态失败'
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  saving.value = true
  error.value = ''
  notice.value = ''
  try {
    const response = await props.api.post(`${pluginBase.value}/config`, toPayloadConfig(configDraft.value))
    const data = unwrapResponse(response)
    status.value = data || status.value
    notice.value = '配置已保存'
  } catch (err) {
    error.value = err?.message || '保存配置失败'
  } finally {
    saving.value = false
  }
}

async function scanLibrary() {
  scaning.value = true
  error.value = ''
  notice.value = ''
  try {
    const response = await props.api.post(`${pluginBase.value}/scan`, {})
    if (response?.success === false) {
      error.value = response.message || '媒体库拉取尚未完成'
      return
    }
    status.value = unwrapResponse(response) || status.value
  } catch (err) {
    error.value = err?.message || '媒体库拉取失败'
  } finally {
    scaning.value = false
  }
}

async function createPlan() {
  planning.value = true
  error.value = ''
  notice.value = ''
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan`, {
      items: selectedPlanItems.value,
      delete_source: deleteSource.value,
    })
    if (response?.success === false) {
      error.value = response.message || '生成清理计划失败'
      return
    }
    const data = unwrapResponse(response)
    status.value = data?.status || status.value
    notice.value = '清理计划已生成'
    activeTab.value = 'plan'
  } catch (err) {
    error.value = err?.message || '生成清理计划失败'
  } finally {
    planning.value = false
  }
}

async function executePlan() {
  if (!pendingPlan.value?.id) return
  error.value = ''
  notice.value = ''
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/execute`, { plan_id: pendingPlan.value.id })
    if (response?.success === false) {
      error.value = response.message || '清理执行被阻止'
      return
    }
    status.value = unwrapResponse(response) || status.value
  } catch (err) {
    error.value = err?.message || '执行清理计划失败'
  }
}

defineExpose({
  loadStatus,
  saveConfig,
  scanLibrary,
  loading,
  saving,
  scaning,
})

onMounted(loadStatus)
</script>

<template>
  <div class="mlk-page">
    <div v-if="!hideTitle" class="mlk-header">
      <div>
        <div class="text-h5 font-weight-bold">媒体库管家</div>
        <div class="text-body-2 text-medium-emphasis">Emby 媒体库整理与空间释放</div>
      </div>
      <VSpacer />
      <VBtn prepend-icon="mdi-database-sync-outline" variant="tonal" :loading="scaning" @click="scanLibrary">
        立即扫描媒体库
      </VBtn>
      <VBtn prepend-icon="mdi-content-save" color="primary" variant="flat" :loading="saving" @click="saveConfig">
        保存设置
      </VBtn>
    </div>

    <VAlert v-if="error" type="error" variant="tonal" density="comfortable">{{ error }}</VAlert>
    <VAlert v-if="notice" type="success" variant="tonal" density="comfortable">{{ notice }}</VAlert>

    <div class="mlk-stats">
      <VSheet v-for="card in statCards" :key="card.label" border rounded class="mlk-stat-card">
        <VIcon :icon="card.icon" :color="card.color" size="28" />
        <div>
          <div class="text-caption text-medium-emphasis">{{ card.label }}</div>
          <div class="text-h6">{{ card.value }}</div>
        </div>
      </VSheet>
    </div>

    <VAlert type="info" variant="tonal" density="comfortable">
      当前版本已完成页面和接口合同。Emby 拉取、整理记录匹配、真实删除链路尚未接入，执行清理会被后端阻止。
    </VAlert>

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
                <span>{{ key }}</span>
              </VSheet>
            </div>
            <VEmptyState
              icon="mdi-database-search-outline"
              title="等待接入媒体库数据"
              text="下一阶段会读取 MoviePilot 已配置的 Emby 服务，并在这里展示空间风险与清理候选。"
            />
          </div>
        </VWindowItem>

        <VWindowItem value="library">
          <div class="mlk-section">
            <div class="mlk-toolbar">
              <VTextField label="搜索名称" prepend-inner-icon="mdi-magnify" density="comfortable" hide-details clearable />
              <VSelect label="观看状态" :items="['全部', '已看完', '未观看', '观看中']" density="comfortable" hide-details />
              <VSelect label="媒体类型" :items="['全部', '电影', '剧集']" density="comfortable" hide-details />
            </div>
            <VDataTable
              v-model="selectedMedia"
              :headers="[
                { title: '名称', key: 'title' },
                { title: '类型', key: 'type' },
                { title: '进度', key: 'progress' },
                { title: '体积', key: 'size' },
                { title: '入库时间', key: 'added_at' },
              ]"
              :items="mediaRows"
              item-value="id"
              show-select
              return-object
              density="comfortable"
              class="mlk-table"
            >
              <template #item.size="{ item }">{{ formatBytes(item.size) }}</template>
              <template #no-data>
                <VEmptyState icon="mdi-folder-open-outline" title="暂无媒体库数据" text="接入 Emby 扫描后会显示电影、剧集和观看进度。" />
              </template>
            </VDataTable>
          </div>
        </VWindowItem>

        <VWindowItem value="recommendations">
          <div class="mlk-section">
            <VDataTable
              :headers="[
                { title: '建议类型', key: 'reason' },
                { title: '媒体', key: 'title' },
                { title: '预计释放', key: 'size' },
                { title: '说明', key: 'message' },
              ]"
              :items="recommendationRows"
              density="comfortable"
            >
              <template #item.size="{ item }">{{ formatBytes(item.size) }}</template>
              <template #no-data>
                <VEmptyState icon="mdi-lightbulb-on-outline" title="暂无清理建议" text="后续会列出已看完、入库最久未观看和体积较大的剧集。" />
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
                  已选择 {{ selectedMedia.length }} 项，预计 {{ formatBytes(selectedSize) }}
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
                <VChip color="warning" variant="tonal">{{ pendingPlan.status }}</VChip>
              </div>
              <VDataTable
                :headers="[
                  { title: '媒体', key: 'title' },
                  { title: '匹配状态', key: 'status' },
                  { title: '预计释放', key: 'size' },
                  { title: '说明', key: 'message' },
                ]"
                :items="pendingPlan.items || []"
                density="comfortable"
              >
                <template #item.size="{ item }">{{ formatBytes(item.size) }}</template>
              </VDataTable>
              <div class="mlk-danger-actions">
                <VBtn color="error" variant="tonal" prepend-icon="mdi-delete-alert-outline" @click="executePlan">
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
                { title: '时间', key: 'created_at' },
                { title: '结果', key: 'status' },
                { title: '释放空间', key: 'reclaim_size' },
                { title: '说明', key: 'message' },
              ]"
              :items="historyRows"
              density="comfortable"
            >
              <template #item.reclaim_size="{ item }">{{ formatBytes(item.reclaim_size) }}</template>
              <template #no-data>
                <VEmptyState icon="mdi-history" title="暂无执行记录" text="真实清理接入后，每次执行结果都会保存在这里。" />
              </template>
            </VDataTable>
          </div>
        </VWindowItem>

        <VWindowItem value="settings">
          <div class="mlk-section mlk-settings">
            <VSwitch v-model="configDraft.enabled" color="primary" inset label="启用插件" />
            <VSwitch v-model="configDraft.show_sidebar_nav" color="primary" inset label="显示侧边栏入口" />
            <VSwitch v-model="configDraft.notify_enabled" color="primary" inset label="启用通知" />
            <VSwitch v-model="configDraft.disk_warning_enabled" color="warning" inset label="启用磁盘容量告警" />
            <div class="mlk-form-grid">
              <VTextField v-model.number="configDraft.disk_warning_free_gb" type="number" label="剩余容量阈值 GB" />
              <VTextField v-model.number="configDraft.disk_warning_free_percent" type="number" label="剩余比例阈值 %" />
              <VTextField v-model="configDraft.scan_cron" label="扫描周期 Cron" />
            </div>
            <VTextarea
              v-model="configDraft.library_names"
              label="限定媒体库名称"
              hint="留空表示全部媒体库。可在接入 Emby 后按行填写媒体库名称。"
              persistent-hint
              auto-grow
              rows="3"
            />
            <VSwitch v-model="configDraft.ai_suggestions" color="primary" inset label="允许 AI 参与清理建议排序" />
            <VSwitch v-model="configDraft.default_delete_source" color="error" inset label="默认同时删除源文件" />
          </div>
        </VWindowItem>
      </VWindow>
    </VSheet>
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
.mlk-danger-actions {
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
.mlk-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.mlk-stat-card,
.mlk-capability,
.mlk-plan-bar,
.mlk-plan-detail {
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
