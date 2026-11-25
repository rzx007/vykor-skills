# 古建蓝图技能

固定来源为 `tanglele110-hash/heritage-blueprint-skill` 提交 `f5e7c5381187e6d362bc375f134688e2b1d91456`，入口见 [SKILL.md](SKILL.md)。

## 内容与许可

保留技能正文、五份参考资料、构建和校验脚本、HTML 模板、完整字体及来源记录，以及 MIT 许可的 Santan 输入范例。原创说明、代码和模板沿用 [MIT LICENSE](LICENSE)，IBM Plex Sans TC 字体保留 [OFL 1.1](assets/fonts/OFL.txt) 和 [来源信息](assets/fonts/provenance.json)。具体版权范围见 [COPYRIGHT.md](COPYRIGHT.md)。

上游另行保留版权的 `assets/examples/santan/approved.html` 和 `docs/media/` 展示作品通过固定上游链接查阅。市场副本将正文及视觉核验说明中的成品链接改为该提交的公开链接，本 README 记录分发来源和内容范围。其余保留的上游文件沿用原文。

## 使用

Python 3 执行 `scripts/build.py`，Node.js 执行 `scripts/verify.cjs`；两份脚本使用标准库。查看成品需要支持 WebGL 的浏览器。每个对象的证据和几何输入按实际任务编写，范例用于说明输入接口。
