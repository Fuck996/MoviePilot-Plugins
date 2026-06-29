import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, t as toEditableConfig, a as toPayloadConfig } from './_plugin-vue_export-helper-DBmJ-E3u.js';

const {createElementVNode:_createElementVNode,resolveComponent:_resolveComponent,createVNode:_createVNode,withCtx:_withCtx,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "mlk-config" };
const _hoisted_2 = { class: "mlk-config-body" };
const _hoisted_3 = { class: "mlk-config-grid" };

const {onMounted,ref} = await importShared('vue');


const _sfc_main = {
  __name: 'Config',
  props: {
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

function saveConfig() {
  emit('save', toPayloadConfig(config.value));
}

onMounted(() => {
  config.value = toEditableConfig(props.initialConfig);
});

return (_ctx, _cache) => {
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VToolbar = _resolveComponent("VToolbar");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VCombobox = _resolveComponent("VCombobox");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VTextarea = _resolveComponent("VTextarea");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_VToolbar, {
      density: "comfortable",
      color: "transparent"
    }, {
      default: _withCtx(() => [
        _cache[13] || (_cache[13] = _createElementVNode("div", { class: "text-h6 ms-3" }, "媒体库管家配置", -1)),
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
      _createVNode(_component_VSwitch, {
        modelValue: config.value.disk_warning_enabled,
        "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.value.disk_warning_enabled) = $event)),
        color: "warning",
        inset: "",
        label: "启用磁盘容量告警"
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VCombobox, {
        modelValue: config.value.mediaservers,
        "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.value.mediaservers) = $event)),
        label: "媒体服务器名称",
        hint: "输入 MoviePilot 媒体服务器名称，留空表示扫描所有 Emby。",
        multiple: "",
        chips: "",
        clearable: "",
        "persistent-hint": ""
      }, null, 8, ["modelValue"]),
      _createElementVNode("div", _hoisted_3, [
        _createVNode(_component_VTextField, {
          modelValue: config.value.disk_warning_free_gb,
          "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.value.disk_warning_free_gb) = $event)),
          modelModifiers: { number: true },
          type: "number",
          min: "0",
          label: "剩余容量阈值 GB"
        }, null, 8, ["modelValue"]),
        _createVNode(_component_VTextField, {
          modelValue: config.value.disk_warning_free_percent,
          "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.value.disk_warning_free_percent) = $event)),
          modelModifiers: { number: true },
          type: "number",
          min: "0",
          label: "剩余比例阈值 %"
        }, null, 8, ["modelValue"]),
        _createVNode(_component_VTextField, {
          modelValue: config.value.scan_cron,
          "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.value.scan_cron) = $event)),
          label: "扫描周期 Cron"
        }, null, 8, ["modelValue"])
      ]),
      _createVNode(_component_VTextarea, {
        modelValue: config.value.library_names,
        "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.value.library_names) = $event)),
        label: "限定媒体库名称",
        hint: "每行一个媒体库名称，留空表示全部媒体库。",
        "persistent-hint": "",
        "auto-grow": "",
        rows: "3"
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VTextarea, {
        modelValue: config.value.storage_paths,
        "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.value.storage_paths) = $event)),
        label: "磁盘容量检查路径",
        hint: "每行一个路径；留空时会尝试使用 MoviePilot 的 LIBRARY_PATH / DOWNLOAD_PATH。",
        "persistent-hint": "",
        "auto-grow": "",
        rows: "3"
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VSwitch, {
        modelValue: config.value.ai_suggestions,
        "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.value.ai_suggestions) = $event)),
        color: "primary",
        inset: "",
        label: "允许 AI 参与清理建议排序",
        disabled: ""
      }, null, 8, ["modelValue"]),
      _createVNode(_component_VSwitch, {
        modelValue: config.value.default_delete_source,
        "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.value.default_delete_source) = $event)),
        color: "error",
        inset: "",
        label: "默认同时删除源文件"
      }, null, 8, ["modelValue"])
    ])
  ]))
}
}

};
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-fb27228e"]]);

export { Config as default };
