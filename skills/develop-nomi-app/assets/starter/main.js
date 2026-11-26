import { connectNomi, restoreLastMessage, sendMessage } from "./nomi-app.js"

const status = document.querySelector("#status")
const identity = document.querySelector("#identity")
const reply = document.querySelector("#reply")
const sentMessage = document.querySelector("#sent-message")
const sentText = document.querySelector("#sent-text")
const runDetails = document.querySelector("#run-details")
const runInfo = document.querySelector("#run-info")
const form = document.querySelector("#send")
const modelSelect = form.elements.namedItem("model")
const messageInput = form.elements.namedItem("message")
const replyMode = form.elements.namedItem("replyMode")
const workspaceSelect = form.elements.namedItem("workspace")
const addProject = document.querySelector("#add-project")
const button = form.querySelector('button[type="submit"]')

const providerId = import.meta.env.VITE_NOMI_PROVIDER_ID?.trim()
const modelId = import.meta.env.VITE_NOMI_MODEL_ID?.trim()
const providers = providerId && modelId ? [{
  name: providerId,
  displayName: providerId,
  models: [{ id: modelId, label: modelId, provider: providerId, providerName: providerId }],
}] : []

function show(result) {
  const nextStep = {
    creation_unknown: "尚未确认会话创建。可以稍后按 F5 查询原请求。",
    created: "已确认原会话创建。此次未提交消息，可以重新发送消息。",
    submitted: "消息已提交。可以按 F5 查看原消息结果。",
    unknown: "尚未查到这条消息的运行。可以稍后按 F5 查询原消息。",
  }[result.status]
  sentText.textContent = result.inputText ?? ""
  sentMessage.hidden = !result.inputText || result.status === "creation_unknown" || result.status === "created"
  reply.textContent = result.reply || nextStep || "本次运行没有可显示的助手回复。"
  runInfo.textContent = [
    `会话 ${result.sessionId}`,
    result.runId && `运行 ${result.runId}`,
    `状态 ${result.status}`,
  ].filter(Boolean).join("\n")
  runDetails.hidden = false
}

function addWorkspace({ id, displayName }) {
  if (![...workspaceSelect.options].some(option => option.value === id)) {
    workspaceSelect.add(new Option(displayName, id))
  }
}

async function start() {
  const nomi = await connectNomi({ providers })
  const { context, dataScopeId } = nomi
  status.textContent = `已连接 Nomi ${context.hostVersion} · Host API ${context.hostApiVersion}`
  identity.textContent = `开发项目 ID ${context.appId}\n数据 ID ${dataScopeId}`
  try {
    const previous = await restoreLastMessage(nomi, AbortSignal.timeout(120_000))
    if (previous) show(previous)
  } catch (error) {
    reply.textContent = `读取原会话失败。${error.message}`
  }
  let cursor
  do {
    const page = await nomi.host.workspace.list(cursor ? { cursor } : undefined)
    page.entries.forEach(addWorkspace)
    cursor = page.nextCursor
  } while (cursor)
  addProject.disabled = false
  addProject.addEventListener("click", async () => {
    addProject.disabled = true
    try {
      const workspace = await nomi.host.workspace.pick()
      if (!workspace) return
      addWorkspace(workspace)
      workspaceSelect.value = workspace.id
    } catch (error) {
      reply.textContent = `无法选择项目。${error.message}`
    } finally {
      addProject.disabled = false
    }
  })
  for (const provider of await nomi.client.models.list()) {
    for (const model of provider.models) {
      const value = JSON.stringify({ provider: provider.name, model: model.id })
      modelSelect.add(new Option(`${provider.displayName} / ${model.label}`, value))
    }
  }
  if (modelSelect.options.length === 1) {
    status.textContent = "已连接 Nomi。请按 README 提供供应商 ID 和模型 ID，再重启开发服务。"
    return
  }
  button.disabled = false
  form.addEventListener("submit", async event => {
    event.preventDefault()
    if (button.disabled) return
    const inputText = messageInput.value.trim()
    if (!inputText) {
      messageInput.focus()
      return
    }
    button.disabled = true
    messageInput.disabled = true
    replyMode.disabled = true
    runDetails.hidden = true
    try {
      const model = JSON.parse(modelSelect.value)
      sentText.textContent = inputText
      sentMessage.hidden = false
      reply.textContent = "正在等待回复…"
      const onText = replyMode.value === "stream"
        ? text => { reply.textContent = text || "正在等待回复…" }
        : undefined
      const result = await sendMessage(nomi, workspaceSelect.value, model, inputText, { signal: AbortSignal.timeout(120_000), onText })
      show({ ...result, inputText })
      if (result.status !== "creation_unknown") messageInput.value = ""
      if (result.status === "submitted") return
    } catch (error) {
      reply.textContent = `本次测试未完成。${error.message}\n如果刚提交过，按 F5 查询原结果。`
      return
    } finally {
      messageInput.disabled = false
      replyMode.disabled = false
    }
    button.disabled = false
  })
}

start().catch(error => {
  status.textContent = error.details?.reason === "host_port_timeout"
    ? "未收到 Nomi 宿主连接，请从 Nomi 开发窗口打开此地址。"
    : `开发联调未就绪。${error.message}`
})
