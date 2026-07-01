import { importShared } from './__federation_fn_import.js';
import AppPage from './__federation_expose_AppPage.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper.js';

const {createVNode:_createVNode,resolveComponent:_resolveComponent,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,Fragment:_Fragment,createElementBlock:_createElementBlock} = await importShared('vue');


const _sfc_main = {
  __name: 'Page',
  props: {
  api: {
    type: Object,
    default: () => ({}),
  },
  pluginId: {
    type: String,
    default: 'MediaLibraryKeeper',
  },
  show_switch: {
    type: Boolean,
    default: true,
  },
},
  emits: ['close', 'switch'],
  setup(__props, { emit: __emit }) {



const emit = __emit;

return (_ctx, _cache) => {
  const _component_VBtn = _resolveComponent("VBtn");

  return (_openBlock(), _createElementBlock(_Fragment, null, [
    _createVNode(AppPage, {
      api: __props.api,
      "plugin-id": __props.pluginId,
      "hide-title": ""
    }, null, 8, ["api", "plugin-id"]),
    (__props.show_switch)
      ? (_openBlock(), _createBlock(_component_VBtn, {
          key: 0,
          class: "mlk-page-settings-fab",
          icon: "mdi-cog",
          color: "primary",
          variant: "flat",
          size: "large",
          onClick: _cache[0] || (_cache[0] = $event => (emit('switch')))
        }))
      : _createCommentVNode("", true)
  ], 64))
}
}

};
const Page = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-9ea6ea64"]]);

export { Page as default };
