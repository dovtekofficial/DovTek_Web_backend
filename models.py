# backend/models.py
from pydantic import BaseModel, Field
from typing import Literal

class ScanRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)

class ScanResult(BaseModel):
    risk_score: int
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    summary: str
    reasons: list[str]
    action: Literal["TRUST", "CAUTION", "BLOCK"]
    what_to_do: str
    pass1_blocked: bool = False