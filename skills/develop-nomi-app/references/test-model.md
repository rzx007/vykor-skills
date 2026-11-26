# 提供模型目录和连接

开发者提供供应商 ID、模型 ID、模型 API 基础地址和 API key。目录来源由应用决定，可以直接填写，也可以调用自己的模型服务。使用数字员工服务时，按需登录，用账号令牌换取模型 API 地址和 key，再读取目录。 [数字员工远程 API](./digital-employee-api.md#模型目录)

## 给页面提供目录

复制 Starter 后，在项目根的 `.env.local` 填入实际供应商 ID 和模型 ID。启动 Vite 时会读取这两个值。

```dotenv
VITE_NOMI_PROVIDER_ID=your-provider
VITE_NOMI_MODEL_ID=your-model
```

Starter 把这两个 ID 整理成 `ModelProviderInfo[]`，随 AppHost 给出的会话连接一起传给 `new BobanNomiClient({ ...connection.clientOptions, providers })`。应用也可以给 `providers` 传自己的异步加载函数。目录可含显示名及能力，`VITE_` 变量会进入页面代码，API key 留在开发者的后台或管理程序。

## 显式保存执行连接

发送消息前，由开发者的管理程序把模型地址、API key 和可执行模型保存到对应项目的 daemon。使用该 daemon 的地址和管理员 token，供应商 ID 和模型 ID 要与页面目录一致。以下示例中的变量由开发者提供，`gatewayUrl` 使用供应商给出的完整 API 基础地址。

```js
import { BobanNomiClient } from "@bobannomi/client"

const admin = new BobanNomiClient({ baseUrl, token })
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

使用已有供应商 ID 更新连接时调用 `admin.modelProviders.updateCustom({ provider: providerId, value })`。管理程序可以用 `admin.modelProviders.defaults.test({ provider: providerId, model: modelId })` 检查连接。AppHost 给普通应用页面的会话连接只用于获准的会话操作。

开发窗口为当前项目启动独立 daemon。需要在本机取得它的管理连接时，按以下步骤定位。

1. 在 Starter 展开「开发连接信息」，记下开发项目 ID 和数据 ID。接入自己的页面时，分别从 `host.getContext()` 和已认证的 `client.protocol.capabilities({ authenticated: true, scope: "protocol" })` 读取 `appId` 和 `dataScopeId`。
2. 在 Nomi 的「存储」设置点「打开数据目录」。会话数据库所在目录的上一级是 `data`。从该级进入 `app-platform/development/instances/<开发项目 ID>/data/daemon/`，找到 `registry.json`。打开开发窗口期间读取这份文件。
3. 在本机 Node 管理程序从 `@bobannomi/client/service` 导入 `Service`。用 `Service.discover({ file })` 查询该文件对应的运行实例。取得 `endpoint` 后，用 `new BobanNomiClient(Service.clientOptions(endpoint))` 建立管理连接。查不到实例时，确认对应的开发窗口还开着，并核对路径和项目 ID。保存配置前，通过该连接的 `protocol.capabilities({ authenticated: true, scope: "protocol" })` 核对 `dataScopeId` 和页面显示的数据 ID 一致。登记文件和管理员 token 留在本机。

页面从 `client.models.list()` 读取应用提供的目录，把选中的 ID 写进 `configuration.model = { provider: providerId, model: modelId }`，再发送测试消息并读取回复。模型不可运行时，核对当前后台保存的供应商和模型 ID，以及地址和 API key。
