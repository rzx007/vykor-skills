# Vykor 技能市场

Vykor 桌面端读取 [官方技能索引](https://rzx007.github.io/vykor-skills/marketplace.json)，从 [Releases](https://github.com/rzx007/vykor-skills/releases) 下载对应版本的 ZIP。

## 收录与更新

在根目录 `marketplace.json` 维护技能清单。每个条目固定上游仓库、完整提交、技能路径与分发版本。根目录技能需要明确列出要打包的文件和目录。检查技能正文、脚本、必要的参考资料及适用许可证，并试用包内的实际入口。保持技能 ID 与 `SKILL.md` 的名称稳定。技能包内容变化时增加条目版本与顶层 `release` 序号。

本地构建使用 Python 3.11+，构建过程读取上游固定提交的归档并打包文件。

```sh
python -m unittest discover -s scripts/__test__
python scripts/market.py build
python scripts/market.py verify
```

`dist/marketplace.json` 是公开索引，记录上游来源、分发版本以及 ZIP 的地址、大小和 SHA-256。ZIP 的根目录含 `SKILL.md` 和 `LICENSE`，辅助文件沿用原相对路径。

## 发布

PR 构建并验证全部条目。main 分支的工作流先发布 Release，确认同名资产的大小与摘要匹配，再部署 Pages 索引。发布任务只上传已验证的构建产物。详见 [脚本说明](scripts/README.md)。
