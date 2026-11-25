# 定稿样式与验收 / Approved style and verification

看 [the upstream Santan example](https://github.com/tanglele110-hash/heritage-blueprint-skill/blob/f5e7c5381187e6d362bc375f134688e2b1d91456/assets/examples/santan/approved.html) 理解最终视觉，不从早期试验版本重新推导风格。新对象替换几何和资料内容，保留清洁、克制的建筑模型表现。

Use the approved HTML as the visual baseline. It is the retained final reference, not a generic geometry source for every landmark.

## 固定设计语言 / Visual contract

| 项目 | 默认规则 |
|---|---|
| 纸张与线条 | 冷灰白纸底、浅蓝网格、钴蓝文字和细线；主体以白、冷浅蓝、少量蓝色分区 |
| 标注引线 | 以三潭印月现有模板为基准：0.75 CSS px 淡蓝实线、半径 1.7 px 蓝色目标点；与装配虚线区分。用户指定其他定稿样式时保留 |
| 标注避让 | 文字框避让各构件投影、固定控件、示意和其他文字；窄屏英文按词换行，保持字号 |
| 光影 | 清晰轻微面色区分；不加黑晕、径向暗影、强 AO 或沉重地面投影 |
| 构图 | 默认正交等距；主体居中、四周留白；1920×1080 为主要构图，并适配手机 |
| 文字层次 | 中文为主，英文独立下一行、字号更小；不新增说明面板 |
| 中文标题/主按钮 | IBM Plex Sans TC Bold 700；主按钮“展開 / 收起” |
| 其他字体 | 英文保持原字体；图中中文标注保持 Microsoft YaHei/PingFang SC，英文标注 Consolas 等等宽系统栈 |
| 标题尺寸 | 普通 20px，≥1600 宽为 23px，手机 18px；字距 .12em，手机 .08em；不借放大字号假装换字体 |
| 主按钮中文 | 16px，≥1600 宽 18px，字距 .12em；英文 12/13px |
| 左上示意 | 固定屏幕坐标，随窗口比例适度缩放；不跟主体平移/旋转。仅在本对象确有有用关系时显示 |
| 边角避让 | 示意图须在 18px 角线下留至少约 12px 空隙；手机约 14px，不能压住折线 |
| 右上工具 | 旋转、平移、复位均 44×44px，间隔 6px；复位隐藏时保留位置，防止跳动 |
| 按钮与画布 | 底部控制区独立于模型画布；展开最大尺寸不能盖按钮或越界 |

模板提供上述线色与目标点，但其默认单侧排版不等于复杂构件避让已经实现。制作时核读并适配实际标注函数，不能只修改本文便宣称渲染器已更新。处理长标题、横向桥梁或不同构件数量时可作局部适配，保留同样的层次、字号关系与留白；检查实际页面，不能仅保证 CSS 有对应数值。组合页的紧凑与放大排版另见 [gallery.md](gallery.md)。

The template supplies the base interface; inspect and adapt its actual callout renderer to meet this contract rather than assuming every later visual rule is already implemented. Adapt long titles or horizontal structures locally without redesigning approved typography and controls. Check visible balance, not just matching CSS declarations.

## 交互 / Interaction

- 默认拖动旋转，水平可转一周，俯仰约 -80° 至 85°。平移模式拖动平移；Shift/中键/右键拖动也可平移。
- 滚轮以光标为缩放中心；触屏单指按当前模式，双指平移+缩放；双指变单指连续，不跳动。缩放约 .55–3.2 倍；复位恢复初始视角、尺度、位置。
- 点击主体、主按钮、Space 或 Enter 展開/收起；拖动不能误触动画，动画期间忽略重复触发。
- 默认 2.85 秒：从上方或适合该结构的第一组构件开始，其他组错开启动并重叠，加减速、轻微过冲、准确停稳。倒放同一时间线收起；结束不自动循环。
- 动画时相机不动，背景网格不漂移；左上示意不动。手动旋转/平移/缩放属于用户控制，不被后续动画自动重置。

Support orbit, pan, cursor-centred zoom, pinch, reset and reversible separation. Ignore repeat animation triggers and distinguish clicks from drags. Keep the paper, inset and automatic fit stable.

## 一轮验收 / One focused acceptance pass

1. **资料对照**：实际打开照片，把模型转到相近方向；核对轮廓、层级、孔洞、顶部、基座和部件比例。记录仍属估计或不可见的部位。
2. **桌面 1920×1080**：完整展开与收起各一次，确认停住、连接/叠置归位、标注文字不遮住主体、固定界面或其他标注、无裁切与按钮遮挡。
3. **手机 390×844 与窄屏 320×740**：标题、按钮、示意图和角线留白；首次交付或相关布局变化时检查 844×390 横屏；局部修订仅复验受影响视口。新对象长标题尤其要看溢出。
4. **交互**：旋转前/侧/后和高低视角；平移、缩放、复位；滚轮锚点；拖动不误触；动画中重复点击无效；键盘操作。可测触摸时检查双指接单指。
5. **技术**：控制台无错误；静态自包含检查与实际断网/文件直开测试分别记；字体实际加载成功且目标字形有覆盖；不残留三潭印月名称/间距/维度在其他对象中。节点接触与孔洞可做本对象专属射线/数值验证。
6. **状态复核**：网格与示意固定、视图自动尺度不漂移、收起回到同一几何、动画终点无持续 RAF；复位后恢复初始镜头。

检查与结果写清已测/未测。模拟 viewport 不是实体手机触摸测试，Node VM 不是浏览器 WebGL 渲染测试，字库声明不是字形已命中。无浏览器时保留成果并准确报告限制，不声称全项通过。

Separate source review, rendered visual inspection, browser behavior and programmatic invariants. A simulated phone viewport does not prove physical-device touch behavior. Report the exact checks performed and meaningful untested boundaries.

## 标注与最终版本复核 / Callouts and final-artifact review

- 默认及复位后的合拢/展开状态都应容纳模型；不要随动画自动缩小镜头来腾标签位置。避让采用各构件投影范围，宽基座不应占满细塔身两侧所有空白。孔洞内部仍属于构件区域，不把文字塞入拱孔或窗洞。
- 先调整文字位置和英文按词换行，再检查引线终点；引线不能划过文字。默认完整展开不能靠漏画标注通过验收。极端手动放大后空间不足时，可暂隐不可容纳的标注，恢复视图后须恢复；不得缩字号或遮盖模型。
- 目标点取自被标构件的真实可见面或边，经该构件当前 `node.world` 和相机投影更新。标注属于左侧时不能仍指右侧轮廓；拱券指券体而非孔内空白，台基指台面/台壁而非地面。文字按列或行对齐只是排版，不能改变锚点含义。换行后以完整中英文文字框重新避让，避免长英文挤到下一条中文；布局适配后再次检查端点和线段。
- 验收前加载最后一次构建的文件；记录实际路径、构建哈希或版本、视口、展开相位/视角及控制台结果。改变几何后，旧截图、旧 QA 或修改前打开的标签页不代表新版通过。
- 保存截图后实际查看，确认目标构件在画面内、裁剪区域正确且不是尚未重绘的旧尺寸画面。细部用相近角度近景，整体另保留未裁切画面；不要把全塔只剩塔顶或只截到左上示意的图片当作接缝证据。
- 文件直开或断网测试受工具限制时，保留本地 HTTP 实测和静态自包含结果，分别报告；不绕过浏览器安全限制，也不声称完成未做过的测试。最终检查通过后结束本次修订，不无理由重测无关页面。

Keep all default-view callouts readable without changing the camera or approved typography. Verify the last build, inspect the saved screenshots, and distinguish HTTP rendering, static offline checks and actual offline/file-opening tests. Retest only behavior affected by the revision.
