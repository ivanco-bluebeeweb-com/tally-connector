"""Resource handlers for Tally Connector."""
from __future__ import annotations
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    DeleteResult,
    ListFormsParams, GetFormParams, ListSubmissionsParams, ConnectionIdParams,
    CreateFormParams, UpdateFormParams, DeleteFormParams,
    FormList, FormRecord, SubmissionList, SubmissionRecord, HealthAuditReport
)
from handlers_connection import resolve_client

@chat.function("list_forms", "List forms in Tally workspace.", action_type="read", chain_callable=True, event="tally-connector.list_forms", effects=["read:forms"], data_model=FormList)
async def list_forms(ctx, params: ListFormsParams) -> ActionResult:
    try:
        client = await resolve_client(ctx, params.connection_id)
        raw_forms = await client.list_forms()
        forms = [FormRecord(id=str(f.get("id", "")), name=f.get("name", "Untitled Form"), status=f.get("status", "published"), submissions_count=f.get("submissionsCount", 0), raw=f) for f in raw_forms]
        return ActionResult.success(FormList(forms=forms, total=len(forms)), summary=f"Loaded {len(forms)} Tally forms.")
    except Exception as e:
        return ActionResult.error(f"Error listing Tally forms: {e}")

@chat.function("get_form", "Get details of one Tally form.", action_type="read", chain_callable=True, event="tally-connector.get_form", effects=["read:form"], data_model=FormRecord)
async def get_form(ctx, params: GetFormParams) -> ActionResult:
    try:
        client = await resolve_client(ctx, params.connection_id)
        f = await client.get_form(params.form_id)
        if not f: return ActionResult.error(f"Form {params.form_id} not found.")
        rec = FormRecord(id=str(f.get("id", "")), name=f.get("name", "Untitled Form"), status=f.get("status", "published"), submissions_count=f.get("submissionsCount", 0), raw=f)
        return ActionResult.success(rec, summary=f"Loaded Tally form: {rec.name}")
    except Exception as e:
        return ActionResult.error(f"Error fetching Tally form: {e}")

@chat.function("list_submissions", "List submissions for one Tally form.", action_type="read", chain_callable=True, event="tally-connector.list_submissions", effects=["read:submissions"], data_model=SubmissionList)
async def list_submissions(ctx, params: ListSubmissionsParams) -> ActionResult:
    try:
        client = await resolve_client(ctx, params.connection_id)
        raw_sub = await client.list_submissions(params.form_id)
        subs = [SubmissionRecord(id=str(s.get("id", "")), form_id=params.form_id, created_at=s.get("createdAt"), answers=s.get("answers", {})) for s in raw_sub]
        return ActionResult.success(SubmissionList(submissions=subs, total=len(subs)), summary=f"Loaded {len(subs)} submissions for form {params.form_id}.")
    except Exception as e:
        return ActionResult.error(f"Error listing submissions: {e}")

@chat.function("audit_survey_health", "Audit active forms and submission volume in Tally.", action_type="read", chain_callable=True, event="tally-connector.audit_survey_health", effects=["read:analytics"], data_model=HealthAuditReport)
async def audit_survey_health(ctx, params: ConnectionIdParams) -> ActionResult:
    try:
        client = await resolve_client(ctx, params.connection_id)
        raw_forms = await client.list_forms()
        active = sum(1 for f in raw_forms if f.get("status") == "published")
        total_sub = sum(f.get("submissionsCount", 0) for f in raw_forms)
        recs = []
        if active == 0: recs.append("No active published forms found in Tally.")
        if total_sub == 0: recs.append("Zero submissions received across forms; verify form links.")
        return ActionResult.success(HealthAuditReport(status="healthy" if active > 0 else "attention_needed", active_forms=active, total_submissions=total_sub, recommendations=recs), summary="Tally survey health audit complete.")
    except Exception as e:
        return ActionResult.error(f"Error auditing Tally health: {e}")


@chat.function("create_form", "Create a new form in Tally.", action_type="write", chain_callable=True, event="tally-connector.create_form", effects=["create:form"], data_model=FormRecord)
async def create_form(ctx, params: CreateFormParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        raw = await client.create_form(name=params.name, status=params.status)
        rec = FormRecord(
            id=str(raw.get("id", "")),
            name=raw.get("name") or params.name,
            status=raw.get("status") or params.status,
            submissions_count=0,
            raw=raw
        )
        return ActionResult.success(rec, summary=f"Created form '{rec.name}' ({rec.id}) in Tally.")
    except Exception as e:
        return ActionResult.error(f"Failed to create form in Tally: {e}")

@chat.function("update_form", "Update an existing form title in Tally.", action_type="write", chain_callable=True, event="tally-connector.update_form", effects=["update:form"], data_model=FormRecord)
async def update_form(ctx, params: UpdateFormParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        raw = await client.update_form(form_id=params.form_id, name=params.name)
        rec = FormRecord(
            id=str(raw.get("id", params.form_id)),
            name=raw.get("name") or params.name,
            status=raw.get("status") or "UNKNOWN",
            submissions_count=raw.get("submissionsCount", 0),
            raw=raw
        )
        return ActionResult.success(rec, summary=f"Updated form '{rec.name}' ({rec.id}) in Tally.")
    except Exception as e:
        return ActionResult.error(f"Failed to update form in Tally: {e}")

@chat.function("delete_form", "Permanently delete a form from Tally.", action_type="destructive", chain_callable=True, event="tally-connector.delete_form", effects=["delete:form"], data_model=DeleteResult)
async def delete_form(ctx, params: DeleteFormParams) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        ok = await client.delete_form(form_id=params.form_id)
        if ok:
            return ActionResult.success(DeleteResult(success=True, message=f"Form {params.form_id} deleted successfully."), summary=f"Deleted form {params.form_id} from Tally.")
        return ActionResult.error(f"Failed to delete form {params.form_id}")
    except Exception as e:
        return ActionResult.error(f"Failed to delete form in Tally: {e}")
