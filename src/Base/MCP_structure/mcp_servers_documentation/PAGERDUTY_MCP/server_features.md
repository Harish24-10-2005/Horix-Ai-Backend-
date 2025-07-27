# PagerDuty MCP Server Overview

## What is the PagerDuty MCP Server?
The PagerDuty MCP Server is a connector within the Vanij Platform that enables seamless interaction with the PagerDuty incident management platform using the PagerDuty REST API. It allows language models and automated systems to access incident data, on-call schedules, team assignments, and more.

---

## Key Features
- ✅ Retrieve incidents, services, teams, users, and escalation policies
- ✅ Query who is currently on-call across teams and schedules
- ✅ Filter incidents by status, urgency, or assigned users
- ✅ Automatically handle API pagination and rate limits
- ✅ Return consistent, LLM-friendly JSON responses with metadata

---

## Capabilities
| Capability             | Description                                                              |
|------------------------|--------------------------------------------------------------------------|
| Incident Management     | List, filter, and search incidents based on status, urgency, or teams    |
| On-call Schedules       | Check current and upcoming on-call assignments across schedules          |
| Team & Service Lookup   | Retrieve PagerDuty services, escalation policies, and teams              |
| User Context Filtering  | Automatically filter resources based on the current user                |
| Response Structuring    | Get clean structured metadata with every query response                 |

---

## Supported PagerDuty Versions
- Uses the stable [PagerDuty REST API v2](https://developer.pagerduty.com/api-reference/)
- Requires a valid PagerDuty **API Token** (REST API scope)
- Supports all PagerDuty commercial and free-tier accounts

---

## Security Notes
- Authenticated via **PagerDuty API Token**
- API token must have permission to read incidents, services, users, teams, and schedules
- All communications must be made over HTTPS
- Token should be treated as a secret and never exposed in public

---

## Integration Use Cases
- Incident triaging and status reporting using LLMs
- On-call schedule awareness and automation
- Real-time alert management in DevOps workflows
- Natural language querying for incident and team data
