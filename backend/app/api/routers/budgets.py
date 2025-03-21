from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.db.deps import get_supabase
from app.models.budget import Budget, BudgetCreate, BudgetRead
from uuid import UUID

router = APIRouter()


@router.post("/", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_in: BudgetCreate,
    user_id: UUID,  # TODO: Get this from auth token
    db: Client = Depends(get_supabase),
) -> BudgetRead:
    """
    Create a new budget for the user.
    """
    try:
        # If this is set as default, unset any existing default budget
        if budget_in.is_default:
            db.table("budgets").update({"is_default": False}).eq(
                "user_id", str(user_id)
            ).execute()

        # Create the new budget
        result = (
            db.table("budgets")
            .insert(
                {
                    "name": budget_in.name,
                    "is_default": budget_in.is_default,
                    "user_id": str(user_id),
                }
            )
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create budget",
            )

        return BudgetRead(**result.data[0])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=List[BudgetRead])
async def get_budgets(
    user_id: UUID, db: Client = Depends(get_supabase)  # TODO: Get this from auth token
) -> List[BudgetRead]:
    """
    Get all budgets for the user.
    """
    try:
        result = db.table("budgets").select("*").eq("user_id", str(user_id)).execute()
        return [BudgetRead(**budget) for budget in result.data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{budget_id}", response_model=BudgetRead)
async def get_budget(
    budget_id: UUID,
    user_id: UUID,  # TODO: Get this from auth token
    db: Client = Depends(get_supabase),
) -> BudgetRead:
    """
    Get a specific budget by ID.
    """
    try:
        result = (
            db.table("budgets")
            .select("*")
            .eq("id", str(budget_id))
            .eq("user_id", str(user_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found"
            )

        return BudgetRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{budget_id}", response_model=BudgetRead)
async def update_budget(
    budget_id: UUID,
    budget_in: BudgetCreate,
    user_id: UUID,  # TODO: Get this from auth token
    db: Client = Depends(get_supabase),
) -> BudgetRead:
    """
    Update a budget.
    """
    try:
        # Check if budget exists and belongs to user
        existing = (
            db.table("budgets")
            .select("*")
            .eq("id", str(budget_id))
            .eq("user_id", str(user_id))
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found"
            )

        # If setting as default, unset other defaults
        if budget_in.is_default:
            db.table("budgets").update({"is_default": False}).eq(
                "user_id", str(user_id)
            ).neq("id", str(budget_id)).execute()

        # Update the budget
        result = (
            db.table("budgets")
            .update({"name": budget_in.name, "is_default": budget_in.is_default})
            .eq("id", str(budget_id))
            .eq("user_id", str(user_id))
            .execute()
        )

        return BudgetRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: UUID,
    user_id: UUID,  # TODO: Get this from auth token
    db: Client = Depends(get_supabase),
) -> None:
    """
    Delete a budget.
    """
    try:
        # Check if budget exists and belongs to user
        existing = (
            db.table("budgets")
            .select("*")
            .eq("id", str(budget_id))
            .eq("user_id", str(user_id))
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found"
            )

        # Delete the budget
        db.table("budgets").delete().eq("id", str(budget_id)).eq(
            "user_id", str(user_id)
        ).execute()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
