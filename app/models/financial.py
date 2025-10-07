from pydantic import BaseModel
from typing import Optional

class LoanApplication(BaseModel):
    user_id: str
    amount: float
    purpose: str = "fishing_equipment"

class InsuranceQuoteRequest(BaseModel):
    user_id: str
    coverage_type: str = "equipment"
    coverage_amount: float = 1000000

class MatchRequest(BaseModel):
    fish_type: str
    quantity_kg: float
    location: str
    user_id: Optional[str] = None
