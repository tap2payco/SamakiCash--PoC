from pydantic import BaseModel
from typing import Optional

class FishCatchRequest(BaseModel):
    fish_type: str
    quantity_kg: float
    location: str
    user_id: str
    image_data: Optional[str] = None
