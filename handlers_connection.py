"""Connection handlers for Tally Connector."""
from __future__ import annotations
import uuid
from imperal_sdk import ActionResult
from app import chat
from schemas import NoParams, ConnectParams, ConnectionIdParams, ConnectionRecord, ConnectionList, DeleteResult
from tally_client import TallyClient

async def resolve_client(ctx, connection_id: str = "") -> TallyClient:
    connections = await ctx.store.get("connections", [])
    if not connections:
        raise ValueError("No Tally connections configured. Use connect_tally first.")
    conn = None
    if connection_id:
        for c in connections:
            if c.get("id") == connection_id:
                conn = c
                break
        if not conn: raise ValueError(f"Connection {connection_id} not found.")
    else:
        conn = connections[0]
    return TallyClient(api_key=conn["api_key"], base_url=conn.get("base_url", ""))

@chat.function("connect_tally", "Connect Tally account via API Key.", action_type="write", chain_callable=True, event="tally-connector.connect_tally", effects=["create:connection"], data_model=ConnectionRecord)
async def connect_tally(params: ConnectParams, ctx) -> ActionResult:
    client = TallyClient(api_key=params.api_key, base_url=params.base_url)
    res = await client.verify_auth()
    if res.get("status") == "error":
        return ActionResult.error(f"Failed to authenticate with Tally: {res.get('error')}")
    connections = await ctx.store.get("connections", [])
    masked = params.api_key[:4] + "..." + params.api_key[-4:] if len(params.api_key) > 8 else "***"
    record = {"id": f"conn_{uuid.uuid4().hex[:8]}", "label": params.label or "Primary Tally", "api_key": params.api_key, "masked_key": masked, "base_url": params.base_url, "is_active": True}
    connections.append(record)
    await ctx.store.set("connections", connections)
    return ActionResult.ok(record, summary=f"Connected Tally account: {record['label']}")

@chat.function("list_connections", "List connected Tally accounts.", action_type="read", chain_callable=True, event="tally-connector.list_connections", effects=["read:connections"], data_model=ConnectionList)
async def list_connections(params: NoParams, ctx) -> ActionResult:
    conns = await ctx.store.get("connections", [])
    records = [ConnectionRecord(id=c["id"], label=c["label"], masked_key=c.get("masked_key", "***"), base_url=c.get("base_url", ""), is_active=c.get("is_active", True)) for c in conns]
    return ActionResult.ok(ConnectionList(connections=records, total=len(records)), summary=f"Found {len(records)} Tally connections.")

@chat.function("disconnect_tally", "Disconnect Tally account.", action_type="destructive", chain_callable=True, event="tally-connector.disconnect_tally", effects=["delete:connection"], data_model=DeleteResult)
async def disconnect_tally(params: ConnectionIdParams, ctx) -> ActionResult:
    conns = await ctx.store.get("connections", [])
    rem = [c for c in conns if c.get("id") != params.connection_id]
    await ctx.store.set("connections", rem)
    return ActionResult.ok(DeleteResult(success=True, message=f"Disconnected {params.connection_id}"), summary="Disconnected Tally account.")
