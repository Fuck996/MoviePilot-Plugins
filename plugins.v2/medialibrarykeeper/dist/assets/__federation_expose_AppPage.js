import { importShared } from './__federation_fn_import.js';
import { _ as _export_sfc, t as toEditableConfig, c as createDefaultConfig, p as planItemFromMedia, f as formatNumber, b as formatBytes, a as toPayloadConfig, u as unwrapResponse, r as readStatusCache, d as createDefaultCleanupRule, w as writeStatusCache } from './_plugin-vue_export-helper.js';

const {createElementVNode:_createElementVNode,resolveComponent:_resolveComponent,createVNode:_createVNode,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,createBlock:_createBlock,renderList:_renderList,Fragment:_Fragment,toDisplayString:_toDisplayString,unref:_unref,withModifiers:_withModifiers,mergeProps:_mergeProps,vShow:_vShow,withDirectives:_withDirectives,normalizeProps:_normalizeProps,guardReactiveProps:_guardReactiveProps} = await importShared('vue');


const _hoisted_1 = { class: "mlk-page" };
const _hoisted_2 = {
  key: 0,
  class: "mlk-header"
};
const _hoisted_3 = { class: "mlk-stats" };
const _hoisted_4 = { class: "text-caption text-medium-emphasis" };
const _hoisted_5 = { class: "text-h6" };
const _hoisted_6 = { class: "mlk-section" };
const _hoisted_7 = {
  key: 0,
  class: "mlk-library-grid"
};
const _hoisted_8 = {
  key: 1,
  class: "mlk-library-fallback"
};
const _hoisted_9 = { class: "mlk-library-meta" };
const _hoisted_10 = { class: "text-subtitle-1 font-weight-medium" };
const _hoisted_11 = { class: "text-caption text-medium-emphasis" };
const _hoisted_12 = { class: "mlk-chip-row" };
const _hoisted_13 = { class: "mlk-capability-grid" };
const _hoisted_14 = {
  key: 1,
  class: "mlk-disk-grid"
};
const _hoisted_15 = { class: "text-subtitle-2" };
const _hoisted_16 = {
  key: 0,
  class: "text-body-2 text-warning"
};
const _hoisted_17 = {
  key: 1,
  class: "text-body-2 text-medium-emphasis"
};
const _hoisted_18 = { class: "mlk-section" };
const _hoisted_19 = { class: "mlk-toolbar" };
const _hoisted_20 = {
  key: 1,
  class: "mlk-media-grid"
};
const _hoisted_21 = { class: "mlk-poster" };
const _hoisted_22 = {
  key: 1,
  class: "mlk-poster-fallback"
};
const _hoisted_23 = { class: "mlk-media-body" };
const _hoisted_24 = { class: "mlk-media-head" };
const _hoisted_25 = { class: "mlk-media-title" };
const _hoisted_26 = { class: "mlk-media-meta" };
const _hoisted_27 = { class: "mlk-chip-row mlk-chip-row--compact" };
const _hoisted_28 = { class: "mlk-media-facts" };
const _hoisted_29 = { class: "mlk-media-fact mlk-media-fact--volume" };
const _hoisted_30 = { class: "mlk-media-fact" };
const _hoisted_31 = { class: "mlk-media-fact" };
const _hoisted_32 = { class: "mlk-section" };
const _hoisted_33 = { class: "mlk-toolbar" };
const _hoisted_34 = {
  key: 1,
  class: "mlk-media-grid"
};
const _hoisted_35 = { class: "mlk-poster" };
const _hoisted_36 = {
  key: 1,
  class: "mlk-poster-fallback"
};
const _hoisted_37 = { class: "mlk-media-body" };
const _hoisted_38 = { class: "mlk-media-head" };
const _hoisted_39 = { class: "mlk-media-title" };
const _hoisted_40 = { class: "mlk-media-meta" };
const _hoisted_41 = { class: "mlk-media-note" };
const _hoisted_42 = { class: "mlk-chip-row mlk-chip-row--compact" };
const _hoisted_43 = { class: "mlk-media-facts" };
const _hoisted_44 = { class: "mlk-media-fact mlk-media-fact--volume" };
const _hoisted_45 = { class: "mlk-section" };
const _hoisted_46 = { class: "mlk-plan-bar-title" };
const _hoisted_47 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_48 = { class: "mlk-plan-summary" };
const _hoisted_49 = { class: "mlk-plan-main" };
const _hoisted_50 = { class: "mlk-plan-bar-title" };
const _hoisted_51 = { class: "text-subtitle-1 font-weight-medium" };
const _hoisted_52 = { class: "text-caption text-medium-emphasis" };
const _hoisted_53 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_54 = { class: "mlk-chip-row" };
const _hoisted_55 = { class: "mlk-plan-actions" };
const _hoisted_56 = { class: "mlk-plan-detail" };
const _hoisted_57 = { class: "mlk-table-actions" };
const _hoisted_58 = { class: "mlk-section" };
const _hoisted_59 = {
  key: 0,
  class: "text-error"
};
const _hoisted_60 = { class: "mlk-table-actions" };
const _hoisted_61 = { class: "mlk-section mlk-settings" };
const _hoisted_62 = { class: "mlk-settings-group" };
const _hoisted_63 = { class: "mlk-switch-grid" };
const _hoisted_64 = { class: "mlk-form-grid" };
const _hoisted_65 = { class: "mlk-settings-group" };
const _hoisted_66 = { class: "mlk-form-grid" };
const _hoisted_67 = { class: "mlk-settings-group" };
const _hoisted_68 = { class: "mlk-section-header" };
const _hoisted_69 = { class: "mlk-settings-group" };
const _hoisted_70 = { class: "mlk-section-header" };
const _hoisted_71 = { class: "mlk-settings-group" };
const _hoisted_72 = { class: "mlk-switch-grid" };
const _hoisted_73 = { class: "mlk-settings-group" };
const _hoisted_74 = { class: "mlk-section-header" };
const _hoisted_75 = { class: "mlk-section-actions" };
const _hoisted_76 = { class: "mlk-rule-title" };
const _hoisted_77 = { class: "mlk-rule-grid" };
const _hoisted_78 = { class: "mlk-settings-actions" };
const _hoisted_79 = { class: "mlk-detail-layout" };
const _hoisted_80 = { class: "mlk-detail-aside" };
const _hoisted_81 = { class: "mlk-detail-poster" };
const _hoisted_82 = {
  key: 1,
  class: "mlk-poster-fallback"
};
const _hoisted_83 = { class: "mlk-detail-aside-info" };
const _hoisted_84 = { class: "mlk-detail-aside-row" };
const _hoisted_85 = { class: "mlk-detail-aside-row" };
const _hoisted_86 = { class: "mlk-detail-aside-row" };
const _hoisted_87 = { class: "mlk-detail-aside-row" };
const _hoisted_88 = { class: "mlk-detail-aside-row" };
const _hoisted_89 = { class: "mlk-detail-content" };
const _hoisted_90 = { class: "mlk-detail-head" };
const _hoisted_91 = { class: "text-h6 font-weight-bold" };
const _hoisted_92 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_93 = { class: "mlk-chip-row" };
const _hoisted_94 = { class: "mlk-overview" };
const _hoisted_95 = { class: "mlk-detail-grid" };
const _hoisted_96 = { class: "text-caption text-medium-emphasis" };
const _hoisted_97 = { class: "mlk-detail-wide" };
const _hoisted_98 = {
  key: 0,
  class: "mlk-detail-wide"
};
const _hoisted_99 = {
  key: 1,
  class: "mlk-detail-wide"
};
const _hoisted_100 = { class: "mlk-chip-row" };
const _hoisted_101 = { class: "mlk-detail-actions" };
const _hoisted_102 = { class: "mlk-plan-target-title mb-3" };
const _hoisted_103 = { class: "text-subtitle-2" };
const _hoisted_104 = {
  key: 0,
  class: "text-body-2 text-medium-emphasis mb-3"
};
const _hoisted_105 = { class: "mb-5" };
const _hoisted_106 = { class: "mlk-target-head" };
const _hoisted_107 = { class: "text-body-2 font-weight-medium" };
const _hoisted_108 = {
  key: 0,
  class: "text-caption text-medium-emphasis"
};
const _hoisted_109 = {
  key: 1,
  class: "text-caption text-medium-emphasis"
};
const _hoisted_110 = {
  key: 2,
  class: "text-caption text-medium-emphasis"
};
const _hoisted_111 = {
  key: 3,
  class: "text-caption text-medium-emphasis"
};
const _hoisted_112 = { class: "mlk-target-head" };
const _hoisted_113 = { class: "text-caption text-medium-emphasis" };
const _hoisted_114 = { class: "text-caption text-medium-emphasis" };
const _hoisted_115 = {
  key: 0,
  class: "text-caption text-medium-emphasis"
};
const _hoisted_116 = {
  key: 2,
  class: "mlk-target-list"
};
const _hoisted_117 = { class: "mlk-target-head" };
const _hoisted_118 = {
  key: 0,
  class: "text-caption text-medium-emphasis"
};
const _hoisted_119 = {
  key: 1,
  class: "text-body-2"
};
const _hoisted_120 = { class: "text-body-2" };
const _hoisted_121 = {
  key: 2,
  class: "text-caption text-medium-emphasis"
};
const _hoisted_122 = {
  key: 3,
  class: "mt-5"
};
const _hoisted_123 = { class: "mlk-target-head" };
const _hoisted_124 = { class: "text-body-2" };
const _hoisted_125 = { class: "text-caption text-medium-emphasis" };
const _hoisted_126 = { class: "text-caption text-medium-emphasis" };
const _hoisted_127 = {
  key: 4,
  class: "mt-5"
};
const _hoisted_128 = { class: "mlk-target-head" };
const _hoisted_129 = { class: "text-body-2" };
const _hoisted_130 = { class: "text-body-2" };
const _hoisted_131 = { class: "text-caption text-medium-emphasis mt-1" };
const _hoisted_132 = { class: "mlk-detail-summary mb-4" };
const _hoisted_133 = { class: "text-body-2 text-medium-emphasis mb-4" };
const _hoisted_134 = {
  key: 0,
  class: "mb-4"
};
const _hoisted_135 = { class: "mlk-chip-row" };
const _hoisted_136 = {
  key: 0,
  class: "text-caption text-medium-emphasis"
};
const _hoisted_137 = {
  key: 1,
  class: "mt-5"
};
const _hoisted_138 = { class: "text-body-2" };
const _hoisted_139 = { class: "text-body-2" };

const {computed,getCurrentInstance,onMounted,onUnmounted,ref,watch} = await importShared('vue');


