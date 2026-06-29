import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, t as toEditableConfig, p as planItemFromMedia, f as formatNumber, b as formatBytes, u as unwrapResponse, a as toPayloadConfig } from './_plugin-vue_export-helper-DyMs-RuR.js';

const {createElementVNode:_createElementVNode,resolveComponent:_resolveComponent,createVNode:_createVNode,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,toDisplayString:_toDisplayString,createBlock:_createBlock,renderList:_renderList,Fragment:_Fragment,unref:_unref} = await importShared('vue');


const _hoisted_1 = { class: "mlk-page" };
const _hoisted_2 = {
  key: 0,
  class: "mlk-header"
};
const _hoisted_3 = { class: "mlk-stats" };
const _hoisted_4 = { class: "text-caption text-medium-emphasis" };
const _hoisted_5 = { class: "text-h6" };
const _hoisted_6 = { class: "mlk-section" };
const _hoisted_7 = { class: "mlk-capability-grid" };
const _hoisted_8 = { class: "mlk-section" };
const _hoisted_9 = { class: "mlk-toolbar" };
const _hoisted_10 = { class: "mlk-section" };
const _hoisted_11 = { class: "mlk-section" };
const _hoisted_12 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_13 = { class: "mlk-plan-title" };
const _hoisted_14 = { class: "text-subtitle-1 font-weight-medium" };
const _hoisted_15 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_16 = { class: "mlk-danger-actions" };
const _hoisted_17 = { class: "mlk-section" };
const _hoisted_18 = { class: "mlk-section mlk-settings" };
const _hoisted_19 = { class: "mlk-form-grid" };

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
const scaning = ref(false);
const error = ref('');
const notice = ref('');
const activeTab = ref('overview');
const selectedMedia = ref([]);
const deleteSource = ref(false);
const configDraft = ref(toEditableConfig());
const status = ref({
  config: cloneConfig(),
  summary: {},
  media: [],
  recommendations: [],
  pending_plan: null,
  history: [],
  capabilities: {},
});

const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`);
const summary = computed(() => status.value.summary || {});
const mediaRows = computed(() => status.value.media || []);
const recommendationRows = computed(() => status.value.recommendations || []);
const pendingPlan = computed(() => status.value.pending_plan);
const historyRows = computed(() => status.value.history || []);
const capabilities = computed(() => status.value.capabilities || {});
const selectedPlanItems = computed(() => selectedMedia.value.map(planItemFromMedia));
const selectedSize = computed(() => selectedMedia.value.reduce((sum, item) => sum + Number(item.size || 0), 0));

const statCards = computed(() => [
  { label: '媒体库', value: formatNumber(summary.value.libraries), icon: 'mdi-folder-multiple-outline', color: 'primary' },
  { label: '电影', value: formatNumber(summary.value.movies), icon: 'mdi-movie-open-outline', color: 'info' },
  { label: '剧集', value: formatNumber(summary.value.series), icon: 'mdi-television-classic', color: 'success' },
  { label: '预计可释放', value: formatBytes(summary.value.estimated_reclaim_size), icon: 'mdi-harddisk-remove', color: 'warning' },
]);

async function loadStatus() {
  loading.value = true;
  error.value = '';
  try {
    const response = await props.api.get(`${pluginBase.value}/status`);
    const data = unwrapResponse(response);
    status.value = data || status.value;
    configDraft.value = toEditableConfig(status.value.config);
    deleteSource.value = Boolean(configDraft.value.default_delete_source);
  } catch (err) {
    error.value = err?.message || '加载媒体库管家状态失败';
  } finally {
    loading.value = false;
  }
}

async function saveConfig() {
  saving.value = true;
  error.value = '';
  notice.value = '';
  try {
    const response = await props.api.post(`${pluginBase.value}/config`, toPayloadConfig(configDraft.value));
    const data = unwrapResponse(response);
    status.value = data || status.value;
    notice.value = '配置已保存';
  } catch (err) {
    error.value = err?.message || '保存配置失败';
  } finally {
    saving.value = false;
  }
}

async function scanLibrary() {
  scaning.value = true;
  error.value = '';
  notice.value = '';
  try {
    const response = await props.api.post(`${pluginBase.value}/scan`, {});
    if (response?.success === false) {
      error.value = response.message || '媒体库拉取尚未完成';
      return
    }
    status.value = unwrapResponse(response) || status.value;
  } catch (err) {
    error.value = err?.message || '媒体库拉取失败';
  } finally {
    scaning.value = false;
  }
}

async function createPlan() {
  planning.value = true;
  error.value = '';
  notice.value = '';
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/plan`, {
      items: selectedPlanItems.value,
      delete_source: deleteSource.value,
    });
    if (response?.success === false) {
      error.value = response.message || '生成清理计划失败';
      return
    }
    const data = unwrapResponse(response);
    status.value = data?.status || status.value;
    notice.value = '清理计划已生成';
    activeTab.value = 'plan';
  } catch (err) {
    error.value = err?.message || '生成清理计划失败';
  } finally {
    planning.value = false;
  }
}

