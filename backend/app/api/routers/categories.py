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
        # First get the category
        result = db.table("categories").select("*").eq("id", str(category_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        category = result.data[0]

        # Now verify the budget belongs to the user
        budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", category["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or you don't have access to it",
            )

        return CategoryRead(**category)

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
        # First get the category
        existing_result = (
            db.table("categories").select("*").eq("id", str(category_id)).execute()
        )

        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        existing_category = existing_result.data[0]

        # Verify the current budget belongs to the user
        current_budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", existing_category["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not current_budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or you don't have access to it",
            )

        # Check if new budget_id belongs to user
        if existing_category["budget_id"] != str(category_in.budget_id):
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
        # First get the category
        existing_result = (
            db.table("categories").select("*").eq("id", str(category_id)).execute()
        )

        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        existing_category = existing_result.data[0]

        # Verify the budget belongs to the user
        budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", existing_category["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or you don't have access to it",
            )

        # Delete the category
        db.table("categories").delete().eq("id", str(category_id)).execute()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
