import { importShared } from './__federation_fn_import.js';
import { _ as _export_sfc, t as toEditableConfig, u as unwrapResponse, a as toPayloadConfig } from './_plugin-vue_export-helper.js';

const {createElementVNode:_createElementVNode,resolveComponent:_resolveComponent,createVNode:_createVNode,withCtx:_withCtx,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "mlk-config" };
const _hoisted_2 = { class: "mlk-config-body" };

const {computed,onMounted,ref} = await importShared('vue');


const _sfc_main = {
  __name: 'Config',
  props: {
  api: {
    type: Object,
    default: () => ({}),
  },
  pluginId: {
    type: String,
    default: 'MediaLibraryKeeper',
  },
  initialConfig: {
    type: Object,
    default: () => ({}),
  },
},
  emits: ['save', 'close'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;
const config = ref(toEditableConfig());
const loadingOptions = ref(false);
const mediaServerOptions = ref([]);
const downloaderOptions = ref([]);
const pluginBase = computed(() => `plugin/${props.pluginId || 'MediaLibraryKeeper'}`);

function saveConfig() {
  emit('save', toPayloadConfig(config.value));
}

async function loadMediaServerOptions() {
  if (!props.api?.get) return
  loadingOptions.value = true;
  try {
    const response = await props.api.get(`${pluginBase.value}/status`);
    const status = unwrapResponse(response) || {};
    mediaServerOptions.value = status.media_server_options || [];
    downloaderOptions.value = status.downloader_options || [];
  } finally {
    loadingOptions.value = false;
  }
}

onMounted(async () => {
  config.value = toEditableConfig(props.initialConfig);
  await loadMediaServerOptions();
});

return (_ctx, _cache) => {
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VToolbar = _resolveComponent("VToolbar");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VSelect = _resolveComponent("VSelect");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_VToolbar, {
      density: "comfortable",
      color: "transparent"
    }, {
      default: _withCtx(() => [
        _cache[9] || (_cache[9] = _createElementVNode("div", { class: "text-h6 ms-3" }, "媒体库管家配置", -1)),
        _createVNode(_component_VSpacer),
        _createVNode(_component_VBtn, {
          icon: "mdi-content-save",
          variant: "text",
          color: "primary",
          onClick: saveConfig
        }),
        _createVNode(_component_VBtn, {
          icon: "mdi-close",
          variant: "text",
          onClick: _cache[0] || (_cache[0] = $event => (emit('close')))
        })
      ]),
      _: 1
    }),
    _createVNode(_component_VDivider),
    _createElementVNode("div", _hoisted_2, [
      _createVNode(_component_VSwitch, {
        modelValue: config.value.enabled,
        "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.value.enabled) = $event)),
        color: "primary",
        inset: "",
        label: "启用插件"
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VSwitch, {
        modelValue: config.value.show_sidebar_nav,
        "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.value.show_sidebar_nav) = $event)),
        color: "primary",
        inset: "",
        label: "显示侧边栏入口"
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VSwitch, {
        modelValue: config.value.notify_enabled,
        "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.value.notify_enabled) = $event)),
        color: "primary",
        inset: "",
        label: "启用通知"
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VSelect, {
        modelValue: config.value.mediaservers,
        "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.value.mediaservers) = $event)),
        label: "媒体服务器",
        items: mediaServerOptions.value,
        multiple: "",
        chips: "",
        clearable: "",
        loading: loadingOptions.value,
        disabled: !mediaServerOptions.value.length,
        hint: "自动读取 MoviePilot 已配置的媒体服务器；留空表示扫描所有 Emby。",
        "persistent-hint": ""
      }, null, 8, ["modelValue", "items", "loading", "disabled"]),
      _createVNode(_component_VSelect, {
        modelValue: config.value.downloaders,
        "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.value.downloaders) = $event)),
        label: "下载器",
        items: downloaderOptions.value,
        multiple: "",
        chips: "",
        clearable: "",
        loading: loadingOptions.value,
        disabled: !downloaderOptions.value.length,
        hint: "自动读取 MoviePilot 已启用的 QB / Transmission；留空表示全部支持的下载器。",
        "persistent-hint": ""
      }, null, 8, ["modelValue", "items", "loading", "disabled"]),
      _createVNode(_component_VSwitch, {
        modelValue: config.value.ai_suggestions,
        "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.value.ai_suggestions) = $event)),
        color: "primary",
        inset: "",
        label: "允许 AI 参与清理建议排序",
        disabled: ""
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VSwitch, {
        modelValue: config.value.default_delete_source,
        "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.value.default_delete_source) = $event)),
        color: "error",
        inset: "",
        label: "默认同时删除源文件"
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VSwitch, {
        modelValue: config.value.delete_seed_tasks,
        "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.value.delete_seed_tasks) = $event)),
        color: "warning",
        inset: "",
        label: "删除资源时同步删除保种任务"
      }, null, 8, ["modelValue"])
    ])
  ]))
}
}

};
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-01416085"]]);

export { Config as default };
