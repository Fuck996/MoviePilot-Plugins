import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, t as toEditableConfig, c as createDefaultConfig, p as planItemFromMedia, f as formatNumber, b as formatBytes, u as unwrapResponse, a as toPayloadConfig } from './_plugin-vue_export-helper-BQW8z7Ve.js';

const {createElementVNode:_createElementVNode,resolveComponent:_resolveComponent,createVNode:_createVNode,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,createBlock:_createBlock,toDisplayString:_toDisplayString,renderList:_renderList,Fragment:_Fragment,unref:_unref,withModifiers:_withModifiers} = await importShared('vue');


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
const _hoisted_16 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_17 = { class: "mlk-section" };
const _hoisted_18 = { class: "mlk-toolbar" };
const _hoisted_19 = { class: "mlk-filter-row" };
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
const _hoisted_24 = { class: "mlk-media-title" };
const _hoisted_25 = { class: "text-caption text-medium-emphasis" };
const _hoisted_26 = { class: "mlk-chip-row" };
const _hoisted_27 = { class: "mlk-section" };
const _hoisted_28 = {
  key: 0,
  class: "mlk-media-grid"
};
const _hoisted_29 = { class: "mlk-poster" };
const _hoisted_30 = {
  key: 1,
  class: "mlk-poster-fallback"
};
const _hoisted_31 = { class: "mlk-media-body" };
const _hoisted_32 = { class: "mlk-media-title" };
const _hoisted_33 = { class: "text-caption text-medium-emphasis" };
const _hoisted_34 = { class: "text-caption text-medium-emphasis" };
const _hoisted_35 = { class: "mlk-chip-row" };
const _hoisted_36 = { class: "mlk-section" };
const _hoisted_37 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_38 = { class: "mlk-plan-title" };
const _hoisted_39 = { class: "text-subtitle-1 font-weight-medium" };
const _hoisted_40 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_41 = { class: "mlk-danger-actions" };
const _hoisted_42 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_43 = { class: "mlk-section" };
const _hoisted_44 = { class: "mlk-section mlk-settings" };
const _hoisted_45 = { class: "mlk-switch-grid" };
const _hoisted_46 = { class: "mlk-form-grid" };
const _hoisted_47 = { class: "mlk-switch-grid" };
const _hoisted_48 = { class: "mlk-detail-layout" };
const _hoisted_49 = { class: "mlk-detail-poster" };
const _hoisted_50 = {
  key: 1,
  class: "mlk-poster-fallback"
};
const _hoisted_51 = { class: "mlk-detail-content" };
const _hoisted_52 = { class: "mlk-detail-head" };
const _hoisted_53 = { class: "text-h6 font-weight-bold" };
const _hoisted_54 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_55 = { class: "mlk-chip-row" };
const _hoisted_56 = { class: "mlk-overview" };
const _hoisted_57 = { class: "mlk-detail-grid" };
const _hoisted_58 = { class: "mlk-detail-wide" };
const _hoisted_59 = {
  key: 0,
  class: "mlk-detail-wide"
};
const _hoisted_60 = { class: "mlk-chip-row" };
const _hoisted_61 = { class: "mlk-detail-actions" };
const _hoisted_62 = { class: "text-body-2" };

const {computed,onMounted,ref} = await importShared('vue');


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
const planning = ref(false);
const scanning = ref(false);
const executing = ref(false);
const error = ref('');
const notice = ref('');
const activeTab = ref('overview');
const selectedMedia = ref([]);
const selectedLibraryId = ref('');
const selectedMediaDetail = ref(null);
const detailDialog = ref(false);
const deleteSource = ref(false);
const searchText = ref('');
const watchFilter = ref('全部');
const typeFilter = ref('全部');
const executeDialog = ref(false);
const executeConfirmed = ref(false);
const configDraft = ref(toEditableConfig());
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
});

