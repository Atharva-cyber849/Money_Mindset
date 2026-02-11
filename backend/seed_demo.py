"""
Seed demo account with sample data for testing
Run with: python seed_demo.py
"""
import sys
from datetime import datetime, timedelta
from random import choice, uniform, randint

from app.models.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.finance import Transaction, Goal, Budget, Conversation
from app.core.security import get_password_hash


def create_demo_user(db):
    """Create or update demo user"""
    demo_user = db.query(User).filter(User.email == "demo@moneymindset.com").first()
    
    if demo_user:
        print("Demo user already exists. Updating...")
        # Update user info
        demo_user.name = "Demo User"
        demo_user.age = 28
        demo_user.occupation = "Software Engineer"
        demo_user.monthly_income = 5500.0
        demo_user.location = "San Francisco, CA"
        demo_user.financial_knowledge = "intermediate"
        demo_user.updated_at = datetime.utcnow()
    else:
        print("Creating new demo user...")
        demo_user = User(
            email="demo@moneymindset.com",
            hashed_password=get_password_hash("demo123"),
            name="Demo User",
            age=28,
            occupation="Software Engineer",
            monthly_income=5500.0,
            location="San Francisco, CA",
            financial_knowledge="intermediate",
            is_active=True
        )
        db.add(demo_user)
    
    db.commit()
    db.refresh(demo_user)
    return demo_user


def clear_demo_data(db, user_id):
    """Clear existing demo data"""
    print("Clearing existing demo data...")
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.query(Goal).filter(Goal.user_id == user_id).delete()
    db.query(Budget).filter(Budget.user_id == user_id).delete()
    db.query(Conversation).filter(Conversation.user_id == user_id).delete()
    db.commit()


def seed_transactions(db, user_id):
    """Create sample transactions for the past 3 months"""
    print("Seeding transactions...")
    
    categories = {
        "credit": [
            ("Salary", "Income", 5500.0),
            ("Freelance Work", "Income", 800.0),
            ("Investment Return", "Investment", 150.0),
            ("Side Project", "Income", 300.0),
        ],
        "debit": [
            ("Starbucks", "Coffee", 5.50),
            ("Whole Foods", "Groceries", 85.30),
            ("Shell Gas Station", "Transportation", 45.00),
            ("Netflix", "Entertainment", 15.99),
            ("Spotify", "Entertainment", 9.99),
            ("Gym Membership", "Health", 89.99),
            ("Electric Bill", "Utilities", 120.00),
            ("Internet", "Utilities", 79.99),
            ("Rent", "Housing", 1800.00),
            ("Amazon", "Shopping", 45.00),
            ("Target", "Shopping", 67.50),
            ("Chipotle", "Dining", 12.50),
            ("Uber", "Transportation", 18.50),
            ("Movie Theater", "Entertainment", 25.00),
            ("Pharmacy", "Health", 34.99),
            ("Insurance", "Insurance", 250.00),
        ]
    }
    
    transactions = []
    today = datetime.now()
    
    # Generate transactions for the past 90 days
    for day_offset in range(90):
        date = today - timedelta(days=day_offset)
        
        # Add salary on the 1st of each month
        if date.day == 1:
            transactions.append(Transaction(
                user_id=user_id,
                date=date,
                description="Monthly Salary",
                category="Income",
                amount=5500.0,
                transaction_type="credit"
            ))
        
        # Random daily transactions
        num_transactions = randint(1, 4)
        for _ in range(num_transactions):
            trans_type = choice(["debit", "debit", "debit", "credit"])  # More debits
            options = categories[trans_type]
            desc, cat, base_amount = choice(options)
            
            # Add some randomness to amounts
            if trans_type == "debit" and base_amount < 100:
                amount = round(uniform(base_amount * 0.8, base_amount * 1.2), 2)
            else:
                amount = base_amount
            
            transactions.append(Transaction(
                user_id=user_id,
                date=date - timedelta(hours=randint(0, 23)),
                description=desc,
                category=cat,
                amount=amount,
                transaction_type=trans_type
            ))
    
    db.bulk_save_objects(transactions)
    db.commit()
    print(f"Created {len(transactions)} transactions")


def seed_goals(db, user_id):
    """Create sample financial goals"""
    print("Seeding goals...")
    
    goals = [
        Goal(
            user_id=user_id,
            name="Emergency Fund",
            target_amount=10000.0,
            current_amount=6500.0,
            deadline=datetime.now() + timedelta(days=180),
            priority=1,
            status="active"
        ),
        Goal(
            user_id=user_id,
            name="Europe Vacation",
            target_amount=5000.0,
            current_amount=1200.0,
            deadline=datetime.now() + timedelta(days=365),
            priority=2,
            status="active"
        ),
        Goal(
            user_id=user_id,
            name="New Laptop",
            target_amount=2000.0,
            current_amount=800.0,
            deadline=datetime.now() + timedelta(days=90),
            priority=3,
            status="active"
        ),
        Goal(
            user_id=user_id,
            name="Investment Portfolio",
            target_amount=50000.0,
            current_amount=12500.0,
            deadline=datetime.now() + timedelta(days=730),
            priority=2,
            status="active"
        ),
        Goal(
            user_id=user_id,
            name="Pay Off Credit Card",
            target_amount=3000.0,
            current_amount=3000.0,
            deadline=datetime.now() - timedelta(days=30),
            priority=1,
            status="completed"
        ),
    ]
    
    db.bulk_save_objects(goals)
    db.commit()
    print(f"Created {len(goals)} goals")