const _sfc_main = {
  __name: 'AppPage',
  props: {
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
},
  setup(__props, { expose: __expose }) {

const props = __props;

const loading = ref(false);
const saving = ref(false);
const creatingPlan = ref(false);
const updatingPlan = ref(false);
const scanning = ref(false);
const syncingLibraries = ref(false);
const ruleScanning = ref(false);
const executing = ref(false);
const fallbackToast = ref({
  show: false,
  text: '',
  color: 'success',
});
const activeTab = ref('overview');
const selectedMedia = ref([]);
const selectedLibraryId = ref('');
const selectedDirectoryFilter = ref('');
const selectedMediaDetail = ref(null);
const detailDialog = ref(false);
const selectedPlanItem = ref(null);
const selectedHistoryItem = ref(null);
const planTargetDialog = ref(false);
const historyDetailDialog = ref(false);
const planExpanded = ref(false);
const selectedPlanExpanded = ref(false);
const searchText = ref('');
const watchFilter = ref('全部');
const typeFilter = ref('全部');
const mediaSort = ref('last_episode_added_at');
const sortDesc = ref(true);
const pageSize = ref(100);
const executeDialog = ref(false);
const executeConfirmed = ref(false);
const deletePlanDialog = ref(false);
const deletePlanConfirmed = ref(false);
const deletingPlan = ref(false);
const queuePollTimer = ref(null);
const configDraft = ref(toEditableConfig());
const status = ref({
  config: createDefaultConfig(),
  summary: {},
  libraries: [],
  media: [],
  recommendations: [],
  pending_plan: null,
  cleanup_queue: [],
  history: [],
  capabilities: {},
  media_server_options: [],
  downloader_options: [],
});

const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`);
const summary = computed(() => status.value.summary || {});
const libraries = computed(() => status.value.libraries || []);
const mediaRows = computed(() => status.value.media || []);
const recommendationRows = computed(() => status.value.recommendations || []);
const pendingPlan = computed(() => status.value.pending_plan);
const pendingPlanItems = computed(() => pendingPlan.value?.items || []);
const cleanupQueueRows = computed(() => status.value.cleanup_queue || []);
const pendingPlanStats = computed(() => pendingPlanItems.value.reduce((stats, item) => {
  if (item.type === 'movie') stats.movies += 1;
  if (item.type === 'series') stats.series += 1;
  stats.size += Number(item.size || 0);
  return stats
}, { movies: 0, series: 0, size: 0 }));
const pendingPlanRecordStats = computed(() => pendingPlanItems.value.reduce((stats, item) => {
  if (item.matched_transfer_records?.length) {
    stats.recorded += 1;
  } else {
    stats.missing += 1;
  }
  return stats
}, { recorded: 0, missing: 0 }));
const historyRows = computed(() => status.value.history || []);
const capabilities = computed(() => status.value.capabilities || {});
const hiddenCapabilityKeys = new Set(['ai_agent_ready']);
const visibleCapabilities = computed(() => Object.fromEntries(
  Object.entries(capabilities.value).filter(([key, value]) => typeof value === 'boolean' && !hiddenCapabilityKeys.has(key)),
));
const aiAgentReady = computed(() => capabilities.value.ai_agent_ready === true);
const aiAgentMessage = computed(() => capabilities.value.ai_agent_message || '未配置智能助手，请先在系统设置中配置并启用智能助手。');
const mediaServerOptions = computed(() => status.value.media_server_options || []);
const downloaderOptions = computed(() => status.value.downloader_options || []);
const selectedPlanItems = computed(() => selectedMedia.value.map(planItemFromMedia));
const historyDetailStats = computed(() => cleanupRecordStats(selectedHistoryItem.value || {}));
const historySeedRows = computed(() => [
  ...((selectedHistoryItem.value?.deleted_seed_tasks || []).map(item => ({ ...item, result: 'success' }))),
  ...((selectedHistoryItem.value?.failed_seed_tasks || []).map(item => ({ ...item, result: 'failed' }))),
]);
const selectedDownloadTasks = computed(() => selectedPlanItem.value?.download_tasks || []);
const selectedMatchedDownloadTasks = computed(() => selectedDownloadTasks.value.filter(downloadTaskMatched));
const selectedHistoryHashSummary = computed(() => {
  const tasks = selectedDownloadTasks.value.filter(task => !downloadTaskMatched(task));
  if (!tasks.length) return null
  const sources = countByLabel(tasks.map(task => task.source_label || task.source || '历史记录'));
  const downloaders = countByLabel(tasks.flatMap(task => {
    const candidates = Array.isArray(task.candidate_downloaders) ? task.candidate_downloaders.filter(Boolean) : [];
    return candidates.length ? candidates : [task.original_downloader || task.downloader || '配置下载器']
  }));
  const titles = [...new Set(tasks.map(task => task.title).filter(Boolean))];
  return { total: tasks.length, sources, downloaders, titles }
});
const selectedDetailInfoRows = computed(() => {
  const item = selectedMediaDetail.value;
  if (!item) return []
  const rows = [
    { label: '服务器', value: item.server || '-' },
  ];
  if (item.type === 'series') {
    rows.push({ label: '入库时间', value: item.added_at || '-' });
  }
  rows.push(
    { label: '最后观看', value: item.last_watched_at || '-' },
    { label: '首播/上映', value: item.premiere_date || '-' },
  );
  if (item.type === 'series') {
    rows.push({ label: '集数', value: `${item.watched_episodes || 0}/${item.total_episodes || 0}` });
  }
  return rows
});

function resolveImageUrl(url) {
  if (!url || /^(https?:|data:|blob:|\/)/.test(url)) return url || ''
  const baseURL = props.api?.defaults?.baseURL || '/api/v1';
  return `${String(baseURL).replace(/\/$/, '')}/${String(url).replace(/^\//, '')}`
}
const selectedSize = computed(() => selectedMedia.value.reduce((sum, item) => sum + Number(item.size || 0), 0));
const planExecutable = computed(() => Number(pendingPlan.value?.ready_count || 0) > 0);
function planItemStatusText(item) {
  if (item.matched_transfer_records?.length) return '有记录'
  if (item.status === 'record_missing' || item.delete_targets?.length) return '记录丢失'
  return '未匹配'
}
function planItemStatusColor(item) {
  if (item.matched_transfer_records?.length) return 'success'
  if (item.status === 'record_missing') return 'error'
  return 'warning'
}
function downloadTaskName(task) {
  const candidates = Array.isArray(task.candidate_downloaders) ? task.candidate_downloaders.filter(Boolean) : [];
  return task.matched_downloader || task.downloader || (candidates.length ? candidates.join(' / ') : '配置下载器')
}
function downloadTaskTitle(task) {
  if (task.task_name) return task.task_name
  if (downloadTaskMatched(task)) return '已定位下载任务，未获取到任务名'
  return '未读取到配置下载器实时任务信息'
}
function downloadTaskMatched(task) {
  return task.downloader_match_source === 'configured_downloader' || Boolean(task.matched_downloader || task.task_name)
}
function downloadTaskStatusText(task) {
  if (!downloadTaskMatched(task)) return '历史Hash'
  return task.task_name ? '已找到' : '已定位'
}
function downloadTaskStateText(task) {
  const state = String(task.task_state || '').trim();
  const labels = {
    paused: '已暂停',
    stopped: '已停止',
    downloading: '下载中',
    stalledDL: '下载停滞',
    uploading: '保种中',
    stalledUP: '保种停滞',
    checkingUP: '校验中',
    checkingDL: '校验中',
    queuedUP: '保种排队',
    queuedDL: '下载排队',
    error: '错误',
    missingFiles: '文件缺失',
  };
  return labels[state] || state
}
function downloadTaskSourceText(task) {
  const source = String(task.source_label || task.source || '').trim();
  const labels = {
    transfer_history: '整理记录',
    download_history: '下载历史',
    transfer_record: '整理记录',
    seed_candidate: '保种候选',
    related_seed: '同资源保种',
    history_hash: '历史Hash',
  };
  return labels[source] || source
}
function downloadTaskHint(task) {
  if (downloadTaskMatched(task)) {
    return task.task_name ? '' : '下载器接口已按 Hash 定位任务，但未返回任务名。'
  }
  return '当前批次只保存了历史 Hash，执行清理时会按 Hash 到配置下载器中尝试删除。'
}
function countByLabel(labels) {
  return labels.reduce((counts, label) => {
    const key = label || '未知';
    counts[key] = (counts[key] || 0) + 1;
    return counts
  }, {})
}
function summaryEntries(summary) {
  return Object.entries(summary || {}).map(([label, count]) => `${label} ${count}`).join(' / ')
}
function seedCandidateDownloaderName(candidate) {
  return candidate.downloader || '配置下载器'
}
const selectedLibrary = computed(() => libraries.value.find(item => item.id === selectedLibraryId.value));
const toast = getCurrentInstance()?.appContext.config.globalProperties?.$toast;
const libraryOptions = computed(() => libraries.value.map(item => ({ title: item.server ? `${item.title} · ${item.server}` : item.title, value: item.id })));
const librarySwitchOptions = computed(() => [
  { title: '全部媒体库', value: '' },
  ...libraryOptions.value,
]);
const directoryFilterOptions = computed(() => [
  { title: '全部目录', value: '', rootPath: '' },
  ...directoryFilterEntries.value,
]);
const directoryFilterEntries = computed(() => {
  const options = new Map();
  for (const item of [...mediaRows.value, ...recommendationRows.value]) {
    for (const root of Array.isArray(item.root_directories) ? item.root_directories : []) {
      const rootPath = normalizeFilterPath(root.path);
      if (!rootPath || options.has(rootPath)) continue
      const name = root.name || rootPath;
      options.set(rootPath, {
        title: `${name}（${rootPath}）`,
        value: rootPath,
        rootPath,
      });
    }
  }
  return [...options.values()].sort((left, right) => left.title.localeCompare(right.title, 'zh-CN'))
});
const sortOptions = [
  { title: '最后一集添加日期', value: 'last_episode_added_at' },
  { title: '最后观看日期', value: 'last_watched_at' },
  { title: '大小', value: 'size' },
  { title: '评分', value: 'rating' },
];
const scanCronOptions = [
  { title: '每 1 小时', value: '0 */1 * * *' },
  { title: '每 3 小时', value: '0 */3 * * *' },
  { title: '每 6 小时', value: '0 */6 * * *' },
  { title: '每 12 小时', value: '0 */12 * * *' },
  { title: '每天 03:00', value: '0 3 * * *' },
  { title: '每周一 03:00', value: '0 3 * * 1' },
];
const mediaWatchFilterOptions = ['全部', '已播放', '未播放'];
const cleanupWatchStateOptions = [
  { title: '不限制', value: 'any' },
  { title: '已看完', value: 'watched' },
  { title: '未看完', value: 'unwatched' },
];
const pageSizeOptions = [50, 100, 500, 1000];

const filteredMediaRows = computed(() => filterMediaRows(mediaRows.value));

const sortedMediaRows = computed(() => sortMediaRows(filteredMediaRows.value));

const visibleMediaRows = computed(() => sortedMediaRows.value.slice(0, pageSize.value));

const filteredRecommendationRows = computed(() => filterMediaRows(recommendationRows.value));

const sortedRecommendationRows = computed(() => sortMediaRows(filteredRecommendationRows.value));

const visibleRecommendationRows = computed(() => sortedRecommendationRows.value.slice(0, pageSize.value));

function filterMediaRows(rows) {
  const keyword = String(searchText.value || '').trim().toLowerCase();
  return rows.filter((item) => {
    if (selectedLibraryId.value && item.library_id !== selectedLibraryId.value) return false
    if (!mediaMatchesDirectoryFilter(item)) return false
    if (keyword) {
      const haystack = `${item.title || ''}${item.overview || ''}${item.path_preview || ''}${item.emby_path_preview || ''}`.toLowerCase();
      if (!haystack.includes(keyword)) return false
    }
    if (typeFilter.value === '电影' && item.type !== 'movie') return false
    if (typeFilter.value === '剧集' && item.type !== 'series') return false
    const watchState = resolveWatchState(item);
    if (watchFilter.value === '已播放' && watchState !== 'watched') return false
    if (watchFilter.value === '未播放' && watchState !== 'unwatched') return false
    return true
  })
}

function sortMediaRows(rows) {
  const key = mediaSort.value;
  const direction = sortDesc.value ? -1 : 1;
  return [...rows].sort((left, right) => {
    const leftValue = sortValue(left, key);
    const rightValue = sortValue(right, key);
    if (leftValue === rightValue) {
      return String(left.title || '').localeCompare(String(right.title || ''), 'zh-CN')
    }
    return leftValue > rightValue ? direction : -direction
  })
}

const libraryCards = computed(() => {
  const counts = mediaRows.value.reduce((acc, item) => {
    const key = item.library_id || 'unknown';
    acc[key] = acc[key] || { total: 0, movies: 0, series: 0, size: 0 };
    acc[key].total += 1;
    acc[key].size += Number(item.size || 0);
    if (item.type === 'movie') acc[key].movies += 1;
    if (item.type === 'series') acc[key].series += 1;
    return acc
  }, {});
  return libraries.value.map(item => ({
    ...item,
    counts: counts[item.id] || { total: 0, movies: 0, series: 0, size: 0 },
  }))
});

const statCards = computed(() => [
  { label: '媒体库', value: formatNumber(summary.value.libraries), icon: 'mdi-folder-multiple-outline', color: 'primary' },
  { label: '电影', value: formatNumber(summary.value.movies), icon: 'mdi-movie-open-outline', color: 'info' },
  { label: '剧集', value: formatNumber(summary.value.series), icon: 'mdi-television-classic', color: 'success' },
  { label: '已播放', value: formatNumber(summary.value.watched), icon: 'mdi-play-circle-check-outline', color: 'success' },
  { label: '预计可释放', value: formatBytes(summary.value.estimated_reclaim_size), icon: 'mdi-harddisk-remove', color: 'warning' },
]);

const capabilityLabels = {
  emby_scan: 'Emby 扫描',
  transfer_history_match: '整理记录匹配',
  storage_delete: '文件删除',
  ai_suggestions: 'AI资源任务识别',
  notification: '通知推送',
};

const planHeaders = [
  { title: '媒体', key: 'title' },
  { title: '状态', key: 'status', width: 110 },
  { title: '预计释放', key: 'size', width: 120 },
  { title: '所属卷', key: 'volume_name', width: 180 },
  { title: '删除目标', key: 'target_count', width: 110 },
  { title: '说明', key: 'message' },
  { title: '操作', key: 'actions', width: 132, sortable: false, align: 'center' },
];
const selectedPlanHeaders = [
  { title: '媒体', key: 'title' },
  { title: '类型', key: 'type_label', width: 100 },
  { title: '观看状态', key: 'watch_state', width: 130 },
  { title: '大小', key: 'size', width: 120 },
  { title: '所在盘', key: 'volume_name', width: 120 },
  { title: '时间', key: 'added_at', width: 190 },
  { title: '操作', key: 'actions', width: 84, sortable: false },
];

const pendingPlanMediaIds = computed(() => new Set(pendingPlanItems.value.map(item => item.media_id).filter(Boolean)));

function isInCurrentSelection(item) {
  return selectedMedia.value.some(selected => selected.id === item.id)
}

function isInPendingPlan(item) {
  return pendingPlanMediaIds.value.has(item?.id)
}

function isSelected(item) {
  return isInCurrentSelection(item) || isInPendingPlan(item)
}

function selectedButtonLabel(item) {
  if (isInPendingPlan(item)) return '已在当前批次'
  return isInCurrentSelection(item) ? '从清理选择中移除' : '加入清理选择'
}

function normalizeFilterPath(path) {
  return String(path || '').trim().replace(/\\/g, '/').replace(/\/+$/, '')
}

function mediaMatchesDirectoryFilter(item) {
  if (!selectedDirectoryFilter.value) return true
  const roots = (Array.isArray(item.root_directories) ? item.root_directories : [])
    .map(root => normalizeFilterPath(root.path))
    .filter(Boolean);
  return roots.includes(selectedDirectoryFilter.value)
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
  const watchState = resolveWatchState(item);
  if (watchState === 'watched') return 'success'
  return 'warning'
}

function watchStateText(item) {
  const watchState = resolveWatchState(item);
  if (watchState === 'watched') return item.type === 'series' ? `已播放 ${item.progress}` : '已播放'
  return item.type === 'series' ? `未播放 ${item.progress}` : '未播放'
}

function mediaVolumeText(item) {
  return item.volume_name || item.volume_summary || '未识别'
}

function mediaVolumeCapacityText(item) {
  const volumes = Array.isArray(item.volumes) ? item.volumes : [];
  if (volumes.length) {
    return volumes
      .map((volume) => {
        const name = volume.display_name || volume.mount_point || '未识别';
        return `${name}（${formatBytes(volume.free)}）`
      })
      .join(' / ')
  }
  if (item.volume_name) {
    const suffix = item.volume_free_percent !== null && item.volume_free_percent !== undefined ? `${item.volume_free_percent}%` : '未知';
    return `${item.volume_name}（${suffix}）`
  }
  return '未识别'
}

function mediaAddedLabelText(item) {
  const label = item.type === 'series' ? '末集' : '入库';
  return `${label} ${item.last_episode_added_at || item.added_at || '-'}`
}

function mediaWatchedLabelText(item) {
  return `观看 ${item.last_watched_at || '-'}`
}

function cleanupRecordStats(item) {
  const deletedTargets = item.deleted_targets || [];
  return {
    mediaFiles: Number(item.deleted_media_files ?? deletedTargets.filter(target => target.kind === 'dest').length),
    scrapingFiles: Number(item.deleted_scraping_files ?? deletedTargets.filter(target => target.kind === 'dest_scraping').length),
    sourceFiles: Number(item.deleted_source_files ?? deletedTargets.filter(target => target.kind === 'src').length),
    seedTasks: (item.deleted_seed_tasks || []).length,
    failedSeedTasks: (item.failed_seed_tasks || []).length,
    failedTargets: (item.failed_targets || []).length,
  }
}

function queueStatusColor(item) {
  if (item.status === 'running') return 'info'
  return 'warning'
}

function queueStatusText(item) {
  if (item.status === 'running') return '执行中'
  return '排队中'
}

function toggleSelected(item) {
  if (isInPendingPlan(item)) {
    showToast('该媒体已在当前批次中', 'warning');
    return
  }
  if (isInCurrentSelection(item)) {
    selectedMedia.value = selectedMedia.value.filter(selected => selected.id !== item.id);
    return
  }
  selectedMedia.value = [...selectedMedia.value, item];
}

function openLibrary(library) {
  selectedLibraryId.value = library?.id || '';
  activeTab.value = 'library';
}

function addCleanupRule() {
  configDraft.value.cleanup_rules = [
    ...(configDraft.value.cleanup_rules || []),
    createDefaultCleanupRule(),
  ];
}

function removeCleanupRule(index) {
  const rules = [...(configDraft.value.cleanup_rules || [])];
  rules.splice(index, 1);
  configDraft.value.cleanup_rules = rules.length ? rules : [createDefaultCleanupRule()];
}

function addPathMapping() {
  configDraft.value.path_mappings = [
    ...(configDraft.value.path_mappings || []),
    { emby_path: '', mp_path: '' },
  ];
}

function removePathMapping(index) {
  const mappings = [...(configDraft.value.path_mappings || [])];
  mappings.splice(index, 1);
  configDraft.value.path_mappings = mappings;
}

function addDownloaderPathMapping() {
  configDraft.value.downloader_path_mappings = [
    ...(configDraft.value.downloader_path_mappings || []),
    { downloader: '', downloader_path: '', resource_path: '' },
  ];
}

function removeDownloaderPathMapping(index) {
  const mappings = [...(configDraft.value.downloader_path_mappings || [])];
  mappings.splice(index, 1);
  configDraft.value.downloader_path_mappings = mappings;
}

function openMediaDetail(item) {
  selectedMediaDetail.value = item;
  detailDialog.value = true;
}

function openPlanTargetDialog(item) {
  selectedPlanItem.value = item;
  planTargetDialog.value = true;
}

function openHistoryDetail(item) {
  selectedHistoryItem.value = item;
  historyDetailDialog.value = true;
}

async function createSinglePlan(item) {
  selectedMedia.value = [item];
  detailDialog.value = false;
  await createPlan();
}

async function loadStatus(showLoading = true) {
  if (showLoading) loading.value = true;
  try {
    const response = await props.api.get(`${pluginBase.value}/status`);
    applyStatus(unwrapResponse(response));
  } catch (err) {
    showToast(err?.message || '加载媒体库管家状态失败', 'error');
  } finally {
    if (showLoading) loading.value = false;
  }
}

async function syncLibraries(showToastOnSuccess = true) {
  if (syncingLibraries.value) return
  syncingLibraries.value = true;
  try {
    const response = await props.api.post(`${pluginBase.value}/libraries/sync`, {
      mediaservers: configDraft.value.mediaservers || [],
    });
    if (response?.success === false) {
      showToast(response.message || '同步媒体库列表失败', 'error');
      return
    }
    applyStatus(unwrapResponse(response), { preserveConfig: true });
    if (showToastOnSuccess) {
      showToast(response?.message || '媒体库列表已同步');
    }
  } catch (err) {
    showToast(err?.message || '同步媒体库列表失败', 'error');
  } finally {
    syncingLibraries.value = false;
  }
}

function loadCachedStatus() {
  const cached = readStatusCache(props.pluginId);
  if (cached) applyStatus(cached, { persist: false });
}

function applyStatus(data, options = {}) {
  if (!data) return
  const normalized = filterCleanedMediaFromStatus(data);
  status.value = normalized.status;
  if (normalized.removedIds.size) {
    selectedMedia.value = selectedMedia.value.filter(item => !normalized.removedIds.has(item.id));
  }
  if (!options.preserveConfig) {
    const nextConfig = toEditableConfig(status.value.config);
    if (!status.value.capabilities?.ai_agent_ready) {
      nextConfig.ai_suggestions = false;
    }
    configDraft.value = nextConfig;
  }
  if (options.persist !== false) {
    writeStatusCache(props.pluginId, status.value);
  }
}

function filterCleanedMediaFromStatus(data) {
  const removedIds = cleanedMediaIdsFromHistory(data.history || []);
  if (!removedIds.size) return { status: data, removedIds }
  const keepMedia = item => !removedIds.has(item.id);
  return {
    status: {
      ...data,
      media: (data.media || []).filter(keepMedia),
      recommendations: (data.recommendations || []).filter(keepMedia),
      pending_plan: data.pending_plan
        ? {
            ...data.pending_plan,
            items: (data.pending_plan.items || []).filter(item => !removedIds.has(item.media_id)),
          }
        : data.pending_plan,
    },
    removedIds,
  }
}

function cleanedMediaIdsFromHistory(history) {
  const removedIds = new Set();
  for (const record of history || []) {
    const failedIds = new Set((record.failed_targets || [])
      .filter(target => target.kind === 'dest' && target.media_id)
      .map(target => target.media_id));
    for (const target of record.deleted_targets || []) {
      if (target.kind === 'dest' && target.media_id && !failedIds.has(target.media_id)) {
        removedIds.add(target.media_id);
      }
    }
  }
  return removedIds
}

async function saveConfig() {
  saving.value = true;
  try {
    const response = await props.api.post(`${pluginBase.value}/config`, toPayloadConfig(configDraft.value));
    applyStatus(unwrapResponse(response));
    showToast('设置已保存');
  } catch (err) {
    showToast(err?.message || '保存设置失败', 'error');
  } finally {
    saving.value = false;
  }
}

function updateAiSuggestions(value) {
  if (value && !aiAgentReady.value) {
    configDraft.value.ai_suggestions = false;
    showToast(aiAgentMessage.value, 'warning');
    return
  }
  configDraft.value.ai_suggestions = Boolean(value);
}

async function scanCleanupRules() {
  ruleScanning.value = true;
  try {
    const configResponse = await props.api.post(`${pluginBase.value}/config`, toPayloadConfig(configDraft.value));
    if (configResponse?.success === false) {
      showToast(configResponse.message || '保存设置失败', 'error');
      return
    }
    const response = await props.api.post(`${pluginBase.value}/cleanup/scan`, {});
    if (response?.success === false) {
      showToast(response.message || '按规则扫描失败', 'error');
      return
    }
    applyStatus(unwrapResponse(response));
    const message = response?.message || '已按当前规则完成扫描识别';
    showToast(message, message.includes('已有') || message.includes('未命中') ? 'warning' : 'success');
    activeTab.value = 'plan';
    planExpanded.value = false;
  } catch (err) {
    showToast(err?.message || '按规则扫描失败', 'error');
  } finally {
    ruleScanning.value = false;
  }
}

async function scanLibrary() {
  scanning.value = true;
  try {
    const response = await props.api.post(`${pluginBase.value}/scan`, {});
    if (response?.success === false) {
      showToast(response.message || '扫描媒体库失败', 'error');
      return
    }
    applyStatus(unwrapResponse(response));
    showToast('媒体库扫描完成');
    if (summary.value.disk_warning) {
      showToast('检测到磁盘容量低于阈值，请查看清理建议。', 'warning');
    }
    activeTab.value = 'overview';
  } catch (err) {
    showToast(err?.message || '扫描媒体库失败', 'error');
  } finally {
    scanning.value = false;
  }
}

async function createPlan() {
  creatingPlan.value = true;
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan`, {
      item_ids: selectedMedia.value.map(item => item.id),
      items: selectedPlanItems.value,
    });
    if (response?.success === false) {
      showToast(response.message || '生成清理计划失败', 'error');
      return
    }
    const data = unwrapResponse(response);
    applyStatus(data?.status);
    showToast('清理计划已生成');
    activeTab.value = 'plan';
    planExpanded.value = false;
    selectedPlanExpanded.value = false;
  } catch (err) {
    showToast(err?.message || '生成清理计划失败', 'error');
  } finally {
    creatingPlan.value = false;
  }
}

async function updatePlanItems(action, itemIds) {
  if (!pendingPlan.value?.id || !itemIds.length) return
  updatingPlan.value = true;
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan/items`, {
      plan_id: pendingPlan.value.id,
      action,
      item_ids: itemIds,
    });
    if (response?.success === false) {
      showToast(response.message || '调整清理批次失败', 'error');
      return
    }
    const data = unwrapResponse(response);
    applyStatus(data?.status);
    if (action === 'add') {
      const addedIds = new Set(itemIds);
      selectedMedia.value = selectedMedia.value.filter(item => !addedIds.has(item.id));
      if (!selectedMedia.value.length) selectedPlanExpanded.value = false;
    }
    showToast(response?.message || (action === 'remove' ? '已移出清理批次' : '已加入清理批次'));
  } catch (err) {
    showToast(err?.message || '调整清理批次失败', 'error');
  } finally {
    updatingPlan.value = false;
  }
}

async function addSelectedToPlan() {
  await updatePlanItems('add', selectedMedia.value.map(item => item.id));
}

async function removePlanItem(item) {
  await updatePlanItems('remove', [item.media_id]);
}

function openExecuteDialog() {
  executeConfirmed.value = false;
  executeDialog.value = true;
}

function openDeletePlanDialog() {
  deletePlanConfirmed.value = false;
  deletePlanDialog.value = true;
}

async function deletePlan() {
  if (!pendingPlan.value?.id || !deletePlanConfirmed.value) return
  deletingPlan.value = true;
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan/delete`, {
      plan_id: pendingPlan.value.id,
      confirm: true,
    });
    if (response?.success === false) {
      showToast(response.message || '删除清理批次失败', 'error');
      return
    }
    applyStatus(unwrapResponse(response));
    showToast(response?.message || '清理批次已删除');
    deletePlanDialog.value = false;
    selectedMedia.value = [];
  } catch (err) {
    showToast(err?.message || '删除清理批次失败', 'error');
  } finally {
    deletingPlan.value = false;
  }
}

async function executePlan() {
  if (!pendingPlan.value?.id || !executeConfirmed.value) return
  executing.value = true;
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/execute`, {
      plan_id: pendingPlan.value.id,
      confirm: true,
    });
    if (response?.success === false) {
      showToast(response.message || '执行清理计划失败', 'error');
      return
    }
    applyStatus(unwrapResponse(response));
    showToast(response?.message || '已加入清理队列');
    executeDialog.value = false;
    selectedMedia.value = [];
    activeTab.value = 'history';
  } catch (err) {
    showToast(err?.message || '执行清理计划失败', 'error');
  } finally {
    executing.value = false;
  }
}

