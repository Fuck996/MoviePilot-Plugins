export function unwrapResponse(response) {
  if (response && Object.prototype.hasOwnProperty.call(response, 'data') && response.success !== undefined) {
    return response.data
  }
  return response?.data ?? response
}

export function createDefaultCleanupRule() {
  return {
    id: `rule-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    operator: 'and',
    watch_state: 'any',
    unwatched_days: 0,
    min_size_gb: 0,
    max_rating: 0,
  }
}

export function createDefaultConfig() {
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

export function statusCacheKey(pluginId = 'MediaLibraryKeeper') {
  return `medialibrarykeeper:${pluginId || 'MediaLibraryKeeper'}:status:v1`
}

export function readStatusCache(pluginId) {
  if (typeof localStorage === 'undefined') return null
  try {
    const cached = JSON.parse(localStorage.getItem(statusCacheKey(pluginId)) || 'null')
    return cached?.status || null
  } catch {
    return null
  }
}

export function writeStatusCache(pluginId, status) {
  if (typeof localStorage === 'undefined' || !status) return
  localStorage.setItem(statusCacheKey(pluginId), JSON.stringify({
    cached_at: new Date().toISOString(),
    status,
  }))
}

export function cloneConfig(config) {
  const cloned = JSON.parse(JSON.stringify({ ...createDefaultConfig(), ...(config || {}) }))
  cloned.library_names = []
  cloned.cleanup_rules = normalizeCleanupRules(config || {}, cloned)
  const firstRule = cloned.cleanup_rules[0] || createDefaultCleanupRule()
  cloned.cleanup_operator = firstRule.operator
  cloned.cleanup_watch_state = firstRule.watch_state
  cloned.cleanup_unwatched_days = firstRule.unwatched_days
  cloned.cleanup_min_size_gb = firstRule.min_size_gb
  cloned.cleanup_max_rating = firstRule.max_rating
  cloned.cleanup_watched = firstRule.watch_state === 'watched'
  return cloned
}

function normalizeCleanupRules(sourceConfig, mergedConfig) {
  const rawRules = Array.isArray(sourceConfig.cleanup_rules) ? sourceConfig.cleanup_rules : []
  const rules = rawRules.length
    ? rawRules
    : [{
        operator: mergedConfig.cleanup_operator,
        watch_state: sourceConfig.cleanup_watch_state ?? (mergedConfig.cleanup_watched ? 'watched' : mergedConfig.cleanup_watch_state),
        watched: mergedConfig.cleanup_watched,
        unwatched_days: mergedConfig.cleanup_unwatched_days,
        min_size_gb: mergedConfig.cleanup_min_size_gb,
        max_rating: mergedConfig.cleanup_max_rating,
      }]
  return rules.map(normalizeCleanupRule)
}

function normalizeCleanupRule(rule) {
  const normalized = { ...createDefaultCleanupRule(), ...(rule || {}) }
  if (!['and', 'or'].includes(normalized.operator)) {
    normalized.operator = 'and'
  }
  if (!['any', 'watched', 'unwatched'].includes(normalized.watch_state)) {
    normalized.watch_state = normalized.watched ? 'watched' : 'any'
  }
  normalized.unwatched_days = Math.max(Number(normalized.unwatched_days || 0), 0)
  normalized.min_size_gb = Math.max(Number(normalized.min_size_gb || 0), 0)
  normalized.max_rating = Math.max(Number(normalized.max_rating || 0), 0)
  return normalized
}

export function toEditableConfig(config) {
  const cloned = cloneConfig(config)
  return cloned
}

export function toPayloadConfig(config) {
  const cloned = cloneConfig(config)
  cloned.cleanup_watched = cloned.cleanup_watch_state === 'watched'
  cloned.library_names = []
  return cloned
}

export function formatNumber(value) {
  const numberValue = Number(value || 0)
  return Number.isFinite(numberValue) ? numberValue.toLocaleString('zh-CN') : '0'
}

export function formatBytes(value) {
  const size = Number(value || 0)
  if (!Number.isFinite(size) || size <= 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  let index = 0
  let nextSize = size
  while (nextSize >= 1024 && index < units.length - 1) {
    nextSize /= 1024
    index += 1
  }
  return `${nextSize.toFixed(nextSize >= 10 || index === 0 ? 0 : 1)} ${units[index]}`
}

export function planItemFromMedia(item) {
  return {
    id: item.id,
    title: item.title,
    type: item.type,
    watched: item.watched,
    size: item.size,
  }
}
