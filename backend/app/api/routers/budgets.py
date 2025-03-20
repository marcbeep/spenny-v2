from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.models.budget import Budget, BudgetCreate, BudgetRead
from app.db.client import get_supabase_client

router = APIRouter()


@router.post("/", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
async def create_budget(budget: BudgetCreate):
    pass


@router.get("/", response_model=List[BudgetRead])
async def get_budgets():
    pass


@router.get("/{budget_id}", response_model=BudgetRead)
async def get_budget(budget_id: UUID):
    pass


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(budget_id: UUID):
    pass
