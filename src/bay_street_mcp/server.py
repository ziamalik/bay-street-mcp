"""Bay Street MCP server.

Exposes one tool, `compliance_lookup`, returning cited passages from
Canadian financial-services regulations. Stdio transport, compatible with
Claude Desktop, Claude Code, Cursor, and any MCP client.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from bay_street_mcp.store import ComplianceStore

log = logging.getLogger("bay_street_mcp")

server: Server = Server("bay-street-mcp")
_store: ComplianceStore | None = None


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="compliance_lookup",
            description=(
                "Search Canadian financial-services regulations (OSFI, PIPEDA, "
                "FINTRAC, Quebec Law 25) and return the most relevant passages "
                "with citation metadata. Use this tool whenever the user asks "
                "about Canadian financial regulation, compliance, AI/data "
                "governance for Canadian financial institutions, AML/ATF, "
                "operational risk, model risk, or related topics."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural-language question about Canadian financial-services compliance.",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of passages to return. Default 5, max 10.",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name != "compliance_lookup":
        raise ValueError(f"Unknown tool: {name}")
    if _store is None:
        raise RuntimeError("Compliance store not initialized")

    query = arguments["query"]
    top_k = min(int(arguments.get("top_k", 5)), 10)

    results = _store.search(query, top_k=top_k)
    if not results:
        return [
            TextContent(
                type="text",
                text="No relevant passages found. The store may be empty; run `bay-street-ingest` to load a regulation.",
            )
        ]

    return [TextContent(type="text", text=json.dumps(results, indent=2))]


async def amain() -> None:
    global _store
    logging.basicConfig(level=logging.INFO)
    _store = ComplianceStore.load_default()
    log.info("Loaded compliance store with %d passages", _store.count())

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
