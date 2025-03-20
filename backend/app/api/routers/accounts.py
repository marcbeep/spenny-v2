from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.models.account import Account, AccountCreate, AccountRead
from app.db.client import get_supabase_client

router = APIRouter()


@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountCreate):
    pass


@router.get("/", response_model=List[AccountRead])
async def get_accounts():
    pass


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(account_id: UUID):
    pass


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: UUID):
    pass