async function executePlan() {
  if (!pendingPlan.value?.id) return
  error.value = '';
  notice.value = '';
  try {
    const response = await props.api.post(`${pluginBase.value}/cleanup/execute`, { plan_id: pendingPlan.value.id });
    if (response?.success === false) {
      error.value = response.message || '清理执行被阻止';
      return
    }
    status.value = unwrapResponse(response) || status.value;
  } catch (err) {
    error.value = err?.message || '执行清理计划失败';
  }
}

__expose({
  loadStatus,
  saveConfig,
  scanLibrary,
  loading,
  saving,
  scaning,
});

onMounted(loadStatus);

return (_ctx, _cache) => {
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VAlert = _resolveComponent("VAlert");
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VSheet = _resolveComponent("VSheet");
  const _component_VTab = _resolveComponent("VTab");
  const _component_VTabs = _resolveComponent("VTabs");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VEmptyState = _resolveComponent("VEmptyState");
  const _component_VWindowItem = _resolveComponent("VWindowItem");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VDataTable = _resolveComponent("VDataTable");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VChip = _resolveComponent("VChip");
  const _component_VTextarea = _resolveComponent("VTextarea");
  const _component_VWindow = _resolveComponent("VWindow");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    (!__props.hideTitle)
      ? (_openBlock(), _createElementBlock("div", _hoisted_2, [
          _cache[16] || (_cache[16] = _createElementVNode("div", null, [
            _createElementVNode("div", { class: "text-h5 font-weight-bold" }, "媒体库管家"),
            _createElementVNode("div", { class: "text-body-2 text-medium-emphasis" }, "Emby 媒体库整理与空间释放")
          ], -1)),
          _createVNode(_component_VSpacer),
          _createVNode(_component_VBtn, {
            "prepend-icon": "mdi-database-sync-outline",
            variant: "tonal",
            loading: scaning.value,
            onClick: scanLibrary
          }, {
            default: _withCtx(() => [...(_cache[14] || (_cache[14] = [
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
            default: _withCtx(() => [...(_cache[15] || (_cache[15] = [
              _createTextVNode(" 保存设置 ", -1)
            ]))]),
            _: 1
          }, 8, ["loading"])
        ]))
      : _createCommentVNode("", true),
    (error.value)
      ? (_openBlock(), _createBlock(_component_VAlert, {
          key: 1,
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
          key: 2,
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
    _createVNode(_component_VAlert, {
      type: "info",
      variant: "tonal",
      density: "comfortable"
    }, {
      default: _withCtx(() => [...(_cache[17] || (_cache[17] = [
        _createTextVNode(" 当前版本已完成页面和接口合同。Emby 拉取、整理记录匹配、真实删除链路尚未接入，执行清理会被后端阻止。 ", -1)
      ]))]),
      _: 1
    }),
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
              default: _withCtx(() => [...(_cache[18] || (_cache[18] = [
                _createTextVNode("总览", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "library" }, {
              default: _withCtx(() => [...(_cache[19] || (_cache[19] = [
                _createTextVNode("媒体库", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "recommendations" }, {
              default: _withCtx(() => [...(_cache[20] || (_cache[20] = [
                _createTextVNode("清理建议", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "plan" }, {
              default: _withCtx(() => [...(_cache[21] || (_cache[21] = [
                _createTextVNode("清理计划", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "history" }, {
              default: _withCtx(() => [...(_cache[22] || (_cache[22] = [
                _createTextVNode("执行记录", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VTab, { value: "settings" }, {
              default: _withCtx(() => [...(_cache[23] || (_cache[23] = [
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
          "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((activeTab).value = $event)),
          touch: false
        }, {
          default: _withCtx(() => [
            _createVNode(_component_VWindowItem, { value: "overview" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_6, [
                  _createElementVNode("div", _hoisted_7, [
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
                          _createElementVNode("span", null, _toDisplayString(key), 1)
                        ]),
                        _: 2
                      }, 1024))
                    }), 128))
                  ]),
                  _createVNode(_component_VEmptyState, {
                    icon: "mdi-database-search-outline",
                    title: "等待接入媒体库数据",
                    text: "下一阶段会读取 MoviePilot 已配置的 Emby 服务，并在这里展示空间风险与清理候选。"
                  })
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "library" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_8, [
                  _createElementVNode("div", _hoisted_9, [
                    _createVNode(_component_VTextField, {
                      label: "搜索名称",
                      "prepend-inner-icon": "mdi-magnify",
                      density: "comfortable",
                      "hide-details": "",
                      clearable: ""
                    }),
                    _createVNode(_component_VSelect, {
                      label: "观看状态",
                      items: ['全部', '已看完', '未观看', '观看中'],
                      density: "comfortable",
                      "hide-details": ""
                    }),
                    _createVNode(_component_VSelect, {
                      label: "媒体类型",
                      items: ['全部', '电影', '剧集'],
                      density: "comfortable",
                      "hide-details": ""
                    })
                  ]),
                  _createVNode(_component_VDataTable, {
                    modelValue: selectedMedia.value,
                    "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((selectedMedia).value = $event)),
                    headers: [
                { title: '名称', key: 'title' },
                { title: '类型', key: 'type' },
                { title: '进度', key: 'progress' },
                { title: '体积', key: 'size' },
                { title: '入库时间', key: 'added_at' },
              ],
                    items: mediaRows.value,
                    "item-value": "id",
                    "show-select": "",
                    "return-object": "",
                    density: "comfortable",
                    class: "mlk-table"
                  }, {
                    "item.size": _withCtx(({ item }) => [
                      _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                    ]),
                    "no-data": _withCtx(() => [
                      _createVNode(_component_VEmptyState, {
                        icon: "mdi-folder-open-outline",
                        title: "暂无媒体库数据",
                        text: "接入 Emby 扫描后会显示电影、剧集和观看进度。"
                      })
                    ]),
                    _: 1
                  }, 8, ["modelValue", "items"])
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "recommendations" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_10, [
                  _createVNode(_component_VDataTable, {
                    headers: [
                { title: '建议类型', key: 'reason' },
                { title: '媒体', key: 'title' },
                { title: '预计释放', key: 'size' },
                { title: '说明', key: 'message' },
              ],
                    items: recommendationRows.value,
                    density: "comfortable"
                  }, {
                    "item.size": _withCtx(({ item }) => [
                      _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                    ]),
                    "no-data": _withCtx(() => [
                      _createVNode(_component_VEmptyState, {
                        icon: "mdi-lightbulb-on-outline",
                        title: "暂无清理建议",
                        text: "后续会列出已看完、入库最久未观看和体积较大的剧集。"
                      })
                    ]),
                    _: 1
                  }, 8, ["items"])
                ])
              ]),
              _: 1
            }),
            _createVNode(_component_VWindowItem, { value: "plan" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_11, [
                  _createVNode(_component_VSheet, {
                    border: "",
                    rounded: "",
                    class: "mlk-plan-bar"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", null, [
                        _cache[24] || (_cache[24] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-medium" }, "待生成计划", -1)),
                        _createElementVNode("div", _hoisted_12, " 已选择 " + _toDisplayString(selectedMedia.value.length) + " 项，预计 " + _toDisplayString(_unref(formatBytes)(selectedSize.value)), 1)
                      ]),
                      _createVNode(_component_VSpacer),
                      _createVNode(_component_VSwitch, {
                        modelValue: deleteSource.value,
                        "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((deleteSource).value = $event)),
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
                        default: _withCtx(() => [...(_cache[25] || (_cache[25] = [
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
                          _createElementVNode("div", _hoisted_13, [
                            _createElementVNode("div", null, [
                              _createElementVNode("div", _hoisted_14, "计划 " + _toDisplayString(pendingPlan.value.id), 1),
                              _createElementVNode("div", _hoisted_15, _toDisplayString(pendingPlan.value.message), 1)
                            ]),
                            _createVNode(_component_VChip, {
                              color: "warning",
                              variant: "tonal"
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode(_toDisplayString(pendingPlan.value.status), 1)
                              ]),
                              _: 1
                            })
                          ]),
                          _createVNode(_component_VDataTable, {
                            headers: [
                  { title: '媒体', key: 'title' },
                  { title: '匹配状态', key: 'status' },
                  { title: '预计释放', key: 'size' },
                  { title: '说明', key: 'message' },
                ],
                            items: pendingPlan.value.items || [],
                            density: "comfortable"
                          }, {
                            "item.size": _withCtx(({ item }) => [
                              _createTextVNode(_toDisplayString(_unref(formatBytes)(item.size)), 1)
                            ]),
                            _: 1
                          }, 8, ["items"]),
                          _createElementVNode("div", _hoisted_16, [
                            _createVNode(_component_VBtn, {
                              color: "error",
                              variant: "tonal",
                              "prepend-icon": "mdi-delete-alert-outline",
                              onClick: executePlan
                            }, {
                              default: _withCtx(() => [...(_cache[26] || (_cache[26] = [
                                _createTextVNode(" 执行清理计划 ", -1)
                              ]))]),
                              _: 1
                            })
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
                _createElementVNode("div", _hoisted_17, [
                  _createVNode(_component_VDataTable, {
                    headers: [
                { title: '时间', key: 'created_at' },
                { title: '结果', key: 'status' },
                { title: '释放空间', key: 'reclaim_size' },
                { title: '说明', key: 'message' },
              ],
                    items: historyRows.value,
                    density: "comfortable"
                  }, {
                    "item.reclaim_size": _withCtx(({ item }) => [
                      _createTextVNode(_toDisplayString(_unref(formatBytes)(item.reclaim_size)), 1)
                    ]),
                    "no-data": _withCtx(() => [
                      _createVNode(_component_VEmptyState, {
                        icon: "mdi-history",
                        title: "暂无执行记录",
                        text: "真实清理接入后，每次执行结果都会保存在这里。"
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
                _createElementVNode("div", _hoisted_18, [
                  _createVNode(_component_VSwitch, {
                    modelValue: configDraft.value.enabled,
                    "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((configDraft.value.enabled) = $event)),
                    color: "primary",
                    inset: "",
                    label: "启用插件"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_VSwitch, {
                    modelValue: configDraft.value.show_sidebar_nav,
                    "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((configDraft.value.show_sidebar_nav) = $event)),
                    color: "primary",
                    inset: "",
                    label: "显示侧边栏入口"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_VSwitch, {
                    modelValue: configDraft.value.notify_enabled,
                    "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((configDraft.value.notify_enabled) = $event)),
                    color: "primary",
                    inset: "",
                    label: "启用通知"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_VSwitch, {
                    modelValue: configDraft.value.disk_warning_enabled,
                    "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((configDraft.value.disk_warning_enabled) = $event)),
                    color: "warning",
                    inset: "",
                    label: "启用磁盘容量告警"
                  }, null, 8, ["modelValue"]),
                  _createElementVNode("div", _hoisted_19, [
                    _createVNode(_component_VTextField, {
                      modelValue: configDraft.value.disk_warning_free_gb,
                      "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((configDraft.value.disk_warning_free_gb) = $event)),
                      modelModifiers: { number: true },
                      type: "number",
                      label: "剩余容量阈值 GB"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VTextField, {
                      modelValue: configDraft.value.disk_warning_free_percent,
                      "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((configDraft.value.disk_warning_free_percent) = $event)),
                      modelModifiers: { number: true },
                      type: "number",
                      label: "剩余比例阈值 %"
                    }, null, 8, ["modelValue"]),
                    _createVNode(_component_VTextField, {
                      modelValue: configDraft.value.scan_cron,
                      "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((configDraft.value.scan_cron) = $event)),
                      label: "扫描周期 Cron"
                    }, null, 8, ["modelValue"])
                  ]),
                  _createVNode(_component_VTextarea, {
                    modelValue: configDraft.value.library_names,
                    "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((configDraft.value.library_names) = $event)),
                    label: "限定媒体库名称",
                    hint: "留空表示全部媒体库。可在接入 Emby 后按行填写媒体库名称。",
                    "persistent-hint": "",
                    "auto-grow": "",
                    rows: "3"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_VSwitch, {
                    modelValue: configDraft.value.ai_suggestions,
                    "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((configDraft.value.ai_suggestions) = $event)),
                    color: "primary",
                    inset: "",
                    label: "允许 AI 参与清理建议排序"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_VSwitch, {
                    modelValue: configDraft.value.default_delete_source,
                    "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((configDraft.value.default_delete_source) = $event)),
                    color: "error",
                    inset: "",
                    label: "默认同时删除源文件"
                  }, null, 8, ["modelValue"])
                ])
              ]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["modelValue"])
      ]),
      _: 1
    })
  ]))
}
}

};
const AppPage = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-cda4bee8"]]);

export { AppPage as default };
