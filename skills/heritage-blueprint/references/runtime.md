# 场景接口 / Scene adapter

`build.py` 把 `scene.json`、几何、可选示意图、资料 JSON 和原装字体打成一个 HTML。浏览器运行时只有原生 WebGL、Canvas 2D、CSS 和 JavaScript，不需要 Python、Node 或外部库。

The build tools run locally; the delivered HTML has no runtime dependencies. Geometry is authored, not generated from a landmark name by the packaging script.

## 文件与配置 / Inputs

工作目录放 `scene.json`、`geometry.js`、`evidence.json` 和可选 `inset.html`。路径相对配置所在目录，脚本不允许越过该目录。最小配置：

```json
{"schemaVersion":1,"titleZh":"已核验字形的标题","titleEn":"ENGLISH TITLE","edition":"01","geometry":"geometry.js","evidence":"evidence.json","durationMs":2850}
```

`titleZh` 是实际显示文字；不要为通过字库检查擅自改名。`inset` 可指向静态 `<figure class="siteplan">…inline SVG…</figure>`；不需要关系图时省略。不得残留案例的距离、标题或塔位。

## geometry.js 契约 / Contract

代码在运行时闭包内执行，返回场景描述。节点按照父节点先于子节点的顺序创建。坐标为 X/Y 水平、Z 向上，统一使用同一长度单位。

```javascript
const root = node('fixed base', null);
const upper = node('upper component', root, p => tr(0, 0, p.gap));
// 在这里为实际对象创建几何；不要保留无依据的占位建筑。
function pose(t) { return {gap: .3 * ease(t, .12, .9)}; }
return {
  root, pose,
  parts: [{node: upper, anchor: [0, 0, 1], zh: '构件名称', text: 'COMPONENT'}],
  guides: () => [{from: point(root.world, [0,0,1]), to: point(upper.world, [0,0,1])}]
};
```

此片段只说明接口，不能独立生成成果。`pose(t)` 定义 0 合拢、1 分解；`ease(t,start,end)` 含加减速、约 2% 轻微过冲并精确归位。时间段错开、适当重叠，收起沿同一条曲线反向。结构根据证据分组，数量不限；不是每个对象都需要六件或轴向上移。

Required return values: `root`, `pose`, `parts`. Nodes form a rigid parent-before-child hierarchy. Define closed and separated poses for the actual assembly; the timeline is reversible and has no automatic loop.

可用几何工具（详情见模板函数）：

- `node(name,parent,transform=()=>I())`、`tr/rx/ry/rz`、`mul`、`point`。
- `poly(node,points,color,outline=true)`：凸面扇形三角化；凹面必须自行拆分，孔洞不能用覆盖色“挖洞”。
- `box(node,x,y,z,w,d,h,color,outline)`、`beam(node,a,b,width,color)`、`cylinder(node,x,y,z,r,h,color,segments,verticalLines)`。
- `lathe(node,profile,color,{segments,rings})`：局部 Z 轴旋转体，`profile` 为 `[z,r,可选dr/dz]`；生成曲面和随视角变化的轮廓。`rings` 只选真实边界，不画每一条网格线。
- `smoothProfile(points,steps)`：按实际高度插值的 C2 曲线，返回半径与导数。保留照片里的束腰/台阶；检查插值是否负半径或越界。`curveProfile` 用于不需严格曲率连续的短轮廓。
- `line(node,a,b,color)`、调色板 `C`（`wall/roof/stone/ink/soft/interior/accent` 等）。

`parts[].anchor` 可为局部坐标，或 `({cameraRight,cameraUp,cameraDepth,yaw,pitch})=>[x,y,z]`。旋转体案例用 `r,z` 的简写，让标注位于右侧轮廓；复杂建筑应给真正构件锚点，勿把所有标注锚在假想圆周上。`guides()` 返回世界坐标端点，只作虚线装配引导。

