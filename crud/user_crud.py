from sqlalchemy.orm import Session
from models import expense_model
from schemas import validation
from auth.auth import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(expense_model.Users).filter(expense_model.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(expense_model.Users).filter(expense_model.Users.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(expense_model.Users).filter(expense_model.Users.username == username).first()

def create_user(db: Session, user: validation.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = expense_model.Users(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create initial balance for user
    db_balance = expense_model.Balance(amount=0.0, user_id=db_user.id)
    db.add(db_balance)
    db.commit()
    
    return db_user
