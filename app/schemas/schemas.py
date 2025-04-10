from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TableBase(BaseModel):
    name: str
    seats: int
    location: str

class TableCreate(TableBase):
    pass

class Table(TableBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ReservationBase(BaseModel):
    customer_name: str
    reservation_time: datetime
    duration_minutes: int

class ReservationCreate(ReservationBase):
    table_id: int

class Reservation(ReservationBase):
    id: int
    table_id: int
    table: Optional[Table] = None
    model_config = ConfigDict(from_attributes=True) 