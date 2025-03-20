from fastapi import APIRouter

from app.api.routers import users, budgets, categories, accounts, transactions

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)
