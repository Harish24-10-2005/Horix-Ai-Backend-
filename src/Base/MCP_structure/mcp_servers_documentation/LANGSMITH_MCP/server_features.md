# LangSmith MCP Server Overview

## What is the LangSmith MCP Server?
The LangSmith MCP Server is a connector within the Vanij Platform that enables seamless interaction with the [LangSmith](https://smith.langchain.com) observability platform using its official API. It allows language models and development tools to fetch and manage prompt templates, datasets, conversations, traces, and more.

---

## Key Features
- ✅ Retrieve conversation histories and thread messages
- ✅ Access and manage prompt templates (public/private)
- ✅ Fetch LangSmith datasets and individual examples
- ✅ Trace and debug LLM runs with rich metadata
- ✅ Secure integration using API key authentication

---

## Capabilities
| Capability              | Description                                                            |
|--------------------------|------------------------------------------------------------------------|
| Prompt Management        | List, retrieve, and filter prompt templates                            |
| Thread History Access    | View full message history of a conversation thread                     |
| Trace Inspection         | Fetch traces using project or trace ID for analysis                    |
| Dataset Access           | List and read LangSmith datasets and associated examples               |
| Run Statistics           | Retrieve run statistics for a LangSmith project                        |
| Example Fetching         | Retrieve specific test examples with metadata and versioning options   |

---

## Supported LangSmith Versions
- Compatible with LangSmith API (stable release)
- Requires valid LangSmith API Key (token starting with `lsv2_`)
- Works with Python 3.10+ environments

---

## Security Notes
- Authenticated via **LangSmith API Key**
- Key must have read permissions for prompts, threads, datasets, and runs
- All requests are secured over HTTPS and scoped to user’s workspace

---

## Integration Use Cases
- AI debugging using conversational traces and run metadata
- Centralized prompt library access from LLM agents
- Fine-tuning workflows using datasets and examples
- Observability and analytics integration in LLM-powered apps
