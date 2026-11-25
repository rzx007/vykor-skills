# Nomi 最小开发项目

新建应用时，把这个目录的文件复制到你为应用选定的新项目目录。已有 Web 项目可直接参照下文「接入已有页面」。`app.manifest.json` 是 Nomi 的应用清单，`nomi-app.js` 是可接入其他网页的浏览器端模块，`main.js` 负责示例表单。`configure-model.mjs` 在运行 Nomi 的机器上为指定的开发后台配置测试模型。

## 版本

这个示例使用 Node.js 24、Client `0.2.0` 和 AppHost `0.2.0`。两份包发布到 npm 后，可在复制出的示例目录安装指定版本。

```sh
npm install --save-exact @bobannomi/app-host@0.2.0 @bobannomi/client@0.2.0
```

发布前用两份 `0.2.0` 候选安装包。需要从源码生成时，在 BobanNomi 仓库根目录运行 `pnpm install --frozen-lockfile --ignore-scripts`，再运行 `pnpm release:sdk:dry -- 0.2.0 --out .tools/sdk-candidate-0.2.0`。输出目录须尚未创建。用打包命令打印的实际路径在 starter 目录安装两份包，再核对版本。

```sh
npm install --save-exact "/path/to/bobannomi-app-host-0.2.0.tgz" "/path/to/bobannomi-client-0.2.0.tgz"
npm ls @bobannomi/app-host @bobannomi/client --depth=0
```

保留 `package-lock.json`，方便复现安装。已有项目沿用原包管理器，只添加缺少的 SDK。只做宿主握手时，仅安装 `@bobannomi/app-host`。

清单里的 `hostApi` 描述应用需要的 Nomi 宿主接口版本。装完 SDK 后，在目标 Nomi 的开发窗口验证握手；需要 Agent 时，再验证会话连接。出现版本不兼容时，告诉开发者实际安装的 SDK 和 Nomi 版本，再根据目标 Nomi 支持的版本选择依赖。

## 跑起来

1. 把 `app.manifest.json` 中的 `id` 和 `name` 改成自己的应用标识。沿用已有 Web 项目的构建入口时，把 `ui.entry` 改成实际路径。此示例用 Nomi 应用存储记住原会话，所以需要 `app.storage`。
2. 在复制后的示例目录运行上面的 SDK 安装命令，它也会安装项目的 Vite 依赖。再运行 `npm run dev`。在 Nomi「常规设置 → 开发应用」启用开发者模式，选这个目录或清单，把 Vite 输出的实际地址填入「开发页面地址」，点「打开开发窗口」。审阅来源，批准 `app.storage` 和开发入口要求的 `agent`。`npm run build` 可单独检查生产页面构建。
3. 优先在页面选择 BobanNomi 模型服务。需要配置服务时，记下页面上的开发项目 ID 和数据 ID，按[测试模型说明](../../references/test-model.md)操作，也可以接入其他 OpenAI 兼容网关。复制示例到单独目录时，模型说明可从原技能目录打开。
4. 回到开发窗口按 F5，在表单里填开发后台能访问的完整执行目录。此 starter 的开发后台运行在 Nomi 桌面机器上。选择测试模型，点击「发送测试消息」。示例绑定会话 ID，通过 `session.prompt()` 提交并等待 `session.waitForRun()` 返回 `completed` 和 `NOMI_NPM_OK`。再按 F5，核对原会话 ID、运行 ID 和回复。
5. 测试结束后关闭开发窗口并确认。Nomi 会等待页面保存并停止开发后台，之后可停止 Vite。

如果应用需要在已有会话中切换模型，按[会话配置与原请求恢复](../../references/web-ui.md#配置已创建的会话)使用会话对象的 `configuration` 方法。

若在 starter 上增加工具审批、后台任务展示或草稿附件，按[页面连接参考](../../references/web-ui.md#会话里的权限后台任务和附件)使用对应的 SDK 入口，并在 Nomi 开发窗口用真实授权范围验证。

## 添加本机目录读取

页面需要提供「选择目录」时，按[本机目录接入](../../references/web-ui.md#读用户选中的本机目录)声明 `workspace.select`。用户点选后，直接在 `host.workspace.pick()` 返回的目录对象上使用 `listFiles()` 和 `readText(path)`。纯目录读取只需 `@bobannomi/app-host`。

目录选择由 Main 在 Nomi 桌面机器上处理。会话运行使用 daemon 的执行目录。这个 starter 的 Client 使用页面会话连接，管理插件、渠道和后台配置的凭据由获准的后台程序持有。

## 添加托管服务

此示例用于验证页面、应用存储和 Agent 会话。需要应用自己的本机业务进程时，按[托管服务接入和验收](../../references/web-ui.md#托管本机服务)准备生产清单和 ZIP，在 Nomi 安装后从页面用 `host.service` 连接本机 HTTP。Agent 会话仍通过本示例的页面连接访问。提供 MCP 工具时加上 `service.mcpPath`，打开应用并等健康检查通过，再从普通 MCP 列表验证。复制 starter 到独立目录后，可从原技能目录打开参考。

要把普通 MCP 配置随 ZIP 一起交付，在清单加 `"agent": { "mcp": "mcp.json" }`，把配置文件放在包内。安装启用并批准 `agent` 后，从 MCP 列表核对服务器。 [清单和配置示例](../../references/web-ui.md#随应用提供-skill-和普通-mcp)

## 接入已有页面

保留应用原有的路由和开发命令，把 `nomi-app.js` 加入浏览器端代码。`connectNomi()` 检查当前页面功能和安装授权，返回宿主、受限 Client 与当前数据身份。`sendTest()` 在应用存储保存创建请求，再用选定目录和模型发一次消息。`restoreTest()` 核对安装与数据身份，查询原创建回执或按原输入 ID 查运行和回复。每次刷新只读原记录。纯页面联调可先用应用清单和开发地址检查握手。需要工作台的独立工作树会话、侧边聊天或 Git 回执时，到 Nomi 自带的工作台按[工作台能力参考](../../references/web-ui.md#工作台的会话准备和临时会话)验收。

有应用目录时调用 `connectNomi({ providers })`。`providers` 是 `ModelProviderInfo[]` 或接收 `{ signal }` 的异步函数。页面用 `nomi.client.models.list()` 读目录。服务地址和凭据由配置脚本经管理连接保存。 [测试模型说明](../../references/test-model.md)
