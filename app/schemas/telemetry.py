from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict

class Telemetry(BaseModel):
    satellite_id: str
    data: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)