"""Resource handlers for Tally Connector."""
from __future__ import annotations
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    ListFormsParams, GetFormParams, ListSubmissionsParams, ConnectionIdParams,
    FormList, FormRecord, SubmissionList, SubmissionRecord, HealthAuditReport
)
from handlers_connection import resolve_client

@chat.function("list_forms", "List forms in Tally workspace.", action_type="read", chain_callable=True, event="tally-connector.list_forms", effects=["read:forms"], data_model=FormList)
async def list_forms(params: ListFormsParams, ctx) -> ActionResult:
    try:
        client = await resolve_client(ctx, params.connection_id)
        raw_forms = await client.list_forms()
        forms = [FormRecord(id=str(f.get("id", "")), name=f.get("name", "Untitled Form"), status=f.get("status", "published"), submissions_count=f.get("submissionsCount", 0), raw=f) for f in raw_forms]
        return ActionResult.ok(FormList(forms=forms, total=len(forms)), summary=f"Loaded {len(forms)} Tally forms.")
    except Exception as e:
        return ActionResult.error(f"Error listing Tally forms: {e}")

@chat.function("get_form", "Get details of one Tally form.", action_type="read", chain_callable=True, event="tally-connector.get_form", effects=["read:form"], data_model=FormRecord)
async def get_form(params: GetFormParams, ctx) -> ActionResult:
    try:
        client = await resolve_client(ctx, params.connection_id)
        f = await client.get_form(params.form_id)
        if not f: return ActionResult.error(f"Form {params.form_id} not found.")
        rec = FormRecord(id=str(f.get("id", "")), name=f.get("name", "Untitled Form"), status=f.get("status", "published"), submissions_count=f.get("submissionsCount", 0), raw=f)
        return ActionResult.ok(rec, summary=f"Loaded Tally form: {rec.name}")
    except Exception as e:
        return ActionResult.error(f"Error fetching Tally form: {e}")

@chat.function("list_submissions", "List submissions for one Tally form.", action_type="read", chain_callable=True, event="tally-connector.list_submissions", effects=["read:submissions"], data_model=SubmissionList)
async def list_submissions(params: ListSubmissionsParams, ctx) -> ActionResult:
    try:
        client = await resolve_client(ctx, params.connection_id)
        raw_sub = await client.list_submissions(params.form_id)
        subs = [SubmissionRecord(id=str(s.get("id", "")), form_id=params.form_id, created_at=s.get("createdAt"), answers=s.get("answers", {})) for s in raw_sub]
        return ActionResult.ok(SubmissionList(submissions=subs, total=len(subs)), summary=f"Loaded {len(subs)} submissions for form {params.form_id}.")
    except Exception as e:
        return ActionResult.error(f"Error listing submissions: {e}")

@chat.function("audit_survey_health", "Audit active forms and submission volume in Tally.", action_type="read", chain_callable=True, event="tally-connector.audit_survey_health", effects=["read:analytics"], data_model=HealthAuditReport)
async def audit_survey_health(params: ConnectionIdParams, ctx) -> ActionResult:
    try:
        client = await resolve_client(ctx, params.connection_id)
        raw_forms = await client.list_forms()
        active = sum(1 for f in raw_forms if f.get("status") == "published")
        total_sub = sum(f.get("submissionsCount", 0) for f in raw_forms)
        recs = []
        if active == 0: recs.append("No active published forms found in Tally.")
        if total_sub == 0: recs.append("Zero submissions received across forms; verify form links.")
        return ActionResult.ok(HealthAuditReport(status="healthy" if active > 0 else "attention_needed", active_forms=active, total_submissions=total_sub, recommendations=recs), summary="Tally survey health audit complete.")
    except Exception as e:
        return ActionResult.error(f"Error auditing Tally health: {e}")
