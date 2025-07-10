from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from enum import Enum

class EmployeeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NOT_STARTED = "NOT_STARTED"
    TERMINATED = "TERMINATED"

class EmployeeSearchRequest(BaseModel):
    org_id: int = Field(..., gt=0, description="Organization ID must be positive")
    search_query: Optional[str] = Field(None, max_length=100, description="Search query for employee names and email")
    status: Optional[List[EmployeeStatus]] = Field(None, description="Filter by employee status")
    locations: Optional[List[str]] = Field(None, max_length=10, description="Filter by locations")
    departments: Optional[List[str]] = Field(None, max_length=10, description="Filter by departments")
    positions: Optional[List[str]] = Field(None, max_length=10, description="Filter by positions")
    offset: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(50, ge=1, le=100, description="Number of results to return (max 100)")

    @field_validator('search_query')
    @classmethod
    def validate_search_query(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v

    @field_validator('locations', 'departments', 'positions')
    @classmethod
    def validate_filter_lists(cls, v):
        if v is not None:
            return list(set(filter(None, [item.strip() for item in v])))
        return v

class EmployeeOut(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra='ignore')

class FilterMetadata(BaseModel):
    statuses: List[str]
    locations: List[str]
    departments: List[str]
    positions: List[str]