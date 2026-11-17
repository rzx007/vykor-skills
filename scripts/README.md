# 市场构建与发布

`market.py build` 从根清单读取固定提交，在 `dist/packages` 创建各技能 ZIP，并生成 `dist/marketplace.json`。`verify` 对照清单与文件核对地址、大小、摘要和包结构。`publish` 在官方仓库 main 分支的 Actions 中上传 Release 资产，再把索引准备到 `dist/public`，由 Pages 部署。维护这几个步骤的代码放在这里，打包测试位于 `__test__`。
