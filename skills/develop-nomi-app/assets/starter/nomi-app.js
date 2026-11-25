import { connectAppHost } from "@bobannomi/app-host"
import {
  applySessionSnapshot,
  BobanNomiClient,
  createInitialClientState,
  createPromptRequestId,
  selectVisibleSessionMessagesWithParts,
} from "@bobannomi/client"

const checkpointKey = "nomi-app-starter.last-test"

/** @param {Pick<import("@bobannomi/client").BobanNomiClientOptions, "providers">} [options] */
export async function connectNomi({ providers } = {}) {
  const host = await connectAppHost({ hostApi: "^0.1.3" })
  if (!host.hasFeature("session-resources-v1")) throw new Error("Nomi 未提供会话连接，请核对桌面版与 SDK 版本。")
  const context = await host.getContext()
  if (context.capabilities["app.storage"]?.granted !== true) {
    throw new Error("请批准 app.storage，用于保存会话和原请求 ID。")
  }
  if (context.capabilities.agent?.granted !== true) {
    throw new Error("请在 Nomi 中批准 agent 能力后重新打开应用。")
  }
  const connection = await host.sessions.getConnection()
  const client = new BobanNomiClient({ ...connection.clientOptions, providers })
  // capabilities 会按安装的 Client SDK 检查后台协议版本。
  const { dataScopeId } = await client.protocol.capabilities({ authenticated: true, scope: "protocol" })
  if (!dataScopeId) throw new Error("无法确认当前 Agent 后台的数据身份。")
  return { host, client, context, dataScopeId }
}

export async function sendTest(nomi, cwd, model, signal) {
  const { host, client, context, dataScopeId } = nomi
  const creation = {
    cwd,
    id: createPromptRequestId(),
    requestId: createPromptRequestId(),
    configuration: { model, tools: { allowed: [] }, pluginsEnabled: false, memory: { enabled: false } },
  }
  const checkpoint = { sessionId: creation.id, creation, promptId: createPromptRequestId(), installationId: context.installationId, dataScopeId }
  // 先记住创建请求，再发出去。回包丢失时，刷新仍能查询同一笔创建。
  await host.storage.set(checkpointKey, checkpoint)
  await client.sessions.create(creation, { signal })
  delete checkpoint.creation
  await host.storage.set(checkpointKey, checkpoint)
  const session = client.sessions.byId(checkpoint.sessionId)
  const admitted = await session.prompt({
    id: checkpoint.promptId,
    items: [{ type: "text", text: "请只回复 NOMI_NPM_OK" }],
  }, { signal })
  if (!admitted.run?.id) return { checkpoint, status: "submitted", reply: "" }
  return observe(session, checkpoint, admitted.run.id, signal)
}

export async function restoreTest(nomi, signal) {
  const { host, client, context, dataScopeId } = nomi
  const saved = await host.storage.get(checkpointKey)
  if (!saved.found) return undefined
  const checkpoint = saved.value
  if (checkpoint.installationId !== context.installationId || checkpoint.dataScopeId !== dataScopeId) {
    throw new Error("当前应用的数据身份与保存的会话不同。")
  }
  if (checkpoint.creation) {
    const receipt = await client.sessions.getCreationResult({
      sessionId: checkpoint.sessionId,
      requestId: checkpoint.creation.requestId,
      original: checkpoint.creation,
    }, { signal })
    if (receipt?.state !== "completed" || receipt.dataScopeId !== dataScopeId ||
        receipt.sessionId !== checkpoint.sessionId || receipt.requestId !== checkpoint.creation.requestId) {
      return { checkpoint, status: "creation_unknown", reply: "" }
    }
    return { checkpoint, status: "created", reply: "" }
  }
  const session = client.sessions.byId(checkpoint.sessionId)
  const snapshot = await session.getState({ signal })
  const run = snapshot.runs.find(item => item.inputId === checkpoint.promptId)
  if (!run) return { checkpoint, status: "unknown", reply: "" }
  if (run.status === "pending" || run.status === "running") return observe(session, checkpoint, run.id, signal)
  const state = applySessionSnapshot(createInitialClientState(), snapshot)
  return result(checkpoint, run, selectVisibleSessionMessagesWithParts(state.buckets[checkpoint.sessionId]))
}

async function observe(session, checkpoint, runId, signal) {
  const { run, messages } = await session.waitForRun(runId, { signal })
  return result(checkpoint, run, messages)
}

function result(checkpoint, run, messages) {
  const reply = messages
    .filter(({ message }) => message.role === "assistant" && message.runId === run.id)
    .map(({ parts }) => parts.filter(part => part.type === "text").map(part => part.text ?? "").join(""))
    .join("\n").trim()
  return { checkpoint, runId: run.id, status: run.status, reply }
}
