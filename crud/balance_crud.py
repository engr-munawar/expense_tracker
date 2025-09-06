from sqlalchemy.orm import Session
from models import expense_model

def update_balance(db: Session, user_id: int, amount: float):
    db_balance = db.query(expense_model.Balance).filter(expense_model.Balance.user_id == user_id).first()
    if db_balance:
        db_balance.amount = amount
        db.commit()
        db.refresh(db_balance)
        return db_balance
    return None

def add_balance(db: Session, user_id: int, amount_to_add: float):
    db_balance = db.query(expense_model.Balance).filter(expense_model.Balance.user_id == user_id).first()
    if db_balance:
        previous_balance = db_balance.amount
        db_balance.amount += amount_to_add
        db.commit()
        db.refresh(db_balance)
        return db_balance, previous_balance, amount_to_add
    return None,0,0

def get_balance(db: Session, user_id: int):
    return db.query(expense_model.Balance).filter(expense_model.Balance.user_id == user_id).first()