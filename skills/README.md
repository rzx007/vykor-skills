# 本仓库维护的技能

这里保存需要由市场直接分发的技能源码。每个技能目录包含 `SKILL.md`、适用许可证和运行所需的参考资料或示例。市场清单引用本仓库的固定提交，更新时先提交技能内容，再更新清单中的提交和版本。

- [develop-nomi-app](develop-nomi-app/SKILL.md) 用于创建 Nomi Web 应用或把已有网页接入 Nomi 桌面。配套参考文档和最小项目保留在同一技能目录。当前快照同步自 Nomi GitLab 主线提交 `c7266086badb4530ebc1ff01e43b5b84be87f8b7`，按 MIT 许可分发。
- [create-plugin](create-plugin/SKILL.md) 用于开发、验证和打包 Vykor 插件，包含 Native Tools 与 MCP 两种后台的天气工程及文本检查示例。首次收录来自 Vykor 提交 `afaddade7a3ca0a7f32f2a3d8b8a223f8c934935`，按 MIT 许可分发。市场副本将天气 Skill 存为模板文件，生成工程时恢复其入口名称。
