# Red Hat API MCP Server Overview

## What is the Red Hat API MCP Server?
The Red Hat API MCP Server is a connector within the Vanij Platform that enables seamless interaction with Red Hat's Case Management and Knowledge APIs. It allows LLM applications to query, retrieve, and process Red Hat support content and technical solutions.

---

## Key Features
- ✅ Search and retrieve Red Hat KCS solutions and articles
- ✅ Access structured solution content like issue, environment, and resolution
- ✅ Search and retrieve Red Hat support cases
- ✅ View full case details including summary, description, severity, and comments
- ✅ Built-in prompt templates for case summarization and resolution workflows

---

## Capabilities
| Capability              | Description                                                        |
|-------------------------|--------------------------------------------------------------------|
| KCS Solution Search     | Query knowledge base solutions with full-text or advanced filters  |
| Solution Retrieval      | Fetch detailed solution content using solution ID                  |
| Case Management         | Search and retrieve support cases                                  |
| Case Insights           | View structured case metadata and conversation history             |
| Prompt-Based Summaries  | Generate technical summaries using LLM-powered prompts             |

---

## Supported Red Hat APIs
- Red Hat Knowledge API (KCS)
- Red Hat Case Management API
- Hydra Query Syntax (Solr-style full-text search)

---

## Security Notes
- Authenticated via **Red Hat offline API token**
- Token must be generated from a valid Red Hat developer or enterprise account
- All communications are secured over HTTPS
- The token must be stored securely and never shared publicly

---

## Integration Use Cases
- Intelligent technical support assistants
- Automated case triaging and analysis
- DevOps workflows with Red Hat API integrations
- Knowledge extraction and summarization from Red Hat KCS articles
