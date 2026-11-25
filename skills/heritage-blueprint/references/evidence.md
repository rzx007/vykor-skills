# 资料与形制 / Evidence and form

## 查找顺序 / Research order

1. 明确地点、对象、年代、现状/旧貌、单体或整体。雷峰塔等对象须核对选定时期，不默认古今形制相同；“断桥”不能按名称画成断裂桥面。
2. 优先文保管理机构、地方政府、档案/博物馆、学术论文、正式修缮或测绘文件。新闻中引用专业人员的尺寸属于“报道数据”，不自动升级成工程实测。注明发布者、日期、原始页链接。
3. 查看实景照片：总体轮廓、不同方向、关键细部。打开原图检查，不从搜索缩略图或标题推断。用户照片可补充形制证据；不要把摄影者、日期未知的照片当作已确认年代证明。
4. 旧照片、历史图纸、方志、考古与修缮记录用于判定变化；区分原物、后修、重建和现代景观配套。旅游插画、效果图只可辅助定位，不决定隐蔽结构。
5. 保留可复核的页码/图号/图片来源、访问日期和观察笔记。只下载任务需要的材料，作品中不外链加载它们；尊重原始许可。

Identify the object and period first. Prefer conservation and primary records for facts, inspect actual photographs for visible form, and use dated historical sources to distinguish changes. A published diagram is not automatically a measured drawing.

## 数据台账 / Evidence ledger

`evidence.json` 的最小结构：

```json
{
  "scope": {"object":"具体对象", "era":"所表现时期", "representation":"三维形制示意", "units":"metres"},
  "sources": [
    {"id":"photo-a", "title":"实景照片名称", "url":"实际原始链接", "type":"official-photo", "date":"实际日期或 unknown", "use":"所观察的轮廓和细部"}
  ],
  "claims": [
    {"parameter":"屋面轮廓", "status":"photo-estimate", "sources":["photo-a"], "basis":"从所查看照片估计；非测量值"},
    {"parameter":"隐蔽连接", "status":"unknown", "sources":[], "basis":"没有结构资料，省略"}
  ]
}
```

上例仅展示字段，不是可替代调查的证据。来源可用 `file` 记录保存在场景目录的图纸/用户照片。脚本检查引用是否存在，不能判断内容真实。

| status | 含义 / Meaning | 用法 |
|---|---|---|
| `documented` | 一手图纸、测量、文保/修缮记录直接支持 / Directly documented | 记录页码、单位、基准、年代，不外推未提供的精度 |
| `reported` | 报道或二手文献给出的数值 / Reported | 写清发布者和转引关系；“约”不可删掉 |
| `photo-estimate` | 从照片提取形状或比例 / Estimated from photos | 给出可见方向、参照尺寸和简化方式，不捏造毫米级尺寸 |
| `unknown` | 缺少支持 / Unknown | 保持未验证，按约定范围留空/省略并说明；仅在约定允许时采用明确标记的简化，不以对称复制冒充证据 |

## 建模前形制表 / Form before code

每个对象单独列出：总体高宽/跨径、层级、基座、孔洞、檐/栏杆、顶部、连接方式、可见装饰与不可见部位。为关键形制写出“照片里看到了什么”，避免只有尺寸没有外形证据。

- 桥：桥拱或梁的真实类型、跨数、桥面坡度、栏杆与桥台；不是把塔身压扁。未知基础不造出桩基。
- 塔：平面边数、层数、逐层收分、塔檐形状、门窗开口、塔刹；不能通用圆柱叠加后冠以真实名称。
- 石构/器物：连续轮廓、转折、孔洞、比例和构件叠置；平滑是几何连续性，不是消除真实束腰、台阶或遮挡。

Use an object-specific form table. Do not force bridge anatomy into a tower stack, invent hidden foundations, or smooth away historically visible transitions.

<a id="dimension-register"></a>
## 尺寸核对表 / Dimension register

