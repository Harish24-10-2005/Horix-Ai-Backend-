import asyncio
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b"
)

client = MultiServerMCPClient({
    "bugsnag": {
        "command": "node",
        "args": ["D:/Adya/MCPs/bugsnag-mcp/build/index.js"],
        "env": {
            "BUGSNAG_API_KEY": "943769e3-a508-4b21-82ed-8e5e6ea93d05"
        },
        "disabled": False,
        "alwaysAllow":[]
    }

})

async def main():
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "how many team in my pagerduty and its name"}]
    })
    for i in response["messages"]:
        i.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())
