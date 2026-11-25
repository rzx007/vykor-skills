# 多模型合为单页 / Multi-model gallery

当用户要求“几个成品合一页”“3×2 排列”“保留调好的窗口位置”“展开后的标注恢复”“独立放大”时读取。输入是已完成的单体 HTML；当前 Skill 的 `scripts/build.py` 仍只构建一个场景。下面是可复用的组装流程，不是已提供的通用 gallery CLI，也不自动重做建筑调查。

Read this for composing existing models. Preserve each approved model, adapt its embedded copy, and validate the combined artifact. The bundled builder is single-model only; implement a project-local composer after inspecting the input runtimes.

## 1. 输入与保留范围 / Inputs and preservation

- 建清单：稳定模型 ID、标题、中英文名、顺序、HTML 路径及哈希、当前认可的默认视角、证据边界。按用户指定文件与标题，不从目录里任意挑“最新”版本。
- 用户已调整窗口时，在任何刷新、重建、导航之前先捕获可用的当前状态；见下一节。不能读取当前状态时，保留页面并询问缺失的数据，不用重新估算覆盖。
- 保留原单体和可恢复的合并页版本。适配写入嵌入副本或构建阶段，原文件哈希在构建后仍一致。记录实际改了什么：外壳、运行时适配、锚点与几何分别列出，不能把“原件未改”说成“嵌入代码未改”。
- 对不同来源的 HTML 先读实际运行结构；只对可信且已审阅的模型执行脚本。需要替换代码段时用唯一锚点并断言命中次数，不对未知版本盲目正则替换。失败则停止这一步并报告，不能漏掉模型后仍称合并成功。

Inventory exact inputs and preserve their hashes. Capture manual work before reload. An unchanged source file does not imply an unchanged embedded runtime. Verify adapter hooks against the actual input rather than silently accepting failed replacements.

## 2. 先保存视角 / Capture views before reload

每个模型记录其现有接口可提供的：`camera`（尺度/中心或等效状态）、`orbit`（yaw/pitch）、展开状态与稳定 `phase`、源视口宽高、模型 ID 与源版本。先等动画停止（如已有 `busy=false` 信号），不要把半途相位作为默认状态。字段是项目约定，**不是现有单体模板通用导出 API**；优先用已支持的导出/调试接口，必要时在可控副本中实现最小状态桥。读取和修改仍服从宿主浏览器能力限制。

将捕获值存为工作 JSON，再写入构建输入。仅写在某个浏览器的 `localStorage` 不能保证离线文件、其他浏览器或发布域名拥有相同默认值。

适配新尺寸时先核对原相机语义：世界单位缩放与 CSS 像素中心不能混算。按原视口保存归一化平移及可解释的 zoom，iframe 获得有效尺寸后应用默认值；只在启动阶段应用，用户开始旋转/平移/缩放后停止覆盖。详情与总览可以分别保存会话视图；返回时恢复总览布局下的原视图，不能每次重置为初始镜头。

Capture stable view state, source viewport and model identity before navigation. Persist defaults in the artifact, not only in browser storage. Map camera units deliberately across viewport changes, and stop startup restoration once the user interacts. Preserve the overview view when entering and leaving detail mode.

## 3. 组合结构 / Composition architecture

| 层级 | 责任 |
|---|---|
| 外层页面 | 页面标题、序号、网格、放大/返回、焦点和滚动 |
| 每个 iframe | 本模型的 WebGL、节点层级、动画、输入控制和标注 |
| 构建输入 | HTML 清单、视图默认值、嵌入适配规则、来源版本 |
| 验证记录 | 原件/结果哈希、实际视口、模型就绪情况、标注数量、交互和截图 |

优先一个模型一个 `iframe srcdoc`，避免重复 ID、全局变量、键盘和指针监听冲突。保留 `sandbox="allow-scripts"` 隔离；组合需要消息通信时不要为了直接访问子 DOM 加上 `allow-same-origin`。父子消息使用明确的项目通道、允许的类型与参数结构；父页面校验 `event.source === 对应 iframe.contentWindow`，子页面校验 `event.source === parent`。沙盒子页为 opaque origin，确需 `postMessage('*')` 时必须同时校验来源和数据，不接受任意脚本/HTML/导航消息。

每页 CSS、脚本、字体仍内嵌，合并后不依赖原 HTML 的磁盘路径或本机服务器。可把重复字体 data URL 提取成外层字典，在赋值 `srcdoc` 前原样还原；验证每份字节一致与许可证保留。JSON 安全序列化，防止内嵌 `</script>` 提前结束外层数据块；不要把标题等字符串直接拼成未转义 HTML。

Keep rendering isolated per iframe and let the outer shell manage layout. Use a narrow, source-checked message protocol; do not weaken the iframe sandbox to simplify state sharing. Inline every runtime asset, safely encode nested HTML, and verify any font deduplication round trip.

## 4. 总览与放大 / Overview and detail

