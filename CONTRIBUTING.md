# Contributing

感谢你帮助改进 `mcp-app-check`。项目优先接受可复现、范围明确、能降低 MCP Apps 开发摩擦的改动。

## 开发环境

要求 Python 3.10+，运行时无第三方依赖。

```powershell
git clone https://github.com/Uky0Yang/mcp-app-check.git
cd mcp-app-check
python -m pip install "ruff>=0.16,<0.17"
ruff format --check mcp_app_check tests
ruff check mcp_app_check tests
python -m unittest discover -s tests -t . -v
python -m compileall -q mcp_app_check tests
```

## 提交规则建议

新增或修改规则时，请同时提供：

1. 一个稳定且未使用的 `MCAxxx` rule ID；
2. 能失败的最小测试 fixture；
3. 正例与反例，避免只验证单一路径；
4. 清楚的严重级别、中文说明和可执行修复建议；
5. README 规则表与边界说明更新。

静态检查无法可靠判断的行为，应留给运行时测试，不要用宽泛正则制造大量误报。

## Pull request

- 保持改动聚焦，不顺带重构无关模块。
- 说明问题、实现和验证命令。
- 确保测试、compileall、wheel build、示例 smoke check 和 Action self-smoke 通过。
- 不提交真实 token、私有 MCP 配置、客户数据或生成目录。

提交 PR 即表示你同意按本项目 MIT 许可证贡献代码。
