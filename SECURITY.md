# Security Policy

## Supported versions

当前只为最新发布版本提供安全修复。

## Reporting a vulnerability

请使用 GitHub 仓库的 **Security → Report a vulnerability** 私下提交报告，不要在公开 issue 中披露可利用细节或真实凭证。

报告请尽量包含：受影响版本、最小复现、预期与实际行为、影响评估，以及你已经尝试的缓解措施。维护者会确认收到报告，并在验证后协调修复与披露。

## Trust boundary

`mcp-app-check` 的设计边界是只读静态分析：不执行目标仓库代码、不安装目标依赖、不启动 MCP server、不调用模型或网络，也不跟随目录 symlink。若发现实现偏离这些边界，请按安全问题报告。
