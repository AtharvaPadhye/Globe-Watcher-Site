from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional

class Telemetry(BaseModel):
    satellite_id: str
    data: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None  # Altitude in kilometers
