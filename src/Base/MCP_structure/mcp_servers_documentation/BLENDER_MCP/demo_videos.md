Here’s the **Blender MCP Server – Demos and Payload Examples** section, adapted to match the same structure and tone as the WordPress version:

---

# Blender MCP Server – Demos and Payload Examples

## 🎥 Demo Video

* **Full Blender MCP setup, Claude integration, and feature walkthrough**:
  [Watch Here](https://drive.google.com/file/d/11hxWUZ0IPeHOLFvfYuYdEwQ2qfcvA3LE/view?usp=drive_link)

---

## 🎥 Addon Installation & Configuration Video

* **Complete end-to-end installation of the MCP Addon + integration **:
  [Watch Here](https://drive.google.com/file/d/1lfKnXcElJqi9ohBLZcT31iVlcTuW6Fg8/view?usp=drive_link)

---

## 🔐 Credential JSON Payload

Although Blender MCP doesn't require credentials for core functionality, here’s the standard placeholder payload format used when calling the Client API:

```json
{
  "BLENDER_MCP": {

  }
}
```

> ⚠️ **Note:** No username/password is needed for Blender MCP.
> The server runs locally on port `9876` via the installed `addon.py` in Blender.

---

## 🎯 Optional Credential Input (Sketchfab & Hyper3D)

If you plan to use external services like **Sketchfab** or **Hyper3D**, you can manually enter their API keys within the Blender MCP panel:



> These keys are not required for core operations but unlock asset import and AI-based 3D generation features inside Blender.

---

Let me know if you'd like this embedded in a larger README, converted to Markdown, or tailored for API documentation systems like Swagger or Postman!
