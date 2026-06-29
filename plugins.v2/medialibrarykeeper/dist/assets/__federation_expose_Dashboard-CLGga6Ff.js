import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, f as formatNumber, b as formatBytes, u as unwrapResponse } from './_plugin-vue_export-helper-DyMs-RuR.js';

const {toDisplayString:_toDisplayString,createElementVNode:_createElementVNode,resolveComponent:_resolveComponent,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,unref:_unref,createTextVNode:_createTextVNode,withCtx:_withCtx,createVNode:_createVNode} = await importShared('vue');


const _hoisted_1 = { class: "mlk-dashboard-head" };
const _hoisted_2 = { class: "text-subtitle-1 font-weight-medium" };
const _hoisted_3 = { class: "text-caption text-medium-emphasis" };
const _hoisted_4 = { class: "mlk-dashboard-grid" };
const _hoisted_5 = { class: "text-h6" };
const _hoisted_6 = { class: "text-h6" };
const _hoisted_7 = { class: "text-h6" };

const {computed,onMounted,ref} = await importShared('vue');


const _sfc_main = {
  __name: 'Dashboard',
  props: {
  api: {
    type: Object,
    default: () => ({}),
  },
  pluginId: {
    type: String,
    default: 'MediaLibraryKeeper',
  },
  config: {
    type: Object,
    default: () => ({ attrs: {} }),
  },
  refreshInterval: {
    type: Number,
    default: 0,
  },
},
  setup(__props) {

const props = __props;

const loading = ref(false);
const status = ref({ summary: {} });

const summary = computed(() => status.value.summary || {});
const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`);
const cardTitle = computed(() => props.config?.attrs?.title || '媒体库管家');
const cardSubtitle = computed(() => props.config?.attrs?.subtitle || '空间风险与清理建议');

async function loadStatus() {
  loading.value = true;
  try {
    const response = await props.api.get(`${pluginBase.value}/status`);
    status.value = unwrapResponse(response) || status.value;
  } finally {
    loading.value = false;
  }
}

onMounted(loadStatus);

return (_ctx, _cache) => {
  const _component_VProgressCircular = _resolveComponent("VProgressCircular");
  const _component_VAlert = _resolveComponent("VAlert");
  const _component_VSheet = _resolveComponent("VSheet");

  return (_openBlock(), _createBlock(_component_VSheet, {
    border: "",
    rounded: "",
    class: "mlk-dashboard"
  }, {
    default: _withCtx(() => [
      _createElementVNode("div", _hoisted_1, [
        _createElementVNode("div", null, [
          _createElementVNode("div", _hoisted_2, _toDisplayString(cardTitle.value), 1),
          _createElementVNode("div", _hoisted_3, _toDisplayString(cardSubtitle.value), 1)
        ]),
        (loading.value)
          ? (_openBlock(), _createBlock(_component_VProgressCircular, {
              key: 0,
              indeterminate: "",
              size: "20",
              width: "2"
            }))
          : _createCommentVNode("", true)
      ]),
      _createElementVNode("div", _hoisted_4, [
        _createElementVNode("div", null, [
          _cache[0] || (_cache[0] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "媒体库", -1)),
          _createElementVNode("div", _hoisted_5, _toDisplayString(_unref(formatNumber)(summary.value.libraries)), 1)
        ]),
        _createElementVNode("div", null, [
          _cache[1] || (_cache[1] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "剧集", -1)),
          _createElementVNode("div", _hoisted_6, _toDisplayString(_unref(formatNumber)(summary.value.series)), 1)
        ]),
        _createElementVNode("div", null, [
          _cache[2] || (_cache[2] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "预计释放", -1)),
          _createElementVNode("div", _hoisted_7, _toDisplayString(_unref(formatBytes)(summary.value.estimated_reclaim_size)), 1)
        ])
      ]),
      _createVNode(_component_VAlert, {
        type: "info",
        variant: "tonal",
        density: "compact"
      }, {
        default: _withCtx(() => [...(_cache[3] || (_cache[3] = [
          _createTextVNode("等待接入 Emby 扫描", -1)
        ]))]),
        _: 1
      })
    ]),
    _: 1
  }))
}
}

};
const Dashboard = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-6bda5f1d"]]);

export { Dashboard as default };
