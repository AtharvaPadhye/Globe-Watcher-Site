from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class Command(BaseModel):
    satellite_id: str
    command_type: str
    parameters: Dict
    priority: int = Field(default=1)  # 1=high, 5=low
    expiry_time: Optional[datetime] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)