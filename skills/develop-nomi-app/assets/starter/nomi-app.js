import { connectAppHost } from "@bobannomi/app-host"
import {
  applySessionSnapshot,
  BobanNomiClient,
  createInitialClientState,
  createPromptRequestId,
  selectVisibleSessionMessagesWithParts,
  waitForRun,
} from "@bobannomi/client"

const checkpointKey = "nomi-app-starter.last-test"

export async function connectNomi() {
  const host = await connectAppHost({ hostApi: "^0.1.3" })
  if (!host.hasFeature("session-resources-v1")) throw new Error("Nomi 未提供会话连接，请核对桌面版与 SDK 版本。")
  const context = await host.getContext()
  const connection = await host.sessions.getConnection()
  const client = new BobanNomiClient(connection.clientOptions)
  const { dataScopeId, protocol } = await client.protocol.capabilities({ authenticated: true, scope: "protocol" })
  if (!dataScopeId || protocol.version !== 7) throw new Error("此示例需要 Agent 后台协议 7 和数据身份。")
  return { host, client, context, dataScopeId }
}

export async function sendTest(nomi, cwd, model, signal) {
  const { host, client, context, dataScopeId } = nomi
  const session = await client.sessions.create({
    cwd,
    id: createPromptRequestId(),
    requestId: createPromptRequestId(),
    configuration: { model, tools: { allowed: [] }, pluginsEnabled: false, memory: { enabled: false } },
  }, { signal })
  const checkpoint = { sessionId: session.id, promptId: createPromptRequestId(), installationId: context.installationId, dataScopeId }
  await host.storage.set(checkpointKey, checkpoint)
  const admitted = await client.sessions.admitPrompt(session.id, {
    id: checkpoint.promptId,
    items: [{ type: "text", text: "请只回复 NOMI_NPM_OK" }],
  }, { signal })
  if (!admitted.run?.id) return { checkpoint, status: "submitted", reply: "" }
  return observe(nomi, checkpoint, admitted.run.id, signal)
}

export async function restoreTest(nomi, signal) {
  const { host, client, context, dataScopeId } = nomi
  const saved = await host.storage.get(checkpointKey)
  if (!saved.found) return undefined
  const checkpoint = saved.value
  if (checkpoint.installationId !== context.installationId || checkpoint.dataScopeId !== dataScopeId) {
    throw new Error("当前应用的数据身份与保存的会话不同。")
  }
  const snapshot = await client.sessions.getState(checkpoint.sessionId, { signal })
  const run = snapshot.runs.find(item => item.inputId === checkpoint.promptId)
  if (!run) return { checkpoint, status: "unknown", reply: "" }
  if (run.status === "pending" || run.status === "running") return observe(nomi, checkpoint, run.id, signal)
  const state = applySessionSnapshot(createInitialClientState(), snapshot)
  return result(checkpoint, run, selectVisibleSessionMessagesWithParts(state.buckets[checkpoint.sessionId]))
}

async function observe({ client }, checkpoint, runId, signal) {
  const { run, messages } = await waitForRun(client, { sessionId: checkpoint.sessionId, runId, signal })
  return result(checkpoint, run, messages)
}

function result(checkpoint, run, messages) {
  const reply = messages
    .filter(({ message }) => message.role === "assistant" && message.runId === run.id)
    .map(({ parts }) => parts.filter(part => part.type === "text").map(part => part.text ?? "").join(""))
    .join("\n").trim()
  return { checkpoint, runId: run.id, status: run.status, reply }
}
