import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'backend')))

from app.models.database import SessionLocal
from app.models.finance import Transaction
from datetime import datetime, timedelta
from sqlalchemy import desc

db = SessionLocal()

# Just try to run the query
try:
    days = 30
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    transactions = db.query(Transaction).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.transaction_type == "debit"
    ).order_by(desc(Transaction.date)).all()
    
    print(f"Success! Found {len(transactions)} transactions.")
    for t in transactions:
        print(t.id, t.date, t.amount, t.category)
except Exception as e:
    print(f"Error querying transactions: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
