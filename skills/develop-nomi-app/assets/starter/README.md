# Nomi 最小开发项目

新建应用时，把这个目录的文件复制到你为应用选定的新项目目录。已有 Web 项目可直接参照下文「接入已有页面」。`app.manifest.json` 是 Nomi 的应用清单，`nomi-app.js` 是可接入其他网页的浏览器端模块，`main.js` 负责示例表单。

## 版本

本例使用 Node.js 24，`package.json` 已固定 AppHost `0.4.0` 和 Client `0.3.1`。运行本例需要支持 `getAuthorizedAgentConnection()` 的 Nomi 桌面，后台需支持应用模型连接和会话目录创建。复制 Starter 后，安装并核对依赖版本。

```sh
npm install
npm ls @bobannomi/app-host @bobannomi/client --depth=0
```

已有项目可运行 `npm install --save-exact @bobannomi/app-host@0.4.0 @bobannomi/client@0.3.1`。验证尚未发布的 Nomi 源码时，使用对应构建和本地打包的 SDK。

保留 `package-lock.json`，方便复现安装。已有项目沿用原包管理器，只添加缺少的 SDK。只做宿主握手时，仅安装 `@bobannomi/app-host`。

清单里的 `hostApi` 描述应用需要的 Nomi 宿主接口版本。装完 SDK 后，在目标 Nomi 的开发窗口验证握手；需要 Agent 时，再验证会话连接。出现版本不兼容时，告诉开发者实际安装的 SDK 和 Nomi 版本，再根据目标 Nomi 支持的版本选择依赖。

## 跑起来

通过 Nomi 开发窗口运行本例，页面需要 AppHost 提供项目目录、会话连接和应用存储。复制后的目录只在本机提供示例的测试模型配置。部署自己的页面时，复用下文的应用模型接入方式。

1. 把 `app.manifest.json` 中的 `id` 和 `name` 改成自己的应用标识。沿用已有 Web 项目的构建入口时，把 `ui.entry` 改成实际路径。此示例用 `app.storage` 记住原会话，用 `workspace.select` 和 `workspace.execute` 选择项目并在其中执行。
2. 开发者在本地 `.env.local` 中一次性填入自己的 OpenAI 兼容模型连接。下面三项是示例值。`vite.config.js` 只在本机开发服务中按需提供配置，API key 保存在服务内存中。

   ```dotenv
   NOMI_MODEL_BASE_URL=https://gateway.example.com/v1
   NOMI_MODEL_API_KEY=your-model-api-key
   NOMI_MODEL_ID=your-model-id
   ```

3. 运行 `npm run dev`。在 Nomi「常规设置 → 开发应用」启用开发者模式，选这个目录或清单，填入 Vite 输出的 `127.0.0.1` 地址，打开开发窗口。审阅来源和权限，确认 `app.storage`、`workspace.select` 和 `workspace.execute`。开发入口会把 `agent` 一并列为必需权限。`npm run build` 可单独检查生产页面构建。
4. 从「工作位置」选项目，默认「不在项目中工作」会让后台创建会话目录。选好模型和「回复方式」，写消息并发送。完整输出等本轮结束后显示回复，流式输出在生成过程中更新气泡。展开「运行详情」，确认状态为 `completed`。按 F5 后核对原消息、回复、会话 ID 和运行 ID。
5. 测试结束后关闭开发窗口并确认，再停止 Vite。

连接提示版本或权限有问题时，在开发窗口核对 `agent` 授权和以上三个清单权限。本例需要宿主提供会话连接和目录列表，对应 `session-resources-v1`、`workspace-v1`、`resource-catalog-v1`。

如果应用需要在已有会话中切换模型，按[会话配置与原请求恢复](../../references/web-ui.md#配置已创建的会话)使用会话对象的 `configuration` 方法。

若在 starter 上增加工具审批、后台任务展示或草稿附件，按[页面连接参考](../../references/web-ui.md#会话里的权限后台任务和附件)使用对应的 SDK 入口，并在 Nomi 开发窗口用真实授权范围验证。

## 添加本机目录读取

页面需要提供「选择目录」时，按[本机目录接入](../../references/web-ui.md#读用户选中的本机目录)声明 `workspace.select`。用户点选后，直接在 `host.workspace.pick()` 返回的目录对象上使用 `listFiles()` 和 `readText(path)`。纯目录读取只需 `@bobannomi/app-host`。

目录选择由 Main 在 Nomi 桌面机器上处理。会话运行使用 daemon 的执行目录。这个 starter 的 Client 使用页面会话连接，管理插件、渠道和后台配置的凭据由获准的后台程序持有。

## 添加托管服务

此示例用于验证页面、应用存储和 Agent 会话。需要应用自己的本机业务进程时，按[托管服务接入和验收](../../references/web-ui.md#托管本机服务)准备生产清单和 ZIP，在 Nomi 安装后从页面用 `host.service` 连接本机 HTTP。Agent 会话仍通过本示例的页面连接访问。提供 MCP 工具时加上 `service.mcpPath`，打开应用并等健康检查通过，再从普通 MCP 列表验证。复制 starter 到独立目录后，可从原技能目录打开参考。

要把普通 MCP 配置随 ZIP 一起交付，在清单加 `"agent": { "mcp": "mcp.json" }`，把配置文件放在包内。安装启用并批准 `agent` 后，从 MCP 列表核对服务器。 [清单和配置示例](../../references/web-ui.md#随应用提供-skill-和普通-mcp)

## 接入已有页面

保留应用原有的路由和开发命令，把 `nomi-app.js` 加入浏览器端代码。`connectNomi()` 检查当前页面功能和安装授权，返回宿主、受限 Client 与当前数据身份。`sendMessage()` 在应用存储保存原请求，用 `client.sessions.create()` 让后台准备所选项目或项目外目录，确认创建成功后发送输入。`restoreLastMessage()` 核对安装与数据身份，查询原创建回执或按原输入 ID 查消息和回复。每次刷新只读原记录。页面卸载或热更新时，Starter 用 `AbortSignal` 结束自己的等待和订阅。AppHost 管理共享连接。需要工作台的独立工作树会话、侧边聊天或 Git 回执时，到 Nomi 自带的工作台验收。 [工作台能力参考](../../references/web-ui.md#工作台的会话准备和临时会话)

完整输出和刷新恢复用 `session.waitForRun(runId)` 读取结果。流式输出通过 `syncEvents()` 观察本次运行，并用 `getVisibleSessionMessages()` 读取 SDK 合并后的助手正文。回复方式在发送前选择。需要刷新后查回执时，示例用浏览器的随机数接口提前生成并保存请求 ID。

调用 `connectNomi({ providers })`，每个供应商的 `models` 提供选项，`connection` 提供地址和 API key，可以是按需加载的异步函数。界面用 `nomi.client.models.list()` 取得模型选项。正式安装的应用要在清单里声明并获批模型网关来源。 [目录和连接示例](../../references/test-model.md)
