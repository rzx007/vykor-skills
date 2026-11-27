---
name: develop-nomi-app
description: 为 Nomi 创建独立 Web 应用，或用 AppHost 和应用清单把 Vue、React、无框架或已部署的网页接入桌面宿主。适用于独立窗口、开发联调、应用自己的 Agent 会话，以及接入数字员工登录、模型、积分和充值。会话里的工具或侧栏交互优先用 create-plugin。
---

# 开发 Nomi 应用

让开发者用已安装的 Nomi 打开自己的 Web 页面。按任务验证页面接入，或进一步发出一条 Agent 消息并在刷新后读回同一次会话。

## 先判断做成什么

看用户从哪里开始操作、主要工作在哪里完成。用户口头说的「应用」或「小工具」，以及已有网页、远程 URL 和选用的框架，都不足以决定交付形态。

| 用户要做的事 | 推荐交付 |
| --- | --- |
| 打开独立页面完成整套业务，保留自己的页面、菜单、路由和数据。例如在独立窗口管理项目看板 | 用本技能做 Web 应用。需要 Agent 时，由应用发起自己的会话 |
| 给用户正在进行的 Nomi 会话增加一个可调用的能力。例如，让助手查任务并在会话侧栏显示结果、确认修改 | 用 `create-plugin`。工具负责查询或执行，需要用户操作时再加 MCP Apps 页面，也就是会话旁边的交互面板 |
| 给助手一份可复用的提示词或操作步骤 | 做普通 Skill |

用户明确指定交付形态时，按其要求，并指出会影响目标的限制。未指定时，给出与主要任务匹配的推荐和一句理由。比如，已有网页的业务接口可以直接被会话插件复用，用户只想在聊天里查数据时，推荐先做这个查询工具。两个入口确实都需要时，先明确主要入口，再复用已有业务服务。只有入口选择会改变交付且需求无法判断时，才问用户希望在独立页面完成任务，还是留在当前会话完成。

推荐插件时，转入 `create-plugin` 技能的制作流程。如果该技能尚未安装，指出需要载入它，并先列清楚会话入口、工具动作和是否需要交互面板。

## 接入项目

先确定用户希望开发的 Web 应用目录。接入已有项目时，用用户指定的应用目录，或在当前工作区定位用户指向的 Web 应用入口。新建项目时，使用用户给出的空目录，或在当前任务工作区选一个未占用的子目录并告诉用户路径。本技能的链接和示例从技能目录读取，清单、应用代码和项目命令都以选定的 Web 应用目录为准。

