# PagerDuty MCP Server – Demos and Payload Examples

## 🎥 Demo Video
- **MCP server setup explanation + API Execution + Features Testing**: [Watch Here](https://drive.google.com/file/d/1Z_rAAzDL8Fo8kOpyqPpGu9-RSOv2_9hX/view?usp=drive_link)

---

## 🎥 Credentials Gathering Video
- **Gathering Credentials & Setup (Full end-to-end video)**: [Watch Here](https://drive.google.com/file/d/1fNg77-bK51S2eVD1fqsmuydlzGGx7Vv0/view?usp=sharing)

---

## 🔐 Credential JSON Payload
Example payload format for sending credentials to the MCP Server which is going to be used in the Client API payload:
```json
{
  "PAGERDUTY": {
    "api_token": "your-pagerduty-api-token"
  }
}
````