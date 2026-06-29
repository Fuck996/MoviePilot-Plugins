function unwrapResponse(response) {
  if (response && Object.prototype.hasOwnProperty.call(response, 'data') && response.success !== undefined) {
    return response.data
  }
  return response?.data ?? response
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
    library_names: [],
    storage_paths: [],
  }
}

function cloneConfig(config) {
  return JSON.parse(JSON.stringify({ ...createDefaultConfig(), ...(config || {}) }))
}

function toEditableConfig(config) {
  const cloned = cloneConfig(config);
  for (const key of ['library_names', 'storage_paths']) {
    if (Array.isArray(cloned[key])) {
      cloned[key] = cloned[key].join('\n');
    }
  }
  return cloned
}

function toPayloadConfig(config) {
  const cloned = cloneConfig(config);
  for (const key of ['library_names', 'storage_paths']) {
    if (typeof cloned[key] === 'string') {
      cloned[key] = cloned[key]
        .split('\n')
        .map(item => item.trim())
        .filter(Boolean);
    }
  }
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

export { _export_sfc as _, toPayloadConfig as a, formatBytes as b, createDefaultConfig as c, formatNumber as f, planItemFromMedia as p, toEditableConfig as t, unwrapResponse as u };
