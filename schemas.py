"""Pydantic schemas for Tally Connector (C32. Survey & Feedback Management)."""
from __future__ import annotations
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    pass

class ConnectParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label.")
    api_key: str = Field(description="Tally API Key.")
    base_url: str = Field(default="https://api.tally.so", description="Tally API base URL.")

class ConnectionIdParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")

class ConnectionRecord(BaseModel):
    id: str
    label: str
    masked_key: str
    base_url: str
    is_active: bool

class ConnectionList(BaseModel):
    connections: list[ConnectionRecord]
    total: int

class DeleteResult(BaseModel):
    success: bool
    message: str

class FormRecord(BaseModel):
    id: str
    name: str
    status: str
    submissions_count: int = 0
    raw: Dict[str, Any] = Field(default_factory=dict)

class FormList(BaseModel):
    forms: list[FormRecord]
    total: int

class ListFormsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")

class GetFormParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    form_id: str = Field(description="Tally form ID.")

class SubmissionRecord(BaseModel):
    id: str
    form_id: str
    created_at: Optional[str] = None
    answers: Dict[str, Any] = Field(default_factory=dict)

class SubmissionList(BaseModel):
    submissions: list[SubmissionRecord]
    total: int

class ListSubmissionsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    form_id: str = Field(description="Tally form ID.")

class HealthAuditReport(BaseModel):
    status: str
    active_forms: int
    total_submissions: int
    recommendations: List[str] = Field(default_factory=list)

class CreateFormParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    name: str = Field(description="Title / Name of the form.")
    status: str = Field(default="PUBLISHED", description="Form status: DRAFT or PUBLISHED.")

class UpdateFormParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    form_id: str = Field(description="Tally form ID to update.")
    name: str = Field(description="New title / Name of the form.")

class DeleteFormParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    form_id: str = Field(description="Tally form ID to delete.")