const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`);
const summary = computed(() => status.value.summary || {});
const libraries = computed(() => status.value.libraries || []);
const mediaRows = computed(() => status.value.media || []);
const recommendationRows = computed(() => status.value.recommendations || []);
const pendingPlan = computed(() => status.value.pending_plan);
const historyRows = computed(() => status.value.history || []);
const capabilities = computed(() => status.value.capabilities || {});
const mediaServerOptions = computed(() => status.value.media_server_options || []);
const selectedPlanItems = computed(() => selectedMedia.value.map(planItemFromMedia));
const selectedSize = computed(() => selectedMedia.value.reduce((sum, item) => sum + Number(item.size || 0), 0));
const planReady = computed(() => pendingPlan.value?.status === 'ready');
const selectedLibrary = computed(() => libraries.value.find(item => item.id === selectedLibraryId.value));

const filteredMediaRows = computed(() => {
  const keyword = searchText.value.trim().toLowerCase();
  return mediaRows.value.filter((item) => {
    if (selectedLibraryId.value && item.library_id !== selectedLibraryId.value) return false
    if (keyword) {
      const haystack = `${item.title || ''}${item.overview || ''}${item.path_preview || ''}`.toLowerCase();
      if (!haystack.includes(keyword)) return false
    }
    if (typeFilter.value === '电影' && item.type !== 'movie') return false
    if (typeFilter.value === '剧集' && item.type !== 'series') return false
    if (watchFilter.value === '已看完' && !item.watched) return false
    if (watchFilter.value === '未看完' && item.watched) return false
    return true
  })
});

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
  { label: '预计可释放', value: formatBytes(summary.value.estimated_reclaim_size), icon: 'mdi-harddisk-remove', color: 'warning' },
]);

const capabilityLabels = {
  emby_scan: 'Emby 扫描',
  transfer_history_match: '整理记录匹配',
  storage_delete: '文件删除',
  ai_suggestions: 'AI 建议',
  notification: '通知推送',
};

const planHeaders = [
  { title: '媒体', key: 'title' },
  { title: '状态', key: 'status', width: 110 },
  { title: '预计释放', key: 'size', width: 120 },
  { title: '删除目标', key: 'target_count', width: 110 },
  { title: '说明', key: 'message' },
];

function isSelected(item) {
  return selectedMedia.value.some(selected => selected.id === item.id)
}

function toggleSelected(item) {
  if (isSelected(item)) {
    selectedMedia.value = selectedMedia.value.filter(selected => selected.id !== item.id);
    return
  }
  selectedMedia.value = [...selectedMedia.value, item];
}

function openLibrary(library) {
  selectedLibraryId.value = library?.id || '';
  activeTab.value = 'library';
}

function clearLibraryFilter() {
  selectedLibraryId.value = '';
}

function openMediaDetail(item) {
  selectedMediaDetail.value = item;
  detailDialog.value = true;
}

async function createSinglePlan(item) {
  selectedMedia.value = [item];
  detailDialog.value = false;
  await createPlan();
}

async function loadStatus() {
  loading.value = true;
  error.value = '';
  try {
    const response = await props.api.get(`${pluginBase.value}/status`);
    applyStatus(unwrapResponse(response));
  } catch (err) {
    error.value = err?.message || '加载媒体库管家状态失败';
  } finally {
    loading.value = false;
  }
}

function applyStatus(data) {
  if (!data) return
  status.value = data;
  configDraft.value = toEditableConfig(status.value.config);
  deleteSource.value = Boolean(configDraft.value.default_delete_source);
}

async function saveConfig() {
  saving.value = true;
  error.value = '';
  notice.value = '';
  try {
    const response = await props.api.post(`${pluginBase.value}/config`, toPayloadConfig(configDraft.value));
    applyStatus(unwrapResponse(response));
    notice.value = '设置已保存';
  } catch (err) {
    error.value = err?.message || '保存设置失败';
  } finally {
    saving.value = false;
  }
}

async function scanLibrary() {
  scanning.value = true;
  error.value = '';
  notice.value = '';
  try {
    const response = await props.api.post(`${pluginBase.value}/scan`, {});
    if (response?.success === false) {
      error.value = response.message || '扫描媒体库失败';
      return
    }
    applyStatus(unwrapResponse(response));
    notice.value = '媒体库扫描完成';
    activeTab.value = 'overview';
  } catch (err) {
    error.value = err?.message || '扫描媒体库失败';
  } finally {
    scanning.value = false;
  }
}

async function createPlan() {
  planning.value = true;
  error.value = '';
  notice.value = '';
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan`, {
      item_ids: selectedMedia.value.map(item => item.id),
      items: selectedPlanItems.value,
      delete_source: deleteSource.value,
    });
    if (response?.success === false) {
      error.value = response.message || '生成清理计划失败';
      return
    }
    const data = unwrapResponse(response);
    applyStatus(data?.status);
    notice.value = '清理计划已生成';
    activeTab.value = 'plan';
  } catch (err) {
    error.value = err?.message || '生成清理计划失败';
  } finally {
    planning.value = false;
  }
}

