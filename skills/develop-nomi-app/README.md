# Nomi 应用开发技能

[SKILL.md](./SKILL.md) 是供 Agent 读取的入口。把完整的 `develop-nomi-app` 目录放入 Agent 已配置的技能目录。调用时告诉 Agent 要接入哪个 Web 项目，例如「用 `develop-nomi-app` 把 `apps/my-board` 接入 Nomi」，也可以指定一个目录来新建应用。

[最小项目](./assets/starter/README.md) 是可直接运行的无框架示例。[页面接入](./references/web-ui.md) 说明如何保留 Vue、React 或其他现有项目，并打开已部署的页面。[测试模型说明](./references/test-model.md) 给出 BobanNomi 模型服务和其他 OpenAI 兼容网关的配置方式。新增示例代码放在最小项目目录，接入和排查说明放在 `references/`。

Nomi 源码仓库中的两套 SDK 文档站直接展示此 starter 的会话源码。公开 SDK 的安装、握手或会话流程变化时，同时核对指南和本技能的示例。
