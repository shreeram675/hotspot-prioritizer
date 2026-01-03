from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Report Schemas (Basic for now)
class ReportBase(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    severity: Optional[str] = "Medium"
    road_importance: Optional[int] = 1 # Added road_importance

class ReportCreate(ReportBase):
    lat: float # Moved from ReportBase
    lon: float # Moved from ReportBase

class ReportResponse(ReportBase):
    report_id: int
    user_id: int
    images: List[str] = [] # Changed type hint from list to List
    lat: float # Added
    lon: float # Added
    road_importance: int # Added
    upvote_count: int
    ai_severity_score: Optional[float] = None
    ai_severity_category: Optional[str] = None
    status: str
    created_at: datetime
    is_upvoted: Optional[bool] = False # Changed to Optional

    class Config:
        from_attributes = True

class AssignmentCreate(BaseModel):
    staff_name: str
    staff_phone: str
    expected_resolution_date: Optional[datetime] = None # Removed note field

class ReportStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None
