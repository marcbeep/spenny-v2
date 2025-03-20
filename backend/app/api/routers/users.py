from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.models.user import User, UserCreate, UserRead
from app.db.client import get_supabase_client

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    pass


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID):
    pass


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID):
    pass
