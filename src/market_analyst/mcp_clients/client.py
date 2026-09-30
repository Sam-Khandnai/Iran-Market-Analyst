import json
import sys
from contextlib import AsyncExitStack
from typing import Any, Self

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolClient:
    def __init__(self, module: str):
        self._params = StdioServerParameters(command=sys.executable, args=["-m", module])
        self._stack: AsyncExitStack | None = None
        self._session: ClientSession | None = None

    async def __aenter__(self) -> Self:
        self._stack = AsyncExitStack()
        read, write = await self._stack.enter_async_context(stdio_client(self._params))
        self._session = await self._stack.enter_async_context(ClientSession(read, write))
        await self._session.initialize()
        return self

    async def __aexit__(self, *exc) -> None:
        if self._stack is not None:
            await self._stack.aclose()

    async def call(self, tool: str, **kwargs: Any) -> dict:
        assert self._session is not None, "client not started; use 'async with'"
        result = await self._session.call_tool(tool, kwargs)
        if result.isError:
            raise RuntimeError(f"MCP tool '{tool}' error: {result.content}")
        structured = getattr(result, "structuredContent", None)
        if structured:
            return structured
        for block in result.content:
            if getattr(block, "type", None) == "text":
                return json.loads(block.text)
        raise RuntimeError(f"MCP tool '{tool}' returned no parsable content")