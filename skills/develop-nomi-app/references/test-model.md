# 提供模型目录和连接

自带供应商时，由开发者提供供应商 ID、模型 ID、模型 API 基础地址和 API key。使用数字员工时，登录后用账号访问令牌获取模型服务的 Base URL 和 API key，需要目录时再用这组连接信息请求模型列表。 [数字员工远程 API](./digital-employee-api.md#模型目录)

## 给页面提供目录

复制 Starter 后，在项目根的 `.env.local` 填入实际供应商 ID 和模型 ID。启动 Vite 时会读取这两个值。

```dotenv
VITE_NOMI_PROVIDER_ID=your-provider
VITE_NOMI_MODEL_ID=your-model
```

Starter 把这两个 ID 整理成 `ModelProviderInfo[]`，随 AppHost 给出的会话连接一起传给 `new BobanNomiClient({ ...connection.clientOptions, providers })`。应用也可以给 `providers` 传自己的异步加载函数。目录可含显示名及能力，`VITE_` 变量会进入页面代码，API key 留在开发者的后台或管理程序。

## 显式保存执行连接

发送消息前，由有管理权限的程序把模型地址、API key 和可执行模型保存到目标 daemon。管理连接由该 daemon 的管理方明确提供。示例中的 `daemonBaseUrl` 和 `daemonAdminToken` 用于连接 Nomi 后台，`gatewayUrl` 和 `apiKey` 来自模型供应商。供应商 ID 和模型 ID 与页面目录一致。`apiFormat: "openai"` 是 daemon 使用的供应商协议设置。接入 Nomi Agent 的应用通过 `session.prompt()` 提交消息，由 daemon 用已保存的连接调用模型。

```js
import { BobanNomiClient } from "@bobannomi/client"

const admin = new BobanNomiClient({ baseUrl: daemonBaseUrl, token: daemonAdminToken })
const value = {
  id: providerId,
  displayName: providerId,
  baseUrl: gatewayUrl,
  apiKey,
  apiFormat: "openai",
  models: [{ id: modelId, displayName: modelId }],
}
await admin.modelProviders.createCustom({ value })
```

使用已有供应商 ID 更新连接时调用 `admin.modelProviders.updateCustom({ provider: providerId, value })`。管理程序可以用 `admin.modelProviders.defaults.test({ provider: providerId, model: modelId })` 检查连接。

开发窗口内的普通应用通过 `host.sessions.getConnection()` 获取会话连接。供应商写入使用管理方提供的连接，管理凭据留在获授权的管理端。Vite 用于开发页面，应用托管服务沿用应用自身的授权范围。当前只有会话连接时，显示「待配置模型」，先确认页面和 AppHost 握手，再由管理方保存连接并验证真实回复。

页面从 `client.models.list()` 读取应用提供的目录，把选中的 ID 写进 `configuration.model = { provider: providerId, model: modelId }`，再发送测试消息并读取回复。模型不可运行时，核对当前后台保存的供应商和模型 ID，以及地址和 API key。
