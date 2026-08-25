READY_APP = """
const RESOURCE_URI = "ui://weather/dashboard.html";

server.registerResource("weather-ui", RESOURCE_URI, {}, async () => ({
  contents: [{
    uri: RESOURCE_URI,
    mimeType: "text/html;profile=mcp-app",
    text: "<html><body>Weather</body></html>",
    _meta: { ui: { csp: { connectDomains: ["https://api.example.com"] } } }
  }]
}));

server.registerTool("weather", {
  _meta: { ui: { resourceUri: RESOURCE_URI } }
}, async () => ({
  content: [{ type: "text", text: "Weather: sunny" }],
  structuredContent: { condition: "sunny" }
}));
""".strip()


OFFICIAL_TYPESCRIPT_HELPERS_APP = """
import {
  registerAppResource,
  registerAppTool,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";

const RESOURCE_URI = "ui://weather/dashboard.html";

registerAppResource(server, "weather-ui", RESOURCE_URI, {
  mimeType: RESOURCE_MIME_TYPE,
}, async () => ({
  contents: [{
    uri: RESOURCE_URI,
    mimeType: RESOURCE_MIME_TYPE,
    text: "<html><body>Weather</body></html>",
  }],
}));

registerAppTool(server, "weather", {
  _meta: { ui: { resourceUri: RESOURCE_URI } },
}, async () => ({
  content: [{ type: "text", text: "Weather: sunny" }],
  structuredContent: { condition: "sunny" },
}));
""".strip()


OFFICIAL_TYPESCRIPT_DEFAULT_MIME_APP = """
import {
  registerAppResource,
  registerAppTool,
} from "@modelcontextprotocol/ext-apps/server";

const RESOURCE_URI = "ui://weather/dashboard.html";

registerAppResource(server, "weather-ui", RESOURCE_URI, {}, async () => ({
  contents: [{ uri: RESOURCE_URI, text: "<html><body>Weather</body></html>" }],
}));

registerAppTool(server, "weather", {
  _meta: { ui: { resourceUri: RESOURCE_URI } },
}, async () => ({
  content: [{ type: "text", text: "Weather: sunny" }],
  structuredContent: { condition: "sunny" },
}));
""".strip()


OFFICIAL_TYPESCRIPT_UNUSED_MIME_IMPORT_APP = """
import { RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";

const RESOURCE_URI = "ui://weather/dashboard.html";

server.registerResource("weather-ui", RESOURCE_URI, {}, async () => ({
  contents: [{ uri: RESOURCE_URI, text: "<html><body>Weather</body></html>" }],
}));

server.registerTool("weather", {
  _meta: { ui: { resourceUri: RESOURCE_URI } },
}, async () => ({
  content: [{ type: "text", text: "Weather: sunny" }],
  structuredContent: { condition: "sunny" },
}));
""".strip()


OFFICIAL_PYTHON_FASTMCP_APP = """
from mcp import types
from mcp.server.fastmcp import FastMCP

VIEW_URI = "ui://say-demo/view.html"
mcp = FastMCP("Say Demo")


@mcp.tool(meta={"ui": {"resourceUri": VIEW_URI}})
def say(text: str) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=f"Spoke: {text}")]


@mcp.resource(VIEW_URI, mime_type="text/html;profile=mcp-app")
def view() -> str:
    return "<html><body>Say demo</body></html>"
""".strip()

OFFICIAL_PYTHON_DIRECT_TEXT_CONTENT_APP = OFFICIAL_PYTHON_FASTMCP_APP.replace(
    "from mcp import types", "from mcp.types import TextContent"
).replace("types.TextContent", "TextContent")


HTML_CONTENT_ATTRIBUTE_WITHOUT_TOOL_FALLBACK = """
const RESOURCE_URI = "ui://weather/dashboard.html";

server.registerResource("weather-ui", RESOURCE_URI, {}, async () => ({
  contents: [{
    uri: RESOURCE_URI,
    mimeType: "text/html;profile=mcp-app",
    text: "<html><head><meta content='light dark'></head></html>",
  }],
}));

server.registerTool("weather", {
  _meta: { ui: { resourceUri: RESOURCE_URI } },
}, async () => ({
  structuredContent: { condition: "sunny" },
}));
""".strip()


UNLOADED_EXTERNAL_URL_APP = (
    READY_APP.replace(
        '_meta: { ui: { csp: { connectDomains: ["https://api.example.com"] } } }',
        "_meta: { ui: {} }",
    )
    + """

const linkUrl = "https://modelcontextprotocol.io/";
const schemaDescription = "Full guide: https://example.com/docs";
"""
)
