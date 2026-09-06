"""HTTP client for Tally API."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_BASE = "https://api.tally.so"

class TallyClient:
    def __init__(self, api_key: str, base_url: str = ""):
        self.api_key = api_key.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Tally-Connector/1.0.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def verify_auth(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/users/me", headers=self.headers)
                if resp.status_code in (200, 201):
                    return {"status": "ok", "data": resp.json()}
                return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    async def list_forms(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/forms", headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                return data if isinstance(data, list) else data.get("forms", [])
            return []

    async def get_form(self, form_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/forms/{form_id}", headers=self.headers)
            return resp.json() if resp.status_code == 200 else {}

    async def list_submissions(self, form_id: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/forms/{form_id}/submissions", headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                return data if isinstance(data, list) else data.get("submissions", [])
            return []
