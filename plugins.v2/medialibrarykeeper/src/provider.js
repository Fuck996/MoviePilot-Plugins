export function unwrapResponse(response) {
  if (response && Object.prototype.hasOwnProperty.call(response, 'data') && response.success !== undefined) {
    return response.data
  }
  return response?.data ?? response
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
    library_names: [],
    cleanup_libraries: [],
    cleanup_operator: 'and',
    cleanup_unwatched_days: 0,
    cleanup_watched: false,
    cleanup_min_size_gb: 0,
    cleanup_max_rating: 0,
  }
}

export function cloneConfig(config) {
  return JSON.parse(JSON.stringify({ ...createDefaultConfig(), ...(config || {}) }))
}

export function toEditableConfig(config) {
  const cloned = cloneConfig(config)
  for (const key of ['library_names']) {
    if (Array.isArray(cloned[key])) {
      cloned[key] = cloned[key].join('\n')
    }
  }
  return cloned
}

export function toPayloadConfig(config) {
  const cloned = cloneConfig(config)
  for (const key of ['library_names']) {
    if (typeof cloned[key] === 'string') {
      cloned[key] = cloned[key]
        .split('\n')
        .map(item => item.trim())
        .filter(Boolean)
    }
  }
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
