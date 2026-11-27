# 接入应用自己的模型

开发者把供应商、模型列表和模型连接一起提供给 `BobanNomiClient`。应用用 `client.models.list()` 取得可选模型。用户选择后，Nomi 用该应用提供的连接执行会话。

- **自带供应商**。使用开发者已有的模型 ID、模型 API 基础地址和 API key。供应商的 `name` 是应用代码里的稳定标识。
- **数字员工**。应用登录后用账号访问令牌获取模型服务地址和 API key，再按需读取模型列表。 [数字员工远程 API](./digital-employee-api.md#模型目录)

下面的 `gatewayUrl`、`apiKey` 和 `models` 由应用提供。接入 Nomi 桌面时，使用 AppHost 已授予的 `agent` 能力。

```js
import { connectAppHost } from "@bobannomi/app-host"
import { BobanNomiClient } from "@bobannomi/client"

const host = await connectAppHost({ hostApi: "^0.1.3" })
const { clientOptions } = await host.getAuthorizedAgentConnection()
const name = "my-provider"
const displayName = "我的供应商"
const client = new BobanNomiClient({
  ...clientOptions,
  providers: [{
    name,
    displayName,
    models: models.map(({ id, label }) => ({ id, label, provider: displayName, providerName: name })),
    connection: { baseUrl: gatewayUrl, apiKey, apiFormat: "openai" },
  }],
})

const choices = (await client.models.list()).flatMap(provider =>
  provider.models.map(model => ({
    label: model.label,
    value: { provider: provider.name, model: model.id },
  })),
)

async function send(model, text) {
  const { id } = await client.sessions.create({ outsideProject: true, configuration: { model } })
  const session = client.sessions.byId(id)
  const { run } = await session.prompt({ items: [{ type: "text", text }] })
  return run ? session.waitForRun(run.id) : undefined
}
```

界面把选项的 `value` 传给 `send()`。已有会话可用 `session.configuration.update()` 切换模型，再发送消息。Starter 提供[选项目、完整或流式回复以及刷新恢复](../assets/starter/README.md#跑起来)。

`providers` 和供应商的 `connection` 都可以用接收 `{ signal }` 的异步函数。读取目录只返回展示数据。应用可把地址和密钥留在可信后台，在 SDK 需要执行时由当前登录按需取得。密钥仅随执行连接传给 Nomi，避免放进构建产物、模型目录和会话恢复记录。

创建会话或保存模型选择成功后，这次提供的地址和密钥才会生效。遇到配置版本冲突，重新读取配置版本再发起新保存。回包丢失时用原请求查询回执。联调时，用同一源码版本的 Nomi 和 Client SDK。

正式安装的应用在清单声明 `network.connect`，把模型网关的 HTTPS 来源放进 `network.allowedOrigins`，安装时一起批准。开发窗口支持 HTTPS 网关和本机测试网关。模型失败时核对当前账号的地址、密钥和模型 ID。
