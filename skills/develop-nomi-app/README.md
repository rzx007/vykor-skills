# Nomi 应用开发技能

[SKILL.md](./SKILL.md) 是供 Agent 读取的入口。把完整的 `develop-nomi-app` 目录放入 Agent 已配置的技能目录。调用时告诉 Agent 要接入哪个 Web 项目，例如「用 `develop-nomi-app` 把 `apps/my-board` 接入 Nomi」，也可以指定一个目录来新建应用。

[最小项目](./assets/starter/README.md) 是可直接运行的无框架示例。[页面接入](./references/web-ui.md) 说明如何保留 Vue、React 或其他现有项目，并打开已部署的页面。[模型目录和连接](./references/test-model.md) 说明如何使用开发者提供的供应商、模型和 API key。新增示例代码放在最小项目目录，接入和排查说明放在 `references/`。

会话源码随技能发布。安装、握手和刷新恢复见[最小项目](./assets/starter/README.md)。

应用要接数字员工登录、模型、积分或充值时，查看[数字员工远程 API](./references/digital-employee-api.md)，其中有一段把模型列表交给 SDK 的示例。
