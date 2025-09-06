from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, date, timezone
from typing import Optional, Annotated, List


class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class BalanceBase(BaseModel):
    amount: Annotated[float, Field(ge=0, description="Amount could not be negative")]

class BalanceResponse(BaseModel):
    id: int
    amount_added: float = Field(..., description="Amount that was added")
    user_id: int
    previous_balance: float = Field(..., description="Balance before update")
    updated_balance: float = Field(..., description="Total balance after update")
    

    class Config:
        from_attributes = True

class GetBalance(BaseModel):
    user_id: int
    balance: Annotated[float, Field(ge=0, description="Amount could not be negative")]

    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    title: str
    amount: Annotated[float, Field(ge=0, description="Amount could not be negative")]
    category: str
    date: Optional[datetime] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ExpenseFilters(BaseModel):
    category: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100

class ExpenseListResponse(BaseModel):
    data: List[Expense]
    pagination: dict
    filters: dict

    class Config:
        from_attributes = True