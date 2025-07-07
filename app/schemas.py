from pydantic import BaseModel
from typing import Optional, List

class EmployeeOut(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    department: Optional[str]
    position: Optional[str]
    location: Optional[str]
    avatar_url: Optional[str]

    class Config:
        orm_mode = True

class FilterMetadata(BaseModel):
    statuses: List[str]
    locations: List[str]
    departments: List[str]
    positions: List[str]