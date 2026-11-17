# 市场构建与发布

`market.py build` 从根清单读取固定提交，在 `dist/packages` 创建各技能 ZIP，并生成 `dist/marketplace.json`。`verify` 对照根清单核对公开索引，再检查每个 ZIP 的大小、摘要和文件结构。`publish` 在官方仓库 main 分支的 Actions 中检查已发布的 `skills-vN` Release 和本次发布的草稿。同名 ZIP 的大小或摘要有变化时，发布会在上传前停止。发布成功后，脚本将索引复制到 `dist/public`，由 Pages 部署。构建和发布测试位于 `__test__`。
