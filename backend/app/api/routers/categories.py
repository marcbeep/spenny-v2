from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.models.category import Category, CategoryCreate, CategoryRead
from app.db.client import get_supabase_client

router = APIRouter()


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate):
    pass


@router.get("/", response_model=List[CategoryRead])
async def get_categories():
    pass


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: UUID):
    pass


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID):
    pass
