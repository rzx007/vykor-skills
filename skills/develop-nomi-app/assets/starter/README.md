# Nomi 最小开发项目

新建应用时，把这个目录的文件复制到你为应用选定的新项目目录。已有 Web 项目可直接参照下文「接入已有页面」。`app.manifest.json` 是 Nomi 的应用清单，`nomi-app.js` 是可接入其他网页的浏览器端模块，`main.js` 负责示例表单。`configure-model.mjs` 在运行 Nomi 的机器上为指定的开发后台配置测试模型。

## 版本

这个示例使用 Node.js 24。首次添加 SDK 时，下面的命令从 npm 读取各自的 `latest` 标签，把安装到的具体版本写入 `package.json`，并生成或更新 `package-lock.json`。保留锁文件，之后安装就能复现这次选择。

```sh
npm install --save-exact @bobannomi/app-host@latest @bobannomi/client@latest
```

用户指定哪个包的版本，就把该包的 `@latest` 换成指定版本，例如 `@bobannomi/app-host@0.1.0`。两个包分别选版本，预览版本由用户指定。已有项目用自己的包管理器，只添加缺少的 SDK；用户明确要求调整时再改已有版本。只做宿主握手时，仅安装 `@bobannomi/app-host`。

清单里的 `hostApi` 描述应用需要的 Nomi 宿主接口版本。装完 SDK 后，在目标 Nomi 的开发窗口验证握手；需要 Agent 时，再验证会话连接。出现版本不兼容时，告诉开发者实际安装的 SDK 和 Nomi 版本，再根据目标 Nomi 支持的版本选择依赖。

## 跑起来

1. 把 `app.manifest.json` 中的 `id` 和 `name` 改成自己的应用标识。沿用已有 Web 项目的构建入口时，把 `ui.entry` 改成实际路径。此示例用 Nomi 应用存储记住原会话，所以需要 `app.storage`。
2. 在复制后的示例目录运行上面的 SDK 安装命令，它也会安装项目的 Vite 依赖。再运行 `npm run dev`，将 Vite 输出的实际地址填到 Nomi「常规设置 → 开发应用」里，并选择这个目录。`npm run build` 可单独检查生产页面构建。
3. 优先在页面选择 BobanNomi 模型服务。需要配置服务时，记下页面上的开发项目 ID 和数据 ID，按[测试模型说明](../../references/test-model.md)操作，也可以接入其他 OpenAI 兼容网关。复制示例到单独目录时，模型说明可从原技能目录打开。
4. 回到开发窗口按 F5，在表单里填桌面本机上实际存在的完整工作目录，选择测试模型并发送。检查 `completed` 和助手回复。再按 F5，核对原会话 ID、运行 ID 和回复。

## 接入已有页面

保留应用原有的路由和开发命令，把 `nomi-app.js` 加入浏览器端代码。`connectNomi()` 返回宿主、业务 Client 与当前数据身份。`sendTest()` 演示带工作目录和模型发一次消息。`restoreTest()` 演示刷新后按原会话和消息查结果。纯页面联调可以只用应用清单和开发地址，只有需要验证 Agent 时才接会话模块。
