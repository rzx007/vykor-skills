# 把 Web 页面接入 Nomi

Nomi 开发窗口加载 Web 地址。应用原有的路由、组件、样式和后台由应用维护。需要调用 Nomi 时，在浏览器代码里增加 AppHost 连接。下面的按钮适合放在调试页，也可以接入现有业务组件。先验证握手，再按需接 Agent、存储等能力。

| 项目场景 | 开发时怎么打开 | Nomi 接入放在哪里 |
| --- | --- | --- |
| Vue | 运行项目已有的开发命令，填实际输出的 URL | Vue 组件里的事件回调。已有 Vue 2 项目可以沿用 `methods` |
| React | 运行项目已有的开发命令，填实际输出的 URL | React 客户端组件里的事件回调。使用服务端渲染时，把连接放进可在浏览器交互的组件 |
| 无框架 | 使用项目已有 Web 服务，或运行本技能的 [Vite 最小示例](../assets/starter/README.md) | 浏览器模块的事件回调。若使用 npm SDK，由项目构建器解析模块并打进网页资源 |
| 已部署的远程站点 | 在 Nomi 开发设置选本机清单，再填 Nomi 所在机器能访问的 HTTP 或 HTTPS 页面 URL | 通过站点自己的发布流程上线浏览器接入代码。Vue、React 或无框架页面都可以部署到远程 |

