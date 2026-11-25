# Blender 制作指南

固定来源为 `arjun988/blender-skills` 提交 `904f095d8f36a6e72adaebb08d07f884a074743d`，保留上游 [MIT LICENSE](LICENSE)。使用入口和完整索引见 [SKILL.md](SKILL.md)。

## 分发内容

将上游 `.claude/skills/` 的 94 份技能正文和 175 份参考资料放在 `guides/`。正文采用 `guide.md` 文件名，由根入口按任务加载。修正 procedural-modeling、sculpting 的跨指南链接，以及共享参考图像匹配文档的相邻路径。

包内 [MCP 设置说明](docs/BLENDER_MCP_SETUP.md)来自同一提交，相关配置示例通过固定上游链接查阅。已有兼容的 Blender MCP 连接可以直接使用；需要配置时按设置说明操作。

## 使用条件

自动操作需要 Blender 和可用的 Blender MCP。缺少连接时，可按指南制定方案或编写由用户运行的 bpy 脚本。Sketchfab、Hyper3D、Hunyuan3D、Poly Haven 按任务需要配置。