可选 `dimension:{from,to,offset,zh,en}` 仅用于单个竖直高度标尺，随展开淡出；没有多尺寸数组或水平标尺接口。逐层层高、檐挑、台基和塔刹尺寸按已核对的共享参数生成静态 `inset.html`，或先实现并验证专属尺寸绘制，不能只填未知配置字段或把水平尺寸套进竖直高度标尺。未知尺寸不显示编造数值。`pivotXY:[x,y]` 可指定具有明确对称中心的对象，默认按完整运动范围居中。`inspect` 可选，只为场景专属检查暴露命名构件；不出现在 UI。

The optional dimension draws one vertical ruler and fades during separation. It is not a multidimensional annotation system. Generate a static inset from verified shared parameters, or implement and validate the missing drawing behavior before claiming support.

## 示意与主体同源 / Shared geometry for the inset

桥面坡度、拱孔、跨径、层高、半径、台基和顶部轮廓应有一个参数来源。主体几何和左上示意都使用这些值或同一轮廓函数；避免维护两套手绘路径。完整立面按同一横纵比例绘制，局部放大另标范围与倍率关系，不能用拱孔局部图冒充整桥。

现有 `build.py` 只接受静态 `inset` 文件，没有自动建筑示意或 `inset_init` 配置接口。可以在场景制作的本地构建步骤中，由同一参数源生成 `geometry.js` 与静态 `inset.html`；若需扩展构建器，应先实现并验证接口，不能假设添加字段就会生效。主体改形后同步重建示意，并在浏览器比较相近方向的轮廓。

Derive the model and inset from shared parameters. Separate whole elevations from enlarged details. The existing builder accepts static inset markup; it does not infer an elevation or execute a new configuration field automatically.

## 场景专属几何检查 / Object-specific geometry checks

楼梯接台、柱脚接地、斜撑接檐、层间叠置和孔洞类型按 [geometry-qa.md](geometry-qa.md) 检查。`inspect` 可暴露命名构件和基准供定向验证；不能仅比较 `inspect` 数值就声称最终网格接触。复杂模型的数值检查与浏览器近景检查分别记录。

Use targeted checks on generated geometry and then inspect visible joints. Metadata and declared contact coordinates are useful inputs, not proof that the rendered surfaces actually meet.

## 保持不变量 / Runtime invariants

- 整段时间线采样求包围体，镜头再覆盖允许的全部旋转角度；只在窗口尺寸变化时适配。动画与旋转不触发自动缩放。手动平移/缩放保留到用户复位。
- CPU 投影、GPU 投影、标注和点击命中共用同一正交基；不以改相机缩放掩盖裁切。
- 曲面轮廓根据构件局部视线计算，包括精确切线端点；转动父节点后不能沿用旧经线当外轮廓。节点变换限刚体旋转/平移；非均匀缩放需重建法线/轮廓算法。
- 孔洞是真实几何空洞，有厚度和背面；深度正确。凹多边形、内外表面、朝向和接触缝需要本对象检查。
- 拖动时复用网格；时间相位变化才更新构件位置。避免在每个 pointermove 对全部三角形做命中检测。
- `verify.cjs` 的 VM 使用模拟 WebGL，仅验证几何数值、取景、时间线、归位和输入状态；实际着色器、字形加载、像素、触摸硬件需浏览器/设备检查。

Keep fit, geometry, projection and input state consistent. The native renderer is intentionally small: extend it when an object's topology or dimensions require it, and verify the affected behavior rather than pretending the current helper already supports it.

## 字体 / Fonts

包内 `assets/fonts/IBMPlexSansTC-Bold.woff2` 是 IBM 官方包 1.1.1 的未修改完整 Bold 字库，附 OFL 和来源摘要。打包直接内联原字体，避免只有 CSS 名称却发生系统字体回退。完整字体使输出约 3.5 MB；无需联网加载。

构建时核对 `titleZh + 展開收起` 的 cmap 覆盖。官方 TC 不含的简体字不能假称已正确渲染；向用户确认传统字形或其他字体选择。三潭印月范例已确认按钮写“展開”；此授权不等于其他对象标题可以自动繁体化。字体变更不得通过放大字号、改变字距来冒充。

Only the Chinese title and main action label use IBM Plex Sans TC. Preserve English and diagram fonts. Check actual glyph coverage; missing characters require an explicit spelling/font choice, not silent fallback. Do not change size or spacing merely to make a font change more visible.
