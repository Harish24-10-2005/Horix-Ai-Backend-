
---

# BlenderMCP Server Overview

## What is the BlenderMCP Server?

The **BlenderMCP Server** integrates **Blender** with Ai Agent like **AI Agent wth Human Feed back loop preferably** via the **Model Context Protocol (MCP)**. It enables prompt-assisted 3D modeling, scene creation, and manipulation — giving AI tools direct access to control Blender in real time.

---

## Key Features

* ✅ **Two-way connection** between AI Agents and Blender
* ✅ **Object creation and manipulation** directly via prompts
* ✅ **Material and lighting control**
* ✅ **Scene inspection** with structured output
* ✅ **Poly Haven** and **Hyper3D** integration for 3D assets
* ✅ **Sketch fab(Market place for 3d Objects)** integration for 3D assets strightly Import via prompt ("Prompt : Download a car model and import in the blender")
* ✅ Run **Python code** inside Blender securely
* ✅ Works with **Claude Desktop**, **Cursor**, and other MCP clients

---

## Capabilities

| Capability              | Description                                                                |
| ----------------------- | -------------------------------------------------------------------------- |
| Object Manipulation     | Create, move, delete, and transform Blender objects via AI commands        |
| Material Control        | Apply, modify, or create new materials, shaders, and textures              |
| Scene Inspection        | Get structured metadata about objects, lights, cameras, and environment    |
| Python Code Execution   | Send arbitrary Python scripts to run inside Blender's Python environment   |
| Asset Integration       | Search/download HDRIs, textures, models via **Poly Haven** and **Hyper3D** |
| Viewport Screenshot     | Capture and return the current Blender viewport as image                   |
| Claude + Cursor Support | Connects as an MCP server in both Claude Desktop and Cursor                |

---

## Supported Versions / Requirements

* **Blender**: 3.0 or newer
* **Python**: 3.10+
* **UV Package Manager** (mandatory):

  * Mac: `brew install uv`
  * Windows: via PowerShell install script ([Docs](https://docs.astral.sh/uv/getting-started/installation/))
* MCP-compatible client: Ai agent with Claude Model / reasoning Advance models
* Internet access for asset downloads (Poly Haven, Hyper3D)

---

## Security Notes

* The `execute_blender_code` tool runs arbitrary Python — **save your project** before use
* Connections use **TCP sockets** on localhost; ensure no public exposure in production
* Only **one MCP server instance** should run at a time (either Claude or Cursor)
* Disable Poly Haven if model download is not desired

---

## Integration Use Cases

* ✅ **Prompt-to-scene** 3D generation via Claude
* ✅ Rapid prototyping for 3D artists using AI
* ✅ **Scene summarization** and asset inspection
* ✅ Programmatic creation of objects, lighting, and materials
* ✅ **Educational workflows** — generate Blender setups via natural language
* ✅ Connect with other creative MCP-enabled tools like Three.js converters
* ✅ **AI-assisted animation planning** — generate camera paths or keyframe skeletons
* ✅ **Concept-to-render pipeline** — go from idea to final render with minimal manual effort
* ✅ **AR/VR asset generation** — build lightweight 3D scenes for immersive platforms
* ✅ Integration with **game engines** — export scenes or models for Unity/Unreal
* ✅ **Virtual set design** — generate backdrops, props, and lighting setups for filmmaking
* ✅ **Architectural visualization** — create building layouts and environments through text prompts
* ✅ Generate **scene graphs** or **JSON schemas** representing the Blender scene
* ✅ **Assistive modeling for accessibility** — enable non-experts to create 3D content
* ✅ Automate **texture/material setup** using Poly Haven and AI-generated shaders
* ✅ **Model repair and clean-up tasks** — detect overlapping meshes, missing UVs, etc.
---