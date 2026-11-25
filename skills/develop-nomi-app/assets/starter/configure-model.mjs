import { realpath } from "node:fs/promises"
import { dirname, isAbsolute, join, normalize, sep } from "node:path"
import { BobanNomiClient } from "@bobannomi/client"
import { Service } from "@bobannomi/client/service"

const [registryArg, scopeId, modelId, mode = "bobannomi"] = process.argv.slice(2)
class ConfigurationError extends Error {}

async function configure() {
  if (!registryArg || !isAbsolute(registryArg) || !scopeId || !modelId?.trim() || !["bobannomi", "gateway"].includes(mode)) {
    throw new ConfigurationError('用法 npm run configure:model -- "<开发项目 registry.json 的绝对路径>" "<页面的数据 ID>" "<模型 ID>" [bobannomi|gateway]')
  }
  const file = await realpath(registryArg)
  const privateRoot = dirname(dirname(dirname(file)))
  const parts = normalize(file).split(sep).slice(-6)
  if (parts[0] !== "development" || parts[1] !== "instances" || !/^_nomi-dev-[a-f0-9]{64}$/.test(parts[2]) ||
      parts.slice(3).join("/") !== "data/daemon/registry.json") {
    throw new ConfigurationError("请选择当前开发项目的登记文件，路径应位于 development/instances/ 下。")
  }
  const endpoint = await Service.discover({ file, timeoutMs: 5_000 })
  if (!endpoint) throw new ConfigurationError("未找到可连接的开发后台。请保持该项目的开发窗口打开，并核对登记文件路径。")
  const client = new BobanNomiClient(Service.clientOptions(endpoint))
  const signal = AbortSignal.timeout(30_000)
  const { dataScopeId, daemonStorage } = await client.protocol.capabilities({ authenticated: true, scope: "protocol", signal })
  if (dataScopeId !== scopeId || daemonStorage?.pid !== endpoint.pid ||
      daemonStorage.configDir !== privateRoot || daemonStorage.storePath !== join(privateRoot, "data", "session-runtime", "sessions.db")) {
    throw new ConfigurationError("登记文件与当前开发窗口的数据身份不一致。请核对页面上的数据 ID 和登记文件路径。")
  }

  const official = mode === "bobannomi"
  const id = official ? "nomi-dev-bobannomi" : "nomi-dev-gateway"
  if (official) {
    const models = await client.models.list({ signal })
    if (models.some(provider => ["bobannomi", id].includes(provider.name) && provider.models.some(model => model.id === modelId))) {
      console.log(`开发后台已列出 BobanNomi 模型 ${modelId}。回到开发窗口按 F5 后选择它。`)
      return
    }
  }
  const address = (official ? process.env.NOMI_DEV_BOBANNOMI_URL : process.env.NOMI_DEV_GATEWAY_URL)?.trim()
  const apiKey = (official ? process.env.NOMI_DEV_BOBANNOMI_API_KEY : process.env.NOMI_DEV_GATEWAY_API_KEY)?.trim()
  if (official && (!address || !apiKey)) {
    throw new ConfigurationError("请按 BobanNomi 提供的模型配置填写 NOMI_DEV_BOBANNOMI_URL 和 NOMI_DEV_BOBANNOMI_API_KEY。")
  }
  if (!address) throw new ConfigurationError("请填写 NOMI_DEV_GATEWAY_URL，使用网关提供的 API 基础地址。")
  const url = URL.parse(address)
  if (!url || !["http:", "https:"].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new ConfigurationError("模型服务地址应是无内嵌凭据、查询参数或片段的 HTTP 或 HTTPS API 基础地址。")
  }
  const baseUrl = url.href.replace(/\/+$/, "")
  const existing = (await client.modelProviders.list({ signal })).find(row => row.name === id)
  if (!existing) {
    await client.modelProviders.createCustom({ value: {
      id, displayName: official ? "BobanNomi 模型服务" : "开发网关", baseUrl, apiFormat: "openai",
      ...(apiKey && { apiKey }),
      models: [{ id: modelId, displayName: modelId }],
    } }, { signal })
  } else if (existing.source !== "custom" || existing.baseUrl?.replace(/\/+$/, "") !== baseUrl || !existing.models.some(row => row.id === modelId)) {
    throw new ConfigurationError(`开发后台里已有 ${id}，其地址或模型不同。请先检查已有配置。`)
  }
  const check = await client.modelProviders.defaults.test({ provider: id, model: modelId }, { signal })
  if (check.status !== "verified") {
    const category = {
      address: "基础地址有误", authentication: "认证失败", model: "模型不在供应商目录中",
      network: "无法连接模型服务", unsupported: "供应商不支持连接测试", service: "模型服务出错",
    }[check.category] ?? "模型连接测试失败"
    throw new ConfigurationError(category)
  }
  console.log(`开发后台的模型已就绪：${id} / ${modelId}。回到开发窗口按 F5。`)
}

configure().catch(error => {
  // SDK errors may include provider response bodies. Keep those out of terminal output.
  const message = error instanceof ConfigurationError ? error.message
    : error.code === "ENOENT" ? "找不到指定的开发后台登记文件。请核对路径和开发窗口状态。"
    : "模型配置请求失败，请检查本机地址、模型及开发后台版本。"
  console.error(message)
  process.exitCode = 1
})
