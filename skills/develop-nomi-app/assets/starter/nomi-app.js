import { connectAppHost } from "@bobannomi/app-host"
import { BobanNomiClient } from "@bobannomi/client"

const checkpointKey = "nomi-app-starter.last-test.v2"

/** @param {Pick<import("@bobannomi/client").BobanNomiClientOptions, "providers"> & { signal?: AbortSignal }} [options] */
export async function connectNomi({ providers, signal } = {}) {
  const host = await connectAppHost({ hostApi: "^0.1.3" })
  if (!["session-resources-v1", "workspace-v1", "resource-catalog-v1"].every(feature => host.hasFeature(feature))) {
    throw new Error("Nomi 未提供目录选择或会话准备，请更新桌面版并从开发窗口打开。")
  }
  const context = await host.getContext()
  if (context.capabilities["app.storage"]?.granted !== true) {
    throw new Error("请批准 app.storage，用于保存会话和原请求 ID。")
  }
  if (context.capabilities.agent?.granted !== true) {
    throw new Error("请在 Nomi 中批准 agent 能力后重新打开应用。")
  }
  if (!context.capabilities["workspace.select"]?.granted || !context.capabilities["workspace.execute"]?.granted) {
    throw new Error("请在 Nomi 中批准目录选择和项目执行权限。")
  }
  signal?.throwIfAborted()
  const { clientOptions } = await host.getAuthorizedAgentConnection()
  const client = new BobanNomiClient({ ...clientOptions, providers })
  // capabilities 会按安装的 Client SDK 检查后台协议版本。
  const { dataScopeId, features } = await client.protocol.capabilities({ authenticated: true, scope: "protocol", signal })
  if (!dataScopeId) throw new Error("无法确认当前 Agent 后台的数据身份。")
  if (!features.sessionDirectoryCreation || (providers && !features.sessionModelConnections)) {
    throw new Error("当前 Nomi 后台还未提供应用模型连接和会话目录，请更新桌面版后重新打开。")
  }
  return { host, client, context, dataScopeId }
}

export async function sendMessage(nomi, workspaceId, model, inputText, { signal, onText } = {}) {
  const { host, client, context, dataScopeId } = nomi
  // 先生成 ID，刷新或丢回包后可以查同一次操作。
  const sessionId = crypto.randomUUID()
  const promptId = crypto.randomUUID()
  const creation = {
    id: sessionId,
    ...(workspaceId ? { workspaceId } : { outsideProject: true }),
    requestId: crypto.randomUUID(),
    configuration: { model, tools: { allowed: [] }, pluginsEnabled: false, memory: { enabled: false } },
  }
  const checkpoint = { sessionId, promptId, installationId: context.installationId, dataScopeId }
  const pending = { ...checkpoint, creation }
  await host.storage.set(checkpointKey, pending)
  const created = await client.sessions.create(creation, { signal })
  if (created.id !== sessionId) return { sessionId, status: "creation_unknown" }
  await host.storage.set(checkpointKey, checkpoint)
  const session = client.sessions.byId(sessionId)
  const { run } = await session.prompt({
    id: promptId,
    items: [{ type: "text", text: inputText }],
  }, { signal })
  if (!run) return { sessionId, status: "submitted" }
  return onText
    ? streamReply(session, run.id, signal, onText)
    : readReply(session, run.id, signal)
}

export async function restoreLastMessage(nomi, signal) {
  const { host, client, context, dataScopeId } = nomi
  const saved = await host.storage.get(checkpointKey)
  if (!saved.found) return undefined
  const { sessionId, promptId, creation, installationId, dataScopeId: savedScope } = saved.value
  if (installationId !== context.installationId || savedScope !== dataScopeId) {
    throw new Error("当前应用的数据身份与保存的会话不同。")
  }
  if (creation) {
    const receipt = await client.sessions.getCreationResult({ sessionId, requestId: creation.requestId, original: creation }, { signal })
    if (receipt?.state !== "completed" || receipt.sessionId !== sessionId ||
        receipt.dataScopeId !== dataScopeId || receipt.requestId !== creation.requestId) {
      return { sessionId, status: "creation_unknown" }
    }
    return { sessionId, status: "created" }
  }
  const session = client.sessions.byId(sessionId)
  const { inputs, runs } = await session.getState({ signal, partView: "summary" })
  const input = inputs.find(input => input.id === promptId)
  const run = runs.find(run => run.inputId === promptId)
  if (!run) return { sessionId, status: input ? "submitted" : "unknown", inputText: input?.content }
  return { ...await readReply(session, run.id, signal), inputText: input?.content }
}

async function readReply(session, runId, signal) {
  const { run, messages } = await session.waitForRun(runId, { signal })
  return { sessionId: session.id, runId, status: run.status, reply: assistantText(messages) }
}

async function streamReply(session, runId, signal, onText) {
  let displayed = ""
  for await (const { runs, messages } of session.observe({ signal })) {
    const run = runs.find(candidate => candidate.id === runId)
    if (!run) continue
    const reply = assistantText(messages.filter(({ message }) => message.runId === runId))
    if (run.status !== "pending" && run.status !== "running") {
      return { sessionId: session.id, runId, status: run.status, reply }
    }
    // 每次用 SDK 合并后的正文刷新气泡，重连或模型重试时也走同一条链路。
    if (reply !== displayed) {
      displayed = reply
      onText(reply)
    }
  }
  signal?.throwIfAborted()
  throw new Error("未读到该次运行的最终状态。")
}

function assistantText(messages) {
  return messages
    .filter(({ message }) => message.role === "assistant")
    .map(({ parts }) => parts.filter(part => part.type === "text").map(part => part.text ?? "").join(""))
    .join("\n").trim()
}
