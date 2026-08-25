# 公开 MCP Apps 兼容性扫描

本报告记录对公开 MCP Apps 源码进行的可复现静态扫描。它是 `mcp-app-check` 规则覆盖证据，不代表任何样本项目已经通过安全认证，也不代表其与所有宿主运行时兼容。

## 扫描快照

- 扫描日期：2026-08-25（Europe/London）
- 扫描器版本：`0.2.3`
- 仓库：10 个公开且未归档的仓库
- 独立 App surface：38 个
- 已扫描源码文件：1,102 个
- 跳过文件：0 个
- 核心错误：0 个
- 建议级警告：20 个
- 无警告 surface：21 个

样本来自对稳定 MCP App MIME 和官方 `registerAppResource` helper 的 GitHub 代码检索。选样刻意覆盖官方示例、社区 demo、面向生产的 server、TypeScript、Python、C# 和框架特定实现。这是用于工程复核的多样化样本，不是具有统计代表性的总体抽样。

判定基线来自 [MCP Apps 官方概览](https://modelcontextprotocol.io/extensions/apps/overview)、[`2026-01-26` stable specification](https://github.com/modelcontextprotocol/ext-apps/blob/10195ad91851502134930e9b80ec2c04e277a720/specification/2026-01-26/apps.mdx) 和 [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)。规则仍是项目自己的保守静态启发式，不把官方来源写成对本工具的认证。

## 固定源码快照

| 仓库 | Commit 与扫描范围 | Surfaces | 文件 | Errors | Warnings |
| --- | --- | ---: | ---: | ---: | ---: |
| `modelcontextprotocol/ext-apps` | [`10195ad` — `examples/*-server`](https://github.com/modelcontextprotocol/ext-apps/tree/10195ad91851502134930e9b80ec2c04e277a720/examples) | 25 | 224 | 0 | 14 |
| `MCPJam/inspector` | [`1dfda1a` — `examples/mcp-apps`](https://github.com/MCPJam/inspector/tree/1dfda1a2e51dee80c5330e0c3cd8ece2b35c5ae4/examples/mcp-apps) | 4 | 55 | 0 | 2 |
| `digitarald/mcp-apps-playground` | [`3ba7445`](https://github.com/digitarald/mcp-apps-playground/tree/3ba7445c83fa7223b59fa54fb8f20fd502ca696f) | 1 | 10 | 0 | 0 |
| `excalidraw/excalidraw-mcp` | [`157aa23`](https://github.com/excalidraw/excalidraw-mcp/tree/157aa23ceb1976008aadc89eb05e3444060f09d6) | 1 | 21 | 0 | 1 |
| `vercel-labs/mcp-apps-nextjs-starter` | [`adca42c`](https://github.com/vercel-labs/mcp-apps-nextjs-starter/tree/adca42ccaeda3c34a322808b51f70200f14e3c89) | 1 | 15 | 0 | 0 |
| `microsoft/flint-chart` | [`34ef451` — `packages/flint-mcp`](https://github.com/microsoft/flint-chart/tree/34ef4516554b323a740a426bd1a1e6ba31ee8245/packages/flint-mcp) | 1 | 35 | 0 | 1 |
| `mapbox/mcp-server` | [`6f031d5`](https://github.com/mapbox/mcp-server/tree/6f031d5fa4f77f1ea921b0390d09c3534db1aaf4) | 1 | 174 | 0 | 0 |
| `tableau/tableau-mcp` | [`0710e07`](https://github.com/tableau/tableau-mcp/tree/0710e07554f0a49d17422e02e0b4d20633453b1c) | 1 | 547 | 0 | 0 |
| `openai/openai-apps-sdk-examples` | [`18cc38e` — two Node examples](https://github.com/openai/openai-apps-sdk-examples/tree/18cc38e78a968712c357bacdc3c79fead5bfc6b4) | 2 | 8 | 0 | 0 |
| `Azure-Samples/remote-mcp-functions-dotnet` | [`468c518` — `src/McpWeatherApp`](https://github.com/Azure-Samples/remote-mcp-functions-dotnet/tree/468c518c884ec318e3001b9573254c9e775409c9/src/McpWeatherApp) | 1 | 13 | 0 | 2 |

官方仓库中每个包含 `server.ts` 或 `server.py` 的示例目录都单独扫描，避免同一仓库里一个完整示例掩盖另一个示例缺少的信号。

## 发现

| 规则 | 数量 | 解释 |
| --- | ---: | --- |
| `MCA004` | 14 | 所选 surface 中没有字面量 `structuredContent` 或 `structured_content`。这是建议级信号，不是协议失败。 |
| `MCA005` | 2 | Python QR 示例返回图像内容而没有文本 fallback。Azure Functions C# 示例返回可序列化对象，但仅凭源码语法无法证明其最终 MCP wire representation。 |
| `MCA006` | 4 | 项目明确声明了 clipboard 或 microphone 权限；人工复核确认警告确实指向权限元数据。 |
| `MCA001`–`MCA003`、`MCA008`、`MCA009` | 0 active | 固定快照中没有报告核心声明、通配 CSP 或常见密钥模式错误。 |

本次扫描暴露出一组 `MCA007` 误报：用作 `openLink` 目标、表单默认值、注释、schema 文档和服务端数据的 HTTPS 字符串，被错误视为浏览器资源加载。`0.2.3` 将规则收紧到直接包含 HTTPS literal 的 `fetch(...)`、`WebSocket(...)`、`EventSource(...)`、`src=`、stylesheet link 和 CSS `url(...)` 等明确加载语法。回归测试同时覆盖应当报警的 `fetch(...)` 正例和不应报警的未加载 URL 反例。

## 复现方法

本次没有安装、构建或执行任何样本项目代码。每个仓库都以 partial/sparse checkout 固定到表格中的精确 commit，然后使用本地 CLI 扫描：

```powershell
python -m mcp_app_check <checked-out-scope> --format json --fail-on none
```

对于包含多个独立 App 的仓库，每个 App 目录分别运行一次。`--fail-on none` 让证据收集在遇到建议级 warning 时继续运行，不会从 JSON 报告中隐藏 finding。

## 边界

- 这是保守的文本静态分析，不是 AST 或 data-flow analysis。
- 没有执行 MCP handshake、resource read、iframe sandbox、认证或宿主渲染。
- Warning 只记录需要复核的信号，不证明样本仓库存在缺陷。
- 框架可能在运行时生成最终 MCP content；Azure Functions C# 返回对象仍是明确的静态分析覆盖缺口。
- 结果只适用于表格列出的 commit 和 scope；上游仓库可能在本报告之后变化。
