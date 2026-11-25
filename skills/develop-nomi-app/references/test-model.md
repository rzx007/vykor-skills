# 给开发项目配置测试模型

每个开发项目有独立的 Nomi 后台和模型配置。模型列表里已有 BobanNomi 提供的模型时，直接选一个可用模型发送测试消息。要新增模型服务时，打开开发窗口并记下「开发项目 ID」和「数据 ID」。接入现有项目时，可以从 `connectNomi()` 的 `context.appId` 和 `dataScopeId` 获取这两个值。

## 默认使用 BobanNomi 模型服务

1. 使用 BobanNomi 账号的模型配置或服务提供方发给你的开发配置，确认 API 基础地址、模型凭据和可用模型 ID。以实际提供的基础地址为准，保留已有路径前缀。
2. 在该桌面实例实际使用的数据根目录下，找到 `data/app-platform/development/instances/<开发项目 ID>/data/daemon/registry.json`。默认根目录是用户主目录下的 `.bobannomi`，自定义启动参数以实际目录为准。只需要文件路径。它属于开发后台，里面有管理凭据。终端只把路径和页面显示的数据 ID 传给脚本。
3. 保持开发窗口打开。在运行 Nomi 的机器上通过本机的机密配置方式设置 `NOMI_DEV_BOBANNOMI_URL` 和 `NOMI_DEV_BOBANNOMI_API_KEY`，分别填 API 基础地址和模型凭据。在复制后的示例目录运行以下命令。已有 Web 项目可以把 [configure-model.mjs](../assets/starter/configure-model.mjs) 放在已安装 Client SDK 的项目目录里，直接运行 `node configure-model.mjs` 并传相同参数。

```sh
npm run configure:model -- "<开发项目 registry.json 的绝对路径>" "<页面上的数据 ID>" "<BobanNomi 模型 ID>"
```

脚本用本机登记文件取得管理员连接，核对后台的实际数据目录、数据 ID 和进程，再用 `client.modelProviders` 配置该开发项目并检查模型目录。回到开发窗口按 F5，用页面的 `client.models.list()` 刷新列表。网页通过当前应用获准的 Agent 连接读取模型，创建会话时传供应商和模型 ID。

应用有独立目录时，可以把 `ModelProviderInfo[]` 或 `({ signal }) => loadProviderList({ signal })` 传给 `new BobanNomiClient({ ...connection.clientOptions, providers })`。`client.models.list()` 返回应用目录，创建或切换会话仍要求选中的两个 ID 对应已保存的后台配置。管理员可用上面的脚本配置执行连接。目录只存放标识、显示名和能力。

普通应用按 starter 的方式提交输入。daemon 会绑定 BobanNomi Run 的已保存连接，排队和继续已中断运行时沿用原绑定。遇到 `model_connection_changed` 时保留草稿并检查已配置的连接。需要改用新连接时发起新的输入。

## 使用其他 OpenAI 兼容网关

设置 `NOMI_DEV_GATEWAY_URL` 为网关提供的 API 基础地址。网关要求认证时，再设置 `NOMI_DEV_GATEWAY_API_KEY`。网关可以是 Nomi 后台能访问的本地服务或远程服务。命令末尾加上 `gateway`，模型 ID 使用该服务实际提供的值。配置仍写入指定开发项目的后台。

```sh
npm run configure:model -- "<开发项目 registry.json 的绝对路径>" "<页面上的数据 ID>" "<网关模型 ID>" gateway
```

模型服务的密钥由本机终端和开发后台持有。远程服务使用 HTTPS 可以保护传输中的密钥和消息内容。

## 常见卡点

- 没有登记文件或数据 ID 时，先确认项目已经在 Nomi 开发窗口握手。网页单独在普通浏览器打开时，无法取得项目后台连接。
- 页面调用供应商管理接口会被拒绝。使用本机终端和该开发项目的登记文件运行配置脚本，管理员 token 和模型服务凭据留在本机配置与后台。
- 模型列表为空时，核对服务基础地址、模型访问权限和项目的数据 ID。配置成功后刷新页面。
- 提交一次测试消息后，F5 读取原会话。收到持久化助手回复才算通过模型执行验收。模型列表连接测试通过只说明可以读到模型目录。
