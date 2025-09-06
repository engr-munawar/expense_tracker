from fastapi import FastAPI
from routers import auth_router, balance_router, expenses_router
from config.database import engine, Base
from models import expense_model

# Create tables (Comment in below code line if alembic is not being used)
#Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers
app.include_router(auth_router.router)
app.include_router(balance_router.router)
app.include_router(expenses_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Expense Tracker API"}


# if alembic is being used then use code lines below to create / update tables and version
# alembic revison --autogenerate -m "message here"
# amembic upgrade head



