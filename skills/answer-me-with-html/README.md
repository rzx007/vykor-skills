# Answer me with HTML

本技能把 Markdown 草稿渲染成单页 HTML，布局与图表由附带的 CLI 生成。

## 来源与保留范围

- 上游：[QingYunA/answer-me-with-html](https://github.com/QingYunA/answer-me-with-html)。
- 固定提交：`4ad397361bcb59b0791b84783ed99ef91d4b2f07`（上游版本 0.6.4）。
- 原始目录：[`skills/answer-me-with-html`](https://github.com/QingYunA/answer-me-with-html/tree/4ad397361bcb59b0791b84783ed99ef91d4b2f07/skills/answer-me-with-html)。
- 该目录的六个文件按原字节保留。另附上游根目录的原始 MIT [LICENSE](LICENSE)、本说明及缺失的第三方许可通知。
- `scripts/am.mjs` 是上游预先构建的单文件程序，无须重新构建或安装 npm 依赖；SHA-256：`44e4610c22917cfd760e35619c394726b69e57881a3f211c2797cb973e41fa88`。

## Vykor 使用

入口是 [SKILL.md](SKILL.md)。基本页面渲染需要 Node.js 20 或更高版本。按上游已有的非 Claude 宿主说明，将命令和引用中的 `${CLAUDE_SKILL_DIR}` 换成实际包含 `SKILL.md` 的绝对目录；Vykor 不需要自动展开这个变量，也无需修改运行脚本。

`references/codebase.md`、`references/settings.md`、`references/video.md` 分别说明代码解读、设置与视频模式。视频导出和语音的额外依赖以相应文档为准。渲染会写页面；上游默认可打开浏览器、检查更新，验证命令可用 `--no-open` 和 `AM_NO_UPDATE_CHECK=1` 禁用这些行为，并用 `AM_HOME` 指向独立测试目录。

上游设置文档中的更新命令描述上游安装方式。本目录由 Vykor 技能包维护；更新此副本应更新固定来源与包内容，不要把其他安装方式的更新命令当作本包更新入口。

## 许可证与构建产物通知

项目代码和文档沿用上游 MIT 许可；这不改变所嵌入第三方内容的许可。

| 内容 | 固定版本与来源 | 保留的许可文件 |
| --- | --- | --- |
| 项目本身 | 上述固定提交 | [LICENSE](LICENSE)，MIT，2026 Answer me with HTML contributors |
| Dagre 与 graphlib | `@dagrejs/dagre` 3.1.3、`@dagrejs/graphlib` 4.0.6 | [scripts/dagre.esm.js.LEGAL.txt](scripts/dagre.esm.js.LEGAL.txt)，MIT，2012–2014 Chris Pettitt |
| Marked | 18.2.0 | [licenses/LICENSE-marked.txt](licenses/LICENSE-marked.txt)，保留 Marked MIT 及其附带的 Markdown 三条款再分发通知 |
| Temml | 0.14.0 | [licenses/NOTICE-Temml.txt](licenses/NOTICE-Temml.txt)，复制 bundle 中完整 MIT 与来源通知；涉及的 Apache 部分另附 [licenses/Apache-2.0.txt](licenses/Apache-2.0.txt) |
| Bangers 字体 | `@fontsource/bangers` 5.3.0 | [licenses/OFL-Bangers.txt](licenses/OFL-Bangers.txt)，SIL OFL 1.1 |

依赖版本取自固定提交的 [package-lock.json](https://github.com/QingYunA/answer-me-with-html/blob/4ad397361bcb59b0791b84783ed99ef91d4b2f07/package-lock.json)。补充文件的原文来源：

- Dagre：[固定提交的 dist/dagre.esm.js.LEGAL.txt](https://raw.githubusercontent.com/dagrejs/dagre/a73acbfebe6fda008e1a3d80f3738170699c3d6b/dist/dagre.esm.js.LEGAL.txt)。该文件与 `am.mjs` 同目录，满足 bundle 尾部的相对文件名提示；它仅是通知，不由运行时代码加载。
- graphlib：[固定提交的 LICENSE](https://raw.githubusercontent.com/dagrejs/graphlib/3d9829c896ad4628136cc223f4a76af9b78ab5b9/LICENSE)，正文与上述 Dagre MIT 许可相同。
- Marked：[18.2.0 npm 包](https://registry.npmjs.org/marked/-/marked-18.2.0.tgz)中的 `package/LICENSE`。
- Temml：[0.14.0 npm 包](https://registry.npmjs.org/temml/-/temml-0.14.0.tgz)；其 `src/utils.js` 注明 `hyphenate`、`escape` 改编自 Facebook React 的 Apache 许可代码。bundle 中的通知还保留 mhchem 的 MathJax Consortium（2011–2015）和 Martin Hensel（2015–2018）版权，见[固定提交中的 mhchem 来源](https://github.com/ronkok/Temml/blob/ac68f15a6e9fa89f9c72e0827a13a6bd0d36f612/contrib/mhchem/mhchem.js)。
- Apache：[官方完整 Apache-2.0 许可文本](https://www.apache.org/licenses/LICENSE-2.0.txt)。

适配只增加来源说明和许可文件，不改上游的技能指令、引用文档、字体许可或生成的 JavaScript。

## 验证说明

上游 frontmatter 的 `argument-hint` 原样保留。skill-creator 的 `quick_validate.py` 使用较窄的字段白名单，会拒绝这一字段；这项检查不能替代 Vykor 实际技能解析与市场安装验证。附带 CLI 的基本 HTML 渲染可以在临时目录中验证，无须预览、截图或启动浏览器。
