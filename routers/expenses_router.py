from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timezone
from schemas import validation
from crud import expenses_crud, balance_crud
from config.database import get_db
from auth.auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/", response_model=validation.Expense)
def create_expense(
    expense: validation.ExpenseCreate,
    current_user: validation.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user has sufficient balance
    balance = balance_crud.get_balance(db, current_user.id)
    if balance.amount < expense.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Create expense
    expense = expenses_crud.create_expense(db, expense, current_user.id)
    
    # Update balance
    new_balance = balance.amount - expense.amount
   
    balance_crud.update_balance(db, current_user.id, new_balance)
    
    return expense

@router.get("/", response_model=validation.ExpenseListResponse)
def read_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    current_user: validation.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate end_date is not in future
    if end_date:
        current_date = datetime.now(timezone.utc).date()
        if end_date > current_date:
            raise HTTPException(
                status_code=400,
                detail="End date cannot be in the future"
            )
    
    # Validate start_date is not in future
    if start_date:
        current_date = datetime.now(timezone.utc).date()
        if start_date > current_date:
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be in the future"
            )
    
    # Validate date range (start_date <= end_date)
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date"
        )
    # Get filtered expenses with pagination
    try:
        expenses = expenses_crud.get_expenses_with_filters(
            db, 
            current_user.id, 
            category=category,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        # Get total count for pagination info
        total_count = expenses_crud.get_expenses_count(
            db,
            current_user.id,
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        return validation.ExpenseListResponse(
            data= expenses,
            pagination= {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total_count
            },
            filters= {
                "category": category,
                "start_date": start_date,
                "end_date": end_date
            }
        )
    except Exception as e:
        print('An invalid exception')
        print(e)
        return None

@router.get("/{expense_id}", response_model=validation.Expense)
def read_expense(
    expense_id: int,
    current_user: validation.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_expense = expenses_crud.get_expense(db, expense_id, current_user.id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@router.put("/{expense_id}", response_model=validation.Expense)
def update_expense(
    expense_id: int,
    expense: validation.ExpenseCreate,
    current_user: validation.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get current expense
    db_expense = expenses_crud.get_expense(db, expense_id, current_user.id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Get current balance
    balance = balance_crud.get_balance(db, current_user.id)
    
    # Calculate difference
    amount_diff = expense.amount - db_expense.amount
    
    # Check if user has sufficient balance for the update
    if balance.amount < amount_diff:
        raise HTTPException(status_code=400, detail="Insufficient balance for this update")
    
    # Update expense
    updated_expense = expenses_crud.update_expense(db, expense_id, expense, current_user.id)
    
    # Update balance
    new_balance = balance.amount - amount_diff
    
    balance_crud.update_balance(db, current_user.id, new_balance)
    
    return updated_expense

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: validation.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get current expense
    db_expense = expenses_crud.get_expense(db, expense_id, current_user.id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Get current balance
    balance = balance_crud.get_balance(db, current_user.id)
    
    # Update balance (return the amount)
    new_balance = balance.amount + db_expense.amount
    
    balance_crud.update_balance(db, current_user.id, new_balance)
    
    # Delete expense
    expenses_crud.delete_expense(db, expense_id, current_user.id)
    
    return {'message': f'expense with expense id ({expense_id}) having expense amount = {db_expense.amount} deleted successfully'}