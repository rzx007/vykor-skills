# Archify PR

固定上游 `tt-a1i/archify` 提交 `62f3a995eb26ee23f784bdea4a7992340078e9be` 的独立 PR 技能，沿用 Apache-2.0 许可并保留上游 NOTICE。入口为 `SKILL.md`，包装命令位于 `bin/archify-pr.mjs`。

需要先安装 `archify` 核心技能。默认从相邻的 `archify/bin/archify.mjs` 定位核心，因此安装到相同个人或项目范围即可。跨目录部署时，按包装器支持的 `ARCHIFY_BIN` 指定核心程序路径。需要 Node.js 18+，完整交付检查还需要 Chrome、Chromium 或 Edge。
