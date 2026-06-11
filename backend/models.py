from pydantic import BaseModel
from typing import Optional
from datetime import date as DateType, datetime


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CategoryCreate(BaseModel):
    name: str
    color: str = "#6b7280"
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    sort_order: int
    user_id: int


class EntryCreate(BaseModel):
    date: DateType
    category_id: int
    content: str
    duration_minutes: int


class EntryUpdate(BaseModel):
    date: Optional[DateType] = None
    category_id: Optional[int] = None
    content: Optional[str] = None
    duration_minutes: Optional[int] = None


class EntryResponse(BaseModel):
    id: int
    user_id: int
    date: DateType
    category_id: int
    content: str
    duration_minutes: int
    created_at: datetime


class DailyDistribution(BaseModel):
    date: DateType
    weekday: str
    hours: float
    entry_count: int


class CategoryBreakdown(BaseModel):
    category: str
    color: str
    hours: float
    percentage: int


class WeeklyEntry(BaseModel):
    date: DateType
    category: str
    content: str
    hours: float


class WeeklyReportResponse(BaseModel):
    week_start: DateType
    week_end: DateType
    week_label: str
    total_hours: float
    entry_count: int
    work_days: int
    top_category: str
    daily_distribution: list[DailyDistribution]
    category_breakdown: list[CategoryBreakdown]
    entries: list[WeeklyEntry]
