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