只验证页面和路由时，在 Nomi 开发窗口选择应用清单、填写页面地址即可。需要 AppHost 时，按[版本选择和安装命令](../assets/starter/README.md#版本)添加 `@bobannomi/app-host`，从用户操作发起连接，在 Nomi 开发窗口验收握手和授权。现有普通浏览器流程照常使用。需要 Agent 时，再添加 `@bobannomi/client`，并参考[会话示例](../assets/starter/nomi-app.js)接入。

## 读用户选中的本机目录

在清单声明 `workspace.select`，由用户在打开开发窗口或安装应用时批准。点击「选择目录」时用下列流程，把文件列表和文本结果显示在页面中。

```js
const directory = await host.workspace.pick()
if (directory) {
  const page = await directory.listFiles()
  const file = page.entries.find(entry => entry.kind === 'file' && entry.name === 'README.md')
  if (file) preview.textContent = (await directory.readText(file.path)).text
}
```

取消返回 `null`。需要记住目录时保存 `directory.id`，下次调用 `host.workspace.open(id)`。`host.workspace.list()` 列出已获准的目录。需要核对一次选择的结果时，先保存 `requestId`，交给 `host.workspace.pick({ requestId })`，再用 `host.workspace.getSelection({ requestId })` 查询。文件路径相对于用户所选目录，文件访问由 Electron 主进程处理。页面可以用 `host.hasFeature('workspace-v1')` 检查窗口是否已接通此功能。按会话读取 Agent 实际运行目录时，用 `client.sessions.byId(sessionId).files.readText(path)`，路径相对于 daemon 的会话执行目录。

本机目录 ID 对应本应用获准读取的目录。后台管理程序可以用自己的 daemon 管理连接调用 `client.projects.list()`。选定 `projectId` 后，用 `client.sessions.getConfigurationOptions({ projectId })` 读取 `optionsRevision`，并在创建会话时一并提交。登记目录已换绑时，先重新查询选项。远程 daemon 的项目路径属于远程执行环境。

获准使用 `trusted-desktop-v1` 的页面可以通过 `host.desktop` 查询已绑定目录的文件和 Git 状态。使用 `host.desktop.terminals` 时，未绑定会话的本机目标由 Main 启动终端，绑定会话的目标使用 daemon 中该会话的执行环境。创建或重启的结果未知时，保留原请求并用 `host.desktop.terminals.getRequest` 核对。仅查看已有会话终端时，用 `client.sessions.byId(sessionId).terminals`。

## 工作台的会话准备和临时会话

`connectAppHost()` 返回 `AppHost`。先用 `host.hasFeature()` 检查窗口提供的功能。普通应用用经 `agent` 授权的 `host.getAuthorizedAgentConnection()` 取得受限连接，交给 Client 管理会话和运行。共享连接由 AppHost 释放。组件卸载时，用自己的 `AbortSignal` 取消请求或订阅。Starter 的项目选择和项目外会话在开发窗口验证。独立工作树、临时侧边聊天、Git 回执和目标窗口按下面的步骤在 Nomi 自带的工作台验证。

- **选择项目或项目外会话**。Starter 在开发窗口用 `host.workspace.list()` 列出应用已授权的目录，用 `host.workspace.pick()` 添加本机项目。用 `client.sessions.create()` 创建会话，选项目时传 `workspaceId`，选项目外时传 `outsideProject: true`。目录选择和项目执行分别需要 `workspace.select` 和 `workspace.execute`。确认创建成功后再发送输入。
- **独立工作树会话**。在 `session-controls-v1` 可用且已授予 `workspace.execute` 时，保存已登记的 `workspaceId`、`dataScopeId`、`sessionId`、`requestId` 和配置，再用 `host.sessions.preparation.create(original)` 提交，`original.taskLocation` 填 `"worktree"`。项目外的会话只支持 `outsideProject: true` 与 `taskLocation: "current"`。daemon 准备目录并保存会话绑定。收到 `retry: "query"` 和原 `requestId` 时，用 `host.sessions.preparation.getResult(original)` 查原回执。工作台可在测试 Git 项目中新建会话，选择「任务工作位置 → 独立工作目录」后发送消息，核对执行目录并清理测试会话。
- **临时侧边聊天**。在 `auxiliary-sessions-v1` 可用时，以当前页面的原会话 `connection` 和 `sessionId` 调 `host.sessions.auxiliary.getOptions`。提交 `open(original)` 前，把选项 ID、`optionsRevision`、原会话连接、会话 ID、`requestId` 与 `id` 留在页面内。`open` 返回临时会话连接，`get(original)` 查询原回执。结束时用 `close(original)` 关闭临时会话，Main 收到关闭回执后释放它的页面连接。保留原会话连接，供回包不明时查询 `closed` 回执。在工作台的「侧边聊天」发送测试消息，关标签时确认「关闭并销毁」。
- **Git 回执和窗口**。对已绑定目标发起 `switchBranch` 或 `createBranch` 前保存分支名、预期 HEAD 和 `requestId`。用 `host.desktop.git.getOperation({ targetId, requestId, original })` 查原回执，`original` 形如 `{ kind: "git.switchBranch", body: { branch, expectedHead } }`。重开页面时先核对数据范围与原目录身份，再绑定该目录取新的目标 ID。用完释放目标。当前宿主窗口走 `host.window`。其他已打开的目标窗口走 `host.desktop.windows`，由宿主校验它们与页面和目标的归属。

## 配置已创建的会话

已取得会话 ID 时，用 `client.sessions.byId(sessionId)` 读 `session.getControls()`、会话配置和目标。配置更新先保存完整请求和读到的版本，再调用 `session.configuration.update(original)`。刷新后重新连接，确认应用安装和 `dataScopeId` 一致，再用 `session.configuration.getResult({ requestId, original })` 查询原配置写入。会话改名等管理操作用 `session.management`，用 `getMutation(requestId)` 查询回执。页面可执行的操作由宿主和 daemon 按当前连接检查。

## 会话里的权限、后台任务和附件

- 使用 AppHost 授权的页面 Client，在自己的会话内用 `client.permissions.requests.list({ sessionId, status: "pending" })` 或从 `session.observe({ signal })` 的 `permissions` 读取待处理请求。在等待运行时把请求交给用户。`Shell`、`Write` 等普通工具审批用原请求 ID 调用 `requests.reply()`，单次批准传 `{ status: "approved", decision: "once" }`，拒绝传 `{ status: "denied" }`。支持 `features.questions >= 1` 的后台可用 `requests.answerQuestion(request.id, { answer })` 回复 `AskUser`。答案用 `JSON.stringify({ selected, custom })` 编码，两个对象都以从 0 开始的题号为键。`selected` 的值是从 0 开始的选项下标数组，`custom` 的值是用户填写的文字。
- daemon 核对原请求、会话授权及当前待处理状态。后台要求由原宿主连接回复时，通过这条获准的宿主连接处理。查询或撤销已保存的批准需要有管理该授权权限的后台连接。
- 后台任务用 `session.jobs.list()` 查询，后续读取或等待传返回的 `job.target`，其中子 Agent 目标还带 `runId`。持续展示会话时用 `session.observe({ signal })`，断流后 SDK 会用最新会话快照恢复。
- 由宿主提供 `attachments-v1` 且已经取得当前草稿目标时，用 `host.attachments.getConnection({ targetId })` 取得受限连接，再用它的 `clientOptions` 创建 `BobanNomiClient`。上传使用该目标的草稿 ID。保存原 `requestId`、`draftId`、SHA-256、字节数、文件名、媒体类型和后台数据身份，回包丢失时在原范围用 `client.attachments.getUpload(original)` 查询。

## 托管本机服务

1. 在生产清单声明 `app.service` 和 `service`，填写协议和业务 API 版本、运行要求、启动命令与健康检查。清单校验会拒绝 `service.activation`。可以直接从[完整示例](https://github.com/rzx007/boban-nomi/tree/main/examples/applications/agent-service-demo)查看清单和服务启动代码。
2. 打包 ZIP，在 Nomi 安装并批准 `app.service`。打开应用页面后，桌面主进程启动服务。服务通过本机 HTTP 提供业务接口和可选的 MCP 接口。页面通过 `host.service` 调用本机业务。
3. 等待 `host.service.getStatus()` 返回 `ready`，再用 `getConnection()` 发一笔真实业务并记录请求 ID。刷新页面后用原 ID 查询结果。完全退出 Nomi 桌面会停止服务，单独重启 Agent 后台不会启动应用服务。
4. 要发布托管服务的 MCP 工具，在 `service.mcpPath` 填服务内的绝对路径，例如 `"/mcp"`，并提供标准 Streamable HTTP。批准 `app.service` 后，Main 在服务通过健康检查时登记。临时失败由 Main 自动补发。
5. 核对停止服务后当前 daemon 的 MCP 条目仍可见，再打开应用确认同名条目可调用。单独重启 daemon 后，检查仍就绪的服务会重新登记。

## 随应用提供 Skill 和普通 MCP

用 `agent.skills` 声明 Skill 目录并放入 `SKILL.md`。用 `"agent": { "mcp": "mcp.json" }` 声明包内普通 MCP 配置，文件形如 `{ "servers": { "search": { "type": "http", "url": "https://mcp.example.com/mcp" } } }`。服务器需要显式填写 `http`、`sse` 或 `stdio`。安装启用并批准 `agent` 后，Main 将这些配置登记到普通 MCP 列表，Agent 按同样的流程发现和调用手动添加与应用登记的工具。停用应用或撤回 `agent` 后，清单声明的普通 MCP 条目会被移除。

HTTP MCP 需要 OAuth 时，在该条配置写入 `"oauth": {}`，需要指定权限时填写 `oauth.scopes`。安装后从现有 MCP 列表完成浏览器授权，再用 `client.sessions.byId(sessionId).mcp.list()` 核对应用当前可访问会话中的连接状态和工具数量。重新授权和退出登录使用同一个列表入口，应用包配置保持只读。

每个应用的 MCP 配置需要装入一条 1 MiB 的登记请求。安装校验会指出超限配置。

如果旧版桌面已经安装托管服务应用，先在旧版卸载这些应用并保留业务数据，再退出旧版并升级。删掉应用清单中显式声明的 `service.activation`。如果旧包在 `agent.mcp` 中用 `app-service` 声明了自己的服务端点，把端点改填到 `service.mcpPath`。修改清单后提高应用版本，再打包并重新安装。

## 新建 Vue 或 React 工程

从零新建时可以用 Vite 官方脚手架。在选定的父目录执行其中一条，把示例目录名替换成你给应用选的名字。需要 TypeScript 时，把模板参数改成 `vue-ts` 或 `react-ts`。[Vite 创建项目](https://vite.dev/guide/#scaffolding-your-first-vite-project)

```sh
npm create vite@latest my-vue-app -- --template vue --no-interactive
npm create vite@latest my-react-app -- --template react --no-interactive
```

进入生成的项目目录，按上面的说明添加用得上的 SDK，接入下文对应的组件，按 [Starter 清单](../assets/starter/app.manifest.json)在项目根填写应用信息和实际需要的权限。安装项目依赖后运行 `npm run dev`，在 Nomi 里选这个项目目录并填写开发服务实际输出的地址。

## Vue 示例

在现有 Vue 3 页面增加一个调试组件，下一段从浏览器点击发起握手。[Vue 事件处理](https://vuejs.org/guide/essentials/event-handling.html)

```vue
<script setup>
import { ref } from 'vue'
import { connectAppHost } from '@bobannomi/app-host'

const status = ref('等待连接')
const busy = ref(false)

async function connect() {
  busy.value = true
  try {
    const host = await connectAppHost({ hostApi: '^0.1.3' })
    const context = await host.getContext()
    status.value = `已连接 Nomi ${context.hostVersion}`
  } catch (error) {
    status.value = `连接失败 ${error.message}`
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <button type="button" :disabled="busy" @click="connect">连接 Nomi</button>
  <p role="status">{{ status }}</p>
</template>
```

## React 示例

把组件放到现有 React 页面。使用 React Server Components 时，将此组件标记为客户端组件。[React 事件处理](https://react.dev/learn/responding-to-events)

```jsx
import { useState } from 'react'
import { connectAppHost } from '@bobannomi/app-host'

export default function NomiConnection() {
  const [status, setStatus] = useState('等待连接')
  const [busy, setBusy] = useState(false)

  async function connect() {
    setBusy(true)
    try {
      const host = await connectAppHost({ hostApi: '^0.1.3' })
      const context = await host.getContext()
      setStatus(`已连接 Nomi ${context.hostVersion}`)
    } catch (error) {
      setStatus(`连接失败 ${error.message}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <button type="button" disabled={busy} onClick={connect}>连接 Nomi</button>
      <p role="status">{status}</p>
    </>
  )
}
```

## 无框架和远程页面

无框架项目可以在 `type="module"` 的网页入口里给按钮绑定 `click`，同样调用 `connectAppHost()` 和 `getContext()`。完整示例包含会话、回复和刷新后的恢复。[无框架示例](../assets/starter/README.md)

远程联调时，部署包含接入代码的网页，在桌面开发设置选本机 `app.manifest.json` 并填写实际页面地址，含子路径时填完整路径。开发窗口加载的是所填地址，跨来源的顶层跳转可能被拦下。页面登录需要跳往其他域名时，先确认正常登录回到应用页面的接法，再检查握手。正式安装清单中的 `ui.type: "remote"` 和 HTTPS `ui.url` 属于应用交付配置。

验收时记录实际加载的页面地址和框架。涉及 AppHost 的联调按[打开开发窗口](../SKILL.md#打开开发窗口)检查握手和功能。仅预览页面和路由时，可以用普通浏览器。热更新使用项目已有能力，已部署的页面通过刷新检查更新。需要验证 Agent 时，用测试模型发一条消息并在刷新后读回原会话。
