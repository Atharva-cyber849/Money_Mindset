# Demo Account Documentation

## Overview
A fully populated demo account is available for testing the Money Mindset application without creating a new account.

## Demo Credentials
- **Email:** `demo@moneymindset.com`
- **Password:** `demo123`

## Demo Data Included

### User Profile
- **Name:** Demo User
- **Age:** 28
- **Occupation:** Software Engineer
- **Monthly Income:** $5,500
- **Location:** San Francisco, CA
- **Financial Knowledge:** Intermediate

### Transactions (214 total)
- **90 days** of transaction history
- **Income transactions:** Monthly salary ($5,500), freelance work, side projects
- **Expense transactions:** 
  - Housing: Rent ($1,800/month)
  - Utilities: Electric, Internet
  - Groceries: Weekly shopping at Whole Foods
  - Dining: Various restaurants and coffee shops
  - Transportation: Gas, Uber rides
  - Entertainment: Netflix, Spotify, movies
  - Health: Gym membership, pharmacy
  - Shopping: Amazon, Target
  - Insurance: Monthly premium

### Financial Goals (5 goals)
1. **Emergency Fund** - $6,500 / $10,000 (65% complete)
   - Priority: High
   - Deadline: 6 months
   - Status: Active

2. **Europe Vacation** - $1,200 / $5,000 (24% complete)
   - Priority: Medium
   - Deadline: 1 year
   - Status: Active

3. **New Laptop** - $800 / $2,000 (40% complete)
   - Priority: Medium
   - Deadline: 3 months
   - Status: Active

4. **Investment Portfolio** - $12,500 / $50,000 (25% complete)
   - Priority: Medium
   - Deadline: 2 years
   - Status: Active

5. **Pay Off Credit Card** - $3,000 / $3,000 (100% complete)
   - Priority: High
   - Status: Completed ✅

### Budgets (Current Month)
| Category | Budgeted | Spent | Status |
|----------|----------|-------|--------|
| Housing | $1,800 | $1,800 | 100% |
| Dining | $400 | $423.50 | 106% ⚠️ Over |
| Groceries | $600 | $487.50 | 81% |
| Transportation | $300 | $245.80 | 82% |
| Entertainment | $200 | $178.90 | 89% |
| Shopping | $300 | $256.30 | 85% |
| Utilities | $250 | $199.99 | 80% |
| Health | $200 | $124.98 | 62% |

### AI Tutor Conversations (3 messages)
Sample conversations demonstrating the AI tutor's financial advice capabilities:
1. "How can I save more money each month?"
2. "Should I invest or pay off debt first?"
3. "What's a good emergency fund amount?"

## How to Use

### First Time Setup
1. **Seed the demo account:**
   ```bash
   cd backend
   python seed_demo.py
   ```

2. **Start the backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

3. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

4. **Log in at:** http://localhost:3000/login

### Re-seeding the Demo Account
If you modify the demo data or want to reset it:
```bash
cd backend
python seed_demo.py
```

This will:
- Clear all existing demo data
- Regenerate fresh transactions, goals, budgets, and conversations
- Preserve the demo user account

## Testing Scenarios

### Scenario 1: Budget Management
1. Navigate to Dashboard
2. View budget status (notice "Dining" is over budget)
3. Explore budget optimization suggestions

### Scenario 2: Goal Tracking
1. Navigate to Goals page
2. View progress on multiple goals
3. See completed goal (Credit Card payoff)

### Scenario 3: Transaction Analysis
1. Navigate to Analytics
2. View spending patterns and trends
3. Test expense classification

### Scenario 4: AI Tutor
1. Navigate to AI Tutor
2. View conversation history
3. Ask new financial questions

### Scenario 5: Simulations
1. Navigate to Simulations
2. Try Coffee Shop Effect simulator
3. Test Emergency Fund calculator
4. Experiment with Investment Simulator

## Technical Details

### Seed Script Features
- **Realistic data generation:** Random variations in amounts and timing
- **Historical depth:** 90 days of transaction history
- **Category diversity:** 8+ spending categories
- **Multiple goal types:** Short-term and long-term goals
- **Budget scenarios:** Mix of under-budget and over-budget categories
- **AI conversation samples:** Demonstrating different financial topics

### Database Schema
The demo account uses the same schema as production:
- `users` table: User profile information
- `transactions` table: Financial transactions
- `goals` table: Savings goals
- `budgets` table: Monthly budgets by category
- `conversations` table: AI tutor chat history

### Password Security
Demo password is hashed using bcrypt with the same security as production accounts.

## Troubleshooting

### "Module not found" errors
Make sure virtual environment is activated:
```bash
cd "C:\Users\admin\OneDrive\Desktop\Money Mindset"
.venv\Scripts\Activate.ps1
cd backend
python seed_demo.py
```

### "bcrypt version" errors
Install compatible bcrypt version:
```bash
pip install bcrypt==3.2.2
```

### Database connection errors
Ensure the database is properly configured in `.env` file:
```env
DATABASE_URL=sqlite:///./money_mindset.db
```

## Security Notes

⚠️ **Important:** This demo account is for testing purposes only.
- Do not use demo credentials in production
- The demo account has public credentials
- All demo data is synthetic and for demonstration only
- In production, implement rate limiting and account lockout policies

## Customization

To customize the demo data, edit `backend/seed_demo.py`:
- Modify `seed_transactions()` for different spending patterns
- Adjust `seed_goals()` for different financial objectives
- Update `seed_budgets()` for different budget allocations
- Change `seed_conversations()` for different AI interactions

Example:
```python
# Add a custom goal
Goal(
    user_id=user_id,
    name="Down Payment for House",
    target_amount=50000.0,
    current_amount=15000.0,
    deadline=datetime.now() + timedelta(days=730),
    priority=1,
    status="active"
)
```

---

**Last Updated:** February 8, 2026
**Script Location:** `backend/seed_demo.py`
**Database:** SQLite (default) or PostgreSQL
