# 构件连接与负空间 / Contacts and negative space

在新增复杂连接、用户指出脱节/穿插，或照片显示孔洞类型与模型不同时读取。它补充场景专属检查，不要求每次小改都运行整套射线测试。

Use this reference for connection repairs, intersecting building parts and ambiguous openings. Choose checks that address the actual defect; this is not a mandatory full test suite for every edit.

## 先分清关系 / Identify the intended relationship

| 部位 | 要确认的可见关系 | 定向检查 |
|---|---|---|
| 外梯与台基 | 末级踏面接到真正的多边形台面边线；石帮连续；围栏入口对齐 | 从台阶中线及两侧采样最终踏面与台面接触；检查入口净空，旁边有栏杆作为正向对照 |
| 柱脚、斜撑 | 脚座落地、头部接檐下；倾斜方向和内外圈来自实照 | 检查最终顶点/面或表面距离；观察脚部与头部近景，不用名义端点代替接触 |
| 屋面与墙体 | 檐下门窗、屋面以上实墙/层带各有正确范围 | 侧视和低角度检查墙体穿檐造成的假窗带、额外楼层及支承头透出屋面 |
| 贯通孔 | 真正留空，有厚度、内壁与正确前后遮挡 | 从照片可见方向做穿孔射线，邻近实体表面应可命中；浏览器转向复核 |
| 假窗/壁龛 | 有后壁和凹入深度，不是贯通玻璃窗 | 检查洞口与后壁的深度关系；背墙不应随视角消失 |
| 开口杯、钵 | 杯沿、内壁、杯底和中央构件彼此分清 | 检查内腔深度与口沿，不用实心鼓包或背景色假孔替代 |
| 叠置构件 | 合拢时接触；分解是解释性位移 | 检查闭合相位的实际面与边缘，收起复原同一网格变换 |

表中采样点数、容差和射线长度由本对象单位、网格和缺陷决定，不照搬上一座塔的数值。多边形外接半径不是面中线到中心的距离；楼梯等附件须接实际边/面，而非接到想象的圆周。

Counts, tolerances and ray lengths are object-specific. Polygon circumradii are not face offsets. Test the actual generated triangles or surfaces, with positive controls, rather than merely comparing declared parameters.

## 修复与复核 / Repair and verify

1. 保留修改前源文件与结果，按照片定位具体边界和接头。小修保持已认可的字体、配色、交互及无关形制。
2. 从根因修正参数、轮廓或面关系。不要用孤立填块遮住楼梯断缝，或用改变相机、黑晕、面片覆盖色掩饰穿插。仅在证据支持时补连接件。
3. 修复不应删掉真实束腰、台阶、口沿或折线；平滑曲面隐藏计算网格线，真实构件分界仍保留。
4. 运行能直接发现本次缺陷的数值/射线检查，并在最终浏览器近景复核连接、内外表面和遮挡。若线框因深度偏移透出屋面，检查线与面的实际位置和已有深度设置，不用加粗或填黑遮掩。
5. 回到整体视图对照多角度实照，检查修复有没有引入额外层、错误收分或比例变化。同步依赖这些参数的示意与取景包络，再做受影响布局和展开/收起检查。

Fix the geometry that causes the gap or intersection. Preserve real profile transitions and approved presentation. Pair a targeted geometric check with final rendered close-ups and an overall photo comparison; neither substitutes for the other.
