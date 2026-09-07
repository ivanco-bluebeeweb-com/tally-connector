"""Connection handlers for Tally Connector."""
from __future__ import annotations
import uuid
from imperal_sdk import ActionResult
from app import chat
from schemas import NoParams, ConnectParams, ConnectionIdParams, ConnectionRecord, ConnectionList, DeleteResult
from tally_client import TallyClient

async def get_connections_list(ctx) -> list[dict]:
    page = await ctx.store.query("connections")
    docs = page.data if hasattr(page, "data") else []
    conns = []
    for d in docs:
        data = d.data if hasattr(d, "data") else d
        doc_id = d.id if hasattr(d, "id") else data.get("id")
        data["_store_id"] = doc_id
        conns.append(data)
    return conns

async def resolve_client(ctx, connection_id: str = "") -> TallyClient:
    conns = await get_connections_list(ctx)
    if not conns:
        raise ValueError("No Tally connections configured. Use connect_tally first.")
    conn = None
    if connection_id:
        for c in conns:
            if c.get("id") == connection_id:
                conn = c
                break
        if not conn:
            raise ValueError(f"Connection {connection_id} not found.")
    else:
        conn = conns[0]
    return TallyClient(api_key=conn["api_key"], base_url=conn.get("base_url", ""))

@chat.function("connect_tally", "Connect Tally account via API Key.", action_type="write", chain_callable=True, event="tally-connector.connect_tally", effects=["create:connection"], data_model=ConnectionRecord)
async def connect_tally(params: ConnectParams, ctx) -> ActionResult:
    client = TallyClient(api_key=params.api_key, base_url=params.base_url)
    res = await client.verify_auth()
    if res.get("status") == "error":
        return ActionResult.error(f"Failed to authenticate with Tally: {res.get('error')}")
    masked = params.api_key[:4] + "*" * (len(params.api_key) - 8) + params.api_key[-4:] if len(params.api_key) > 8 else "***"
    record = {
        "id": f"conn_{uuid.uuid4().hex[:8]}",
        "label": params.label or "Primary Tally",
        "api_key": params.api_key,
        "masked_key": masked,
        "base_url": params.base_url,
        "is_active": True
    }
    await ctx.store.create("connections", record)
    return ActionResult.success(ConnectionRecord(**record), summary=f"Connected Tally account: {record['label']}")

@chat.function("list_connections", "List connected Tally accounts.", action_type="read", chain_callable=True, event="tally-connector.list_connections", effects=["read:connections"], data_model=ConnectionList)
async def list_connections(params: NoParams, ctx) -> ActionResult:
    conns = await get_connections_list(ctx)
    records = [
        ConnectionRecord(
            id=c["id"],
            label=c["label"],
            masked_key=c.get("masked_key", "***"),
            base_url=c.get("base_url", ""),
            is_active=c.get("is_active", True)
        )
        for c in conns
    ]
    return ActionResult.success(ConnectionList(connections=records, total=len(records)), summary=f"Found {len(records)} Tally connections.")

@chat.function("disconnect_tally", "Disconnect Tally account.", action_type="destructive", chain_callable=True, event="tally-connector.disconnect_tally", effects=["delete:connection"], data_model=DeleteResult)
async def disconnect_tally(params: ConnectionIdParams, ctx) -> ActionResult:
    conns = await get_connections_list(ctx)
    deleted = False
    for c in conns:
        if c.get("id") == params.connection_id:
            store_id = c.get("_store_id")
            if store_id:
                await ctx.store.delete("connections", store_id)
                deleted = True
                break
    return ActionResult.success(DeleteResult(success=deleted, message=f"Disconnected {params.connection_id}"), summary="Disconnected Tally account.")
