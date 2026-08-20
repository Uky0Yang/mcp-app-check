## Summary

说明问题和最小改动。

## Verification

- [ ] `python -m unittest discover -s tests -t . -v`
- [ ] `python -m compileall -q mcp_app_check tests`
- [ ] `python -m mcp_app_check examples\ready-app --fail-on warning`
- [ ] 新规则包含正例、反例、稳定 ID、修复建议和 README 更新
- [ ] 未提交真实凭证、私有配置或生成文件
