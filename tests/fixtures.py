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
