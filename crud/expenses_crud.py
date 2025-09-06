from sqlalchemy.orm import Session
from models import expense_model
from schemas import validation
from typing import Optional
from datetime import date, datetime

def get_expenses_with_filters(
    db: Session, 
    user_id: int, 
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(expense_model.Expense).filter(expense_model.Expense.user_id == user_id)
    
    # Apply category filter
    if category:
        query = query.filter(expense_model.Expense.category.ilike(f"%{category}%"))
    
    # Apply date range filter
    if start_date:
        query = query.filter(expense_model.Expense.date >= start_date)
    if end_date:
        # Add 1 day to include the entire end date
        next_day = datetime.combine(end_date, datetime.min.time()) 
        next_day = next_day.replace(day=next_day.day + 1)
        query = query.filter(expense_model.Expense.date < next_day)
    
    # Apply pagination
    return query.order_by(expense_model.Expense.date.desc()).offset(skip).limit(limit).all()

def get_expenses_count(
    db: Session, 
    user_id: int, 
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    query = db.query(expense_model.Expense).filter(expense_model.Expense.user_id == user_id)
    
    if category:
        query = query.filter(expense_model.Expense.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(expense_model.Expense.date >= start_date)
    if end_date:
        next_day = datetime.combine(end_date, datetime.min.time())
        next_day = next_day.replace(day=next_day.day + 1)
        query = query.filter(expense_model.Expense.date < next_day)
    
    return query.count()


def create_expense(db: Session, expense: validation.ExpenseCreate, user_id: int):
    db_expense = expense_model.Expense(**expense.model_dump(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(expense_model.Expense).filter(expense_model.Expense.user_id == user_id).offset(skip).limit(limit).all()

def get_expense(db: Session, expense_id: int, user_id: int):
    return db.query(expense_model.Expense).filter(
        expense_model.Expense.id == expense_id,
        expense_model.Expense.user_id == user_id
    ).first()

def update_expense(db: Session, expense_id: int, expense: validation.ExpenseCreate, user_id: int):
    db_expense = get_expense(db, expense_id, user_id)
    if db_expense:
        for key, value in expense.model_dump().items():
            setattr(db_expense, key, value)
        db.commit()
        db.refresh(db_expense)
        return db_expense
    return None

def delete_expense(db: Session, expense_id: int, user_id: int):
    db_expense = get_expense(db, expense_id, user_id)
    if db_expense:
        db.delete(db_expense)
        db.commit()
        return True
    return False