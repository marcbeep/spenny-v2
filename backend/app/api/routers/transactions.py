from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from supabase import Client

from app.models.transaction import Transaction, TransactionCreate, TransactionRead
from app.db.deps import get_supabase
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_in: TransactionCreate,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> TransactionRead:
    """
    Create a new transaction.
    """
    try:
        # Check if budget exists and belongs to user
        budget_result = (
            db.table("budgets")
            .select("id")
            .eq("id", str(transaction_in.budget_id))
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found or you don't have access to it",
            )

        # Check if account exists and belongs to the budget
        account_result = (
            db.table("accounts")
            .select("id")
            .eq("id", str(transaction_in.account_id))
            .eq("budget_id", str(transaction_in.budget_id))
            .execute()
        )

        if not account_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or does not belong to this budget",
            )

        # Check if category exists and belongs to the budget (if provided)
        if transaction_in.category_id:
            category_result = (
                db.table("categories")
                .select("id")
                .eq("id", str(transaction_in.category_id))
                .eq("budget_id", str(transaction_in.budget_id))
                .execute()
            )

            if not category_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found or does not belong to this budget",
                )

        # Create the transaction
        transaction_data = {
            "date": transaction_in.date.isoformat(),
            "payee": transaction_in.payee,
            "amount": str(transaction_in.amount),
            "budget_id": str(transaction_in.budget_id),
            "account_id": str(transaction_in.account_id),
            "cleared": transaction_in.cleared,
        }

        # Add optional fields if provided
        if transaction_in.category_id:
            transaction_data["category_id"] = str(transaction_in.category_id)
        if transaction_in.note:
            transaction_data["note"] = transaction_in.note

        result = db.table("transactions").insert(transaction_data).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create transaction",
            )

        return TransactionRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=List[TransactionRead])
async def get_transactions(
    budget_id: UUID = None,
    account_id: UUID = None,
    category_id: UUID = None,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> List[TransactionRead]:
    """
    Get all transactions, with optional filtering by budget_id, account_id, or category_id.
    """
    try:
        query = db.table("transactions").select("*")

        # Apply filters if provided
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

        # Apply account filter if provided
        if account_id:
            query = query.eq("account_id", str(account_id))

        # Apply category filter if provided
        if category_id:
            query = query.eq("category_id", str(category_id))

        result = query.execute()
        return [TransactionRead(**transaction) for transaction in result.data]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> TransactionRead:
    """
    Get a specific transaction by ID.
    """
    try:
        # First get the transaction
        result = (
            db.table("transactions").select("*").eq("id", str(transaction_id)).execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )

        transaction = result.data[0]

        # Now verify the budget belongs to the user
        budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", transaction["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or you don't have access to it",
            )

        return TransactionRead(**transaction)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: UUID,
    transaction_in: TransactionCreate,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> TransactionRead:
    """
    Update a transaction.
    """
    try:
        # First get the transaction
        existing_result = (
            db.table("transactions").select("*").eq("id", str(transaction_id)).execute()
        )

        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )

        existing_transaction = existing_result.data[0]

        # Verify the current budget belongs to the user
        current_budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", existing_transaction["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not current_budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or you don't have access to it",
            )

        # Check if new budget_id belongs to user
        if existing_transaction["budget_id"] != str(transaction_in.budget_id):
            budget_check = (
                db.table("budgets")
                .select("id")
                .eq("id", str(transaction_in.budget_id))
                .eq("user_id", current_user_id)
                .execute()
            )

            if not budget_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid budget ID"
                )

        # Check if new account belongs to the budget
        account_check = (
            db.table("accounts")
            .select("id")
            .eq("id", str(transaction_in.account_id))
            .eq("budget_id", str(transaction_in.budget_id))
            .execute()
        )

        if not account_check.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account not found or does not belong to this budget",
            )

        # Check if new category belongs to the budget (if provided)
        if transaction_in.category_id:
            category_check = (
                db.table("categories")
                .select("id")
                .eq("id", str(transaction_in.category_id))
                .eq("budget_id", str(transaction_in.budget_id))
                .execute()
            )

            if not category_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found or does not belong to this budget",
                )

        # Update the transaction
        transaction_data = {
            "date": transaction_in.date.isoformat(),
            "payee": transaction_in.payee,
            "amount": str(transaction_in.amount),
            "budget_id": str(transaction_in.budget_id),
            "account_id": str(transaction_in.account_id),
            "cleared": transaction_in.cleared,
            "category_id": None,  # Default to null
        }

        # Add optional fields if provided
        if transaction_in.category_id:
            transaction_data["category_id"] = str(transaction_in.category_id)
        if transaction_in.note:
            transaction_data["note"] = transaction_in.note

        result = (
            db.table("transactions")
            .update(transaction_data)
            .eq("id", str(transaction_id))
            .execute()
        )

        return TransactionRead(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: Client = Depends(get_supabase),
) -> None:
    """
    Delete a transaction.
    """
    try:
        # First get the transaction
        existing_result = (
            db.table("transactions").select("*").eq("id", str(transaction_id)).execute()
        )

        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )

        existing_transaction = existing_result.data[0]

        # Verify the budget belongs to the user
        budget_check = (
            db.table("budgets")
            .select("id")
            .eq("id", existing_transaction["budget_id"])
            .eq("user_id", current_user_id)
            .execute()
        )

        if not budget_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or you don't have access to it",
            )

        # Delete the transaction
        db.table("transactions").delete().eq("id", str(transaction_id)).execute()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