function openExecuteDialog() {
  executeConfirmed.value = false;
  executeDialog.value = true;
}

async function executePlan() {
  if (!pendingPlan.value?.id || !executeConfirmed.value) return
  executing.value = true;
  error.value = '';
  notice.value = '';
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/execute`, {
      plan_id: pendingPlan.value.id,
      confirm: true,
    });
    if (response?.success === false) {
      error.value = response.message || '执行清理计划失败';
      return
    }
    applyStatus(unwrapResponse(response));
    notice.value = '清理计划已执行';
    executeDialog.value = false;
    selectedMedia.value = [];
  } catch (err) {
    error.value = err?.message || '执行清理计划失败';
  } finally {
    executing.value = false;
  }
}

__expose({
  loadStatus,
  saveConfig,
  scanLibrary,
  loading,
  saving,
  scanning,
});

onMounted(loadStatus);

return (_ctx, _cache) => {
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VProgressLinear = _resolveComponent("VProgressLinear");
  const _component_VAlert = _resolveComponent("VAlert");
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VSheet = _resolveComponent("VSheet");
  const _component_VTab = _resolveComponent("VTab");
  const _component_VTabs = _resolveComponent("VTabs");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VImg = _resolveComponent("VImg");
  const _component_VChip = _resolveComponent("VChip");
  const _component_VEmptyState = _resolveComponent("VEmptyState");
  const _component_VWindowItem = _resolveComponent("VWindowItem");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VDataTable = _resolveComponent("VDataTable");
  const _component_VTextarea = _resolveComponent("VTextarea");
  const _component_VWindow = _resolveComponent("VWindow");
  const _component_VCard = _resolveComponent("VCard");
  const _component_VDialog = _resolveComponent("VDialog");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_VCheckbox = _resolveComponent("VCheckbox");
  const _component_VCardText = _resolveComponent("VCardText");
  const _component_VCardActions = _resolveComponent("VCardActions");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    (!__props.hideTitle)
      ? (_openBlock(), _createElementBlock("div", _hoisted_2, [
          _cache[27] || (_cache[27] = _createElementVNode("div", null, [
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
            default: _withCtx(() => [...(_cache[25] || (_cache[25] = [
              _createTextVNode(" 立即扫描媒体库 ", -1)
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
            default: _withCtx(() => [...(_cache[26] || (_cache[26] = [
              _createTextVNode(" 保存设置 ", -1)
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
    (error.value)
      ? (_openBlock(), _createBlock(_component_VAlert, {
          key: 2,
          type: "error",
          variant: "tonal",
          density: "comfortable"
        }, {
          default: _withCtx(() => [
            _createTextVNode(_toDisplayString(error.value), 1)
          ]),
          _: 1
        }))
      : _createCommentVNode("", true),
    (notice.value)
      ? (_openBlock(), _createBlock(_component_VAlert, {
          key: 3,
          type: "success",
          variant: "tonal",
          density: "comfortable"
        }, {
          default: _withCtx(() => [
            _createTextVNode(_toDisplayString(notice.value), 1)
          ]),
          _: 1
        }))
      : _createCommentVNode("", true),
    (summary.value.disk_warning)
      ? (_openBlock(), _createBlock(_component_VAlert, {
          key: 4,
          type: "warning",
          variant: "tonal",
          density: "comfortable"
        }, {
          default: _withCtx(() => [...(_cache[28] || (_cache[28] = [
            _createTextVNode(" 检测到磁盘容量低于阈值，请优先查看清理建议。 ", -1)
          ]))]),
          _: 1
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
              default: _withCtx(() => [...(_cache[29] || (_cache[29] = [
                _createTextVNode("总览", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "library" }, {
              default: _withCtx(() => [...(_cache[30] || (_cache[30] = [
                _createTextVNode("媒体库", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "recommendations" }, {
              default: _withCtx(() => [...(_cache[31] || (_cache[31] = [
                _createTextVNode("清理建议", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "plan" }, {
              default: _withCtx(() => [...(_cache[32] || (_cache[32] = [
                _createTextVNode("清理计划", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "history" }, {
              default: _withCtx(() => [...(_cache[33] || (_cache[33] = [
                _createTextVNode("执行记录", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "settings" }, {
              default: _withCtx(() => [...(_cache[34] || (_cache[34] = [
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
          "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((activeTab).value = $event)),
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
                                    src: library.image_url,
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
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(capabilities.value, (enabled, key) => {
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
                                _createElementVNode("div", _hoisted_15, _toDisplayString(disk.path), 1),
                                _createElementVNode("div", _hoisted_16, "剩余 " + _toDisplayString(_unref(formatBytes)(disk.free)) + " / " + _toDisplayString(disk.free_percent) + "%", 1)
                              ]),
                              _createVNode(_component_VChip, {
                                color: disk.warning ? 'warning' : 'success',
                                variant: "tonal"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(disk.warning ? '容量紧张' : '容量正常'), 1)
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
                _createElementVNode("div", _hoisted_17, [
                  _createElementVNode("div", _hoisted_18, [
                    _createVNode(_component_VTextField, {
                      modelValue: searchText.value,
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((searchText).value = $event)),
                      label: "搜索名称、简介或路径",
                      "prepend-inner-icon": "mdi-magnify",
                      density: "comfortable",
                      "hide-details": "",
                      clearable: ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: watchFilter.value,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((watchFilter).value = $event)),
                      label: "观看状态",
                      items: ['全部', '已看完', '未看完'],
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSelect, {
                      modelValue: typeFilter.value,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((typeFilter).value = $event)),
                      label: "媒体类型",
                      items: ['全部', '电影', '剧集'],
                      density: "comfortable",
                      "hide-details": ""
                    }, null, 8, ["modelValue"])
                  ]),
                  _createElementVNode("div", _hoisted_19, [
                    _createVNode(_component_VChip, {
                      color: !selectedLibraryId.value ? 'primary' : undefined,
                      variant: !selectedLibraryId.value ? 'flat' : 'tonal',
                      onClick: clearLibraryFilter
                    }, {
                      default: _withCtx(() => [...(_cache[35] || (_cache[35] = [
                        _createTextVNode(" 全部媒体库 ", -1)
                      ]))]),
                      _: 1
                    }, 8, ["color", "variant"]),
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(libraryCards.value, (library) => {
                      return (_openBlock(), _createBlock(_component_VChip, {
                        key: library.id,
                        color: selectedLibraryId.value === library.id ? 'primary' : undefined,
                        variant: selectedLibraryId.value === library.id ? 'flat' : 'tonal',
                        onClick: $event => (openLibrary(library))
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(library.title), 1)
                        ]),
                        _: 2
                      }, 1032, ["color", "variant", "onClick"]))
                    }), 128))
                  ]),
                  (selectedLibrary.value)
                    ? (_openBlock(), _createBlock(_component_VAlert, {
                        key: 0,
                        type: "info",
                        variant: "tonal",
                        density: "compact"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(" 当前入口：" + _toDisplayString(selectedLibrary.value.title) + "，共 " + _toDisplayString(filteredMediaRows.value.length) + " 个媒体条目。 ", 1)
                        ]),
                        _: 1
                      }))
                    : _createCommentVNode("", true),
                  (filteredMediaRows.value.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_20, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(filteredMediaRows.value, (item) => {
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
                                      src: item.image_url,
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
                                  onClick: _withModifiers($event => (toggleSelected(item)), ["stop"])
                                }, null, 8, ["icon", "color", "onClick"])
                              ]),
                              _createElementVNode("div", _hoisted_23, [
                                _createElementVNode("div", _hoisted_24, _toDisplayString(item.title), 1),
                                _createElementVNode("div", _hoisted_25, _toDisplayString(item.year || '未知年份') + " · " + _toDisplayString(item.type_label) + " · " + _toDisplayString(item.library || item.server), 1),
                                _createElementVNode("div", _hoisted_26, [
                                  _createVNode(_component_VChip, {
                                    size: "small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(item.rating || '-') + " 分", 1)
                                    ]),
                                    _: 2
                                  }, 1024),
                                  _createVNode(_component_VChip, {
                                    size: "small",
                                    color: item.watched ? 'success' : 'warning',
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(item.progress), 1)
                                    ]),
                                    _: 2
                                  }, 1032, ["color"]),
                                  _createVNode(_component_VChip, {
                                    size: "small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
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
                _createElementVNode("div", _hoisted_27, [
                  (recommendationRows.value.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_28, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(recommendationRows.value, (item) => {
                          return (_openBlock(), _createBlock(_component_VSheet, {
                            key: item.id,
                            border: "",
                            rounded: "",
                            class: "mlk-media-card",
                            onClick: $event => (openMediaDetail(item))
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_29, [
                                (item.image_url)
                                  ? (_openBlock(), _createBlock(_component_VImg, {
                                      key: 0,
                                      src: item.image_url,
                                      cover: ""
                                    }, null, 8, ["src"]))
                                  : (_openBlock(), _createElementBlock("div", _hoisted_30, [
                                      _createVNode(_component_VIcon, {
                                        icon: item.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline',
                                        size: "44"
                                      }, null, 8, ["icon"])
                                    ]))
                              ]),
                              _createElementVNode("div", _hoisted_31, [
                                _createElementVNode("div", _hoisted_32, _toDisplayString(item.title), 1),
                                _createElementVNode("div", _hoisted_33, _toDisplayString(item.reason), 1),
                                _createElementVNode("div", _hoisted_34, _toDisplayString(item.message), 1),
                                _createElementVNode("div", _hoisted_35, [
                                  _createVNode(_component_VChip, {
                                    size: "small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(item.progress), 1)
                                    ]),
                                    _: 2
                                  }, 1024),
                                  _createVNode(_component_VChip, {
                                    size: "small",
                                    variant: "tonal"
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
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
                    : (_openBlock(), _createBlock(_component_VEmptyState, {
                        key: 1,
                        icon: "mdi-lightbulb-on-outline",
                        title: "暂无清理建议",
                        text: "扫描后会列出已看完、入库较久未观看和占用较大的候选。"
                      }))
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "plan" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_36, [
                  _createVNode(_component_VSheet, {
                    border: "",
                    rounded: "",
                    class: "mlk-plan-bar"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", null, [
                        _cache[36] || (_cache[36] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "待生成计划", -1)),
                        _createElementVNode("div", _hoisted_37, " 已选择 " + _toDisplayString(selectedMedia.value.length) + " 项，当前 Emby 可见体积 " + _toDisplayString(_unref(formatBytes)(selectedSize.value)), 1)
                      ]),
                      _createVNode(_component_VSpacer),
                      _createVNode(_component_VSwitch, {
                        modelValue: deleteSource.value,
                        "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((deleteSource).value = $event)),
                        color: "error",
                        "hide-details": "",
                        inset: "",
                        label: "同时删除源文件"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "flat",
                        loading: planning.value,
                        disabled: !selectedMedia.value.length,
                        onClick: createPlan
                      }, {
                        default: _withCtx(() => [...(_cache[37] || (_cache[37] = [
                          _createTextVNode(" 生成清理计划 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading", "disabled"])
                    ]),
                    _: 1
                  }),
                  (pendingPlan.value)
                    ? (_openBlock(), _createBlock(_component_VSheet, {
                        key: 0,
                        border: "",
                        rounded: "",
                        class: "mlk-plan-detail"
                      }, {
                        default: _withCtx(() => [
                          _createElementVNode("div", _hoisted_38, [
                            _createElementVNode("div", null, [
                              _createElementVNode("div", _hoisted_39, "计划 " + _toDisplayString(pendingPlan.value.id), 1),
                              _createElementVNode("div", _hoisted_40, _toDisplayString(pendingPlan.value.message), 1)
                            ]),
                            _createVNode(_component_VChip, {
                              color: planReady.value ? 'success' : 'warning',
                              variant: "tonal"
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode(_toDisplayString(planReady.value ? '可执行' : '需处理'), 1)
                              ]),
                              _: 1
                            }, 8, ["color"])
                          ]),
                          _createVNode(_component_VDataTable, {
                            headers: planHeaders,
                            items: pendingPlan.value.items || [],
                            density: "comfortable"
                          }, {
                            "item.status": _withCtx(({ item }) => [
                              _createVNode(_component_VChip, {
                                color: item.status === 'ready' ? 'success' : 'warning',
                                variant: "tonal",
                                size: "small"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(item.status === 'ready' ? '已匹配' : '未匹配'), 1)
                                ]),
                                _: 2
                              }, 1032, ["color"])
                            ]),
                            "item.size": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                            ]),
                            "item.target_count": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(item.delete_targets?.length || 0), 1)
                            ]),
                            _: 1
                          }, 8, ["items"]),
                          _createElementVNode("div", _hoisted_41, [
                            _createElementVNode("div", _hoisted_42, " 预计释放 " + _toDisplayString(_unref(formatBytes)(pendingPlan.value.estimated_reclaim_size)), 1),
                            _createVNode(_component_VBtn, {
                              color: "error",
                              variant: "tonal",
                              "prepend-icon": "mdi-delete-alert-outline",
                              disabled: !planReady.value,
                              onClick: openExecuteDialog
                            }, {
                              default: _withCtx(() => [...(_cache[38] || (_cache[38] = [
                                _createTextVNode(" 执行清理计划 ", -1)
                              ]))]),
                              _: 1
                            }, 8, ["disabled"])
                          ])
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
                _createElementVNode("div", _hoisted_43, [
                  _createVNode(_component_VDataTable, {
                    headers: [
                { title: '时间', key: 'created_at', width: 168 },
                { title: '结果', key: 'status', width: 110 },
                { title: '释放空间', key: 'reclaim_size', width: 120 },
                { title: '整理记录', key: 'deleted_records', width: 110 },
                { title: '说明', key: 'message' },
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
                _createElementVNode("div", _hoisted_44, [
                  _createElementVNode("div", _hoisted_45, [
                    _createVNode(_component_VSwitch, {
                      modelValue: configDraft.value.enabled,
                      "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((configDraft.value.enabled) = $event)),
                      color: "primary",
                      inset: "",
                      label: "启用插件"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSwitch, {
                      modelValue: configDraft.value.show_sidebar_nav,
                      "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((configDraft.value.show_sidebar_nav) = $event)),
                      color: "primary",
                      inset: "",
                      label: "显示侧边栏入口"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSwitch, {
                      modelValue: configDraft.value.notify_enabled,
                      "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((configDraft.value.notify_enabled) = $event)),
                      color: "primary",
                      inset: "",
                      label: "启用通知"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSwitch, {
                      modelValue: configDraft.value.disk_warning_enabled,
                      "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((configDraft.value.disk_warning_enabled) = $event)),
                      color: "warning",
                      inset: "",
                      label: "启用磁盘容量告警"
                    }, null, 8, ["modelValue"])
                  ]),
                  _createVNode(_component_VSelect, {
                    modelValue: configDraft.value.mediaservers,
                    "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((configDraft.value.mediaservers) = $event)),
                    label: "媒体服务器",
                    items: mediaServerOptions.value,
                    multiple: "",
                    chips: "",
                    clearable: "",
                    hint: "留空表示扫描所有 Emby 媒体服务器。",
                    "persistent-hint": ""
                  }, null, 8, ["modelValue", "items"]),
                  _createElementVNode("div", _hoisted_46, [
                    _createVNode(_component_VTextField, {
                      modelValue: configDraft.value.disk_warning_free_gb,
                      "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((configDraft.value.disk_warning_free_gb) = $event)),
                      modelModifiers: { number: true },
                      type: "number",
                      min: "0",
                      label: "剩余容量阈值 GB"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VTextField, {
                      modelValue: configDraft.value.disk_warning_free_percent,
                      "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((configDraft.value.disk_warning_free_percent) = $event)),
                      modelModifiers: { number: true },
                      type: "number",
                      min: "0",
                      label: "剩余比例阈值 %"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VTextField, {
                      modelValue: configDraft.value.scan_cron,
                      "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((configDraft.value.scan_cron) = $event)),
                      label: "扫描周期 Cron"
                    }, null, 8, ["modelValue"])
                  ]),
                  _createVNode(_component_VTextarea, {
                    modelValue: configDraft.value.library_names,
                    "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((configDraft.value.library_names) = $event)),
                    label: "限定媒体库名称",
                    hint: "每行一个媒体库名称，留空表示全部媒体库。",
                    "persistent-hint": "",
                    "auto-grow": "",
                    rows: "3"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_VAlert, {
                    type: "info",
                    variant: "tonal",
                    density: "comfortable"
                  }, {
                    default: _withCtx(() => [...(_cache[39] || (_cache[39] = [
                      _createTextVNode(" 磁盘容量会跟随 Emby 扫描到的电影文件和剧集分集路径自动识别，支持多个挂载磁盘，无需手动配置路径。 ", -1)
                    ]))]),
                    _: 1
                  }),
                  _createElementVNode("div", _hoisted_47, [
                    _createVNode(_component_VSwitch, {
                      modelValue: configDraft.value.ai_suggestions,
                      "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((configDraft.value.ai_suggestions) = $event)),
                      color: "primary",
                      inset: "",
                      label: "允许 AI 参与清理建议排序",
                      disabled: ""
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VSwitch, {
                      modelValue: configDraft.value.default_delete_source,
                      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((configDraft.value.default_delete_source) = $event)),
                      color: "error",
                      inset: "",
                      label: "默认同时删除源文件"
                    }, null, 8, ["modelValue"])
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
      "onUpdate:modelValue": _cache[21] || (_cache[21] = $event => ((detailDialog).value = $event)),
      "max-width": "920"
    }, {
      default: _withCtx(() => [
        (selectedMediaDetail.value)
          ? (_openBlock(), _createBlock(_component_VCard, { key: 0 }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_48, [
                  _createElementVNode("div", _hoisted_49, [
                    (selectedMediaDetail.value.image_url)
                      ? (_openBlock(), _createBlock(_component_VImg, {
                          key: 0,
                          src: selectedMediaDetail.value.image_url,
                          cover: ""
                        }, null, 8, ["src"]))
                      : (_openBlock(), _createElementBlock("div", _hoisted_50, [
                          _createVNode(_component_VIcon, {
                            icon: selectedMediaDetail.value.type === 'series' ? 'mdi-television-classic' : 'mdi-movie-open-outline',
                            size: "54"
                          }, null, 8, ["icon"])
                        ]))
                  ]),
                  _createElementVNode("div", _hoisted_51, [
                    _createElementVNode("div", _hoisted_52, [
                      _createElementVNode("div", null, [
                        _createElementVNode("div", _hoisted_53, _toDisplayString(selectedMediaDetail.value.title), 1),
                        _createElementVNode("div", _hoisted_54, _toDisplayString(selectedMediaDetail.value.year || '未知年份') + " · " + _toDisplayString(selectedMediaDetail.value.type_label) + " · " + _toDisplayString(selectedMediaDetail.value.library || selectedMediaDetail.value.server), 1)
                      ]),
                      _createVNode(_component_VBtn, {
                        icon: "mdi-close",
                        variant: "text",
                        onClick: _cache[17] || (_cache[17] = $event => (detailDialog.value = false))
                      })
                    ]),
                    _createElementVNode("div", _hoisted_55, [
                      _createVNode(_component_VChip, {
                        color: "primary",
                        variant: "tonal"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(selectedMediaDetail.value.rating || '-') + " 分", 1)
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_VChip, {
                        color: selectedMediaDetail.value.watched ? 'success' : 'warning',
                        variant: "tonal"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(selectedMediaDetail.value.progress), 1)
                        ]),
                        _: 1
                      }, 8, ["color"]),
                      _createVNode(_component_VChip, { variant: "tonal" }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(_unref(formatBytes)(selectedMediaDetail.value.size)), 1)
                        ]),
                        _: 1
                      })
                    ]),
                    _createElementVNode("p", _hoisted_56, _toDisplayString(selectedMediaDetail.value.overview || '暂无简介。'), 1),
                    _createElementVNode("div", _hoisted_57, [
                      _createElementVNode("div", null, [
                        _cache[40] || (_cache[40] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "服务器", -1)),
                        _createElementVNode("div", null, _toDisplayString(selectedMediaDetail.value.server), 1)
                      ]),
                      _createElementVNode("div", null, [
                        _cache[41] || (_cache[41] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "入库时间", -1)),
                        _createElementVNode("div", null, _toDisplayString(selectedMediaDetail.value.added_at || '-'), 1)
                      ]),
                      _createElementVNode("div", null, [
                        _cache[42] || (_cache[42] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "首播/上映", -1)),
                        _createElementVNode("div", null, _toDisplayString(selectedMediaDetail.value.premiere_date || '-'), 1)
                      ]),
                      _createElementVNode("div", null, [
                        _cache[43] || (_cache[43] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "集数", -1)),
                        _createElementVNode("div", null, _toDisplayString(selectedMediaDetail.value.type === 'series' ? `${selectedMediaDetail.value.watched_episodes}/${selectedMediaDetail.value.total_episodes}` : '-'), 1)
                      ]),
                      _createElementVNode("div", _hoisted_58, [
                        _cache[44] || (_cache[44] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "路径", -1)),
                        _createElementVNode("div", null, _toDisplayString(selectedMediaDetail.value.path_preview || selectedMediaDetail.value.path || '-'), 1)
                      ]),
                      (selectedMediaDetail.value.genres?.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_59, [
                            _cache[45] || (_cache[45] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "类型", -1)),
                            _createElementVNode("div", _hoisted_60, [
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
                    _createElementVNode("div", _hoisted_61, [
                      _createVNode(_component_VSwitch, {
                        modelValue: deleteSource.value,
                        "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((deleteSource).value = $event)),
                        color: "error",
                        "hide-details": "",
                        inset: "",
                        label: "同时删除源文件"
                      }, null, 8, ["modelValue"]),
                      _createVNode(_component_VSpacer),
                      _createVNode(_component_VBtn, {
                        variant: "tonal",
                        color: isSelected(selectedMediaDetail.value) ? 'success' : 'primary',
                        onClick: _cache[19] || (_cache[19] = $event => (toggleSelected(selectedMediaDetail.value)))
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(isSelected(selectedMediaDetail.value) ? '移出清理选择' : '加入清理选择'), 1)
                        ]),
                        _: 1
                      }, 8, ["color"]),
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "flat",
                        loading: planning.value,
                        onClick: _cache[20] || (_cache[20] = $event => (createSinglePlan(selectedMediaDetail.value)))
                      }, {
                        default: _withCtx(() => [...(_cache[46] || (_cache[46] = [
                          _createTextVNode(" 为此项生成计划 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
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
      modelValue: executeDialog.value,
      "onUpdate:modelValue": _cache[24] || (_cache[24] = $event => ((executeDialog).value = $event)),
      "max-width": "640"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VCard, null, {
          default: _withCtx(() => [
            _createVNode(_component_VCardTitle, null, {
              default: _withCtx(() => [...(_cache[47] || (_cache[47] = [
                _createTextVNode("确认执行清理计划", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VCardText, null, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_62, " 本次计划将删除 " + _toDisplayString(pendingPlan.value?.items?.length || 0) + " 个媒体条目关联文件，预计释放 " + _toDisplayString(_unref(formatBytes)(pendingPlan.value?.estimated_reclaim_size)) + "。执行成功后会删除对应整理记录。 ", 1),
                _createVNode(_component_VAlert, {
                  type: "warning",
                  variant: "tonal",
                  density: "comfortable",
                  class: "mt-4"
                }, {
                  default: _withCtx(() => [...(_cache[48] || (_cache[48] = [
                    _createTextVNode(" 这是不可逆操作；请确认媒体库文件和源文件范围都符合预期。 ", -1)
                  ]))]),
                  _: 1
                }),
                _createVNode(_component_VCheckbox, {
                  modelValue: executeConfirmed.value,
                  "onUpdate:modelValue": _cache[22] || (_cache[22] = $event => ((executeConfirmed).value = $event)),
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
                  onClick: _cache[23] || (_cache[23] = $event => (executeDialog.value = false))
                }, {
                  default: _withCtx(() => [...(_cache[49] || (_cache[49] = [
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
                  default: _withCtx(() => [...(_cache[50] || (_cache[50] = [
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
    }, 8, ["modelValue"])
  ]))
}
}

};
const AppPage = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-5358887e"]]);

export { AppPage as default };
