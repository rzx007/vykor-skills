---
name: heritage-blueprint
description: "按实景照片、史料和测绘资料制作蓝图风格古建或文物三维 HTML，或将多个已有模型合并成单页。Build offline heritage models from photos and records, or combine existing models into one interactive page."
---

# 古建与文物蓝图 · Heritage Blueprint

作者 / Author：[@木渡川（tanglele）](https://x.com/tanglele0318) · [MIT License](LICENSE) · [版权范围 / Scope](COPYRIGHT.md)

交付可离线打开的 HTML，支持旋转、平移、缩放、分解和复位。模型用原生 WebGL 渲染；脚本、样式和字体全部内嵌，不依赖 CDN 或外部资源。资料台账另存。

Build a self-contained HTML from the object's own evidence. Keep approved geometry and manual views. Mark estimates and unknowns; inspect the final page before delivery.

## 从哪里开始

| 任务 | 做法 |
|---|---|
| 新建或修改单体 | 按下面四步制作 |
| 多个成品合成一页 | 读 [合页流程](references/gallery.md)，保留原模型，适配布局、视角和标注 |
| 修改合页中的某个建筑 | 先改该单体，再更新嵌入副本 |

用户已调好的视角，先保存再刷新。已确认的对象、年代和样式直接沿用。

## 1. 查资料

读 [证据与尺寸](references/evidence.md)。确定地点、年代和表现范围，打开实景照片、文保记录及可得的测绘或修缮图纸。照片要看原图，图纸要记页码、单位和基准。

每项形制和尺寸记录来源，分清一手记录、报道值、照片估计和未知项。资料冲突时核对年代、修缮和测量口径。缺数据就留空，不能用等分层高或通用塔身补成“已核准”。

核准塔类尺寸时，逐项填写 [尺寸核对表](references/evidence.md#dimension-register)：层高、收分、檐挑、台基、塔刹。区分内外层级、对边与对角尺寸、地坪与构件标高。示意图保留“约”“报道”“估计”等标识；用户要求精细核准的部位不能擅自简化。

## 2. 建模

读 [场景接口](references/runtime.md)。用 `assets/blueprint.template.html` 保留蓝图界面和交互，在工作目录编写：

- `scene.json`：标题、文件路径和动画时长。
- `geometry.js`：本对象的几何、构件层级、分解动作和标注锚点。
- `evidence.json`：来源、尺寸和未验证项。
- `inset.html`：需要时生成的静态形制示意。

先比对整体轮廓、层级和孔洞，再做砖缝、瓦垄等细节。示意图与主体共用参数；整体和局部放大分别标明。现有构建器只接收静态示意，单个竖直标尺也不能代替逐层或水平尺寸绘制。

孔洞须有真实空腔和厚度；构件接触、屋面穿插、柱脚与台阶问题按 [几何检查](references/geometry-qa.md) 处理。平滑曲面保留真实转折，隐藏计算网格，不加暗色光晕。

分解通过构件节点变换实现，默认时长 2.85 秒。展示位移不表示原建筑存在折叠机构。无测绘数据时，不称精确复原、数字孪生、CAD 或 BIM。

## 3. 排版与标注

按 [样式与验收](references/visual-qa.md) 排版：冷灰白底、浅蓝网格、中文在上、英文小一行。引线沿用三潭印月的淡蓝细线和圆点，目标落在对应构件的可见面或边，随构件展开和旋转。

先测量完整文字框，再避让主体、控件和其他标注。默认展开要显示全部标注。多模型页面分别检查总览和放大状态，不能隐藏标注来解决拥挤。

## 4. 构建与交付

```text
python <skill>/scripts/build.py <work>/scene.json <output>/landmark.html
node <skill>/scripts/verify.cjs <output>/landmark.html
```

`build.py` 仅构建单体，校验来源引用和标题字形，嵌入 IBM Plex Sans TC Bold 及许可证。默认不覆盖文件；替换同一成果时加 `--force`。多模型合页需按输入文件编写项目内组合器。

加载最后构建的页面，检查：

1. 与相近角度实照对照，核对轮廓、细部、孔洞和接头。
2. 桌面及受影响的窄屏布局；展开、收起、旋转、平移、缩放和复位。
3. 字形、标注、示意、固定网格和控制台；合页另查独立操作与默认视角。
4. 保存并查看截图，记下文件版本、视口和已测/未测项。修改后复验受影响部分。

`verify.cjs` 检查程序不变量；照片符合度、实际 WebGL 和标注排版仍需查看页面。浏览器不可用时列明未测项；本地 HTTP、文件直开和断网测试分别记录。

交付 HTML 路径或可用链接、关键来源、未核准项及检查结果。页面保持简洁，证据保存在内嵌 JSON 和工作台账中。部署按用户授权执行，更新 Skill 本身不触发重新发布。

## 范例与调用

[三潭印月成品](https://github.com/tanglele110-hash/heritage-blueprint-skill/blob/f5e7c5381187e6d362bc375f134688e2b1d91456/assets/examples/santan/approved.html) 用于看样式；[场景配置](assets/examples/santan/scene.json)、[几何代码](assets/examples/santan/geometry.js) 和 [证据台账](assets/examples/santan/evidence.json) 用于看接口。新对象须重写几何、尺寸、标注和示意。参考照片的再分发许可未确认，不随作品自动打包。

- `用 $heritage-blueprint 做杭州断桥，核对现状照片和尺寸，生成可离线打开的三维 HTML。`
- `用 $heritage-blueprint 把这六个 HTML 合成“杭州地标”，3×2 排列，保留我调好的视角、展开标注和独立放大。`
