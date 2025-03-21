from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from supabase import Client

from app.models.account import Account, AccountCreate, AccountRead
from app.db.deps import get_supabase
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_in: AccountCreate,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> AccountRead:
    """
    Create a new account for a budget.
    """
    try:
        # Check if budget exists and belongs to user
        budget_result = (
            db.table("budgets")
            .select("id")
            .eq("id", str(account_in.budget_id))
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found or you don't have access to it",
            )

        # Create the account
        result = (
            db.table("accounts")
            .insert(
                {
                    "name": account_in.name,
                    "type": account_in.type,
                    "balance": str(account_in.balance),
                    "budget_id": str(account_in.budget_id),
                }
            )
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create account",
            )

        return AccountRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=List[AccountRead])
async def get_accounts(
    budget_id: UUID = None,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> List[AccountRead]:
    """
    Get all accounts, optionally filtered by budget_id.
    """
    try:
        query = db.table("accounts").select("*")

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
        return [AccountRead(**account) for account in result.data]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> AccountRead:
    """
    Get a specific account by ID.
    """
    try:
        # First get the account
        result = db.table("accounts").select("*").eq("id", str(account_id)).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )

        account = result.data[0]

        # Now verify the budget belongs to the user
        budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", account["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or you don't have access to it",
            )

        return AccountRead(**account)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: UUID,
    account_in: AccountCreate,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> AccountRead:
    """
    Update an account.
    """
    try:
        # First get the account
        existing_result = (
            db.table("accounts").select("*").eq("id", str(account_id)).execute()
        )

        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )

        existing_account = existing_result.data[0]

        # Verify the current budget belongs to the user
        current_budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", existing_account["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not current_budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or you don't have access to it",
            )

        # Check if new budget_id belongs to user
        if existing_account["budget_id"] != str(account_in.budget_id):
            budget_check = (
                db.table("budgets")
                .select("id")
                .eq("id", str(account_in.budget_id))
                .eq("user_id", current_user_id)
                .execute()
            )

            if not budget_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid budget ID"
                )

        # Update the account
        result = (
            db.table("accounts")
            .update(
                {
                    "name": account_in.name,
                    "type": account_in.type,
                    "balance": str(account_in.balance),
                    "budget_id": str(account_in.budget_id),
                }
            )
            .eq("id", str(account_id))
            .execute()
        )

        return AccountRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> None:
    """
    Delete an account.
    """
    try:
        # First get the account
        existing_result = (
            db.table("accounts").select("*").eq("id", str(account_id)).execute()
        )

        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
            )

        existing_account = existing_result.data[0]

        # Verify the budget belongs to the user
        budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", existing_account["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or you don't have access to it",
            )

        # Delete the account
        db.table("accounts").delete().eq("id", str(account_id)).execute()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