function showToast(message, type = 'success') {
  const toastMethod = toast?.[type] || toast;
  if (typeof toastMethod === 'function') {
    toastMethod(message);
    return
  }
  fallbackToast.value = {
    show: true,
    text: message,
    color: type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'success',
  };
}

function startQueuePolling() {
  if (queuePollTimer.value) return
  queuePollTimer.value = window.setInterval(() => {
    if (!cleanupQueueRows.value.length) {
      stopQueuePolling();
      return
    }
    loadStatus(false);
  }, 4000);
}

function stopQueuePolling() {
  if (!queuePollTimer.value) return
  window.clearInterval(queuePollTimer.value);
  queuePollTimer.value = null;
}

__expose({
  loadStatus,
  saveConfig,
  syncLibraries,
  scanLibrary,
  scanCleanupRules,
  loading,
  saving,
  scanning,
  ruleScanning,
});

onMounted(() => {
  loadCachedStatus();
  loadStatus().then(() => {
    if (!libraryOptions.value.length) {
      syncLibraries(false);
    }
  });
});

watch(cleanupQueueRows, (rows) => {
  if (rows.length) {
    startQueuePolling();
    return
  }
  stopQueuePolling();
});

onUnmounted(() => {
  stopQueuePolling();
});

return (_ctx, _cache) => {
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VProgressLinear = _resolveComponent("VProgressLinear");
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VSheet = _resolveComponent("VSheet");
  const _component_VTab = _resolveComponent("VTab");
  const _component_VTabs = _resolveComponent("VTabs");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VImg = _resolveComponent("VImg");
  const _component_VChip = _resolveComponent("VChip");
  const _component_VEmptyState = _resolveComponent("VEmptyState");
  const _component_VWindowItem = _resolveComponent("VWindowItem");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VAlert = _resolveComponent("VAlert");
  const _component_VTooltip = _resolveComponent("VTooltip");
  const _component_VDataTable = _resolveComponent("VDataTable");
  const _component_VExpandTransition = _resolveComponent("VExpandTransition");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VWindow = _resolveComponent("VWindow");
  const _component_VCard = _resolveComponent("VCard");
  const _component_VDialog = _resolveComponent("VDialog");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_VCardText = _resolveComponent("VCardText");
  const _component_VCardActions = _resolveComponent("VCardActions");
  const _component_VCheckbox = _resolveComponent("VCheckbox");
  const _component_VSnackbar = _resolveComponent("VSnackbar");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    (!__props.hideTitle)
      ? (_openBlock(), _createElementBlock("div", _hoisted_2, [
          _cache[49] || (_cache[49] = _createElementVNode("div", null, [
            _createElementVNode("div", { class: "text-h5 font-weight-bold" }, "媒体库管家"),
            _createElementVNode("div", { class: "text-body-2 text-medium-emphasis" }, "按 Emby 媒体库入口管理观看进度和空间释放")
          ], -1)),
          _createVNode(_component_VSpacer),
          _createVNode(_component_VBtn, {
            "prepend-icon": "mdi-database-sync-outline",
            variant: "tonal",
            loading: scanning.value,
            onClick: scanLibrary
          }, {
            default: _withCtx(() => [...(_cache[48] || (_cache[48] = [
              _createTextVNode(" 立即扫描媒体库 ", -1)
            ]))]),
            _: 1
          }, 8, ["loading"])
        ]))
      : _createCommentVNode("", true),
    (loading.value)
      ? (_openBlock(), _createBlock(_component_VProgressLinear, {
          key: 1,
          indeterminate: "",
          color: "primary",
          rounded: ""
        }))
      : _createCommentVNode("", true),
    _createElementVNode("div", _hoisted_3, [
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(statCards.value, (card) => {
        return (_openBlock(), _createBlock(_component_VSheet, {
          key: card.label,
          border: "",
          rounded: "",
          class: "mlk-stat-card"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_VIcon, {
              icon: card.icon,
              color: card.color,
              size: "28"
            }, null, 8, ["icon", "color"]),
            _createElementVNode("div", null, [
              _createElementVNode("div", _hoisted_4, _toDisplayString(card.label), 1),
              _createElementVNode("div", _hoisted_5, _toDisplayString(card.value), 1)
            ])
          ]),
          _: 2
        }, 1024))
      }), 128))
    ]),
    _createVNode(_component_VSheet, {
      border: "",
      rounded: "",
      class: "mlk-panel"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VTabs, {
          modelValue: activeTab.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((activeTab).value = $event)),
          density: "comfortable"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_VTab, { value: "overview" }, {
              default: _withCtx(() => [...(_cache[50] || (_cache[50] = [
                _createTextVNode("总览", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "library" }, {
              default: _withCtx(() => [...(_cache[51] || (_cache[51] = [
                _createTextVNode("媒体库", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "recommendations" }, {
              default: _withCtx(() => [...(_cache[52] || (_cache[52] = [
                _createTextVNode("清理建议", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "plan" }, {
              default: _withCtx(() => [...(_cache[53] || (_cache[53] = [
                _createTextVNode("清理计划", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "history" }, {
              default: _withCtx(() => [...(_cache[54] || (_cache[54] = [
                _createTextVNode("执行记录", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "settings" }, {
              default: _withCtx(() => [...(_cache[55] || (_cache[55] = [
                _createTextVNode("设置", -1)
              ]))]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["modelValue"]),
        _createVNode(_component_VDivider),
        _createVNode(_component_VWindow, {
          modelValue: activeTab.value,
          "onUpdate:modelValue": _cache[32] || (_cache[32] = $event => ((activeTab).value = $event)),
          touch: false
        }, {
          default: _withCtx(() => [
            _createVNode(_component_VWindowItem, { value: "overview" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_6, [
                  (libraryCards.value.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_7, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(libraryCards.value, (library) => {
                          return (_openBlock(), _createBlock(_component_VSheet, {
                            key: library.id,
                            border: "",
                            rounded: "",
                            class: "mlk-library-card",
                            onClick: $event => (openLibrary(library))
                          }, {
                            default: _withCtx(() => [
                              (library.image_url)
                                ? (_openBlock(), _createBlock(_component_VImg, {
                                    key: 0,
                                    src: resolveImageUrl(library.image_url),
                                    cover: "",
                                    class: "mlk-library-image"
                                  }, null, 8, ["src"]))
                                : (_openBlock(), _createElementBlock("div", _hoisted_8, [
                                    _createVNode(_component_VIcon, {
                                      icon: "mdi-folder-multiple-image",
                                      size: "42"
                                    })
                                  ])),
                              _createElementVNode("div", _hoisted_9, [
                                _createElementVNode("div", _hoisted_10, _toDisplayString(library.title), 1),
                                _createElementVNode("div", _hoisted_11, _toDisplayString(library.server) + " · " + _toDisplayString(library.type_label), 1),
                                _createElementVNode("div", _hoisted_12, [
                                  _createVNode(_component_VChip, {
                                    size: "small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(library.counts.movies) + " 部电影", 1)
                                    ]),
                                    _: 2
                                  }, 1024),
                                  _createVNode(_component_VChip, {
                                    size: "small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(library.counts.series) + " 部剧集", 1)
                                    ]),
                                    _: 2
                                  }, 1024),
                                  _createVNode(_component_VChip, {
                                    size: "small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_unref(formatBytes)(library.counts.size)), 1)
                                    ]),
                                    _: 2
                                  }, 1024)
                                ])
                              ])
                            ]),
                            _: 2
                          }, 1032, ["onClick"]))
                        }), 128))
                      ]))
                    : _createCommentVNode("", true),
                  _createElementVNode("div", _hoisted_13, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(visibleCapabilities.value, (enabled, key) => {
                      return (_openBlock(), _createBlock(_component_VSheet, {
                        key: key,
                        border: "",
                        rounded: "",
                        class: "mlk-capability"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: enabled ? 'mdi-check-circle-outline' : 'mdi-progress-wrench',
                            color: enabled ? 'success' : 'warning'
                          }, null, 8, ["icon", "color"]),
                          _createElementVNode("span", null, _toDisplayString(capabilityLabels[key] || key), 1)
                        ]),
                        _: 2
                      }, 1024))
                    }), 128))
                  ]),
                  (summary.value.disk_status?.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_14, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(summary.value.disk_status, (disk) => {
                          return (_openBlock(), _createBlock(_component_VSheet, {
                            key: disk.path,
                            border: "",
                            rounded: "",
                            class: "mlk-disk-row"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", null, [
                                _createElementVNode("div", _hoisted_15, _toDisplayString(disk.display_name || disk.mount_point || '未知卷'), 1),
                                (disk.unavailable)
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_16, _toDisplayString(disk.error || '路径不可访问'), 1))
                                  : (_openBlock(), _createElementBlock("div", _hoisted_17, "剩余 " + _toDisplayString(_unref(formatBytes)(disk.free)) + " / " + _toDisplayString(disk.free_percent) + "%", 1))
                              ]),
                              _createVNode(_component_VChip, {
                                color: disk.unavailable || disk.warning ? 'warning' : 'success',
                                variant: "tonal"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(disk.unavailable ? '不可访问' : disk.warning ? '容量紧张' : '容量正常'), 1)
                                ]),
                                _: 2
                              }, 1032, ["color"])
                            ]),
                            _: 2
                          }, 1024))
                        }), 128))
                      ]))
                    : _createCommentVNode("", true),
                  (!mediaRows.value.length)
                    ? (_openBlock(), _createBlock(_component_VEmptyState, {
                        key: 2,
                        icon: "mdi-database-search-outline",
                        title: "尚未扫描媒体库",
                        text: "完成媒体服务器配置后，执行一次媒体库扫描即可查看电影、剧集、进度和清理候选。"
                      }))
                    : _createCommentVNode("", true)
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "library" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_18, [
                  _createElementVNode("div", _hoisted_19, [
                    _createVNode(_component_VSelect, {
                      modelValue: selectedLibraryId.value,
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((selectedLibraryId).value = $event)),
                      label: "媒体库",
                      items: librarySwitchOptions.value,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue", "items"]),
                    _createVNode(_component_VSelect, {
                      modelValue: selectedDirectoryFilter.value,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((selectedDirectoryFilter).value = $event)),
                      label: "目录",
                      items: directoryFilterOptions.value,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue", "items"]),
                    _createVNode(_component_VTextField, {
                      modelValue: searchText.value,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((searchText).value = $event)),
                      label: "搜索名称、简介或路径",
                      "prepend-inner-icon": "mdi-magnify",
                      density: "comfortable",
                      "hide-details": "",
                      clearable: ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: watchFilter.value,
                      "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((watchFilter).value = $event)),
                      label: "观看状态",
                      items: mediaWatchFilterOptions,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: typeFilter.value,
                      "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((typeFilter).value = $event)),
                      label: "媒体类型",
                      items: ['全部', '电影', '剧集'],
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: mediaSort.value,
                      "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((mediaSort).value = $event)),
                      label: "排序规则",
                      items: sortOptions,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: pageSize.value,
                      "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((pageSize).value = $event)),
                      modelModifiers: { number: true },
                      label: "显示数量",
                      items: pageSizeOptions,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VBtn, {
                      "prepend-icon": sortDesc.value ? 'mdi-sort-descending' : 'mdi-sort-ascending',
                      variant: "tonal",
                      onClick: _cache[8] || (_cache[8] = $event => (sortDesc.value = !sortDesc.value))
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(sortDesc.value ? '降序' : '升序'), 1)
                      ]),
                      _: 1
                    }, 8, ["prepend-icon"])
                  ]),
                  (selectedLibrary.value)
                    ? (_openBlock(), _createBlock(_component_VAlert, {
                        key: 0,
                        type: "info",
                        variant: "tonal",
                        density: "compact"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(" 当前入口：" + _toDisplayString(selectedLibrary.value.title) + "，共 " + _toDisplayString(filteredMediaRows.value.length) + " 个媒体条目，显示 " + _toDisplayString(visibleMediaRows.value.length) + " 个。 ", 1)
                        ]),
                        _: 1
                      }))
                    : _createCommentVNode("", true),
                  (visibleMediaRows.value.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_20, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(visibleMediaRows.value, (item) => {
                          return (_openBlock(), _createBlock(_component_VSheet, {
                            key: item.id,
                            border: "",
                            rounded: "",
                            class: "mlk-media-card",
                            onClick: $event => (openMediaDetail(item))
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_21, [
                                (item.image_url)
                                  ? (_openBlock(), _createBlock(_component_VImg, {
                                      key: 0,
                                      src: resolveImageUrl(item.image_url),
                                      cover: ""
                                    }, null, 8, ["src"]))
                                  : (_openBlock(), _createElementBlock("div", _hoisted_22, [
                                      _createVNode(_component_VIcon, {
                                        icon: item.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline',
                                        size: "44"
                                      }, null, 8, ["icon"])
                                    ])),
                                _createVNode(_component_VBtn, {
                                  class: "mlk-select-btn",
                                  icon: isSelected(item) ? 'mdi-check-circle' : 'mdi-plus-circle-outline',
                                  color: isSelected(item) ? 'success' : undefined,
                                  variant: "text",
                                  "aria-label": selectedButtonLabel(item),
                                  onClick: _withModifiers($event => (toggleSelected(item)), ["stop"])
                                }, null, 8, ["icon", "color", "aria-label", "onClick"])
                              ]),
                              _createElementVNode("div", _hoisted_23, [
                                _createElementVNode("div", _hoisted_24, [
                                  _createElementVNode("div", _hoisted_25, _toDisplayString(item.title), 1),
                                  _createElementVNode("div", _hoisted_26, _toDisplayString(item.year || '未知年份') + " · " + _toDisplayString(item.type_label) + " · " + _toDisplayString(item.library || item.server), 1)
                                ]),
                                _createElementVNode("div", _hoisted_27, [
                                  _createVNode(_component_VChip, {
                                    size: "x-small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(item.rating || '-') + " 分", 1)
                                    ]),
                                    _: 2
                                  }, 1024),
                                  _createVNode(_component_VChip, {
                                    size: "x-small",
                                    color: watchStateColor(item),
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(watchStateText(item)), 1)
                                    ]),
                                    _: 2
                                  }, 1032, ["color"]),
                                  _createVNode(_component_VChip, {
                                    size: "x-small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                                    ]),
                                    _: 2
                                  }, 1024)
                                ]),
                                _createElementVNode("div", _hoisted_28, [
                                  _createElementVNode("div", _hoisted_29, [
                                    _createVNode(_component_VIcon, {
                                      icon: "mdi-harddisk",
                                      size: "14"
                                    }),
                                    _createElementVNode("span", null, "所在盘 " + _toDisplayString(mediaVolumeText(item)), 1)
                                  ]),
                                  _createElementVNode("div", _hoisted_30, [
                                    _createVNode(_component_VIcon, {
                                      icon: "mdi-calendar-import",
                                      size: "14"
                                    }),
                                    _createElementVNode("span", null, _toDisplayString(mediaAddedLabelText(item)), 1)
                                  ]),
                                  _createElementVNode("div", _hoisted_31, [
                                    _createVNode(_component_VIcon, {
                                      icon: "mdi-play-circle-outline",
                                      size: "14"
                                    }),
                                    _createElementVNode("span", null, _toDisplayString(mediaWatchedLabelText(item)), 1)
                                  ])
                                ])
                              ])
                            ]),
                            _: 2
                          }, 1032, ["onClick"]))
                        }), 128))
                      ]))
                    : (_openBlock(), _createBlock(_component_VEmptyState, {
                        key: 2,
                        icon: "mdi-folder-open-outline",
                        title: "没有匹配的媒体",
                        text: "调整媒体库入口、类型、观看状态或搜索关键词后再试。"
                      }))
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "recommendations" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_32, [
                  _createElementVNode("div", _hoisted_33, [
                    _createVNode(_component_VSelect, {
                      modelValue: selectedLibraryId.value,
                      "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((selectedLibraryId).value = $event)),
                      label: "媒体库",
                      items: librarySwitchOptions.value,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue", "items"]),
                    _createVNode(_component_VSelect, {
                      modelValue: selectedDirectoryFilter.value,
                      "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((selectedDirectoryFilter).value = $event)),
                      label: "目录",
                      items: directoryFilterOptions.value,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue", "items"]),
                    _createVNode(_component_VTextField, {
                      modelValue: searchText.value,
                      "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((searchText).value = $event)),
                      label: "搜索名称、简介或路径",
                      "prepend-inner-icon": "mdi-magnify",
                      density: "comfortable",
                      "hide-details": "",
                      clearable: ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: watchFilter.value,
                      "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((watchFilter).value = $event)),
                      label: "观看状态",
                      items: mediaWatchFilterOptions,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: typeFilter.value,
                      "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((typeFilter).value = $event)),
                      label: "媒体类型",
                      items: ['全部', '电影', '剧集'],
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: mediaSort.value,
                      "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((mediaSort).value = $event)),
                      label: "排序规则",
                      items: sortOptions,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: pageSize.value,
                      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((pageSize).value = $event)),
                      modelModifiers: { number: true },
                      label: "显示数量",
                      items: pageSizeOptions,
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VBtn, {
                      "prepend-icon": sortDesc.value ? 'mdi-sort-descending' : 'mdi-sort-ascending',
                      variant: "tonal",
                      onClick: _cache[16] || (_cache[16] = $event => (sortDesc.value = !sortDesc.value))
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(sortDesc.value ? '降序' : '升序'), 1)
                      ]),
                      _: 1
                    }, 8, ["prepend-icon"])
                  ]),
                  (recommendationRows.value.length)
                    ? (_openBlock(), _createBlock(_component_VAlert, {
                        key: 0,
                        type: "info",
                        variant: "tonal",
                        density: "compact"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(" 当前清理建议 " + _toDisplayString(recommendationRows.value.length) + " 个，筛选后 " + _toDisplayString(filteredRecommendationRows.value.length) + " 个，显示 " + _toDisplayString(visibleRecommendationRows.value.length) + " 个。 ", 1)
                        ]),
                        _: 1
                      }))
                    : _createCommentVNode("", true),
                  (visibleRecommendationRows.value.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_34, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(visibleRecommendationRows.value, (item) => {
                          return (_openBlock(), _createBlock(_component_VSheet, {
                            key: item.id,
                            border: "",
                            rounded: "",
                            class: "mlk-media-card",
                            onClick: $event => (openMediaDetail(item))
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_35, [
                                (item.image_url)
                                  ? (_openBlock(), _createBlock(_component_VImg, {
                                      key: 0,
                                      src: resolveImageUrl(item.image_url),
                                      cover: ""
                                    }, null, 8, ["src"]))
                                  : (_openBlock(), _createElementBlock("div", _hoisted_36, [
                                      _createVNode(_component_VIcon, {
                                        icon: item.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline',
                                        size: "44"
                                      }, null, 8, ["icon"])
                                    ])),
                                _createVNode(_component_VBtn, {
                                  class: "mlk-select-btn",
                                  icon: isSelected(item) ? 'mdi-check-circle' : 'mdi-plus-circle-outline',
                                  color: isSelected(item) ? 'success' : undefined,
                                  variant: "text",
                                  "aria-label": selectedButtonLabel(item),
                                  onClick: _withModifiers($event => (toggleSelected(item)), ["stop"])
                                }, null, 8, ["icon", "color", "aria-label", "onClick"])
                              ]),
                              _createElementVNode("div", _hoisted_37, [
                                _createElementVNode("div", _hoisted_38, [
                                  _createElementVNode("div", _hoisted_39, _toDisplayString(item.title), 1),
                                  _createElementVNode("div", _hoisted_40, _toDisplayString(item.reason), 1)
                                ]),
                                _createElementVNode("div", _hoisted_41, _toDisplayString(item.message), 1),
                                _createElementVNode("div", _hoisted_42, [
                                  _createVNode(_component_VChip, {
                                    size: "x-small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(item.progress), 1)
                                    ]),
                                    _: 2
                                  }, 1024),
                                  _createVNode(_component_VChip, {
                                    size: "x-small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                                    ]),
                                    _: 2
                                  }, 1024)
                                ]),
                                _createElementVNode("div", _hoisted_43, [
                                  _createElementVNode("div", _hoisted_44, [
                                    _createVNode(_component_VIcon, {
                                      icon: "mdi-harddisk",
                                      size: "14"
                                    }),
                                    _createElementVNode("span", null, "所在盘 " + _toDisplayString(mediaVolumeText(item)), 1)
                                  ])
                                ])
                              ])
                            ]),
                            _: 2
                          }, 1032, ["onClick"]))
                        }), 128))
                      ]))
                    : (_openBlock(), _createBlock(_component_VEmptyState, {
                        key: 2,
                        icon: "mdi-lightbulb-on-outline",
                        title: recommendationRows.value.length ? '没有匹配的清理建议' : '暂无清理建议',
                        text: recommendationRows.value.length ? '调整筛选、搜索或排序条件后再试。' : '扫描后会列出已看完、入库较久未观看和占用较大的候选。'
                      }, null, 8, ["title", "text"]))
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "plan" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_45, [
                  _createVNode(_component_VSheet, {
                    border: "",
                    rounded: "",
                    class: "mlk-plan-bar"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", null, [
                        _createElementVNode("div", _hoisted_46, [
                          _cache[56] || (_cache[56] = _createElementVNode("span", { class: "text-subtitle-1 font-weight-medium" }, "当前选择", -1)),
                          _createVNode(_component_VTooltip, {
                            text: selectedPlanExpanded.value ? '收起待生成明细' : '展开待生成明细',
                            location: "top"
                          }, {
                            activator: _withCtx(({ props: tooltipProps }) => [
                              _createVNode(_component_VBtn, _mergeProps(tooltipProps, {
                                icon: selectedPlanExpanded.value ? 'mdi-chevron-up' : 'mdi-chevron-down',
                                variant: "text",
                                size: "small",
                                disabled: !selectedMedia.value.length,
                                onClick: _cache[17] || (_cache[17] = $event => (selectedPlanExpanded.value = !selectedPlanExpanded.value))
                              }), null, 16, ["icon", "disabled"])
                            ]),
                            _: 1
                          }, 8, ["text"])
                        ]),
                        _createElementVNode("div", _hoisted_47, " 已选择 " + _toDisplayString(selectedMedia.value.length) + " 项，当前 Emby 可见体积 " + _toDisplayString(_unref(formatBytes)(selectedSize.value)), 1)
                      ]),
                      _createVNode(_component_VSpacer),
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "flat",
                        loading: creatingPlan.value,
                        disabled: !selectedMedia.value.length || updatingPlan.value,
                        onClick: createPlan
                      }, {
                        default: _withCtx(() => [...(_cache[57] || (_cache[57] = [
                          _createTextVNode(" 生成新批次 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading", "disabled"]),
                      _createVNode(_component_VBtn, {
                        variant: "tonal",
                        loading: updatingPlan.value,
                        disabled: !pendingPlan.value || !selectedMedia.value.length || creatingPlan.value,
                        onClick: addSelectedToPlan
                      }, {
                        default: _withCtx(() => [...(_cache[58] || (_cache[58] = [
                          _createTextVNode(" 加入当前批次 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading", "disabled"])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_VExpandTransition, null, {
                    default: _withCtx(() => [
                      _withDirectives(_createVNode(_component_VSheet, {
                        border: "",
                        rounded: "",
                        class: "mlk-selection-detail"
                      }, {
                        default: _withCtx(() => [
                          _cache[59] || (_cache[59] = _createElementVNode("div", { class: "mlk-section-header" }, [
                            _createElementVNode("div", null, [
                              _createElementVNode("div", { class: "text-subtitle-2 font-weight-medium" }, "待生成批次明细"),
                              _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "这些条目只会在点击对应按钮后生成新批次或加入当前批次。")
                            ])
                          ], -1)),
                          _createVNode(_component_VDataTable, {
                            headers: selectedPlanHeaders,
                            items: selectedMedia.value,
                            density: "compact"
                          }, {
                            "item.type_label": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(item.type_label || (item.type === 'series' ? '剧集' : '电影')), 1)
                            ]),
                            "item.watch_state": _withCtx(({ item }) => [
                              _createVNode(_component_VChip, {
                                color: watchStateColor(item),
                                variant: "tonal",
                                size: "small"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(watchStateText(item)), 1)
                                ]),
                                _: 2
                              }, 1032, ["color"])
                            ]),
                            "item.size": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                            ]),
                            "item.volume_name": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(mediaVolumeCapacityText(item)), 1)
                            ]),
                            "item.added_at": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(mediaAddedLabelText(item)), 1)
                            ]),
                            "item.actions": _withCtx(({ item }) => [
                              _createVNode(_component_VBtn, {
                                icon: "mdi-minus-circle-outline",
                                variant: "text",
                                color: "error",
                                onClick: $event => (toggleSelected(item))
                              }, null, 8, ["onClick"])
                            ]),
                            _: 1
                          }, 8, ["items"])
                        ]),
                        _: 1
                      }, 512), [
                        [_vShow, selectedPlanExpanded.value && selectedMedia.value.length]
                      ])
                    ]),
                    _: 1
                  }),
                  (pendingPlan.value)
                    ? (_openBlock(), _createBlock(_component_VSheet, {
                        key: 0,
                        border: "",
                        rounded: "",
                        class: "mlk-plan-card"
                      }, {
                        default: _withCtx(() => [
                          _createElementVNode("div", _hoisted_48, [
                            _createElementVNode("div", _hoisted_49, [
                              _createElementVNode("div", _hoisted_50, [
                                _createElementVNode("span", _hoisted_51, "批次 " + _toDisplayString(pendingPlan.value.batch_id || pendingPlan.value.id), 1),
                                _createVNode(_component_VTooltip, {
                                  text: planExpanded.value ? '收起批次明细' : '展开批次明细',
                                  location: "top"
                                }, {
                                  activator: _withCtx(({ props: tooltipProps }) => [
                                    _createVNode(_component_VBtn, _mergeProps(tooltipProps, {
                                      icon: planExpanded.value ? 'mdi-chevron-up' : 'mdi-chevron-down',
                                      variant: "text",
                                      size: "small",
                                      onClick: _cache[18] || (_cache[18] = $event => (planExpanded.value = !planExpanded.value))
                                    }), null, 16, ["icon"])
                                  ]),
                                  _: 1
                                }, 8, ["text"])
                              ]),
                              _createElementVNode("div", _hoisted_52, _toDisplayString(pendingPlan.value.source_label || '手动选择') + " · " + _toDisplayString(pendingPlan.value.created_at), 1),
                              _createElementVNode("div", _hoisted_53, _toDisplayString(pendingPlan.value.message), 1),
                              _createElementVNode("div", _hoisted_54, [
                                _createVNode(_component_VChip, {
                                  size: "small",
                                  variant: "tonal",
                                  color: "info"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode("电影 " + _toDisplayString(pendingPlanStats.value.movies), 1)
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VChip, {
                                  size: "small",
                                  variant: "tonal",
                                  color: "success"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode("剧集 " + _toDisplayString(pendingPlanStats.value.series), 1)
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VChip, {
                                  size: "small",
                                  variant: "tonal",
                                  color: "primary"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode("有记录 " + _toDisplayString(pendingPlanRecordStats.value.recorded) + "/" + _toDisplayString(pendingPlanItems.value.length), 1)
                                  ]),
                                  _: 1
                                }),
                                (pendingPlanRecordStats.value.missing)
                                  ? (_openBlock(), _createBlock(_component_VChip, {
                                      key: 0,
                                      size: "small",
                                      variant: "tonal",
                                      color: "warning"
                                    }, {
                                      default: _withCtx(() => [
                                        _createTextVNode("记录丢失 " + _toDisplayString(pendingPlanRecordStats.value.missing), 1)
                                      ]),
                                      _: 1
                                    }))
                                  : _createCommentVNode("", true),
                                _createVNode(_component_VChip, {
                                  size: "small",
                                  variant: "tonal",
                                  color: "warning"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode("预计释放 " + _toDisplayString(_unref(formatBytes)(pendingPlan.value.estimated_reclaim_size || pendingPlanStats.value.size)), 1)
                                  ]),
                                  _: 1
                                })
                              ])
                            ]),
                            _createElementVNode("div", _hoisted_55, [
                              _createVNode(_component_VTooltip, {
                                text: "删除当前批次记录，不删除文件",
                                location: "top"
                              }, {
                                activator: _withCtx(({ props: tooltipProps }) => [
                                  _createElementVNode("span", _normalizeProps(_guardReactiveProps(tooltipProps)), [
                                    _createVNode(_component_VBtn, {
                                      color: "error",
                                      variant: "text",
                                      "prepend-icon": "mdi-close-circle-outline",
                                      loading: deletingPlan.value,
                                      onClick: openDeletePlanDialog
                                    }, {
                                      default: _withCtx(() => [...(_cache[60] || (_cache[60] = [
                                        _createTextVNode(" 删除批次 ", -1)
                                      ]))]),
                                      _: 1
                                    }, 8, ["loading"])
                                  ], 16)
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_VTooltip, {
                                text: "执行当前批次中可执行的清理条目",
                                location: "top"
                              }, {
                                activator: _withCtx(({ props: tooltipProps }) => [
                                  _createElementVNode("span", _normalizeProps(_guardReactiveProps(tooltipProps)), [
                                    _createVNode(_component_VBtn, {
                                      color: "error",
                                      variant: "tonal",
                                      "prepend-icon": "mdi-delete-alert-outline",
                                      disabled: !planExecutable.value,
                                      onClick: openExecuteDialog
                                    }, {
                                      default: _withCtx(() => [...(_cache[61] || (_cache[61] = [
                                        _createTextVNode(" 执行清理 ", -1)
                                      ]))]),
                                      _: 1
                                    }, 8, ["disabled"])
                                  ], 16)
                                ]),
                                _: 1
                              })
                            ])
                          ]),
                          _createVNode(_component_VExpandTransition, null, {
                            default: _withCtx(() => [
                              _withDirectives(_createElementVNode("div", _hoisted_56, [
                                _createVNode(_component_VDataTable, {
                                  headers: planHeaders,
                                  items: pendingPlanItems.value,
                                  density: "comfortable"
                                }, {
                                  "item.status": _withCtx(({ item }) => [
                                    _createVNode(_component_VChip, {
                                      color: planItemStatusColor(item),
                                      variant: "tonal",
                                      size: "small"
                                    }, {
                                      default: _withCtx(() => [
                                        _createTextVNode(_toDisplayString(planItemStatusText(item)), 1)
                                      ]),
                                      _: 2
                                    }, 1032, ["color"])
                                  ]),
                                  "item.size": _withCtx(({ item }) => [
                                    _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                                  ]),
                                  "item.volume_name": _withCtx(({ item }) => [
                                    _createTextVNode(_toDisplayString(mediaVolumeCapacityText(item)), 1)
                                  ]),
                                  "item.target_count": _withCtx(({ item }) => [
                                    _createTextVNode(_toDisplayString(item.delete_targets?.length || 0), 1)
                                  ]),
                                  "item.actions": _withCtx(({ item }) => [
                                    _createElementVNode("div", _hoisted_57, [
                                      _createVNode(_component_VTooltip, {
                                        text: "查看删除目标",
                                        location: "top"
                                      }, {
                                        activator: _withCtx(({ props: tooltipProps }) => [
                                          _createElementVNode("span", _normalizeProps(_guardReactiveProps(tooltipProps)), [
                                            _createVNode(_component_VBtn, {
                                              icon: "mdi-file-eye-outline",
                                              variant: "text",
                                              disabled: !item.delete_targets?.length,
                                              "aria-label": "查看删除目标",
                                              onClick: $event => (openPlanTargetDialog(item))
                                            }, null, 8, ["disabled", "onClick"])
                                          ], 16)
                                        ]),
                                        _: 2
                                      }, 1024),
                                      _createVNode(_component_VTooltip, {
                                        text: "从批次移除",
                                        location: "top"
                                      }, {
                                        activator: _withCtx(({ props: tooltipProps }) => [
                                          _createVNode(_component_VBtn, _mergeProps(tooltipProps, {
                                            icon: "mdi-minus-circle-outline",
                                            variant: "text",
                                            color: "error",
                                            loading: updatingPlan.value,
                                            "aria-label": "从批次移除",
                                            onClick: $event => (removePlanItem(item))
                                          }), null, 16, ["loading", "onClick"])
                                        ]),
                                        _: 2
                                      }, 1024)
                                    ])
                                  ]),
                                  _: 1
                                }, 8, ["items"])
                              ], 512), [
                                [_vShow, planExpanded.value]
                              ])
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      }))
                    : _createCommentVNode("", true)
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "history" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_58, [
                  (cleanupQueueRows.value.length)
                    ? (_openBlock(), _createBlock(_component_VSheet, {
                        key: 0,
                        border: "",
                        rounded: "",
                        class: "mlk-queue-card"
                      }, {
                        default: _withCtx(() => [
                          _cache[62] || (_cache[62] = _createElementVNode("div", { class: "mlk-section-header" }, [
                            _createElementVNode("div", null, [
                              _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "清理队列"),
                              _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "清理任务在后台执行，完成后会写入下方执行记录。")
                            ])
                          ], -1)),
                          _createVNode(_component_VDataTable, {
                            headers: [
                  { title: '加入时间', key: 'created_at', width: 168 },
                  { title: '状态', key: 'status', width: 110 },
                  { title: '媒体', key: 'ready_count', width: 110 },
                  { title: '预计释放', key: 'estimated_reclaim_size', width: 120 },
                  { title: '说明', key: 'message' },
                ],
                            items: cleanupQueueRows.value,
                            density: "compact"
                          }, {
                            "item.status": _withCtx(({ item }) => [
                              _createVNode(_component_VChip, {
                                color: queueStatusColor(item),
                                variant: "tonal",
                                size: "small"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(queueStatusText(item)), 1)
                                ]),
                                _: 2
                              }, 1032, ["color"])
                            ]),
                            "item.ready_count": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(item.ready_count || 0) + "/" + _toDisplayString(item.item_count || 0), 1)
                            ]),
                            "item.estimated_reclaim_size": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(_unref(formatBytes)(item.estimated_reclaim_size)), 1)
                            ]),
                            _: 1
                          }, 8, ["items"])
                        ]),
                        _: 1
                      }))
                    : _createCommentVNode("", true),
                  _createVNode(_component_VDataTable, {
                    headers: [
                { title: '时间', key: 'created_at', width: 168 },
                { title: '结果', key: 'status', width: 110 },
                { title: '释放空间', key: 'reclaim_size', width: 120 },
                { title: '媒体库文件', key: 'deleted_media_files', width: 120 },
                { title: '刮削文件', key: 'deleted_scraping_files', width: 110 },
                { title: '源文件', key: 'deleted_source_files', width: 100 },
                { title: '保种任务', key: 'seed_tasks', width: 110 },
                { title: '整理记录', key: 'deleted_records', width: 110 },
                { title: '说明', key: 'message' },
                { title: '详情', key: 'actions', width: 90, sortable: false, align: 'center' },
              ],
                    items: historyRows.value,
                    density: "comfortable"
                  }, {
                    "item.status": _withCtx(({ item }) => [
                      _createVNode(_component_VChip, {
                        color: item.status === 'success' ? 'success' : 'error',
                        variant: "tonal",
                        size: "small"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(item.status === 'success' ? '成功' : '失败'), 1)
                        ]),
                        _: 2
                      }, 1032, ["color"])
                    ]),
                    "item.reclaim_size": _withCtx(({ item }) => [
                      _createTextVNode(_toDisplayString(_unref(formatBytes)(item.reclaim_size)), 1)
                    ]),
                    "item.deleted_media_files": _withCtx(({ item }) => [
                      _createTextVNode(_toDisplayString(cleanupRecordStats(item).mediaFiles), 1)
                    ]),
                    "item.deleted_scraping_files": _withCtx(({ item }) => [
                      _createTextVNode(_toDisplayString(cleanupRecordStats(item).scrapingFiles), 1)
                    ]),
                    "item.deleted_source_files": _withCtx(({ item }) => [
                      _createTextVNode(_toDisplayString(cleanupRecordStats(item).sourceFiles), 1)
                    ]),
                    "item.seed_tasks": _withCtx(({ item }) => [
                      _createTextVNode(_toDisplayString(cleanupRecordStats(item).seedTasks) + " ", 1),
                      (cleanupRecordStats(item).failedSeedTasks)
                        ? (_openBlock(), _createElementBlock("span", _hoisted_59, "/" + _toDisplayString(cleanupRecordStats(item).failedSeedTasks) + " 失败", 1))
                        : _createCommentVNode("", true)
                    ]),
                    "item.actions": _withCtx(({ item }) => [
                      _createElementVNode("div", _hoisted_60, [
                        _createVNode(_component_VBtn, {
                          icon: "mdi-file-eye-outline",
                          variant: "text",
                          "aria-label": "查看清理记录详情",
                          onClick: $event => (openHistoryDetail(item))
                        }, null, 8, ["onClick"])
                      ])
                    ]),
                    "no-data": _withCtx(() => [
                      _createVNode(_component_VEmptyState, {
                        icon: "mdi-history",
                        title: "暂无执行记录",
                        text: "每次真实清理的结果都会保存在这里。"
                      })
                    ]),
                    _: 1
                  }, 8, ["items"])
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "settings" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_61, [
                  _createElementVNode("div", _hoisted_62, [
                    _cache[63] || (_cache[63] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "基础配置", -1)),
                    _createElementVNode("div", _hoisted_63, [
                      _createVNode(_component_VSwitch, {
                        modelValue: configDraft.value.enabled,
                        "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((configDraft.value.enabled) = $event)),
                        color: "primary",
                        inset: "",
                        label: "启用插件"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VSwitch, {
                        modelValue: configDraft.value.show_sidebar_nav,
                        "onUpdate:modelValue": _cache[20] || (_cache[20] = $event => ((configDraft.value.show_sidebar_nav) = $event)),
                        color: "primary",
                        inset: "",
                        label: "显示侧边栏入口"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VSwitch, {
                        modelValue: configDraft.value.notify_enabled,
                        "onUpdate:modelValue": _cache[21] || (_cache[21] = $event => ((configDraft.value.notify_enabled) = $event)),
                        color: "primary",
                        inset: "",
                        label: "启用通知"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VSwitch, {
                        modelValue: configDraft.value.disk_warning_enabled,
                        "onUpdate:modelValue": _cache[22] || (_cache[22] = $event => ((configDraft.value.disk_warning_enabled) = $event)),
                        color: "warning",
                        inset: "",
                        label: "启用磁盘容量告警"
                      }, null, 8, ["modelValue"])
                    ]),
                    _createElementVNode("div", _hoisted_64, [
                      _createVNode(_component_VSelect, {
                        modelValue: configDraft.value.mediaservers,
                        "onUpdate:modelValue": _cache[23] || (_cache[23] = $event => ((configDraft.value.mediaservers) = $event)),
                        label: "媒体服务器",
                        items: mediaServerOptions.value,
                        multiple: "",
                        chips: "",
                        clearable: "",
                        hint: "留空表示扫描所有 Emby 媒体服务器。",
                        "persistent-hint": ""
                      }, null, 8, ["modelValue", "items"]),
                      _createVNode(_component_VSelect, {
                        modelValue: configDraft.value.downloaders,
                        "onUpdate:modelValue": _cache[24] || (_cache[24] = $event => ((configDraft.value.downloaders) = $event)),
                        label: "下载器",
                        items: downloaderOptions.value,
                        multiple: "",
                        chips: "",
                        clearable: "",
                        hint: "留空表示全部支持的下载器。",
                        "persistent-hint": ""
                      }, null, 8, ["modelValue", "items"])
                    ])
                  ]),
                  _createElementVNode("div", _hoisted_65, [
                    _cache[65] || (_cache[65] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "扫描和清理计划", -1)),
                    _createElementVNode("div", _hoisted_66, [
                      _createVNode(_component_VSelect, {
                        modelValue: configDraft.value.scan_cron,
                        "onUpdate:modelValue": _cache[25] || (_cache[25] = $event => ((configDraft.value.scan_cron) = $event)),
                        label: "扫描周期",
                        items: scanCronOptions
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VTextField, {
                        modelValue: configDraft.value.disk_warning_free_gb,
                        "onUpdate:modelValue": _cache[26] || (_cache[26] = $event => ((configDraft.value.disk_warning_free_gb) = $event)),
                        modelModifiers: { number: true },
                        type: "number",
                        min: "0",
                        label: "剩余容量低于 GB"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VTextField, {
                        modelValue: configDraft.value.disk_warning_free_percent,
                        "onUpdate:modelValue": _cache[27] || (_cache[27] = $event => ((configDraft.value.disk_warning_free_percent) = $event)),
                        modelModifiers: { number: true },
                        type: "number",
                        min: "0",
                        label: "剩余比例低于 %"
                      }, null, 8, ["modelValue"])
                    ]),
                    _createVNode(_component_VAlert, {
                      type: "info",
                      variant: "tonal",
                      density: "comfortable"
                    }, {
                      default: _withCtx(() => [...(_cache[64] || (_cache[64] = [
                        _createTextVNode(" 定时任务会先扫描 Emby 媒体库，刷新容量状态和磁盘告警，再按下方清理计划规则生成待确认批次。 ", -1)
                      ]))]),
                      _: 1
                    })
                  ]),
                  _createElementVNode("div", _hoisted_67, [
                    _createElementVNode("div", _hoisted_68, [
                      _cache[67] || (_cache[67] = _createElementVNode("div", null, [
                        _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "目录映射"),
                        _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "将 Emby 容器路径转换为 MoviePilot 容器内可访问路径。")
                      ], -1)),
                      _createVNode(_component_VBtn, {
                        "prepend-icon": "mdi-plus",
                        color: "primary",
                        variant: "tonal",
                        onClick: addPathMapping
                      }, {
                        default: _withCtx(() => [...(_cache[66] || (_cache[66] = [
                          _createTextVNode(" 添加映射 ", -1)
                        ]))]),
                        _: 1
                      })
                    ]),
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(configDraft.value.path_mappings, (mapping, index) => {
                      return (_openBlock(), _createBlock(_component_VSheet, {
                        key: `path-mapping-${index}`,
                        border: "",
                        rounded: "",
                        class: "mlk-path-mapping-row"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VTextField, {
                            modelValue: mapping.emby_path,
                            "onUpdate:modelValue": $event => ((mapping.emby_path) = $event),
                            label: "Emby 路径前缀",
                            placeholder: "/video",
                            density: "comfortable",
                            "hide-details": ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                          _createVNode(_component_VTextField, {
                            modelValue: mapping.mp_path,
                            "onUpdate:modelValue": $event => ((mapping.mp_path) = $event),
                            label: "MP 路径前缀",
                            placeholder: "/media/video",
                            density: "comfortable",
                            "hide-details": ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                          _createVNode(_component_VBtn, {
                            icon: "mdi-delete-outline",
                            color: "error",
                            variant: "text",
                            onClick: $event => (removePathMapping(index))
                          }, null, 8, ["onClick"])
                        ]),
                        _: 2
                      }, 1024))
                    }), 128)),
                    (!(configDraft.value.path_mappings || []).length)
                      ? (_openBlock(), _createBlock(_component_VAlert, {
                          key: 0,
                          type: "info",
                          variant: "tonal",
                          density: "comfortable"
                        }, {
                          default: _withCtx(() => [...(_cache[68] || (_cache[68] = [
                            _createTextVNode(" Emby 与 MoviePilot 挂载路径一致时无需配置。 ", -1)
                          ]))]),
                          _: 1
                        }))
                      : _createCommentVNode("", true)
                  ]),
                  _createElementVNode("div", _hoisted_69, [
                    _createElementVNode("div", _hoisted_70, [
                      _cache[70] || (_cache[70] = _createElementVNode("div", null, [
                        _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "下载器目录映射"),
                        _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "建立下载器任务路径与 MoviePilot 资源目录的对应关系，用于保种任务缺少 Hash 时辅助排查。")
                      ], -1)),
                      _createVNode(_component_VBtn, {
                        "prepend-icon": "mdi-plus",
                        color: "primary",
                        variant: "tonal",
                        onClick: addDownloaderPathMapping
                      }, {
                        default: _withCtx(() => [...(_cache[69] || (_cache[69] = [
                          _createTextVNode(" 添加映射 ", -1)
                        ]))]),
                        _: 1
                      })
                    ]),
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(configDraft.value.downloader_path_mappings, (mapping, index) => {
                      return (_openBlock(), _createBlock(_component_VSheet, {
                        key: `downloader-path-mapping-${index}`,
                        border: "",
                        rounded: "",
                        class: "mlk-downloader-path-mapping-row"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VSelect, {
                            modelValue: mapping.downloader,
                            "onUpdate:modelValue": $event => ((mapping.downloader) = $event),
                            label: "下载器",
                            items: downloaderOptions.value,
                            density: "comfortable",
                            "hide-details": ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue", "items"]),
                          _createVNode(_component_VTextField, {
                            modelValue: mapping.downloader_path,
                            "onUpdate:modelValue": $event => ((mapping.downloader_path) = $event),
                            label: "下载器路径前缀",
                            placeholder: "/downloads",
                            density: "comfortable",
                            "hide-details": ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                          _createVNode(_component_VTextField, {
                            modelValue: mapping.resource_path,
                            "onUpdate:modelValue": $event => ((mapping.resource_path) = $event),
                            label: "MP 资源路径前缀",
                            placeholder: "/media/downloads",
                            density: "comfortable",
                            "hide-details": ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                          _createVNode(_component_VBtn, {
                            icon: "mdi-delete-outline",
                            color: "error",
                            variant: "text",
                            onClick: $event => (removeDownloaderPathMapping(index))
                          }, null, 8, ["onClick"])
                        ]),
                        _: 2
                      }, 1024))
                    }), 128)),
                    (!(configDraft.value.downloader_path_mappings || []).length)
                      ? (_openBlock(), _createBlock(_component_VAlert, {
                          key: 0,
                          type: "info",
                          variant: "tonal",
                          density: "comfortable"
                        }, {
                          default: _withCtx(() => [...(_cache[71] || (_cache[71] = [
                            _createTextVNode(" 只有下载器任务路径和 MoviePilot 资源目录不一致，且需要排查缺少 Hash 的保种任务时才需要配置。 ", -1)
                          ]))]),
                          _: 1
                        }))
                      : _createCommentVNode("", true)
                  ]),
                  _createElementVNode("div", _hoisted_71, [
                    _cache[73] || (_cache[73] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "删除行为", -1)),
                    _createElementVNode("div", _hoisted_72, [
                      _createVNode(_component_VSwitch, {
                        "model-value": configDraft.value.ai_suggestions,
                        color: "primary",
                        inset: "",
                        label: "AI资源任务识别",
                        "onUpdate:modelValue": updateAiSuggestions
                      }, null, 8, ["model-value"]),
                      _createVNode(_component_VSwitch, {
                        modelValue: configDraft.value.default_delete_source,
                        "onUpdate:modelValue": _cache[28] || (_cache[28] = $event => ((configDraft.value.default_delete_source) = $event)),
                        color: "error",
                        inset: "",
                        label: "默认同时删除源文件"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VSwitch, {
                        modelValue: configDraft.value.delete_seed_tasks,
                        "onUpdate:modelValue": _cache[29] || (_cache[29] = $event => ((configDraft.value.delete_seed_tasks) = $event)),
                        color: "warning",
                        inset: "",
                        label: "删除资源时同步删除保种任务"
                      }, null, 8, ["modelValue"])
                    ]),
                    _createVNode(_component_VAlert, {
                      type: "info",
                      variant: "tonal",
                      density: "comfortable"
                    }, {
                      default: _withCtx(() => [...(_cache[72] || (_cache[72] = [
                        _createTextVNode(" AI资源任务识别用于整理记录或 download hash 缺失时，把目录映射生成的候选源文件和下载器路径交给系统 AI 辅助判断；AI结果只作为待确认候选展示，不会绕过人工确认自动删除。 ", -1)
                      ]))]),
                      _: 1
                    })
                  ]),
                  _createVNode(_component_VDivider),
                  _createElementVNode("div", _hoisted_73, [
                    _createElementVNode("div", _hoisted_74, [
                      _cache[76] || (_cache[76] = _createElementVNode("div", null, [
                        _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "清理计划"),
                        _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "先限定参与计划的媒体库，再配置多条条件组合；任意一组命中即进入待清理批次。")
                      ], -1)),
                      _createElementVNode("div", _hoisted_75, [
                        _createVNode(_component_VBtn, {
                          "prepend-icon": "mdi-database-sync-outline",
                          color: "info",
                          variant: "tonal",
                          loading: syncingLibraries.value,
                          onClick: _cache[30] || (_cache[30] = $event => (syncLibraries()))
                        }, {
                          default: _withCtx(() => [...(_cache[74] || (_cache[74] = [
                            _createTextVNode(" 同步媒体库列表 ", -1)
                          ]))]),
                          _: 1
                        }, 8, ["loading"]),
                        _createVNode(_component_VBtn, {
                          "prepend-icon": "mdi-plus",
                          color: "primary",
                          variant: "tonal",
                          onClick: addCleanupRule
                        }, {
                          default: _withCtx(() => [...(_cache[75] || (_cache[75] = [
                            _createTextVNode(" 添加组合 ", -1)
                          ]))]),
                          _: 1
                        })
                      ])
                    ]),
                    _createVNode(_component_VSelect, {
                      modelValue: configDraft.value.cleanup_libraries,
                      "onUpdate:modelValue": _cache[31] || (_cache[31] = $event => ((configDraft.value.cleanup_libraries) = $event)),
                      label: "清理媒体库",
                      items: libraryOptions.value,
                      multiple: "",
                      chips: "",
                      clearable: "",
                      hint: "留空表示全部媒体库。",
                      "persistent-hint": ""
                    }, null, 8, ["modelValue", "items"]),
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(configDraft.value.cleanup_rules, (rule, index) => {
                      return (_openBlock(), _createBlock(_component_VSheet, {
                        key: rule.id || index,
                        border: "",
                        rounded: "",
                        class: "mlk-rule-row"
                      }, {
                        default: _withCtx(() => [
                          _createElementVNode("div", _hoisted_76, "组合 " + _toDisplayString(index + 1), 1),
                          _createElementVNode("div", _hoisted_77, [
                            _createVNode(_component_VSelect, {
                              modelValue: rule.operator,
                              "onUpdate:modelValue": $event => ((rule.operator) = $event),
                              label: "组内关系",
                              items: [
                      { title: '全部满足', value: 'and' },
                      { title: '任一满足', value: 'or' },
                    ],
                              density: "comfortable",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_VSelect, {
                              modelValue: rule.watch_state,
                              "onUpdate:modelValue": $event => ((rule.watch_state) = $event),
                              label: "观看状态",
                              items: cleanupWatchStateOptions,
                              density: "comfortable",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_VTextField, {
                              modelValue: rule.unwatched_days,
                              "onUpdate:modelValue": $event => ((rule.unwatched_days) = $event),
                              modelModifiers: { number: true },
                              type: "number",
                              min: "0",
                              label: "未观看天数",
                              density: "comfortable",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_VTextField, {
                              modelValue: rule.min_size_gb,
                              "onUpdate:modelValue": $event => ((rule.min_size_gb) = $event),
                              modelModifiers: { number: true },
                              type: "number",
                              min: "0",
                              label: "大于 GB",
                              density: "comfortable",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_VTextField, {
                              modelValue: rule.max_rating,
                              "onUpdate:modelValue": $event => ((rule.max_rating) = $event),
                              modelModifiers: { number: true },
                              type: "number",
                              min: "0",
                              step: "0.1",
                              label: "评分低于/等于",
                              density: "comfortable",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_VBtn, {
                              icon: "mdi-delete-outline",
                              color: "error",
                              variant: "text",
                              disabled: configDraft.value.cleanup_rules.length <= 1,
                              onClick: $event => (removeCleanupRule(index))
                            }, null, 8, ["disabled", "onClick"])
                          ])
                        ]),
                        _: 2
                      }, 1024))
                    }), 128)),
                    _cache[77] || (_cache[77] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "数字条件填 0 表示不启用；每条组合至少启用一个条件才会生效。", -1))
                  ]),
                  _createElementVNode("div", _hoisted_78, [
                    _createVNode(_component_VBtn, {
                      class: "mlk-rule-scan-btn",
                      "prepend-icon": "mdi-playlist-plus",
                      color: "primary",
                      variant: "flat",
                      loading: ruleScanning.value,
                      onClick: scanCleanupRules
                    }, {
                      default: _withCtx(() => [...(_cache[78] || (_cache[78] = [
                        _createTextVNode(" 扫描并生成批次 ", -1)
                      ]))]),
                      _: 1
                    }, 8, ["loading"]),
                    _createVNode(_component_VBtn, {
                      "prepend-icon": "mdi-content-save",
                      color: "primary",
                      variant: "flat",
                      loading: saving.value,
                      onClick: saveConfig
                    }, {
                      default: _withCtx(() => [...(_cache[79] || (_cache[79] = [
                        _createTextVNode(" 保存设置 ", -1)
                      ]))]),
                      _: 1
                    }, 8, ["loading"])
                  ])
                ])
              ]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["modelValue"])
      ]),
      _: 1
    }),
    _createVNode(_component_VDialog, {
      modelValue: detailDialog.value,
      "onUpdate:modelValue": _cache[36] || (_cache[36] = $event => ((detailDialog).value = $event)),
      "max-width": "920"
    }, {
      default: _withCtx(() => [
        (selectedMediaDetail.value)
          ? (_openBlock(), _createBlock(_component_VCard, { key: 0 }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_79, [
                  _createElementVNode("div", _hoisted_80, [
                    _createElementVNode("div", _hoisted_81, [
                      (selectedMediaDetail.value.image_url)
                        ? (_openBlock(), _createBlock(_component_VImg, {
                            key: 0,
                            src: resolveImageUrl(selectedMediaDetail.value.image_url),
                            cover: ""
                          }, null, 8, ["src"]))
                        : (_openBlock(), _createElementBlock("div", _hoisted_82, [
                            _createVNode(_component_VIcon, {
                              icon: selectedMediaDetail.value.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline',
                              size: "54"
                            }, null, 8, ["icon"])
                          ]))
                    ]),
                    _createElementVNode("div", _hoisted_83, [
                      _cache[84] || (_cache[84] = _createElementVNode("div", { class: "text-subtitle-2 font-weight-medium" }, "媒体摘要", -1)),
                      _createElementVNode("div", _hoisted_84, [
                        _cache[80] || (_cache[80] = _createElementVNode("span", null, "观看状态", -1)),
                        _createElementVNode("strong", null, _toDisplayString(watchStateText(selectedMediaDetail.value)), 1)
                      ]),
                      _createElementVNode("div", _hoisted_85, [
                        _cache[81] || (_cache[81] = _createElementVNode("span", null, "媒体大小", -1)),
                        _createElementVNode("strong", null, _toDisplayString(_unref(formatBytes)(selectedMediaDetail.value.size)), 1)
                      ]),
                      _createElementVNode("div", _hoisted_86, [
                        _cache[82] || (_cache[82] = _createElementVNode("span", null, "所在盘", -1)),
                        _createElementVNode("strong", null, _toDisplayString(selectedMediaDetail.value.volume_name || '-'), 1)
                      ]),
                      _createElementVNode("div", _hoisted_87, [
                        _cache[83] || (_cache[83] = _createElementVNode("span", null, "卷剩余", -1)),
                        _createElementVNode("strong", null, _toDisplayString(selectedMediaDetail.value.volume_free_percent !== null && selectedMediaDetail.value.volume_free_percent !== undefined ? `${selectedMediaDetail.value.volume_free_percent}%` : '-'), 1)
                      ]),
                      _createElementVNode("div", _hoisted_88, [
                        _createElementVNode("span", null, _toDisplayString(selectedMediaDetail.value.type === 'series' ? '末集添加' : '入库时间'), 1),
                        _createElementVNode("strong", null, _toDisplayString(selectedMediaDetail.value.type === 'series' ? (selectedMediaDetail.value.last_episode_added_at || '-') : (selectedMediaDetail.value.added_at || '-')), 1)
                      ])
                    ])
                  ]),
                  _createElementVNode("div", _hoisted_89, [
                    _createElementVNode("div", _hoisted_90, [
                      _createElementVNode("div", null, [
                        _createElementVNode("div", _hoisted_91, _toDisplayString(selectedMediaDetail.value.title), 1),
                        _createElementVNode("div", _hoisted_92, _toDisplayString(selectedMediaDetail.value.year || '未知年份') + " · " + _toDisplayString(selectedMediaDetail.value.type_label) + " · " + _toDisplayString(selectedMediaDetail.value.library || selectedMediaDetail.value.server), 1)
                      ]),
                      _createVNode(_component_VBtn, {
                        icon: "mdi-close",
                        variant: "text",
                        onClick: _cache[33] || (_cache[33] = $event => (detailDialog.value = false))
                      })
                    ]),
                    _createElementVNode("div", _hoisted_93, [
                      _createVNode(_component_VChip, {
                        color: "primary",
                        variant: "tonal"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(selectedMediaDetail.value.rating || '-') + " 分", 1)
                        ]),
                        _: 1
                      })
                    ]),
                    _createElementVNode("p", _hoisted_94, _toDisplayString(selectedMediaDetail.value.overview || '暂无简介。'), 1),
                    _createElementVNode("div", _hoisted_95, [
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(selectedDetailInfoRows.value, (row) => {
                        return (_openBlock(), _createElementBlock("div", {
                          key: row.label
                        }, [
                          _createElementVNode("div", _hoisted_96, _toDisplayString(row.label), 1),
                          _createElementVNode("div", null, _toDisplayString(row.value), 1)
                        ]))
                      }), 128)),
                      _createElementVNode("div", _hoisted_97, [
                        _cache[85] || (_cache[85] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "路径", -1)),
                        _createElementVNode("div", null, _toDisplayString(selectedMediaDetail.value.path_preview || selectedMediaDetail.value.path || '-'), 1)
                      ]),
                      (selectedMediaDetail.value.emby_path_preview)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_98, [
                            _cache[86] || (_cache[86] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "Emby 原路径", -1)),
                            _createElementVNode("div", null, _toDisplayString(selectedMediaDetail.value.emby_path_preview), 1)
                          ]))
                        : _createCommentVNode("", true),
                      (selectedMediaDetail.value.genres?.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_99, [
                            _cache[87] || (_cache[87] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "类型", -1)),
                            _createElementVNode("div", _hoisted_100, [
                              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(selectedMediaDetail.value.genres, (genre) => {
                                return (_openBlock(), _createBlock(_component_VChip, {
                                  key: genre,
                                  size: "small",
                                  variant: "tonal"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(genre), 1)
                                  ]),
                                  _: 2
                                }, 1024))
                              }), 128))
                            ])
                          ]))
                        : _createCommentVNode("", true)
                    ]),
                    _createVNode(_component_VDivider),
                    _createElementVNode("div", _hoisted_101, [
                      _createVNode(_component_VBtn, {
                        variant: "tonal",
                        color: isSelected(selectedMediaDetail.value) ? 'success' : 'primary',
                        onClick: _cache[34] || (_cache[34] = $event => (toggleSelected(selectedMediaDetail.value)))
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(selectedButtonLabel(selectedMediaDetail.value)), 1)
                        ]),
                        _: 1
                      }, 8, ["color"]),
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "flat",
                        loading: creatingPlan.value,
                        disabled: updatingPlan.value,
                        onClick: _cache[35] || (_cache[35] = $event => (createSinglePlan(selectedMediaDetail.value)))
                      }, {
                        default: _withCtx(() => [...(_cache[88] || (_cache[88] = [
                          _createTextVNode(" 为此项生成计划 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading", "disabled"])
                    ])
                  ])
                ])
              ]),
              _: 1
            }))
          : _createCommentVNode("", true)
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_VDialog, {
      modelValue: planTargetDialog.value,
      "onUpdate:modelValue": _cache[38] || (_cache[38] = $event => ((planTargetDialog).value = $event)),
      "max-width": "820"
    }, {
      default: _withCtx(() => [
        (selectedPlanItem.value)
          ? (_openBlock(), _createBlock(_component_VCard, { key: 0 }, {
              default: _withCtx(() => [
                _createVNode(_component_VCardTitle, null, {
                  default: _withCtx(() => [...(_cache[89] || (_cache[89] = [
                    _createTextVNode("审核删除目标", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_VCardText, null, {
                  default: _withCtx(() => [
                    _createElementVNode("div", _hoisted_102, [
                      _createElementVNode("div", _hoisted_103, _toDisplayString(selectedPlanItem.value.title), 1),
                      _createVNode(_component_VChip, {
                        color: planItemStatusColor(selectedPlanItem.value),
                        variant: "tonal",
                        size: "small"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(planItemStatusText(selectedPlanItem.value)), 1)
                        ]),
                        _: 1
                      }, 8, ["color"])
                    ]),
                    (selectedPlanItem.value.message)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_104, _toDisplayString(selectedPlanItem.value.message), 1))
                      : _createCommentVNode("", true),
                    (selectedPlanItem.value.ai_resource_message && !selectedPlanItem.value.ai_resource_candidates?.length)
                      ? (_openBlock(), _createBlock(_component_VAlert, {
                          key: 1,
                          type: "info",
                          variant: "tonal",
                          density: "comfortable",
                          class: "mb-3"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(" AI资源任务识别：" + _toDisplayString(selectedPlanItem.value.ai_resource_message), 1)
                          ]),
                          _: 1
                        }))
                      : _createCommentVNode("", true),
                    _createElementVNode("div", _hoisted_105, [
                      _cache[94] || (_cache[94] = _createElementVNode("div", { class: "text-subtitle-2 mb-2" }, "下载器任务", -1)),
                      (selectedMatchedDownloadTasks.value.length)
                        ? (_openBlock(), _createBlock(_component_VSheet, {
                            key: 0,
                            border: "",
                            rounded: "",
                            class: "mlk-target-row"
                          }, {
                            default: _withCtx(() => [
                              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(selectedMatchedDownloadTasks.value, (task) => {
                                return (_openBlock(), _createElementBlock("div", {
                                  key: `${task.downloader}-${task.download_hash}`,
                                  class: "mlk-download-task-row"
                                }, [
                                  _createElementVNode("div", _hoisted_106, [
                                    _createVNode(_component_VChip, {
                                      color: "success",
                                      variant: "tonal",
                                      size: "small"
                                    }, {
                                      default: _withCtx(() => [
                                        _createTextVNode(_toDisplayString(downloadTaskStatusText(task)), 1)
                                      ]),
                                      _: 2
                                    }, 1024),
                                    _createVNode(_component_VChip, {
                                      variant: "tonal",
                                      size: "small"
                                    }, {
                                      default: _withCtx(() => [
                                        _createTextVNode(_toDisplayString(downloadTaskName(task)), 1)
                                      ]),
                                      _: 2
                                    }, 1024),
                                    (downloadTaskStateText(task))
                                      ? (_openBlock(), _createBlock(_component_VChip, {
                                          key: 0,
                                          variant: "tonal",
                                          size: "small"
                                        }, {
                                          default: _withCtx(() => [
                                            _createTextVNode(_toDisplayString(downloadTaskStateText(task)), 1)
                                          ]),
                                          _: 2
                                        }, 1024))
                                      : _createCommentVNode("", true),
                                    (downloadTaskSourceText(task))
                                      ? (_openBlock(), _createBlock(_component_VChip, {
                                          key: 1,
                                          variant: "tonal",
                                          size: "small"
                                        }, {
                                          default: _withCtx(() => [
                                            _createTextVNode(_toDisplayString(downloadTaskSourceText(task)), 1)
                                          ]),
                                          _: 2
                                        }, 1024))
                                      : _createCommentVNode("", true)
                                  ]),
                                  _createElementVNode("div", _hoisted_107, _toDisplayString(downloadTaskTitle(task)), 1),
                                  (downloadTaskHint(task))
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_108, _toDisplayString(downloadTaskHint(task)), 1))
                                    : _createCommentVNode("", true),
                                  (task.save_path)
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_109, "保存目录：" + _toDisplayString(task.save_path), 1))
                                    : _createCommentVNode("", true),
                                  (task.content_path && task.content_path !== task.save_path)
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_110, "内容路径：" + _toDisplayString(task.content_path), 1))
                                    : _createCommentVNode("", true),
                                  (task.original_downloader && task.original_downloader !== downloadTaskName(task))
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_111, "原下载器：" + _toDisplayString(task.original_downloader), 1))
                                    : _createCommentVNode("", true)
                                ]))
                              }), 128))
                            ]),
                            _: 1
                          }))
                        : _createCommentVNode("", true),
                      (selectedHistoryHashSummary.value)
                        ? (_openBlock(), _createBlock(_component_VSheet, {
                            key: 1,
                            border: "",
                            rounded: "",
                            class: "mlk-target-row mt-3"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_112, [
                                _createVNode(_component_VChip, {
                                  color: "warning",
                                  variant: "tonal",
                                  size: "small"
                                }, {
                                  default: _withCtx(() => [...(_cache[90] || (_cache[90] = [
                                    _createTextVNode("历史Hash线索", -1)
                                  ]))]),
                                  _: 1
                                }),
                                _createVNode(_component_VChip, {
                                  variant: "tonal",
                                  size: "small"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(selectedHistoryHashSummary.value.total) + " 条", 1)
                                  ]),
                                  _: 1
                                })
                              ]),
                              _cache[91] || (_cache[91] = _createElementVNode("div", { class: "text-body-2 font-weight-medium" }, "未读取到配置下载器实时任务信息", -1)),
                              _cache[92] || (_cache[92] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, " 当前批次只保存历史 Hash，未在配置下载器实时任务中定位到任务；执行清理时仍会按 Hash 到配置下载器尝试删除。 ", -1)),
                              _createElementVNode("div", _hoisted_113, "来源：" + _toDisplayString(summaryEntries(selectedHistoryHashSummary.value.sources)), 1),
                              _createElementVNode("div", _hoisted_114, "候选下载器：" + _toDisplayString(summaryEntries(selectedHistoryHashSummary.value.downloaders)), 1),
                              (selectedHistoryHashSummary.value.titles.length)
                                ? (_openBlock(), _createElementBlock("div", _hoisted_115, " 历史记录：" + _toDisplayString(selectedHistoryHashSummary.value.titles.slice(0, 3).join(' / ')) + _toDisplayString(selectedHistoryHashSummary.value.titles.length > 3 ? ` 等 ${selectedHistoryHashSummary.value.titles.length} 条` : ''), 1))
                                : _createCommentVNode("", true)
                            ]),
                            _: 1
                          }))
                        : _createCommentVNode("", true),
                      (!selectedMatchedDownloadTasks.value.length && !selectedHistoryHashSummary.value)
                        ? (_openBlock(), _createBlock(_component_VAlert, {
                            key: 2,
                            type: "warning",
                            variant: "tonal",
                            density: "comfortable"
                          }, {
                            default: _withCtx(() => [...(_cache[93] || (_cache[93] = [
                              _createTextVNode(" 未找到下载器任务；如果整理记录缺少 download hash，需要通过“保种排查候选”确认后再处理。 ", -1)
                            ]))]),
                            _: 1
                          }))
                        : _createCommentVNode("", true)
                    ]),
                    (selectedPlanItem.value.delete_targets?.length)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_116, [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(selectedPlanItem.value.delete_targets, (target) => {
                            return (_openBlock(), _createBlock(_component_VSheet, {
                              key: `${target.kind}-${target.path}`,
                              border: "",
                              rounded: "",
                              class: "mlk-target-row"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_117, [
                                  _createVNode(_component_VChip, {
                                    color: target.kind === 'src' ? 'error' : 'primary',
                                    variant: "tonal",
                                    size: "small"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(target.kind_label || (target.kind === 'src' ? '源文件' : '媒体库文件')), 1)
                                    ]),
                                    _: 2
                                  }, 1032, ["color"]),
                                  (target.match_source === 'directory_mapping')
                                    ? (_openBlock(), _createBlock(_component_VChip, {
                                        key: 0,
                                        color: "info",
                                        variant: "tonal",
                                        size: "small"
                                      }, {
                                        default: _withCtx(() => [
                                          _createTextVNode(_toDisplayString(target.match_source_label || '目录映射识别'), 1)
                                        ]),
                                        _: 2
                                      }, 1024))
                                    : _createCommentVNode("", true),
                                  (target.match_source === 'ai_resource_recognition')
                                    ? (_openBlock(), _createBlock(_component_VChip, {
                                        key: 1,
                                        color: "warning",
                                        variant: "tonal",
                                        size: "small"
                                      }, {
                                        default: _withCtx(() => [...(_cache[95] || (_cache[95] = [
                                          _createTextVNode(" AI识别 ", -1)
                                        ]))]),
                                        _: 1
                                      }))
                                    : _createCommentVNode("", true)
                                ]),
                                (target.kind === 'src' && target.filename)
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_118, "源文件名"))
                                  : _createCommentVNode("", true),
                                (target.kind === 'src' && target.filename)
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_119, _toDisplayString(target.filename), 1))
                                  : _createCommentVNode("", true),
                                _cache[96] || (_cache[96] = _createElementVNode("div", { class: "text-caption text-medium-emphasis mt-1" }, "文件路径", -1)),
                                _createElementVNode("div", _hoisted_120, _toDisplayString(target.path || target.path_preview), 1),
                                (target.directory_mapping)
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_121, " 目录配置：" + _toDisplayString(target.directory_mapping.name || '未命名目录配置') + "；整理方式：" + _toDisplayString(target.directory_mapping.transfer_type || '未知'), 1))
                                  : _createCommentVNode("", true)
                              ]),
                              _: 2
                            }, 1024))
                          }), 128))
                        ]))
                      : _createCommentVNode("", true),
                    (selectedPlanItem.value.seed_candidates?.length)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_122, [
                          _cache[99] || (_cache[99] = _createElementVNode("div", { class: "text-subtitle-2 mb-2" }, "保种排查候选", -1)),
                          _createVNode(_component_VAlert, {
                            type: "warning",
                            variant: "tonal",
                            density: "comfortable",
                            class: "mb-3"
                          }, {
                            default: _withCtx(() => [...(_cache[97] || (_cache[97] = [
                              _createTextVNode(" 以下候选来自下载器目录映射，缺少 download hash，不能自动删除；需要 AI 或人工确认对应下载任务后再处理。 ", -1)
                            ]))]),
                            _: 1
                          }),
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(selectedPlanItem.value.seed_candidates, (candidate) => {
                            return (_openBlock(), _createBlock(_component_VSheet, {
                              key: `${candidate.downloader}-${candidate.downloader_path}`,
                              border: "",
                              rounded: "",
                              class: "mlk-target-row"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_123, [
                                  _createVNode(_component_VChip, {
                                    color: "warning",
                                    variant: "tonal",
                                    size: "small"
                                  }, {
                                    default: _withCtx(() => [...(_cache[98] || (_cache[98] = [
                                      _createTextVNode("待确认", -1)
                                    ]))]),
                                    _: 1
                                  }),
                                  _createVNode(_component_VChip, {
                                    variant: "tonal",
                                    size: "small"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(seedCandidateDownloaderName(candidate)), 1)
                                    ]),
                                    _: 2
                                  }, 1024)
                                ]),
                                _createElementVNode("div", _hoisted_124, _toDisplayString(candidate.downloader_path), 1),
                                _createElementVNode("div", _hoisted_125, "MP 资源路径：" + _toDisplayString(candidate.source_path), 1),
                                _createElementVNode("div", _hoisted_126, _toDisplayString(candidate.reason), 1)
                              ]),
                              _: 2
                            }, 1024))
                          }), 128))
                        ]))
                      : _createCommentVNode("", true),
                    (selectedPlanItem.value.ai_resource_candidates?.length)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_127, [
                          _cache[104] || (_cache[104] = _createElementVNode("div", { class: "text-subtitle-2 mb-2" }, "AI识别候选源文件", -1)),
                          _createVNode(_component_VAlert, {
                            type: "info",
                            variant: "tonal",
                            density: "comfortable",
                            class: "mb-3"
                          }, {
                            default: _withCtx(() => [...(_cache[100] || (_cache[100] = [
                              _createTextVNode(" 以下候选由系统 AI 根据媒体信息和目录映射判断，仅用于人工审核，不会自动加入删除目标。 ", -1)
                            ]))]),
                            _: 1
                          }),
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(selectedPlanItem.value.ai_resource_candidates, (candidate) => {
                            return (_openBlock(), _createBlock(_component_VSheet, {
                              key: candidate.source_path,
                              border: "",
                              rounded: "",
                              class: "mlk-target-row"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_128, [
                                  _createVNode(_component_VChip, {
                                    color: "warning",
                                    variant: "tonal",
                                    size: "small"
                                  }, {
                                    default: _withCtx(() => [...(_cache[101] || (_cache[101] = [
                                      _createTextVNode("AI识别", -1)
                                    ]))]),
                                    _: 1
                                  }),
                                  _createVNode(_component_VChip, {
                                    variant: "tonal",
                                    size: "small"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(Math.round((candidate.confidence || 0) * 100)) + "%", 1)
                                    ]),
                                    _: 2
                                  }, 1024)
                                ]),
                                _cache[102] || (_cache[102] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "源文件名", -1)),
                                _createElementVNode("div", _hoisted_129, _toDisplayString(candidate.filename || '-'), 1),
                                _cache[103] || (_cache[103] = _createElementVNode("div", { class: "text-caption text-medium-emphasis mt-1" }, "路径", -1)),
                                _createElementVNode("div", _hoisted_130, _toDisplayString(candidate.source_path), 1),
                                _createElementVNode("div", _hoisted_131, _toDisplayString(candidate.reason), 1)
                              ]),
                              _: 2
                            }, 1024))
                          }), 128))
                        ]))
                      : _createCommentVNode("", true),
                    (!selectedPlanItem.value.delete_targets?.length && !selectedPlanItem.value.seed_candidates?.length && !selectedPlanItem.value.ai_resource_candidates?.length)
                      ? (_openBlock(), _createBlock(_component_VEmptyState, {
                          key: 5,
                          icon: "mdi-file-search-outline",
                          title: "没有可审核的删除目标"
                        }))
                      : _createCommentVNode("", true)
                  ]),
                  _: 1
                }),
                _createVNode(_component_VCardActions, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_VSpacer),
                    _createVNode(_component_VBtn, {
                      variant: "text",
                      onClick: _cache[37] || (_cache[37] = $event => (planTargetDialog.value = false))
                    }, {
                      default: _withCtx(() => [...(_cache[105] || (_cache[105] = [
                        _createTextVNode("关闭", -1)
                      ]))]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }))
          : _createCommentVNode("", true)
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_VDialog, {
      modelValue: historyDetailDialog.value,
      "onUpdate:modelValue": _cache[40] || (_cache[40] = $event => ((historyDetailDialog).value = $event)),
      "max-width": "980"
    }, {
      default: _withCtx(() => [
        (selectedHistoryItem.value)
          ? (_openBlock(), _createBlock(_component_VCard, { key: 0 }, {
              default: _withCtx(() => [
                _createVNode(_component_VCardTitle, null, {
                  default: _withCtx(() => [...(_cache[106] || (_cache[106] = [
                    _createTextVNode("清理记录详情", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_VCardText, null, {
                  default: _withCtx(() => [
                    _createElementVNode("div", _hoisted_132, [
                      _createVNode(_component_VChip, {
                        color: selectedHistoryItem.value.status === 'success' ? 'success' : 'error',
                        variant: "tonal",
                        size: "small"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(selectedHistoryItem.value.status === 'success' ? '成功' : '失败'), 1)
                        ]),
                        _: 1
                      }, 8, ["color"]),
                      _createVNode(_component_VChip, {
                        variant: "tonal",
                        size: "small"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode("媒体库文件 " + _toDisplayString(historyDetailStats.value.mediaFiles), 1)
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_VChip, {
                        variant: "tonal",
                        size: "small"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode("刮削文件 " + _toDisplayString(historyDetailStats.value.scrapingFiles), 1)
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_VChip, {
                        variant: "tonal",
                        size: "small"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode("源文件 " + _toDisplayString(historyDetailStats.value.sourceFiles), 1)
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_VChip, {
                        variant: "tonal",
                        size: "small"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode("保种任务 " + _toDisplayString(historyDetailStats.value.seedTasks), 1)
                        ]),
                        _: 1
                      }),
                      (historyDetailStats.value.failedTargets || historyDetailStats.value.failedSeedTasks)
                        ? (_openBlock(), _createBlock(_component_VChip, {
                            key: 0,
                            color: "error",
                            variant: "tonal",
                            size: "small"
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode(" 失败 " + _toDisplayString(historyDetailStats.value.failedTargets + historyDetailStats.value.failedSeedTasks), 1)
                            ]),
                            _: 1
                          }))
                        : _createCommentVNode("", true)
                    ]),
                    _createElementVNode("div", _hoisted_133, _toDisplayString(selectedHistoryItem.value.message), 1),
                    (selectedHistoryItem.value.items?.length)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_134, [
                          _cache[107] || (_cache[107] = _createElementVNode("div", { class: "text-subtitle-2 mb-2" }, "本次媒体", -1)),
                          _createElementVNode("div", _hoisted_135, [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(selectedHistoryItem.value.items, (item) => {
                              return (_openBlock(), _createBlock(_component_VChip, {
                                key: `${item.title}-${item.type}`,
                                size: "small",
                                variant: "tonal"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(item.title) + " · " + _toDisplayString(_unref(formatBytes)(item.size)), 1)
                                ]),
                                _: 2
                              }, 1024))
                            }), 128))
                          ])
                        ]))
                      : _createCommentVNode("", true),
                    _cache[109] || (_cache[109] = _createElementVNode("div", { class: "text-subtitle-2 mb-2" }, "删除文件", -1)),
                    _createVNode(_component_VDataTable, {
                      headers: [
              { title: '媒体', key: 'media_title', width: 180 },
              { title: '类型', key: 'kind_label', width: 120 },
              { title: '大小', key: 'size', width: 110 },
              { title: '路径', key: 'path_preview' },
            ],
                      items: selectedHistoryItem.value.deleted_targets || [],
                      density: "compact"
                    }, {
                      "item.media_title": _withCtx(({ item }) => [
                        _createTextVNode(_toDisplayString(item.media_title || '-'), 1)
                      ]),
                      "item.size": _withCtx(({ item }) => [
                        _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                      ]),
                      "item.kind_label": _withCtx(({ item }) => [
                        _createVNode(_component_VChip, {
                          color: item.kind === 'src' ? 'error' : item.kind === 'dest_scraping' ? 'info' : 'primary',
                          variant: "tonal",
                          size: "small"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(item.kind_label || item.kind), 1)
                          ]),
                          _: 2
                        }, 1032, ["color"])
                      ]),
                      "no-data": _withCtx(() => [
                        _createVNode(_component_VEmptyState, {
                          icon: "mdi-file-remove-outline",
                          title: "没有删除文件明细"
                        })
                      ]),
                      _: 1
                    }, 8, ["items"]),
                    _cache[110] || (_cache[110] = _createElementVNode("div", { class: "text-subtitle-2 mt-5 mb-2" }, "保种任务", -1)),
                    _createVNode(_component_VDataTable, {
                      headers: [
              { title: '标题', key: 'title', width: 220 },
              { title: '下载器', key: 'downloader', width: 140 },
              { title: '结果', key: 'result', width: 110 },
            ],
                      items: historySeedRows.value,
                      density: "compact"
                    }, {
                      "item.downloader": _withCtx(({ item }) => [
                        _createElementVNode("div", null, _toDisplayString(item.downloader || '-'), 1),
                        (item.original_downloader && item.original_downloader !== item.downloader)
                          ? (_openBlock(), _createElementBlock("div", _hoisted_136, " 原 " + _toDisplayString(item.original_downloader), 1))
                          : _createCommentVNode("", true)
                      ]),
                      "item.title": _withCtx(({ item }) => [
                        _createTextVNode(_toDisplayString(downloadTaskTitle(item)), 1)
                      ]),
                      "item.result": _withCtx(({ item }) => [
                        _createVNode(_component_VChip, {
                          color: item.result === 'success' ? 'success' : 'error',
                          variant: "tonal",
                          size: "small"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(item.result === 'success' ? '已删除' : (item.error || '失败')), 1)
                          ]),
                          _: 2
                        }, 1032, ["color"])
                      ]),
                      "no-data": _withCtx(() => [
                        _createVNode(_component_VEmptyState, {
                          icon: "mdi-download-off-outline",
                          title: "没有保种任务明细"
                        })
                      ]),
                      _: 1
                    }, 8, ["items"]),
                    (selectedHistoryItem.value.failed_targets?.length)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_137, [
                          _cache[108] || (_cache[108] = _createElementVNode("div", { class: "text-subtitle-2 mb-2" }, "失败项", -1)),
                          _createVNode(_component_VDataTable, {
                            headers: [
                { title: '类型', key: 'kind_label', width: 120 },
                { title: '路径', key: 'path_preview' },
                { title: '错误', key: 'error' },
              ],
                            items: selectedHistoryItem.value.failed_targets,
                            density: "compact"
                          }, null, 8, ["items"])
                        ]))
                      : _createCommentVNode("", true)
                  ]),
                  _: 1
                }),
                _createVNode(_component_VCardActions, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_VSpacer),
                    _createVNode(_component_VBtn, {
                      variant: "text",
                      onClick: _cache[39] || (_cache[39] = $event => (historyDetailDialog.value = false))
                    }, {
                      default: _withCtx(() => [...(_cache[111] || (_cache[111] = [
                        _createTextVNode("关闭", -1)
                      ]))]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }))
          : _createCommentVNode("", true)
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_VDialog, {
      modelValue: executeDialog.value,
      "onUpdate:modelValue": _cache[43] || (_cache[43] = $event => ((executeDialog).value = $event)),
      "max-width": "640"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VCard, null, {
          default: _withCtx(() => [
            _createVNode(_component_VCardTitle, null, {
              default: _withCtx(() => [...(_cache[112] || (_cache[112] = [
                _createTextVNode("确认执行清理计划", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VCardText, null, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_138, " 本次计划将删除 " + _toDisplayString(pendingPlan.value?.ready_count || 0) + " 个可执行媒体条目关联文件，预计释放 " + _toDisplayString(_unref(formatBytes)(pendingPlan.value?.estimated_reclaim_size)) + "。执行成功后会删除对应整理记录。 ", 1),
                (pendingPlan.value && (pendingPlan.value.ready_count || 0) < pendingPlanItems.value.length)
                  ? (_openBlock(), _createBlock(_component_VAlert, {
                      key: 0,
                      type: "info",
                      variant: "tonal",
                      density: "comfortable",
                      class: "mt-4"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(" 批次中还有 " + _toDisplayString(pendingPlanItems.value.length - (pendingPlan.value.ready_count || 0)) + " 个不可执行条目，本次不会执行这些条目。 ", 1)
                      ]),
                      _: 1
                    }))
                  : _createCommentVNode("", true),
                _createVNode(_component_VAlert, {
                  type: "warning",
                  variant: "tonal",
                  density: "comfortable",
                  class: "mt-4"
                }, {
                  default: _withCtx(() => [...(_cache[113] || (_cache[113] = [
                    _createTextVNode(" 这是不可逆操作；请确认媒体库文件和源文件范围都符合预期。 ", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_VCheckbox, {
                  modelValue: executeConfirmed.value,
                  "onUpdate:modelValue": _cache[41] || (_cache[41] = $event => ((executeConfirmed).value = $event)),
                  color: "error",
                  label: "我已确认删除范围，允许执行清理",
                  "hide-details": "",
                  class: "mt-2"
                }, null, 8, ["modelValue"])
              ]),
              _: 1
            }),
            _createVNode(_component_VCardActions, null, {
              default: _withCtx(() => [
                _createVNode(_component_VSpacer),
                _createVNode(_component_VBtn, {
                  variant: "text",
                  onClick: _cache[42] || (_cache[42] = $event => (executeDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[114] || (_cache[114] = [
                    _createTextVNode("取消", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_VBtn, {
                  color: "error",
                  variant: "flat",
                  loading: executing.value,
                  disabled: !executeConfirmed.value,
                  onClick: executePlan
                }, {
                  default: _withCtx(() => [...(_cache[115] || (_cache[115] = [
                    _createTextVNode(" 确认删除 ", -1)
                  ]))]),
                  _: 1
                }, 8, ["loading", "disabled"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_VDialog, {
      modelValue: deletePlanDialog.value,
      "onUpdate:modelValue": _cache[46] || (_cache[46] = $event => ((deletePlanDialog).value = $event)),
      "max-width": "560"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VCard, null, {
          default: _withCtx(() => [
            _createVNode(_component_VCardTitle, null, {
              default: _withCtx(() => [...(_cache[116] || (_cache[116] = [
                _createTextVNode("删除当前清理批次", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VCardText, null, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_139, " 将删除批次 " + _toDisplayString(pendingPlan.value?.batch_id || pendingPlan.value?.id) + " 的待处理记录，不会删除媒体文件、源文件或整理记录。 ", 1),
                _createVNode(_component_VCheckbox, {
                  modelValue: deletePlanConfirmed.value,
                  "onUpdate:modelValue": _cache[44] || (_cache[44] = $event => ((deletePlanConfirmed).value = $event)),
                  color: "error",
                  label: "我确认只删除当前批次记录",
                  "hide-details": "",
                  class: "mt-4"
                }, null, 8, ["modelValue"])
              ]),
              _: 1
            }),
            _createVNode(_component_VCardActions, null, {
              default: _withCtx(() => [
                _createVNode(_component_VSpacer),
                _createVNode(_component_VBtn, {
                  variant: "text",
                  onClick: _cache[45] || (_cache[45] = $event => (deletePlanDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[117] || (_cache[117] = [
                    _createTextVNode("取消", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_VBtn, {
                  color: "error",
                  variant: "flat",
                  loading: deletingPlan.value,
                  disabled: !deletePlanConfirmed.value,
                  onClick: deletePlan
                }, {
                  default: _withCtx(() => [...(_cache[118] || (_cache[118] = [
                    _createTextVNode(" 删除批次 ", -1)
                  ]))]),
                  _: 1
                }, 8, ["loading", "disabled"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_VSnackbar, {
      modelValue: fallbackToast.value.show,
      "onUpdate:modelValue": _cache[47] || (_cache[47] = $event => ((fallbackToast.value.show) = $event)),
      color: fallbackToast.value.color,
      location: "bottom right",
      timeout: "3200"
    }, {
      default: _withCtx(() => [
        _createTextVNode(_toDisplayString(fallbackToast.value.text), 1)
      ]),
      _: 1
    }, 8, ["modelValue", "color"])
  ]))
}
}

};
const AppPage = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-d8763310"]]);

export { AppPage as default };
