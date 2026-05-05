import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))
from app.models.database import SessionLocal
from app.models.finance import Transaction
from app.models.user import User
from datetime import datetime, timedelta
from collections import defaultdict

db = SessionLocal()

try:
    user = db.query(User).first()
    months = 6
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 30)
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.transaction_type == "debit"
    ).order_by(Transaction.date).all()
    
    monthly_data = defaultdict(lambda: defaultdict(float))
    for txn in transactions:
        month_key = txn.date.strftime("%Y-%m")
        monthly_data[month_key][txn.category] += txn.amount
    
    sorted_months = sorted(monthly_data.keys())
    monthly_totals = [
        {
            "month": month,
            "total": sum(monthly_data[month].values()),
            "data": dict(monthly_data[month])
        }
        for month in sorted_months
    ]
    
    if len(monthly_totals) >= 2:
        recent_avg = sum(m["total"] for m in monthly_totals[-3:]) / min(3, len(monthly_totals))
        older_avg = sum(m["total"] for m in monthly_totals[:-3]) / max(1, len(monthly_totals) - 3)
        trend_direction = "increasing" if recent_avg > older_avg else ("decreasing" if recent_avg < older_avg else "stable")
        trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
    else:
        trend_direction = "stable"
        trend_percentage = 0
    
    all_categories = defaultdict(float)
    for month_data in monthly_totals:
        for cat, amount in month_data["data"].items():
            all_categories[cat] += amount
    
    highest_category = max(all_categories.items(), key=lambda x: x[1])[0] if all_categories else "N/A"
    
    res = {
        "monthly_data": monthly_totals,
        "trend": {
            "direction": trend_direction,
            "change_percentage": round(trend_percentage, 1),
            "message": f"Spending is {trend_direction} by {abs(trend_percentage):.1f}%"
        },
        "highest_category": highest_category,
        "forecasts": [
            {
                "month": (end_date + timedelta(days=30*(i+1))).strftime("%Y-%m"),
                "predicted_spend": round(monthly_totals[-1]["total"] * (1 + trend_percentage/100) if len(monthly_totals) > 0 else 0, 2),
                "confidence": 0.75
            }
            for i in range(3)
        ] if monthly_totals else []
    }
    print(json.dumps(res, indent=2))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
