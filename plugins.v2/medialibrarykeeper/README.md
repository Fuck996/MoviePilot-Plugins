# 媒体库管家

媒体库管家是一个 MoviePilot V2 插件，通过 MoviePilot 已配置的 Emby 媒体服务器读取媒体库，结合整理记录生成可确认、可追踪的空间释放计划。

## 功能

- 扫描 Emby 电影和剧集，展示名称、评分、图片、观看进度、集数、入库时间和路径。
- 按整理记录匹配媒体库文件和源文件，生成清理计划。
- 执行前必须在页面确认删除范围；执行时复用 `StorageChain` 删除文件，成功后删除对应整理记录。
- 支持磁盘容量阈值检查，容量不足时推送清理候选通知。
- 管理页面以 Vue 联邦远程组件形式加载。

## 编译

后端 Python 插件不需要传统编译，通常做语法检查即可：

```bash
python -m py_compile plugins.v2/medialibrarykeeper/__init__.py
```

V2 管理页是 Vue 联邦远程组件，需要构建前端产物：

```bash
cd plugins.v2/medialibrarykeeper
npm install --no-package-lock
npm run build
```

构建产物位于 `dist/assets`，MoviePilot 通过 `remoteEntry.js` 加载远程组件。
