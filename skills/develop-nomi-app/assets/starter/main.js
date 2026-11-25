import { connectNomi, restoreTest, sendTest } from "./nomi-app.js"

const status = document.querySelector("#status")
const identity = document.querySelector("#identity")
const reply = document.querySelector("#reply")
const form = document.querySelector("#send")
const modelSelect = form.elements.namedItem("model")
const button = form.querySelector("button")

function show(result) {
  const nextStep = {
    creation_unknown: "尚未确认会话创建。可以稍后按 F5 查询原请求。",
    created: "已确认原会话创建。此次未提交消息，可以手动开始新的测试。",
    submitted: "消息已提交。可以按 F5 查看原消息结果。",
    unknown: "尚未查到这条消息的运行。可以稍后按 F5 查询原消息。",
  }[result.status]
  reply.textContent = [
    `会话 ${result.checkpoint.sessionId}`,
    result.runId && `运行 ${result.runId}`,
    `状态 ${result.status}`,
    result.reply || nextStep || "本次运行没有可显示的助手回复。",
  ].filter(Boolean).join("\n")
}

async function start() {
  const nomi = await connectNomi()
  const { context, dataScopeId } = nomi
  status.textContent = `已连接 Nomi ${context.hostVersion} · Host API ${context.hostApiVersion}`
  identity.textContent = `开发项目 ID ${context.appId}\n数据 ID ${dataScopeId}`
  try {
    const previous = await restoreTest(nomi, AbortSignal.timeout(120_000))
    if (previous) show(previous)
  } catch (error) {
    reply.textContent = `读取原会话失败。${error.message}`
  }
  const providers = await nomi.client.models.list({ signal: AbortSignal.timeout(15_000) })
  let preferredModel
  for (const provider of providers) {
    for (const model of provider.models) {
      const value = JSON.stringify({ provider: provider.name, model: model.id })
      modelSelect.add(new Option(`${provider.displayName} / ${model.label}`, value))
      if (["bobannomi", "nomi-dev-bobannomi"].includes(provider.name)) preferredModel ??= value
    }
  }
  if (modelSelect.options.length === 1) {
    status.textContent = "已连接 Nomi。请为此项目配置 BobanNomi 模型服务或其他 OpenAI 兼容网关，再按 F5。"
    return
  }
  if (preferredModel) modelSelect.value = preferredModel
  button.disabled = false
  form.addEventListener("submit", async event => {
    event.preventDefault()
    if (button.disabled) return
    button.disabled = true
    reply.textContent = "正在等待回复…"
    try {
      const cwd = form.elements.namedItem("cwd").value.trim()
      if (!cwd) throw new Error("请输入会话执行目录。")
      const result = await sendTest(nomi, cwd, JSON.parse(modelSelect.value), AbortSignal.timeout(120_000))
      show(result)
      if (result.status === "submitted") return
    } catch (error) {
      reply.textContent = `本次测试未完成。${error.message}\n如果刚提交过，按 F5 查询原结果。`
      return
    }
    button.disabled = false
  })
}

start().catch(error => {
  status.textContent = error.details?.reason === "host_port_timeout"
    ? "未收到 Nomi 宿主连接，请从 Nomi 开发窗口打开此地址。"
    : `开发联调未就绪。${error.message}`
})
