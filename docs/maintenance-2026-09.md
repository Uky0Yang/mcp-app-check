# 显式配置与忽略规则（v0.3.0）

```bash
mcp-app-check . --ignore MCA004 --ignore MCA005
mcp-app-check . --config /trusted/policy.json --format json
```

可信 policy.json 示例：

```json
{"ignore": ["MCA004"], "fail_on": "warning"}
```

配置只接受 ignore 和 fail_on。未知规则、拼写错误、错误字段类型和无效 JSON
返回退出码 2。命令行 --ignore 与配置合并，显式 --fail-on 优先于配置。
工具不会自动发现目标仓库中的配置，避免被扫描项目自行降低检查门槛。

JSON/text/SARIF 报告保留被抑制问题数量；忽略规则不代表问题已修复。
GitHub Action 支持 config 输入，fail-on 输入仍由 workflow 明确控制。
