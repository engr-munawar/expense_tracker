from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from schemas import validation
from crud import balance_crud
from config.database import get_db
from auth.auth import get_current_user

router = APIRouter(prefix="/balance", tags=["balance"])

@router.post("/", response_model=validation.BalanceResponse)
def update_balance(
    balance: validation.BalanceBase,
    current_user: validation.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update balance by ADDING the amount
    updated_balance, previous_balance, amount_added = balance_crud.add_balance(
        db, current_user.id, balance.amount)
    if updated_balance is None:
        raise HTTPException(status_code=500, detail="Failed to update balance")
    
    return validation.BalanceResponse(
        id=updated_balance.id,
        amount_added=amount_added,
        user_id=updated_balance.user_id,
        previous_balance=previous_balance,
        updated_balance=updated_balance.amount
    )

@router.get("/", response_model=validation.GetBalance)
def get_balance(
    current_user: validation.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_balance = balance_crud.get_balance(db, current_user.id)
    if db_balance is None:
        raise HTTPException(status_code=404, detail="Balance not found")
    return validation.GetBalance(
        user_id=current_user.id,
        balance=db_balance.amount
    )