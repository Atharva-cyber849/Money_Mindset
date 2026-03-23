"""Goal routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.user import User
from app.models.finance import Goal
from app.core.security import get_current_user
from app.schemas.schemas import GoalCreate, GoalUpdate, GoalResponse

router = APIRouter()


@router.get("", response_model=List[GoalResponse])
async def get_goals(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Get all goals for current user."""
	goals = db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.created_at.desc()).all()
	return goals


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
	payload: GoalCreate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Create a new goal for current user."""
	goal = Goal(
		user_id=current_user.id,
		name=payload.name,
		target_amount=payload.target_amount,
		current_amount=payload.current_amount,
		deadline=payload.deadline,
		priority=payload.priority,
		status="active",
	)
	db.add(goal)
	db.commit()
	db.refresh(goal)
	return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
	goal_id: int,
	payload: GoalUpdate,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Update an existing goal."""
	goal = db.query(Goal).filter(
		Goal.id == goal_id,
		Goal.user_id == current_user.id,
	).first()

	if not goal:
		raise HTTPException(status_code=404, detail="Goal not found")

	updates = payload.model_dump(exclude_unset=True)
	for key, value in updates.items():
		setattr(goal, key, value)

	db.commit()
	db.refresh(goal)
	return goal


@router.delete("/{goal_id}")
async def delete_goal(
	goal_id: int,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	"""Delete an existing goal."""
	goal = db.query(Goal).filter(
		Goal.id == goal_id,
		Goal.user_id == current_user.id,
	).first()

	if not goal:
		raise HTTPException(status_code=404, detail="Goal not found")

	db.delete(goal)
	db.commit()

	return {"status": "success", "message": "Goal deleted"}
