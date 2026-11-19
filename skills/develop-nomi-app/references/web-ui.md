# 把 Web 页面接入 Nomi

Nomi 开发窗口加载 Web 地址。应用原有的路由、组件、样式和后台由应用维护。需要调用 Nomi 时，在浏览器代码里增加 AppHost 连接。下面的按钮适合放在调试页，也可以接入现有业务组件。先验证握手，再按需接 Agent、存储等能力。

| 项目场景 | 开发时怎么打开 | Nomi 接入放在哪里 |
| --- | --- | --- |
| Vue | 运行项目已有的开发命令，填实际输出的 URL | Vue 组件里的事件回调。已有 Vue 2 项目可以沿用 `methods` |
| React | 运行项目已有的开发命令，填实际输出的 URL | React 客户端组件里的事件回调。使用服务端渲染时，把连接放进可在浏览器交互的组件 |
| 无框架 | 使用项目已有 Web 服务，或运行本技能的 [Vite 最小示例](../assets/starter/README.md) | 浏览器模块的事件回调。若使用 npm SDK，由项目构建器解析模块并打进网页资源 |
| 已部署的远程站点 | 在 Nomi 开发设置选本机清单，再填 Nomi 所在机器能访问的 HTTP 或 HTTPS 页面 URL | 通过站点自己的发布流程上线浏览器接入代码。Vue、React 或无框架页面都可以部署到远程 |

页面只需在开发窗口显示时，选择有效的应用清单并填写页面地址即可。需要验证 AppHost 时，按[版本选择和安装命令](../assets/starter/README.md#版本)添加 `@bobannomi/app-host`。连接从用户操作中发起，页面遇到连接错误时可显示调试提示，现有普通浏览器流程继续可用。需要 Agent 时，再添加 `@bobannomi/client`，并参考[会话示例](../assets/starter/nomi-app.js)接入。

## 新建 Vue 或 React 工程

从零新建时可以用 Vite 官方脚手架。在选定的父目录执行其中一条，把示例目录名替换成你给应用选的名字。需要 TypeScript 时，把模板参数改成 `vue-ts` 或 `react-ts`。[Vite 创建项目](https://vite.dev/guide/#scaffolding-your-first-vite-project)

```sh
npm create vite@latest my-vue-app -- --template vue --no-interactive
npm create vite@latest my-react-app -- --template react --no-interactive
```

进入生成的项目目录，按上面的说明添加用得上的 SDK，接入下文对应的组件，把[最小清单](../assets/starter/app.manifest.json)复制到项目根并填写自己的应用信息。安装项目依赖后运行 `npm run dev`，在 Nomi 里选这个项目目录并填写开发服务实际输出的地址。

## Vue 示例

在现有 Vue 3 页面增加一个调试组件，下一段从浏览器点击发起握手。[Vue 事件处理](https://vuejs.org/guide/essentials/event-handling.html)

```vue
<script setup>
import { ref } from 'vue'
import { connectAppHost } from '@bobannomi/app-host'

const status = ref('等待连接')
const busy = ref(false)

async function connect() {
  busy.value = true
  try {
    const host = await connectAppHost({ hostApi: '^0.1.3' })
    const context = await host.getContext()
    status.value = `已连接 Nomi ${context.hostVersion}`
  } catch (error) {
    status.value = `连接失败 ${error.message}`
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <button type="button" :disabled="busy" @click="connect">连接 Nomi</button>
  <p role="status">{{ status }}</p>
</template>
```

## React 示例

把组件放到现有 React 页面。使用 React Server Components 时，将此组件标记为客户端组件。[React 事件处理](https://react.dev/learn/responding-to-events)

```jsx
import { useState } from 'react'
import { connectAppHost } from '@bobannomi/app-host'

export default function NomiConnection() {
  const [status, setStatus] = useState('等待连接')
  const [busy, setBusy] = useState(false)

  async function connect() {
    setBusy(true)
    try {
      const host = await connectAppHost({ hostApi: '^0.1.3' })
      const context = await host.getContext()
      setStatus(`已连接 Nomi ${context.hostVersion}`)
    } catch (error) {
      setStatus(`连接失败 ${error.message}`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <button type="button" disabled={busy} onClick={connect}>连接 Nomi</button>
      <p role="status">{status}</p>
    </>
  )
}
```

## 无框架和远程页面

无框架项目可以在 `type="module"` 的网页入口里给按钮绑定 `click`，同样调用 `connectAppHost()` 和 `getContext()`。完整示例包含会话、回复和刷新后的恢复。[无框架示例](../assets/starter/README.md)

远程联调时，部署包含接入代码的网页，在桌面开发设置选本机 `app.manifest.json` 并填写实际页面地址，含子路径时填完整路径。开发窗口加载的是所填地址，跨来源的顶层跳转可能被拦下。页面登录需要跳往其他域名时，先确认正常登录回到应用页面的接法，再检查握手。正式安装清单中的 `ui.type: "remote"` 和 HTTPS `ui.url` 属于应用交付配置。

验收时记录实际加载的页面地址和框架。用普通浏览器检查已有路由和页面，用 Nomi 开发窗口单独确认握手。热更新使用项目已有能力，已部署的页面通过刷新检查更新。需要验证 Agent 时，用测试模型发一条消息并在刷新后读回原会话。