def seed_budgets(db, user_id):
    """Create sample budgets for current month"""
    print("Seeding budgets...")
    
    now = datetime.now()
    
    budgets = [
        Budget(
            user_id=user_id,
            month=now.month,
            year=now.year,
            category="Housing",
            budgeted_amount=1800.0,
            spent_amount=1800.0
        ),
        Budget(
            user_id=user_id,
            month=now.month,
            year=now.year,
            category="Groceries",
            budgeted_amount=600.0,
            spent_amount=487.50
        ),
        Budget(
            user_id=user_id,
            month=now.month,
            year=now.year,
            category="Transportation",
            budgeted_amount=300.0,
            spent_amount=245.80
        ),
        Budget(
            user_id=user_id,
            month=now.month,
            year=now.year,
            category="Entertainment",
            budgeted_amount=200.0,
            spent_amount=178.90
        ),
        Budget(
            user_id=user_id,
            month=now.month,
            year=now.year,
            category="Dining",
            budgeted_amount=400.0,
            spent_amount=423.50
        ),
        Budget(
            user_id=user_id,
            month=now.month,
            year=now.year,
            category="Shopping",
            budgeted_amount=300.0,
            spent_amount=256.30
        ),
        Budget(
            user_id=user_id,
            month=now.month,
            year=now.year,
            category="Utilities",
            budgeted_amount=250.0,
            spent_amount=199.99
        ),
        Budget(
            user_id=user_id,
            month=now.month,
            year=now.year,
            category="Health",
            budgeted_amount=200.0,
            spent_amount=124.98
        ),
    ]
    
    db.bulk_save_objects(budgets)
    db.commit()
    print(f"Created {len(budgets)} budgets")


def seed_conversations(db, user_id):
    """Create sample AI tutor conversation history"""
    print("Seeding conversations...")
    
    conversations = [
        Conversation(
            user_id=user_id,
            message="How can I save more money each month?",
            response="Great question! Based on your spending patterns, I see you're spending about $423 on dining out this month, which is over your $400 budget. Here are some tips: 1) Try meal prepping on Sundays to reduce dining expenses. 2) Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings. 3) Set up automatic transfers to your savings account right after payday.",
            context='{"category": "budgeting", "user_spending": {"dining": 423.50}}',
            created_at=datetime.now() - timedelta(days=5)
        ),
        Conversation(
            user_id=user_id,
            message="Should I invest or pay off debt first?",
            response="This depends on the interest rates! Generally, if your debt has an interest rate above 6-7%, prioritize paying it off first. I see you recently completed paying off your credit card - excellent work! Now you can focus on building your emergency fund (currently at 65% of your $10K goal) before investing more aggressively.",
            context='{"category": "investment", "debt_paid": true}',
            created_at=datetime.now() - timedelta(days=3)
        ),
        Conversation(
            user_id=user_id,
            message="What's a good emergency fund amount?",
            response="A solid emergency fund typically covers 3-6 months of essential expenses. Looking at your data, your monthly essentials (rent, utilities, groceries, insurance) come to about $2,700. So aim for $8,100 to $16,200. Your current goal of $10,000 is perfect for a 3.7-month buffer. You're already at $6,500 - keep going!",
            context='{"category": "emergency_fund", "monthly_essentials": 2700}',
            created_at=datetime.now() - timedelta(days=1)
        ),
    ]
    
    db.bulk_save_objects(conversations)
    db.commit()
    print(f"Created {len(conversations)} conversations")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("MONEY MINDSET - Demo Account Seeder")
    print("=" * 60)
    
    # Create tables if they don't exist
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create demo user
        demo_user = create_demo_user(db)
        print(f"✓ Demo user created/updated (ID: {demo_user.id})")
        
        # Clear existing data
        clear_demo_data(db, demo_user.id)
        print("✓ Existing demo data cleared")
        
        # Seed all data
        seed_transactions(db, demo_user.id)
        print("✓ Transactions seeded")
        
        seed_goals(db, demo_user.id)
        print("✓ Goals seeded")
        
        seed_budgets(db, demo_user.id)
        print("✓ Budgets seeded")
        
        seed_conversations(db, demo_user.id)
        print("✓ Conversations seeded")
        
        print("\n" + "=" * 60)
        print("✅ Demo account seeded successfully!")
        print("=" * 60)
        print("\nDemo Account Credentials:")
        print("  Email:    demo@moneymindset.com")
        print("  Password: demo123")
        print("\nYou can now log in with these credentials.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error seeding demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

