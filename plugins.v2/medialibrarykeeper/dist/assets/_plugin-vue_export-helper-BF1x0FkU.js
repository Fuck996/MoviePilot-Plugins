function unwrapResponse(response) {
  if (response && Object.prototype.hasOwnProperty.call(response, 'data') && response.success !== undefined) {
    return response.data
  }
  return response?.data ?? response
}

function createDefaultCleanupRule() {
  return {
    id: `rule-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    operator: 'and',
    watch_state: 'any',
    unwatched_days: 0,
    min_size_gb: 0,
    max_rating: 0,
  }
}

function createDefaultConfig() {
  return {
    enabled: false,
    show_sidebar_nav: true,
    notify_enabled: true,
    disk_warning_enabled: true,
    disk_warning_free_gb: 200,
    disk_warning_free_percent: 10,
    scan_cron: '0 */6 * * *',
    ai_suggestions: false,
    default_delete_source: false,
    mediaservers: [],
    downloaders: [],
    path_mappings: [],
    downloader_path_mappings: [],
    delete_seed_tasks: false,
    library_names: [],
    cleanup_libraries: [],
    cleanup_rules: [createDefaultCleanupRule()],
    cleanup_operator: 'and',
    cleanup_watch_state: 'any',
    cleanup_unwatched_days: 0,
    cleanup_watched: false,
    cleanup_min_size_gb: 0,
    cleanup_max_rating: 0,
  }
}

function statusCacheKey(pluginId = 'MediaLibraryKeeper') {
  return `medialibrarykeeper:${pluginId || 'MediaLibraryKeeper'}:status:v2`
}

function readStatusCache(pluginId) {
  if (typeof localStorage === 'undefined') return null
  try {
    const cached = JSON.parse(localStorage.getItem(statusCacheKey(pluginId)) || 'null');
    return cached?.status || null
  } catch {
    return null
  }
}

function writeStatusCache(pluginId, status) {
  if (typeof localStorage === 'undefined' || !status) return
  const key = statusCacheKey(pluginId);
  try {
    localStorage.setItem(key, JSON.stringify(createCachePayload(status)));
  } catch {
    try {
      localStorage.removeItem(key);
      localStorage.setItem(key, JSON.stringify(createCachePayload(compactStatus(status))));
    } catch {
      localStorage.removeItem(key);
    }
  }
}

function createCachePayload(status) {
  return {
    cached_at: new Date().toISOString(),
    status,
  }
}

function compactStatus(status) {
  return {
    ...status,
    media: (status.media || []).map(compactMediaItem),
    recommendations: (status.recommendations || []).map(compactMediaItem),
    pending_plan: compactPlan(status.pending_plan),
    cleanup_queue: (status.cleanup_queue || []).map(compactQueueItem),
    history: (status.history || []).slice(0, 20).map(compactHistoryItem),
  }
}

function compactMediaItem(item) {
  return pickFields(item, [
    'id',
    'server',
    'server_type',
    'item_id',
    'title',
    'type',
    'type_label',
    'year',
    'library',
    'library_id',
    'library_item_id',
    'library_type',
    'path_preview',
    'emby_path_preview',
    'rating',
    'image_url',
    'genres',
    'premiere_date',
    'added_at',
    'last_episode_added_at',
    'last_watched_at',
    'watched',
    'watch_state',
    'progress',
    'watched_episodes',
    'total_episodes',
    'size',
    'reason',
    'message',
    'volume_name',
    'volume_free_percent',
    'volume_summary',
    'volumes',
  ])
}

function compactPlan(plan) {
  if (!plan) return plan
  return {
    ...plan,
    items: (plan.items || []).map(item => ({
      ...pickFields(item, [
        'media_id',
        'title',
        'type',
        'type_label',
        'watched',
        'watch_state',
        'size',
        'library',
        'rating',
        'progress',
        'last_episode_added_at',
        'last_watched_at',
        'status',
        'message',
      ]),
      delete_targets: (item.delete_targets || []).map(compactDeleteTarget),
      seed_candidates: (item.seed_candidates || []).map(compactSeedCandidate),
    })),
  }
}

function compactSeedCandidate(candidate) {
  return pickFields(candidate, [
    'title',
    'media_id',
    'downloader',
    'source_path',
    'downloader_path',
    'reason',
    'status',
  ])
}

function compactDeleteTarget(target) {
  return pickFields(target, [
    'record_id',
    'kind',
    'kind_label',
    'path',
    'path_preview',
    'size',
    'match_source',
    'media_id',
    'media_title',
    'media_type',
    'media_type_label',
    'parent_media_path',
    'directory_mapping',
  ])
}

function compactHistoryItem(item) {
  const compacted = pickFields(item, [
    'plan_id',
    'queue_id',
    'created_at',
    'queued_at',
    'started_at',
    'status',
    'delete_source',
    'reclaim_size',
    'deleted_records',
    'deleted_media_files',
    'deleted_scraping_files',
    'deleted_source_files',
    'message',
  ]);
  compacted.items = (item.items || []).map(entry => pickFields(entry, ['title', 'type', 'size']));
  compacted.deleted_targets = (item.deleted_targets || []).map(compactDeleteTarget);
  compacted.failed_targets = (item.failed_targets || []).map(compactFailedTarget);
  compacted.deleted_seed_tasks = (item.deleted_seed_tasks || []).map(compactSeedTask);
  compacted.failed_seed_tasks = (item.failed_seed_tasks || []).map(compactSeedTask);
  return compacted
}

function compactQueueItem(item) {
  return pickFields(item, [
    'id',
    'plan_id',
    'batch_id',
    'created_at',
    'started_at',
    'status',
    'message',
    'item_count',
    'ready_count',
    'estimated_reclaim_size',
    'delete_source',
  ])
}

function compactFailedTarget(target) {
  return {
    ...compactDeleteTarget(target),
    error: target?.error,
  }
}

function compactSeedTask(task) {
  return pickFields(task, [
    'record_id',
    'title',
    'downloader',
    'original_downloader',
    'downloader_type',
    'download_hash',
    'source',
    'error',
  ])
}

function pickFields(source, fields) {
  return fields.reduce((result, field) => {
    if (source && source[field] !== undefined) {
      result[field] = source[field];
    }
    return result
  }, {})
}

function cloneConfig(config) {
  const cloned = JSON.parse(JSON.stringify({ ...createDefaultConfig(), ...(config || {}) }));
  cloned.library_names = [];
  cloned.path_mappings = normalizePathMappings(config?.path_mappings ?? cloned.path_mappings);
  cloned.downloader_path_mappings = normalizeDownloaderPathMappings(config?.downloader_path_mappings ?? cloned.downloader_path_mappings);
  cloned.cleanup_rules = normalizeCleanupRules(config || {}, cloned);
  const firstRule = cloned.cleanup_rules[0] || createDefaultCleanupRule();
  cloned.cleanup_operator = firstRule.operator;
  cloned.cleanup_watch_state = firstRule.watch_state;
  cloned.cleanup_unwatched_days = firstRule.unwatched_days;
  cloned.cleanup_min_size_gb = firstRule.min_size_gb;
  cloned.cleanup_max_rating = firstRule.max_rating;
  cloned.cleanup_watched = firstRule.watch_state === 'watched';
  return cloned
}

function normalizePathMappings(mappings) {
  if (!Array.isArray(mappings)) return []
  return mappings
    .map(mapping => ({
      emby_path: normalizePathText(mapping?.emby_path),
      mp_path: normalizePathText(mapping?.mp_path),
    }))
    .filter(mapping => mapping.emby_path && mapping.mp_path)
}

function normalizeDownloaderPathMappings(mappings) {
  if (!Array.isArray(mappings)) return []
  return mappings
    .map(mapping => ({
      downloader: String(mapping?.downloader || '').trim(),
      downloader_path: normalizePathText(mapping?.downloader_path),
      resource_path: normalizePathText(mapping?.resource_path),
    }))
    .filter(mapping => mapping.downloader && mapping.downloader_path && mapping.resource_path)
}

function normalizePathText(path) {
  return String(path || '').trim().replace(/\\/g, '/').replace(/\/+$/, '')
}

function normalizeCleanupRules(sourceConfig, mergedConfig) {
  const rawRules = Array.isArray(sourceConfig.cleanup_rules) ? sourceConfig.cleanup_rules : [];
  const rules = rawRules.length
    ? rawRules
    : [{
        operator: mergedConfig.cleanup_operator,
        watch_state: sourceConfig.cleanup_watch_state ?? (mergedConfig.cleanup_watched ? 'watched' : mergedConfig.cleanup_watch_state),
        watched: mergedConfig.cleanup_watched,
        unwatched_days: mergedConfig.cleanup_unwatched_days,
        min_size_gb: mergedConfig.cleanup_min_size_gb,
        max_rating: mergedConfig.cleanup_max_rating,
      }];
  return rules.map(normalizeCleanupRule)
}

function normalizeCleanupRule(rule) {
  const normalized = { ...createDefaultCleanupRule(), ...(rule || {}) };
  if (!['and', 'or'].includes(normalized.operator)) {
    normalized.operator = 'and';
  }
  if (!['any', 'watched', 'unwatched'].includes(normalized.watch_state)) {
    normalized.watch_state = normalized.watched ? 'watched' : 'any';
  }
  normalized.unwatched_days = Math.max(Number(normalized.unwatched_days || 0), 0);
  normalized.min_size_gb = Math.max(Number(normalized.min_size_gb || 0), 0);
  normalized.max_rating = Math.max(Number(normalized.max_rating || 0), 0);
  return normalized
}

function toEditableConfig(config) {
  const cloned = cloneConfig(config);
  return cloned
}

function toPayloadConfig(config) {
  const cloned = cloneConfig(config);
  cloned.cleanup_watched = cloned.cleanup_watch_state === 'watched';
  cloned.library_names = [];
  return cloned
}

function formatNumber(value) {
  const numberValue = Number(value || 0);
  return Number.isFinite(numberValue) ? numberValue.toLocaleString('zh-CN') : '0'
}

function formatBytes(value) {
  const size = Number(value || 0);
  if (!Number.isFinite(size) || size <= 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];
  let index = 0;
  let nextSize = size;
  while (nextSize >= 1024 && index < units.length - 1) {
    nextSize /= 1024;
    index += 1;
  }
  return `${nextSize.toFixed(nextSize >= 10 || index === 0 ? 0 : 1)} ${units[index]}`
}

function planItemFromMedia(item) {
  return {
    id: item.id,
    title: item.title,
    type: item.type,
    watched: item.watched,
    size: item.size,
  }
}

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

export { _export_sfc as _, toPayloadConfig as a, formatBytes as b, createDefaultConfig as c, createDefaultCleanupRule as d, formatNumber as f, planItemFromMedia as p, readStatusCache as r, toEditableConfig as t, unwrapResponse as u, writeStatusCache as w };
