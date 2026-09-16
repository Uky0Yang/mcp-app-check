# Roadmap

路线图只表示候选方向，不代表已经实现或承诺发布时间。

## v0.1 — Released

- [x] `ui://`、MIME、工具绑定和返回数据静态检查
- [x] CSP、敏感浏览器权限与常见密钥风险检查
- [x] 中文文本报告和 JSON 输出
- [x] 可配置 CI 失败阈值
- [x] 可复用 GitHub Action wrapper
- [x] Windows 与 Linux CI 覆盖的纯 Python 实现

## v0.2 — Current

- [x] SARIF 2.1.0 输出和源码位置映射
- [x] GitHub Action 可选报告输出文件
- [x] GitHub Code Scanning 上传示例
- [x] 官方 TypeScript `RESOURCE_MIME_TYPE` 与 `registerAppResource` 默认 MIME
- [x] 官方 Python FastMCP `TextContent` 文本降级识别
- [x] 10 个公开仓库、38 个 App surface 的固定 SHA 兼容性扫描
- [x] 区分外部资源加载与普通 HTTPS 字符串，降低 `MCA007` 误报

## Next — Planned

v0.3 已实现：`--ignore`、显式 JSON 配置和可见的 suppression 计数。

- [ ] 更多 Python 边界用例与 C# SDK 语法 fixture
- [ ] 在不泄露值的前提下增强 secret diagnostics

## Later — Explore

- [ ] 稳定规范与 draft 规范 profile
- [ ] 资源 URI 与工具引用的静态一致性检查
- [ ] MCP Inspector 导出的运行时证据导入
- [ ] 基于真实误报反馈的自动修复建议

不在当前范围：自动启动未知 MCP server、执行目标脚本、代替宿主端兼容性测试。
