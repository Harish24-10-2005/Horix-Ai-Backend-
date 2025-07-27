# Bugsnag MCP Server Overview

## What is the Bugsnag MCP Server?
The Bugsnag MCP Server is a connector that enables seamless interaction with the [Bugsnag](https://www.bugsnag.com) error monitoring platform using its REST API. It allows LLM tools like Cursor and Claude to explore, debug, and resolve application issues in real time.

---

## Key Features
- ✅ Browse organizations and projects in Bugsnag
- ✅ Filter and inspect application errors
- ✅ View detailed stacktraces with source code context
- ✅ Visualize exception chains to identify root causes
- ✅ Search errors by message, class, or version
- ✅ Track all occurrences of specific issues

---

## Capabilities

| Capability               | Description                                                    |
|--------------------------|----------------------------------------------------------------|
| Organization Listing     | Retrieve all Bugsnag organizations linked to your account      |
| Project Navigation       | List projects within an organization                           |
| Error Discovery          | Filter, sort, and analyze project-specific errors              |
| Stacktrace Exploration   | Inspect source-enriched stacktraces from error events          |
| Exception Chain Viewing  | Visualize and trace full exception chains                      |
| Issue Search             | Search for issues by error class, app version, or keywords     |
| Event History Tracking   | Access historical event logs for specific errors               |

---

## Supported Platforms
- Compatible with:
  - Cursor IDE
  - Claude Desktop
  - Any MCP-compatible LLM client
- No installation needed (runs via `npx`)
- Requires Bugsnag REST API access token

---

## Security Notes
- Authenticated via **Bugsnag API Key**
- API key must have the following scopes:
  - Read Projects
  - Read/Write Errors
  - Read/Write Comments
- Do not share your token publicly
- All interactions secured via HTTPS

---

## Integration Use Cases
- IDE integration for debugging with LLM agents
- Automated error triage and prioritization
- Root cause analysis of recurring issues
- LLM-powered monitoring dashboards