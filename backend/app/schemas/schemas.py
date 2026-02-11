"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    age: Optional[int] = None
    occupation: Optional[str] = None
    monthly_income: float = 0.0
    location: Optional[str] = None
    financial_knowledge: str = "beginner"


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    monthly_income: Optional[float] = None
    location: Optional[str] = None
    financial_knowledge: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Transaction schemas
class TransactionBase(BaseModel):
    date: datetime
    description: str
    category: str
    amount: float
    transaction_type: str


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Goal schemas
class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[datetime] = None
    priority: int = 1


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None


class GoalResponse(GoalBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Budget schemas
class BudgetBase(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int
    category: str
    budgeted_amount: float


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    spent_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# AI Tutor schemas
class AIMessage(BaseModel):
    message: str
    context: Optional[dict] = None


class AIResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None
    insights: Optional[dict] = None


# Simulation schemas
class SimulationRequest(BaseModel):
    scenario_type: str  # "budget", "investment", "debt_payoff"
    initial_amount: float = 0.0
    monthly_contribution: float = 0.0
    time_horizon_months: int = 12
    parameters: Optional[dict] = None


class SimulationResponse(BaseModel):
    scenario_type: str
    outcomes: dict
    visualizations: dict
    recommendations: List[str]


# Analytics schemas
class SpendingAnalysis(BaseModel):
    total_spending: float
    by_category: dict
    top_categories: List[tuple]
    trends: List[dict]
    alerts: List[dict]
