import sys
import os

sys.path.insert(0, os.path.abspath("."))
from app.models.database import SessionLocal
from app.models.finance import Transaction
from app.models.user import User
from datetime import datetime, timedelta

db = SessionLocal()

try:
    user = db.query(User).first()
    if not user:
        print("No users found.")
    else:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        txns = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.transaction_type == "debit"
        ).all()
        print(f"User {user.email} has {len(txns)} transactions in the last 30 days.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
