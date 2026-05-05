"""Transaction routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.user import User
from app.models.finance import Transaction
from app.core.security import get_current_user
from app.schemas.schemas import TransactionCreate, TransactionResponse

router = APIRouter()


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Get all transactions for current user."""
	return (
		db.query(Transaction)
		.filter(Transaction.user_id == current_user.id)
		.order_by(Transaction.date.desc())
		.all()
	)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
	payload: TransactionCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Create a transaction for current user."""
	if payload.amount < 0:
		raise HTTPException(status_code=400, detail="Amount must be non-negative")

	if payload.transaction_type not in {"debit", "credit"}:
		raise HTTPException(status_code=400, detail="transaction_type must be 'debit' or 'credit'")

	txn = Transaction(
		user_id=current_user.id,
		date=payload.date,
		description=payload.description,
		category=payload.category,
		amount=payload.amount,
		transaction_type=payload.transaction_type,
	)
	db.add(txn)
	db.commit()
	db.refresh(txn)
	return txn
