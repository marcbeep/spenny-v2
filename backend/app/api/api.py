from fastapi import APIRouter

from app.api.routers import users, budgets, categories, accounts, transactions, auth

api_router = APIRouter()

# Auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Protected routes
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)