用户要求“核准尺寸”“不能简化”时，逐项建表，而非用一个总高缩放整座建筑。每项包含：参数名、值或范围、单位、起止点/基准、内外构件、年代与修缮状态、来源 ID 及页码/图号、上表中的 `status`、冲突或缺失说明。没有可读测绘或修缮数据的项目保持未知，不填平均值；照片推算保留 `photo-estimate`，不得改写成实测。

| 核对项 | 必须区分的口径 |
|---|---|
| 层高 | 逐层楼面标高、檐口标高与两檐之间可见高度；外部檐层不等于内部楼层，不能把总高等分 |
| 收分 | 每层墙身、柱圈、檐缘分别计；八角形对边宽、对角宽、外接半径不能互换 |
| 檐挑 | 明确从墙面/柱轴到檐缘的水平距离；不以倾斜屋面长度或透视照片像素直接代替 |
| 台基 | 台面尺寸、台壁外露高度、室外地坪与台阶高差；山体与局部遮挡另列 |
| 塔刹 | 起算面、末端是否含针/避雷装置、各段数量和高宽；总高口径和后修状态分别核对 |

图纸尺寸也须检查扫描可读性、单位、年代与测量基准；模糊数字不靠 OCR 猜定。示意图的尺寸线和端点由已核对的同一几何参数生成，保留原资料的“约”和合理精度；报道值注明“报道”，照片估计注明“估计”，未知项不画成确定尺寸。若用户要求移除某个可见说明区，仅删除指定界面，台账和形制图仍按其选择保留，不重新塞回说明面板。

Track every requested measurement with its datum, endpoints, period and evidence status. Do not divide total height into equal storeys or substitute corner diameter for face width. Generate dimension endpoints from shared geometry; label reported and estimated values, and keep unknowns unresolved. Removing visible UI does not turn uncertain evidence into verified data.

## 标高、比例与可见范围 / Datums, proportions and visibility

- 读工程剖面时分别记录项目总高、±0.000、各楼层/构件标高、室外地坪与地形线；同时核对单位、起算点及所示方向。保护空间的总高度不等于整圈外露墙高，一个方向的地坪不代表全周。
- 原图仅有论文尾页、成果图或局部节点时，准确记录页码/图号及取得范围；不能称已取得完整施工图、原始点云或全部测量数据。
- 若山体、树木或水面遮住下部，允许表现有证据的上部片段。将显示截取位置和实际地面区分，保留整体尺寸的原始基准；不把人为截取高度写成现场尺寸。该选择写入 `scope`/说明及相关 claim 的 `basis`，不另造一个未受构建器支持的 status。
- 同一构件的分段比例尽量从同一张照片和同一尺度归一，再用其他角度交叉核对。照片像素值只是估计范围，不因保留小数而获得测绘精度。新照片推翻旧估计时，重算对应参数，不把旧代码值当成证据。
- 复杂塔刹/顶部先分清座、珠、开杯、环、盖、颈、尖的独立轮廓，再跨照片核对数量及高宽关系。相轮不能连华盖或座缘一起计数；不把某座塔的环数和比例写成其他对象的默认值。现场照片与修缮拆件可能处于不同状态，注明差异。

Keep engineering datums, visible ground and illustration cuts distinct. Normalize related proportions consistently, count actual components across views, and revise old estimates when new evidence contradicts them. A partial engineering figure does not establish unseen geometry or survey precision.

## 照片验收 / Photo comparison

把模型转到与照片相近的方位，比较外轮廓与关键负空间，再看装饰。照片透视与模型正交投影不同：先校准主要方向和共同尺度，不能要求像素完全重合。比例误差若来自未知拍摄参数，标明限制，不改成不真实的结构迎合单张照片。

至少检查：顶部形状、上下宽度关系、层数/开间、孔洞数与窗头、基座、构件接触。比较结论具体到部位；“代码无错”“已搜索”不等于“符合史实”。缺失侧面、年代冲突等会实质影响模型时，先进行可独立完成的调查，再向用户说明窄问题。

Compare the model from matching directions. Verify silhouette and negative space before ornament, accounting for perspective versus orthographic projection. State uncertainty at the affected feature rather than declaring unqualified historical accuracy.
