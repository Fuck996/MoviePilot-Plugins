# 媒体库管家

媒体库管家是一个 MoviePilot V2 插件，目标是通过 MoviePilot 已配置的媒体服务器管理 Emby 媒体库，结合整理记录生成安全的空间释放计划。

## 当前阶段

- 已提供 Vue 联邦远程组件页面。
- 已提供插件后端 API 合同。
- 已提供清理计划预览接口。
- 真实 Emby 拉取、整理记录匹配、文件删除尚未接入。

当前版本会阻止真实清理执行，避免占位逻辑误删文件。

## 编译

```bash
cd plugins.v2/medialibrarykeeper
npm install --no-package-lock
npm run build
```

构建产物位于 `dist/assets`，MoviePilot 通过 `remoteEntry.js` 加载远程组件。
