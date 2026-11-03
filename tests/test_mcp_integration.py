import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from cubicle import store
from sqlalchemy import create_engine


def test_mcp_stdio_lists_tools_and_creates_task(tmp_path):
    url = f"sqlite:///{tmp_path / 'mcp.db'}"
    store.initialize_database(create_engine(url))
    env = os.environ.copy()
    env["CUBICLE_DATABASE_URL"] = url
    env["CUBICLE_HOME"] = str(tmp_path)

    async def exercise():
        params = StdioServerParameters(command="python", args=["-m", "cubicle.mcp_server"], env=env)
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert {"create_task", "show_graph", "create_backlog_item"} <= {
                    tool.name for tool in tools.tools
                }
                result = await session.call_tool("create_task", {
                    "title": "Fix", "objective": "Fix issue", "project": "repo",
                    "kind": "coding", "acceptance": ["tests pass"],
                })
                assert not result.isError
                result = await session.call_tool("list_tasks", {})
                assert not result.isError
                assert "Fix" in str(result.content)

    asyncio.run(exercise())