- 行列由用户要求和数量决定。六个、3×2 是可复用示例，不是所有项目的固定规则。若用户明确要始终保持三列，窄屏可使用最小卡片宽度加横向滚动；否则按可读性改成少列。不要未经说明改变已指定排列。
- 总览减少重复标题、长提示和小示意窗，保留模型、必要控制和**完整展开标注**。不准以 `.annotations{display:none}` 解决拥挤。底部控件预留空间，避免展开几何覆盖按钮。
- 放大复用同一个 iframe，改变容器尺寸并发送展示模式；不销毁重建模型，不因移除再插入 iframe 而重载内部浏览会话。检查实际渲染实例和用户状态保留，不能只比较 DOM 变量身份。恢复该单体需要的标注和示意，按用户已明确移除的 UI 保持精简，不能把删掉的状态文字和按钮重新显示。
- 退出支持返回按钮和 Escape，回到触发按钮的键盘焦点；其他卡片在详情态不可交互。不要靠移动某张截图冒充独立三维窗口。
- iframe 初始化可能异步；确认全部模型已就绪后再截图或保存默认值。可用已有 ready 信号或有意义的渲染状态，单凭 iframe `load` 不代表 WebGL 和字体全部成功。

Choose the grid for the requested count and layout. Compact mode may hide redundant chrome, never the required expanded labels. Reuse the same live iframe in detail mode, restore focus on return, and distinguish document load from render readiness.

## 5. 统一标注且指向明确 / Consistent, grounded callouts

沿用 [visual-qa.md](visual-qa.md) 的线宽、目标圆点与中英文层次。先确定真实构件锚点，再投影并排文字：

1. `anchorLocal → part.node.world → camera projection → anchorScreen`；目标点随构件展开和旋转。左侧文字应选对应可见面，不能仍连右侧轮廓或假想外接圆。
2. 桥可上/下排、塔可左/右列，按实际目标顺序安排；根据当前 `parts` 数量分配，不硬编码“桥 5 条、塔 6 条”或某个索引永远代表台基。
3. 测量完整中文和英文换行后的框，再做列对齐、避让与边界检查。使用实际卡片宽**和高**；只按 `width<600` 套比例，或排版结束后强改某一行 y 值，会重新引入重叠。
4. 引线从真实锚点到文字框外缘，可折线绕开主体与其他文字；目标点不能为迁就排版移动到空白处。几何裁切或极端用户缩放造成锚点离屏时按现有交互处理，但默认展开不能漏项。
5. 总览和详情分别验收。调好小卡片不能证明放大后标注还在，统一颜色也不能证明标的是正确构件。

标注锚点中的具体半径、层高、部件索引和侧面逻辑只属于对应模型。整理引线不构成史料尺寸核准；公开尺寸仍按 [evidence.md](evidence.md#dimension-register) 处理。

Resolve real animated surface anchors before laying out labels. Measure complete bilingual boxes, handle actual part counts and both viewport dimensions, then check leader paths. A model-specific anchor repair is not a reusable architectural dimension or proof of historical accuracy.

## 6. 合并验收与交付 / Gallery acceptance

对本次最终生成物执行一轮有针对性的验证：

- 输入数与卡片数、身份顺序一致；源 HTML 哈希不变；字体和运行资源仍自包含。适配脚本真实失败时不能忽略。
- 实际浏览器查看所有模型成功渲染、默认状态和完整标注；检查至少实际总览尺寸与影响布局的窄/矮视口。特别检查多行英文和同列密集标签，不只检查 JSON 中的数量。
- 抽查代表性的横向/竖向模型：独立旋转不影响其他窗口，展开/收起、放大/返回、键盘退出、刷新后默认状态，以及一次尺寸变化。不同运行时需各自验证受影响行为。
- 用户手动视角与持久化值按相机语义比较；像素坐标随尺寸变化时比较规范化量，不用新的自动居中值冒充用户默认。
- 保存并**实际查看**最终截图，记录 URL/路径、构建哈希、视口、已测/未测项；控制台、渲染与视觉布局分别判断。HTTP 预览、文件直开和真正断网测试不可混称。

本机预览出现 `ERR_CONNECTION_REFUSED` 时先查目标端口和对应进程；启动或恢复只服务该输出目录的服务器后验证 HTTP 与页面。按宿主要求隐藏启动窗口；不要终止无关服务器。给出实际验证过的 URL，本机地址不称公开链接。

Verify the final combined artifact, not merely its six inputs. Check isolation, view persistence, labels at the actual card dimensions, focus transitions and errors. Inspect the saved screenshot. A dead localhost server is a delivery-path issue; restore the specific preview service and verify it rather than calling the artifact unavailable.

## 7. 用户要求发布时 / Publishing when requested

只有用户要求部署时才进入发布步骤，已有同范围明确授权继续有效。先准备可审阅的独立公开副本，只上传网站运行所需文件；完整研究台账、备份和 QA 留在本地。内嵌非显示 JSON 也会公开，检查并移除本机路径和不应公开的元数据，同时保留公开来源 URL、证据状态和精度说明。清理后比较模型代码、字体、默认视角与标注，避免以脱敏为由改形。

使用服务已有的插件、CLI 或官方控制台；认证未完成就如实记录。官方授权回调失效时先确认进程/过期情况，再使用官方支持的登录方式或已登录控制台，不反复使用失效码，不读取凭证文件或把认证材料写入作品。具体平台 UI 与命令以当时官方入口为准，不把本次点击路径写成永久接口。

平台显示成功后，核验公开 URL、HTTP 响应和实际文件一致性；平台修改响应时比较预期差异，不伪称哈希相同。浏览器检查全部模型是否加载、字体与交互是否正常，保留发布回执和截图。更新内容是否发布与 Skill 是否更新是两件事，不能顺带重新部署用户未要求修改的作品。

Publish only within the user's deployment authorization. Sanitize a separate public copy, including inert metadata, without altering models or evidence status. Use official authentication paths and verify the live artifact after upload. Updating this Skill alone does not authorize or require redeploying existing sites.
