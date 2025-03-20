from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.models.transaction import Transaction, TransactionCreate, TransactionRead
from app.db.client import get_supabase_client

router = APIRouter()


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate):
    pass


@router.get("/", response_model=List[TransactionRead])
async def get_transactions():
    pass


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(transaction_id: UUID):
    pass


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: UUID):
    pass
