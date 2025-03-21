from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.db.deps import get_supabase
from app.models.category import Category, CategoryCreate, CategoryRead
from app.utils.auth import get_current_user
from uuid import UUID

router = APIRouter()


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> CategoryRead:
    """
    Create a new category for a budget.
    """
    try:
        # Check if budget exists and belongs to user
        budget_result = (
            db.table("budgets")
            .select("id")
            .eq("id", str(category_in.budget_id))
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found or you don't have access to it",
            )

        # Create the category
        result = (
            db.table("categories")
            .insert(
                {
                    "name": category_in.name,
                    "allocated": str(category_in.allocated),
                    "budget_id": str(category_in.budget_id),
                }
            )
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create category",
            )

        return CategoryRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=List[CategoryRead])
async def get_categories(
    budget_id: UUID = None,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> List[CategoryRead]:
    """
    Get all categories, optionally filtered by budget_id.
    """
    try:
        query = db.table("categories").select("*")

        if budget_id:
            # Verify budget belongs to user
            budget_check = (
                db.table("budgets")
                .select("id")
                .eq("id", str(budget_id))
                .eq("user_id", current_user_id)
                .execute()
            )

            if not budget_check.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Budget not found or you don't have access to it",
                )

            query = query.eq("budget_id", str(budget_id))
        else:
            # Get all budgets for the user
            budgets = (
                db.table("budgets")
                .select("id")
                .eq("user_id", current_user_id)
                .execute()
            )

            if not budgets.data:
                return []

            budget_ids = [budget["id"] for budget in budgets.data]
            query = query.in_("budget_id", budget_ids)

        result = query.execute()
        return [CategoryRead(**category) for category in result.data]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> CategoryRead:
    """
    Get a specific category by ID.
    """
    try:
        # Use a join to verify the category belongs to user's budget
        result = (
            db.table("categories")
            .select("categories.*")
            .eq("categories.id", str(category_id))
            .join("budgets", "categories.budget_id", "budgets.id")
            .eq("budgets.user_id", current_user_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        return CategoryRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    category_in: CategoryCreate,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> CategoryRead:
    """
    Update a category.
    """
    try:
        # Check if category exists and belongs to user's budget
        existing = (
            db.table("categories")
            .select("categories.*")
            .eq("categories.id", str(category_id))
            .join("budgets", "categories.budget_id", "budgets.id")
            .eq("budgets.user_id", current_user_id)
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        # Check if budget_id belongs to user
        if existing.data[0]["budget_id"] != str(category_in.budget_id):
            budget_check = (
                db.table("budgets")
                .select("id")
                .eq("id", str(category_in.budget_id))
                .eq("user_id", current_user_id)
                .execute()
            )

            if not budget_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid budget ID"
                )

        # Update the category
        result = (
            db.table("categories")
            .update(
                {
                    "name": category_in.name,
                    "allocated": str(category_in.allocated),
                    "budget_id": str(category_in.budget_id),
                }
            )
            .eq("id", str(category_id))
            .execute()
        )

        return CategoryRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> None:
    """
    Delete a category.
    """
    try:
        # Check if category exists and belongs to user's budget
        existing = (
            db.table("categories")
            .select("categories.*")
            .eq("categories.id", str(category_id))
            .join("budgets", "categories.budget_id", "budgets.id")
            .eq("budgets.user_id", current_user_id)
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        # Delete the category
        db.table("categories").delete().eq("id", str(category_id)).execute()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
