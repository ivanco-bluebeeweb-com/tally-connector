"""Extension declaration, capabilities, health check for Tally Connector."""
from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "tally-connector",
    version="0.1.0",
    display_name="Tally",
    icon="icon.svg",
    capabilities=["tally:manage"],
    description="Official Imperal connector for Tally (C30. Email Marketing & Newsletter). Manage operations securely."
)

chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get("tally_connections")
    try:
        count = len(json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": f"{count} Tally connection(s) configured." if count else "Not connected yet."
    }
