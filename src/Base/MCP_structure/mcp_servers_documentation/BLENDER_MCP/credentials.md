# Blender MCP Server Credentials

## Overview

This document outlines how credentials are handled for the **Blender MCP Server** integration within the **Vanij Platform**. Unlike other MCP connectors, Blender MCP does **not require traditional API credentials**. Instead, it relies on a local addon and port-based communication.

---

## Credential Format

Although no credentials are required by default, the standard JSON format is:

```json
{
  "BLENDER_MCP": {

  }
}
```

> ✅ **Note:** You can leave this object empty for basic Blender MCP functionality.

---

## Setup Instructions

Blender MCP operates by installing a local Blender addon and running a socket server on port **9876**. No authentication or tokens are required for this local connection.

### Required Steps:

## 🧩 Blender MCP Addon Installation & Connection Guide

Follow these steps to install and start the Blender MCP server on your local machine:

### 🔧 Installation Steps

1. **Download** the [`addon.py`](https://github.com/ahujasid/blender-mcp/blob/main/addon.py) file from the official repository.
2. **Open Blender** and navigate to:
   `Edit > Preferences > Add-ons`
3. Click **Install...**, select the downloaded `addon.py` file.
4. Enable the addon by checking the box next to **"Interface: Blender MCP"**.
5. Once enabled, the MCP server will automatically start and **listen on port `9876`**.

---

### 🚀 Connecting to Ai Agent

![Addon Instructions](https://github.com/adya-hackathon/adya_mcp_hackathon/blob/main/mcp_servers/python/servers/BLENDER_MCP/blender-mcp/assets/addon-instructions.png?raw=true)

1. In Blender, open the **3D View**.
2. Press `N` to open the right-hand sidebar (if it's not already visible).
3. Navigate to the **BlenderMCP** tab.
4. (Optional) Enable the **Poly Haven** checkbox to allow asset import via their API.
5. Click the **"Connect to Claude"** button.
6. Ensure the MCP server is also running via terminal (via AI Agent) for proper communication.

> ✅ Once connected, you can begin using natural language commands via Claude to create and manipulate 3D scenes inside Blender.


---

## Optional: Sketchfab and Hyper3D Credentials

If you wish to use external services like **Sketchfab** or **Hyper3D**, you can enter the necessary API keys **directly in the Blender interface**.

### Instructions:

* Open Blender with the MCP addon enabled.
* Navigate to the **BlenderMCP** tab in the right-hand sidebar (`N` key).
* Look for the fields to enter:

  * **Sketchfab API Key**
  * **Hyper3D API Key**

These credentials are stored locally and used to access advanced 3D model generation and downloading features.

---

## Notes

* No internet-facing credentials are required for core Blender MCP operations.
* Always keep your local setup secure, especially if running on shared systems.
* Port `9876` must remain open locally for communication between Claude/Vanij and Blender.

---