1. **现有项目**先看入口、包管理器、开发命令和构建路径。沿用现有框架、路由、组件和后端，把 Nomi 接入放进浏览器端入口或一个独立调试页。**空项目**以用户指定的框架起步，Vue 或 React 可以用[新建工程命令](references/web-ui.md#新建-vue-或-react-工程)。简单验证可直接复制无框架的[最小项目](assets/starter/README.md)。已有项目和部署站点的接法见[页面接入](references/web-ui.md)。
2. 需要连接宿主时安装公开 `@bobannomi/app-host`，需要 Agent 会话时再装 `@bobannomi/client`。已有项目沿用包管理器和锁文件。复制 Starter 后运行 `npm install`，安装发布版 AppHost 和 Client `0.5.0`，并选用支持应用模型连接的 Nomi。在项目根填写自己的应用 ID、名称、入口和权限。只验证页面和路由时，权限数组可留空，沿用项目原有依赖。 [版本和安装](assets/starter/README.md#版本) · [Starter 清单](assets/starter/app.manifest.json)
3. 启动项目的开发服务，记录终端实际输出且运行 Nomi 桌面的电脑能访问的 HTTP/HTTPS 地址。已有远程站点可以沿用部署方式。热更新由项目开发服务器提供。

应用需要用户选择本机目录并读取文本时，在清单声明 `workspace.select`，按[本机目录接入](references/web-ui.md#读用户选中的本机目录)从点击事件调用 `host.workspace.pick()`。

需要应用自己的本机业务进程时，按[托管服务接入和验收](references/web-ui.md#托管本机服务)准备应用 ZIP。服务提供本机 HTTP，页面用 `host.service` 验证业务连接。要公开 MCP 工具，在 `service.mcpPath` 声明路径，等服务就绪后从普通 MCP 列表验证。

要随应用包提供 Skill 或已经可连接的普通 MCP，按[清单声明和验证流程](references/web-ui.md#随应用提供-skill-和普通-mcp)配置 `agent.skills` 或 `agent.mcp`，安装后批准 `agent`。

## 打开开发窗口

本次任务涉及 AppHost 时（例如自定义标题栏、窗口拖动或最小化、目录选择、会话连接、应用存储），用终端发 HTTP 请求检查开发服务是否就绪。服务就绪后，第一次打开应用页面就用 `AppDevelopmentOpen` 或下面的手动开窗步骤。窗口已开时聚焦或刷新现有开发窗口。确认握手和授权后，再验证本次使用的能力。

服务就绪后，以当前会话能否调用 Nomi 工作台内置的 `AppDevelopmentOpen` 选择开窗方式。工具按需显示时，先用当前会话的工具查找功能按名称查找。

**Nomi 内置工具可用，且已确认本机清单路径。** 调用 `AppDevelopmentOpen`，传 `manifestPath`（Nomi 所在电脑上的 `app.manifest.json` 绝对路径）和 `url`（实际开发地址）。需要为开发副本指定后台数据目录时，额外传 `dataRoot`，填写 Nomi 所在电脑上的绝对目录。需要确认时，请用户在当前对话的卡片核对实际数据目录并确认。`opened` 或 `focused` 表示已开窗。收到 `denied` 就结束开窗步骤。收到 `changed` 就先核对当前项目、地址和数据目录，再发起请求。

**外部 Agent、内置工具不可用，或需要用户准备本机清单。** 说明实际原因和 AppHost 验收进度，直接给出以下手动开窗步骤，填入本次的实际项目或清单路径及完整地址。如果项目在远程机器或容器中，把清单文件或内容交给用户保存到 Nomi 所在电脑，并提供该电脑能访问的端口转发或部署地址。

1. 在 Nomi 桌面打开「常规设置 → 开发应用」，开启「应用开发者模式」。
2. 点「选择项目目录」或「选择清单文件」，选择本机的项目目录或 `app.manifest.json`。
3. 在「开发页面地址」填入实际 HTTP/HTTPS 地址，点「打开开发窗口」，按提示确认来源和能力。

Main 启动开发后台。手动开窗或省略 `dataRoot` 时，默认用当前用户主目录下的 `.<appId>`，其中 `appId` 取清单的 `id`。同一个 `appId` 的不同开发副本需要隔离时，分别传不同的绝对目录。使用同一目录会访问同一份数据库，会话可见范围仍由应用授权决定，同一目录同一时间只由一个后台占用。需要继续用原有开发库时，传它原来的数据根目录。

开发窗口以普通应用身份通过 AppHost 取得后台连接。联调结束后关闭窗口并确认，等 Nomi 停止开发后台再停 Web 开发服务。托管服务用正式安装的应用验收。开发窗口内的目录选择按清单授予 `workspace.select`。独立工作树、临时侧边聊天、Git 回执和目标窗口用 Nomi 自带的工作台验收。 [工作台能力参考](references/web-ui.md#工作台的会话准备和临时会话)

## 数字员工远程服务

数字员工登录、模型目录、积分和充值包含各自的接口、认证和订单结果查询。模型目录与连接一起通过 `providers` 传给 `BobanNomiClient`。 [数字员工远程 API](references/digital-employee-api.md) · [SDK 接入示例](references/digital-employee-api.md#把远程模型交给-sdk)

## 调用 Agent

应用需要 Nomi Agent 能力时，把实际发送入口接到 AppHost 授权的 Nomi 会话，用 `BobanNomiClient` 的 `session.prompt()` 发消息，从同一个 Run 读取结果。第三方聊天或终端组件负责界面交互。模型供应商决定 daemon 使用的连接。应用直连模型须有用户明确要求，调用路径以供应商文档为准。

模型来源还未明确时，先向用户说明下面两种接法。

- **自带供应商**。使用开发者提供的模型 ID、模型 API 地址和 API key。供应商标识由应用代码管理。 [模型目录和连接](references/test-model.md)
- **数字员工服务（可选）**。登录后取得账号访问令牌，再用它请求 `GET /digital/api/v1/model/provider`，获取模型服务的 Base URL（`apiUrl`）和 API key。需要模型列表时，用该 API key 请求 `GET {apiUrl}/models`。登录入口和登录后的业务流程由应用决定。 [数字员工登录](references/digital-employee-api.md#登录) · [获取模型配置和目录](references/digital-employee-api.md#模型目录)

模型来源待定时，可以先实现业务页面和待配置提示。取得模型来源后，把目录和执行连接一并传给 SDK。供应商的 `connection` 支持开发者配置的地址和密钥，或从当前登录异步取得。应用界面用目录生成选项，用户选模型即可发消息。正式安装时在清单里声明并获批模型网关的 HTTPS 来源。 [模型目录和连接](references/test-model.md)

在开发窗口用 `connectAppHost()` 握手。核对 `session-resources-v1` 和 `agent` 授权，再用 `host.getAuthorizedAgentConnection()` 返回的 `clientOptions` 和开发者提供的 `providers` 列表或异步加载函数创建 `BobanNomiClient`。从 `client.models.list()` 选供应商 `name` 和模型 `id`，填入 `client.sessions.create()` 的 `configuration.model`。用 AppHost 选择项目时传 `workspaceId`，项目外会话传 `outsideProject: true`。直接连接已有 daemon 时，可以传由该后台访问的执行目录作为 `cwd`。 [Starter 开发窗口步骤](assets/starter/README.md#跑起来)

同一页面共享的 Agent 连接由 AppHost 管理。组件用自己的 `AbortController` 取消请求和订阅。需要停止后台运行时，调用 `session.interrupt()`。

普通应用页面的连接用于获准的会话操作。插件、渠道、后台 MCP、项目登记或清理等操作由有管理权限的后台连接发起。用户选择本机目录时使用 AppHost，返回的目录 ID 用于 AppHost 文件访问。daemon 按已登记项目创建会话时使用该 daemon 的 `projectId`。

桌面用户可以从内置工作台的「应用设置 → 连接」配置飞书。独立应用需要管理渠道时，在可信后台使用 `client.channels` 和对应的管理连接。

### 会话工具、状态和回复

- **声明工具。** 在清单声明 `agent` 并取得授权。创建会话时在 `configuration.tools.allowed` 填需要的工具名，例如 `WebSearch`、`WebFetch` 或 `AskUser`。`allowed: []` 关闭所有工具，省略 `allowed` 使用后台和角色的默认工具范围，仍受权限限制。
- **获取运行状态。** 用 `client.sessions.byId(sessionId)` 取得会话对象，再用 `session.prompt()` 提交输入。用回执里的 `run.id` 区分本次运行。回执尚无 `run` 或回包丢失时，按原输入 ID 从 `session.getState()` 或后续更新查输入和关联的运行。用 `session.observe({ signal })` 同时读取运行、消息和权限。 [Starter 会话示例](assets/starter/nomi-app.js)
- **处理审批和提问。** 会话可以用 `configuration.approvalMode: "ask"` 让需要审批的操作等待用户决定。普通应用用同一个 Client 观察自己获准访问的会话的运行和待处理请求。`Shell`、`Write` 等普通工具审批按用户选择用 `client.permissions.requests.reply()` 提交，`AskUser` 提问用 `requests.answerQuestion()` 提交。两者都使用原请求 ID。应用决定如何把请求交给用户，daemon 核对会话和请求，再决定运行能否继续。 [审批和提问入口](references/web-ui.md#会话里的权限后台任务和附件)

  联调普通应用的工具审批时，使用支持应用回复人工审批的 Nomi 后台。Nomi 1.2.38 可以查到 `Shell` 或 `Write` 的待审请求，提交回复时会返回 `403 resource_unavailable`。

- **把回复交给应用。** `session.waitForRun(run.id)` 返回 `{ run, messages }`，先看 `run.status` 再处理结果。实时读取时从 `session.observe()` 取 `messages`，按 `message.runId` 取本轮消息。每条消息都包含 `{ message, parts }`，例如从 `message.role === "assistant"` 的消息中取 `part.type === "text"` 的正文。界面怎么展示、回复如何保存或交给哪段业务代码，都由应用开发者决定。

在 BobanNomi 源码的 `apps/client-docs/examples/node/` 下可参考 `first-run.ts`、`sync-events.ts` 和 `run-with-permissions.ts`。`apps/client-docs/src/content/docs/guides/permissions.mdx` 还演示了 `AskUser` 的单独答复。

需要刷新恢复时，创建前保存会话 ID、创建请求 ID 和原参数，发送前保存输入 ID。刷新后重新握手，核对安装身份和后台数据身份。Starter 用 `client.sessions.getCreationResult()` 查未确认的创建，用 `session.getState()` 按原输入 ID 找 Run ID，再用同一个 `waitForRun()` 读取回复。

应用要调整已有会话的模型或工具时，先用 `session.configuration.get()` 读取有效配置和版本。保存数据范围、会话 ID 和原请求，再调用 `session.configuration.update()` 提交要修改的字段。回包丢失后，在原数据范围用 `session.configuration.getResult()` 查结果。收到版本冲突时重新读取并让用户确认。

后台任务从 `session.jobs` 查询。需要附件时，先检查宿主是否提供草稿附件连接。 [会话里的后台任务和附件](references/web-ui.md#会话里的权限后台任务和附件)

## 验收和排查

- 任务只验收页面展示、路由或热更新时，可以用内置浏览器或普通浏览器走原有 Web 流程。
- 本机目录验收从已批准 `workspace.select` 的应用窗口开始。确认取消选择、列出目录、读取文本，以及刷新后用保存的目录 ID 重新打开。再停止 Agent 后台，检查当前应用仍能列目录和读文本。
- 托管服务验收从已安装的应用启动，观察 `host.service` 的就绪状态并提交一笔业务。页面刷新后用原请求 ID 查结果，完全退出 Nomi 桌面后确认进程已停止。
- 用户要发布可安装 ZIP 时，按安装后的实际地址和服务在 Nomi 验收本次功能。开发源码 ZIP 标明用途。
- 加载失败先检查服务地址和页面来源。握手失败先确认打开的是开发窗口，再核对 Nomi、SDK 版本和本次使用的宿主功能。模型列表为空时检查传入的 `providers`。模型不可运行时核对应用提供的连接、当前账号和所选模型。 [模型目录和连接](references/test-model.md)
- 实际验收记录加载地址、Nomi 和 SDK 版本。手动开窗以用户反馈或实际的宿主连接结果为准。Agent 验收从应用实际发送入口追到 `session.prompt()`，确认同一次 Nomi 运行返回回复，并在刷新后核对原会话、运行和回复。切换项目时 Nomi 会先保存旧页面并停止原开发后台。
- 应用接入审批或提问时，从自己的会话触发对应请求，核对原请求 ID、用户决定和同一次运行的后续状态。

交付项目改动、可运行命令和实际验证结果，写清页面构建和 Nomi 联调各做到哪一步。本技能面向开发联调，使用现有 Nomi 安装和项目开发命令。
