# Money Mindset: Q&A and Domain Knowledge Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [Games & Simulations](#games--simulations)
4. [Analytics Features](#analytics-features)
5. [API Structure](#api-structure)
6. [Data Flow](#data-flow)
7. [Q&A Section](#qa-section)

---

## Architecture Overview

### Tech Stack
- **Frontend**: Next.js 15 (TypeScript, React)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (primary) / SQLite (fallback)
- **Cache**: Redis (optional)
- **Market Data**: yFinance, Finnhub, Indian Market APIs
- **AI/LLM**: OpenAI-compatible (OpenRouter), Anthropic

### Folder Structure
```
Money-Mindset/
├── frontend/
│   └── src/
│       ├── app/               # Next.js routes
│       ├── components/        # Reusable components
│       ├── lib/              # Utilities, APIs, auth
│       └── styles/           # Global CSS
├── backend/
│   └── app/
│       ├── api/v1/           # API routes
│       ├── core/             # Config, security
│       ├── models/           # DB models, enums
│       ├── schemas/          # Pydantic schemas
│       └── services/         # Business logic
│           ├── simulation/   # Game simulators
│           ├── analytics/    # Analytics engines
│           ├── gamification/ # Badges, XP, progress
│           └── api_clients/  # External API clients
└── docker/                   # Docker configuration
```

---

## Database Schema

### Core User Models
```
┌─────────────────────────────────────────┐
│              Users                      │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ email, username, password_hash          │
│ is_active, is_verified                  │
│ personality_type, risk_profile          │
│ created_at, updated_at                  │
└─────────────────────────────────────────┘
        │
        ├──> Transactions
        ├──> Budgets
        ├──> Goals
        ├──> [Game Sessions]
        └──> Conversations (AI history)
```

### Game Session Models
Each game has its own session and event tracking:

#### Gullak Sessions
- `GullakSession`: Game session metadata
- `GullakLifeEvent`: Monthly life events and decisions
- Tracks: jar allocations, total wealth, achievements

#### SIP Chronicles Sessions
- `SIPSession`: SIP investment tracking
- `SIPInterruption`: Market events (crashes, bull runs, etc.)
- `SIPDecision`: Player's responses (continue, pause, upgrade, withdraw)

#### Karobaar Sessions
- `KarobarSession`: Business simulation session
- `KarobarDecision`: Business decisions
- `KarobarMilestone`: Milestones achieved

#### Paper Trading Sessions
- `PaperTradingSession`: Trading session with paper money
- `PaperTrade`: Individual trades (buy/sell)
- `PaperPortfolioSnapshot`: Daily portfolio snapshots
- `PaperTradingEvent`: Market events during session

#### Dalal Street & Black Swan
- Similar session + decision + event models

---

## Games & Simulations

### 1. **GULLAK (Piggy Bank Game)** 🎯
**Location**: `/games/gullak`
**Backend**: `gullak_simulator.py`, **DB**: `GullakSession`

#### How It Works
- **Concept**: Indian personal finance with 5 jar system (age 22→32, 10 years)
- **Jars** (allocation targets):
  - 🚨 **Emergency Fund**: 6-12 months expenses (15% target)
  - 🛡️ **Insurance**: Health + Life insurance (10% target)
  - 💰 **Short-term Goals**: 1-3 year goals (20% target)
  - 📈 **Long-term Investments**: Stocks/Mutual Funds (40% target)
  - 🏆 **Gold**: Inflation hedge (15% target)

- **Monthly Cycle**:
  1. Income arrives (salaried/gig_work/business)
  2. Player allocates income to jars
  3. Monthly life event occurs
  4. Player makes decision
  5. Jars experience growth/loss

- **Life Events** (20+ Indian scenarios):
  - Medical emergency (use emergency fund)
  - Wedding expenses
  - Market correction
  - Salary increase (rebalancing opportunity)
  - GST crash, Demonetization, Monsoon failure
  - Dowry negotiation, Property appreciation

- **Scoring**:
  - Wise decisions earn XP + badges
  - Jar health percentage impacts final score
  - 10-year wealth accumulation matters

**API Endpoint**: `POST /api/v1/games/gullak/create`, `/api/v1/games/gullak/{session_id}/decision`

---

### 2. **SIP CHRONICLES (Compound Interest Simulation)** 📊
**Location**: `/games/sip-chronicles`
**Backend**: `sip_chronicles_simulator.py`, **DB**: `SIPSession`

#### How It Works
- **Concept**: Idle game showing power of compound interest (age 22→60, 38 years)
- **Starting Conditions**:
  - ₹500/month SIP automatically invested
  - Choose investment: Nifty 50, Midcap, Gold, ELSS, Liquid Fund, etc.
  - Passive wealth accumulation with ~15% annual returns⚡

- **Interruptions** (test investment discipline):
  - 🔴 **Market Crash**: Stock drops 40%+
    - Options: Continue investing (rupee cost averaging), Panic sell
  - 💼 **Job Loss**: Income interrupted
    - Options: Pause SIP, Withdraw emergency fund, Use savings
  - 📈 **Bull Run**: Market rallies 50%+
    - FOMO test: Stay invested or take profits?
  - 💰 **Salary Increase**: Income +₹10k
    - Option: Upgrade SIP from ₹500 to ₹1000+
  - 🎯 **Budget Announcement**: Policy changes
  - ⚖️ **Circuit Breaker**: Market halt (circuit breaker triggers)
  - 🏦 **RBI Policy Decision**: Interest rate changes

- **Decision Outcomes**:
  - Wise decisions: Continue investing = massive wealth (₹2.5L+ over 38 years)
  - Panic selling: Wealth stagnates at ₹50-80k
  - Upgrading SIP wisely: Wealth accelerates

- **Graphics**: Compelling wealth growth chart showing compound effect

**API Endpoint**: `POST /api/v1/games/sip-chronicles/create`, `/api/v1/games/sip-chronicles/{session_id}/decision`

---

### 3. **PAPER TRADING** 💹
**Location**: `/games/paper-trading`
**Backend**: `paper_trading_simulator.py`, **DB**: `PaperTradingSession`

#### How It Works
- **Concept**: Real stock market trading with paper money
- **Setup**:
  - Choose market: India (NIFTY 50), US (S&P 500), or Both
  - Starting capital: ₹100k / $5k
  - Session duration: 3-6 months real-time market data

- **Stocks Available**:
  - **India**: Reliance, TCS, HDFC Bank, Bharti Airtel, etc.
  - **US**: Apple, Microsoft, Google, Tesla, Amazon, etc.

- **Features**:
  - Real historical price data (via yFinance)
  - Buy/Sell orders
  - Portfolio tracking (daily snapshots)
  - Market events (earnings, policy announcements)
  - Return % calculation
  - Leaderboard (compare with peers)

- **Learning Goals**:
  - Understand market volatility
  - Learn risk/reward tradeoffs
  - Emotional trading vs strategic trading
  - Sector rotation dynamics

**API Endpoint**: `POST /api/v1/games/paper-trading/create`, `/api/v1/games/paper-trading/{session_id}/trade`

---

### 4. **KAROBAAR (Business Simulation)** 🏪
**Location**: `/games/karobaar`
**Backend**: `karobaar_simulator.py`, **DB**: `KarobarSession`

#### How It Works
- **Concept**: Running a small business (retail shop / startup)
- **Player Profile**:
  - Choose: Gender, City, Education level
  - Career path: Salaried → Business owner
  - Starting capital + skills

- **Monthly Decisions**:
  - Staff hiring/firing
  - Inventory management
  - Marketing spend
  - Pricing strategy
  - Supplier negotiations

- **Challenges**:
  - Seasonal demand variations
  - Competition
  - Unexpected expenses
  - Market downturns

- **Metrics**:
  - Revenue, Profit, Cashflow
  - Customer satisfaction
  - Business growth rate

**API Endpoint**: `POST /api/v1/games/karobaar/create`, `/api/v1/games/karobaar/{session_id}/decision`

---

### 5. **DALAL STREET (Stock Market Gamification)** 📈
**Location**: `/games/dalal-street`
**Backend**: `dalal_street_simulator.py`

#### How It Works
- **Concept**: Historical stock market scenarios with social trading
- **Market Eras**: Bull Run / Bear Market / Crash Recovery
- **Trade Types**:
  - Intraday trading
  - Swing trading
  - Long-term investing
- **News Events**: Real historical events trigger market reactions
- **Social Features**: Compare performance with other traders

---

### 6. **BLACK SWAN (Crisis Management)** 🐦
**Location**: `/games/black-swan`
**Backend**: `black_swan_simulator.py`

#### How It Works
- **Concept**: Handling unexpected financial crises
- **Crisis Types**:
  - Job loss scenario
  - Medical emergency
  - Market crash
  - Business failure
  - Debt crisis

- **Player Decisions**:
  - Draw from emergency fund?
  - Take loan?
  - Reduce lifestyle?
  - Prioritize payments?

- **Outcomes**:
  - Recovery speed
  - Final financial health
  - Lessons learned

---

## Analytics Features

All analytics features are in `backend/app/services/analytics/` and exposed via `/api/v1/analytics`

### 1. **Expense Classification** 📋
**Service**: `expense_classifier.py`

#### How It Works
- **Input**: Transaction description + amount
- **Process**:
  - ML-based text classification
  - Merchant database lookup
  - Amount-based rules

- **Categories**:
  - Food & Dining
  - Transportation
  - Shopping
  - Entertainment
  - Utilities
  - Healthcare
  - Education
  - Savings
  - Investments
  - (Custom categories)

#### API Endpoints
```
POST /api/v1/analytics/classify/transaction
  - Classify single transaction

POST /api/v1/analytics/classify/batch
  - Classify multiple transactions

GET /api/v1/analytics/classify/merchant/{merchant_name}
  - Get category for merchant (rule setup)
```

**Data Storage**: Stored in `transactions` table with category column

---

### 2. **Market Simulation** 🎰
**Service**: `market_simulator.py`

#### How It Works
- **Monte Carlo Simulation**: Runs 1000-10000 random market scenarios
- **Asset Classes**:
  - Aggressive Stocks (18% return, 25% volatility)
  - Large Cap (12% return, 15% volatility)
  - Balanced (10% return, 12% volatility)
  - Conservative (7% return, 8% volatility)
  - Bonds (6% return, 5% volatility)
  - Savings (4% return, 0% volatility)

#### Simulation Scenarios
1. **Investment Growth**: `simulate_investment()`
   - Input: Initial amount, monthly contribution, years, asset class
   - Output: 50th percentile, 75th percentile, 95th percentile wealth
   - Shows: Best case, average case, worst case scenarios

2. **Asset Comparison**: `compare_asset_classes()`
   - Compare risk/return across asset types
   - Helps choose optimal allocation

3. **Risk vs Return**: `risk_vs_return_analysis()`
   - Question: "What's needed to reach $X in Y years?"
   - Suggests: "Need 70% stocks, 30% bonds"

4. **Market Crash Scenario**: `simulate_market_crash()`
   - What if market crashes 30% in year 5?
   - Shows recovery trajectory
   - Teaches: Crashes are temporary, long-term investing wins

#### API Endpoints
```
POST /api/v1/analytics/simulate/investment
POST /api/v1/analytics/simulate/compare-assets
POST /api/v1/analytics/simulate/risk-analysis
POST /api/v1/analytics/simulate/market-crash
GET /api/v1/analytics/simulate/asset-classes
```

---

### 3. **Budget Optimization** 💳
**Service**: `budget_optimizer.py`

#### Budget Rules (Financial Principles)
| Category | Max % | Ideal % | Notes |
|----------|-------|---------|-------|
| Essentials | 50% | 40% | Housing, food, transport |
| Wants | 35% | 30% | Entertainment, hobbies |
| Savings | 20% | 30% | Investments, emergency fund |
| Insurance | 5% | - | As % of income |
| Debt | 15% | <10% | Should decrease over time |

#### Services Offered
1. **Budget Analysis**: `analyze_budget()`
   - Input: Income, expenses by category, savings
   - Output: Health score, violations, recommendations

2. **Budget Suggestion**: `suggest_budget_allocation()`
   - 50/30/20 rule: 50% needs, 30% wants, 20% savings
   - Golden ratio based on income level

3. **Peer Comparison**: `compare_to_peers()`
   - Benchmark: "How does your food spending vs peers?"
   - Age groups: 18-24, 25-34, 35-44, 45-54, 55-64, 65+
   - Locations: National, metro, tier-2, rural

#### API Endpoints
```
POST /api/v1/analytics/budget/analyze
POST /api/v1/analytics/budget/suggest/{income}
POST /api/v1/analytics/budget/compare-peers
GET /api/v1/analytics/budget/rules
```

---

### 4. **Forecasting** 🔮
**Service**: `forecasting.py`

#### Forecasting Methods
1. **Time Series Forecasting**: `forecast_spending()`
   - Input: Historical transaction data (last 6-12 months)
   - Output: Predicted spending for next 3 months
   - Method: ARIMA / Exponential Smoothing

2. **Category Forecasting**: `predict_category_spending()`
   - Input: Category spending history
   - Output: Next month's predicted spend with confidence intervals

3. **Anomaly Detection**: `anomaly_detection()`
   - Identifies unusual spending patterns
   - Example: "You spent 3x normal on groceries this month"
   - Uses: Standard deviation threshold

4. **Budget vs Forecast**: `compare_forecast_to_budget()`
   - Question: "Will I exceed my food budget?"
   - Output: Probability of overrun, suggested adjustments

#### API Endpoints
```
POST /api/v1/analytics/forecast/spending
POST /api/v1/analytics/forecast/category
POST /api/v1/analytics/forecast/compare-budget
POST /api/v1/analytics/forecast/anomalies
```

---

## API Structure

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.moneymindset.com`

### Authentication
All endpoints (except `/auth`) require JWT token:
```
Authorization: Bearer <jwt_token>
```

### API Versioning
All endpoints: `/api/v1/*`

### Standard Response Format
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "error": null
}
```

### API Routes
```
/api/v1/auth              - Login, register, refresh token
/api/v1/users             - User profile, preferences
/api/v1/transactions      - Transaction history, add/update
/api/v1/budgets           - Budget management
/api/v1/goals             - Financial goals tracking
/api/v1/games             - All game endpoints
/api/v1/simulations       - Monte Carlo & other simulations
/api/v1/analytics         - Classification, forecasting, optimization
/api/v1/personality       - Personality assessment
/api/v1/progress          - Gamification (badges, XP, levels)
/api/v1/market            - Real-time market data
/api/v1/ai-tutor          - AI tutoring endpoints
```

---

## Data Flow

### User Game Flow (Example: SIP Chronicles)

```
1. USER CREATES SESSION
   Frontend: POST /api/v1/games/sip-chronicles/create
   ├─ Payload: { user_id, investment_type, initial_sip }
   └─ Backend: Creates SIPSession record in DB

2. GAME RUNS (Idle)
   Frontend: Accumulates wealth locally / every minute polls backend
   ├─ Monthly snapshot generated
   ├─ Compound interest calculated
   └─ Interruption event triggered (~10 times over 38 years)

3. INTERRUPTION OCCURS
   Backend: Generates interruption event
   ├─ Payload: { type, description, options: [action1, action2, ...] }
   └─ Frontend: Shows modal with options

4. USER MAKES DECISION
   Frontend: POST /api/v1/games/sip-chronicles/{session_id}/decision
   ├─ Payload: { month, decision_type, chosen_action }
   ├─ Backend: Updates SIPDecision record
   ├─ Recalculates wealth based on choice
   └─ Calculates XP reward

5. USER COMPLETES SESSION
   Frontend: POST /api/v1/games/sip-chronicles/{session_id}/complete
   ├─ Backend: Finalizes session, awards badges
   ├─ Stores in PaperTradingSession table
   └─ Updates user gamification stats
```

### Data Storage Pattern
```
┌─────────────────────────────────────┐
│     PostgreSQL Database             │
├─────────────────────────────────────┤
│                                     │
│  User Profile                       │
│  ├─ Personal info, credentials      │
│  ├─ Personality type, risk profile  │
│  └─ Gamification stats (XP, level)  │
│                                     │
│  Financial Data                     │
│  ├─ Transactions (imported/manual)  │
│  ├─ Budgets (monthly allocations)   │
│  └─ Goals (targets)                 │
│                                     │
│  Game Sessions                      │
│  ├─ GullakSession + GullakLifeEvent │
│  ├─ SIPSession + SIPInterruption    │
│  ├─ PaperTradingSession + Trades    │
│  └─ [Other game models]             │
│                                     │
│  Gamification                       │
│  ├─ Badges earned                   │
│  ├─ Achievement progress            │
│  └─ Progress tracking               │
│                                     │
│  AI/Analytics                       │
│  └─ Conversation history            │
│                                     │
└─────────────────────────────────────┘
         ↓ (Cache layer)
     Redis (optional)
```

### Real-Time Market Data Flow
```
1. EXTERNAL DATA SOURCES
   ├─ yFinance: Historical OHLC data (free, public)
   ├─ Finnhub: Real-time quotes + news (API key required)
   ├─ Indian Market API: NSE data (custom integration)
   └─ NewsAPI: Financial news (optional)

2. DATA FETCHING (Backend)
   ├─ Scheduled: Prefetch daily market data
   ├─ On-demand: Fetch specific stock prices
   └─ Cache: Store in memory/Redis for 5 mins

3. GAME SIMULATION
   ├─ Paper Trading: Uses real historical data
   ├─ Market Simulator: Uses historical stats (returns, volatility)
   └─ Forecast: Uses transaction history patterns

4. FRONTEND RENDERING
   ├─ Charts: Price movements, portfolio growth
   ├─ Tables: Holdings, trades, portfolio value
   └─ Real-time updates: Via websockets (optional)
```

---

## Q&A Section

### **General Questions**

#### Q1: How do I start the Money Mindset app locally?
**A**:
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
Backend runs on `http://localhost:8000`, Frontend on `http://localhost:3000`

#### Q2: What's the tech stack and why these choices?
**A**:
- **FastAPI**: Modern, fast, auto-docs, type-safe
- **Next.js**: Full-stack React, excellent performance, built-in API routes
- **PostgreSQL**: Mature, reliable, spatial queries for geo-analytics
- **SQLAlchemy ORM**: Type-safe database queries in Python
- **Redis**: Optional but recommended for caching market data & session management

#### Q3: How is user authentication handled?
**A**:
1. User registers/logs in
2. Backend generates JWT token (expires in 30 mins)
3. Frontend stores token in localStorage/sessionStorage
4. All API requests include `Authorization: Bearer <token>` header
5. Backend validates token on each request
6. Route: `POST /api/v1/auth/login`, `POST /api/v1/auth/register`

---

### **Games & Simulations**

#### Q4: How does Gullak game work?
**A**:
- 10-year simulation with monthly income allocation into 5 jars
- Each month: (1) Income arrives, (2) Player allocates, (3) Life event occurs, (4) Decision impacts wealth
- Wisdom of allocation + smart decisions during crises = higher score
- Example: Allocating 15% to emergency fund saves you during medical emergency (-2000 rupees), but wise decision to not touch long-term investments earns +50 XP
- Data stored in `GullakSession` + `GullakLifeEvent` tables

#### Q5: How does SIP Chronicles compound interest work?
**A**:
- Monthly return = (accumulated_wealth + monthly_sip) × (annual_return / 12)
- Example: ₹500 SIP, 15% annual return on Nifty 50
  - Month 1: ₹500 accumulated
  - Month 2: (₹500 + ₹500) × (0.15/12) = ₹12.50 return + ₹500 SIP = ₹1012.50
  - Month 3: (₹1012.50 + ₹500) × (0.15/12) = ₹18.90 return + ₹500 SIP = ₹2031.40
  - After 38 years: ₹25,00,000+ (power of compound interest!)
- Interruptions test: Will player stay invested during crashes or panic sell?

#### Q6: How does Paper Trading get real stock prices?
**A**:
- Uses **yFinance** library (open-source, free, Yahoo Finance backend)
- Fetches historical OHLC (Open, High, Low, Close) data
- Example API: `yf.download('RELIANCE.NS', start='2024-01-01', end='2024-03-24')`
- For real-time data, uses **Finnhub API** (limited free tier, paid for production)
- Prices updated daily, games use real historical data for accuracy

#### Q7: How is game progress saved?
**A**:
- Each decision creates record in DB: `GullakLifeEvent`, `SIPDecision`, `PaperTrade`, etc.
- Session can be resumed: Previous state is reconstructed from DB records
- Example: Resume SIP game shows last month's wealth, next interruption ready
- Completion finalized in session record with: final wealth, achievements earned, XP gained

#### Q8: Can players play multiple games simultaneously?
**A**:
- Yes! Each game has separate session management
- User can have active `GullakSession`, `SIPSession`, `PaperTradingSession` simultaneously
- DB allows multiple sessions per user
- Frontend manages navigation between active sessions

---

### **Analytics Features**

#### Q9: How accurate is expense classification?
**A**:
- Uses text-based ML classifier (trained on merchant names + descriptions)
- Merchant database rules: "Starbucks" → Food & Dining, "Uber" → Transportation
- Amount rules: Large transfers likely transfers, small amounts might be tips
- Supports manual override + user feedback to improve future classifications
- Accuracy: ~85-90% on common merchants, lower on custom/small businesses

#### Q10: How does market simulation work?
**A**:
- **Monte Carlo Method**:
  1. Run 1000 simulations
  2. Each simulation: Random returns drawn from normal distribution
  3. Distribution parameters from historical data (mean return, std deviation)
  4. Each month: wealth = wealth × (1 + random_return)
  5. Track: P10, P50, P90 percentiles
- Output shows: "50% chance of reaching ₹10L, 10% chance of ₹15L, worst case ₹5L"
- Educational value: Understand probability, not certainty

#### Q11: What's the 50/30/20 budget rule?
**A**:
- **50%**: Essential needs (housing, food, transport, insurance)
- **30%**: Wants (entertainment, dining out, hobbies)
- **20%**: Savings (investments, emergency fund, debt repayment)
- App recommends based on income level with regional adjustments
- Example: ₹50,000 monthly income
  - Needs: ₹25,000
  - Wants: ₹15,000
  - Savings: ₹10,000

#### Q12: How are anomalies detected in spending?
**A**:
- **Method**: Z-score (standard deviation units from mean)
- Example: Average food spending = ₹5,000/month, std dev = ₹500
  - Month X spending: ₹8,000
  - Z-score = (8000 - 5000) / 500 = 6 standard deviations
  - Flagged as anomaly (threshold = 2σ typically)
- Helps identify: Unusual purchases, lifestyle changes, potential fraud

#### Q13: What data sources feed the analytics?
**A**:
- User's own: Transactions, budgets, goals (manual entry or bank import)
- Market data: yFinance (historical), Finnhub (real-time)
- Peer benchmarks: Built-in database by age/location/income
- News API: Optional financial news context
- App improves with more user data (transactions history = better forecasts)

---

### **Architecture & Database**

#### Q14: Where is user data stored?
**A**:
- **PostgreSQL Database** (production) or **SQLite** (local development)
- Tables:
  - `users`: Core profile, authentication
  - `transactions`: All financial transactions
  - `budgets`: Monthly budget allocations
  - `goals`: Financial goals with targets
  - `[game_sessions]`: Specific to each game (GullakSession, SIPSession, etc.)
  - `conversations`: AI tutor chat history
- **Sensitive data**: Passwords hashed with bcrypt, no plain-text storage
- **API keys**: Stored in `.env` file (never in version control)

#### Q15: How are API calls structured?
**A**:
- **Request format**: JSON (POST/PUT) or query parameters (GET)
- **Authentication**: JWT token in header
- Example:
```bash
curl -X POST http://localhost:8000/api/v1/games/sip-chronicles/create \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "investment_type": "nifty_50",
    "initial_sip": 500
  }'
```
- **Response**: JSON with `success`, `data`, `error` fields

#### Q16: How does frontend communicate with backend?
**A**:
- **Framework**: React Query (TanStack Query) for data fetching
- **Pattern**:
  ```javascript
  // Fetch can be done via hooks
  const { data, isLoading } = useQuery({
    queryKey: ['game', sessionId],
    queryFn: () => fetch(`/api/v1/games/${sessionId}`).then(r => r.json())
  })
  ```
- **Error handling**: Automatic retries, fallback UI states
- **Caching**: React Query caches responses, reduces redundant API calls

#### Q17: What happens when database connection fails?
**A**:
- Backend returns HTTP 500 error with error message
- Frontend shows error toast notification
- User can retry operation
- **Fallback**: SQLite (local) can be used for development if PostgreSQL unavailable

#### Q18: How are game sessions recovered if connection drops?
**A**:
- Session ID stored in URL + browser storage
- On reconnection: Frontend refetches session state from backend
- DB contains all game decisions, so state reconstructed from history
- Last decision replayed to show current state
- No data loss (all stored in DB)

---

### **Performance & Scalability**

#### Q19: How many concurrent users can the system handle?
**A**:
- **Backend capacity**: FastAPI can handle 1000s of concurrent requests
- **Bottleneck**: Database (PostgreSQL) connection pool
- **Optimization**:
  - Redis caching for market data
  - Connection pooling (SQLAlchemy)
  - Async/await in FastAPI
- **Recommended**: Horizontal scaling with load balancer

#### Q20: How is market data performance optimized?
**A**:
- **Caching**: 5-minute cache for stock prices (data updates daily)
- **Lazy loading**: Prices fetched only when needed (on-demand)
- **Background job**: Prefetch popular stocks daily
- **CDN**: Historical data can be cached on CDN for distribution
- **Compression**: API responses gzip-compressed by default

#### Q21: How are simulations optimized?
**A**:
- **Monte Carlo**: Run in background job, results cached
- **Vectorization**: NumPy for fast matrix operations
- **Pagination**: Large result sets paginated to avoid memory overload
- **Example**: 10,000 simulations take ~2-5 seconds, result stored in cache

---

### **Development & Deployment**

#### Q22: How do I add a new game?
**A**:
1. Create simulator: `backend/app/services/simulation/my_game_simulator.py`
2. Create DB models: Add to `backend/app/models/finance.py`
3. Create API routes: `backend/app/api/v1/games.py` (add endpoints)
4. Create frontend page: `frontend/src/app/(dashboard)/games/my-game/page.tsx`
5. Register in router: Add to `backend/app/main.py`
6. Test with API docs: `http://localhost:8000/docs`

#### Q23: How do I add a new analytics feature?
**A**:
1. Create service: `backend/app/services/analytics/my_feature.py`
2. Add routes: Add to `backend/app/api/v1/analytics.py`
3. Create frontend component
4. Test with Swagger: `http://localhost:8000/docs`

#### Q24: How do I test the API?
**A**:
- **Interactive API docs**: Visit `http://localhost:8000/docs` (Swagger UI)
- **Alternative**: `http://localhost:8000/redoc` (ReDoc)
- **CLI**:
  ```bash
  curl -X POST http://localhost:8000/api/v1/games/sip-chronicles/create \
    -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
    -d '{"investment_type":"nifty_50"}'
  ```
- **Postman**: Import OpenAPI spec from `/openapi.json`

#### Q25: How is the app deployed?
**A**:
- **Backend**: Docker container on cloud (AWS/GCP/Azure)
  - Image built from `backend/Dockerfile`
  - Environment variables from `.env` (stored in secrets manager)
  - PostgreSQL database (managed DB service)

- **Frontend**: Deployed on Vercel or similar
  - NextJS builds to static + dynamic rendering
  - Environment: `NEXT_PUBLIC_API_URL` points to backend

- **CI/CD**: GitHub Actions
  - Run tests on push
  - Build Docker image
  - Deploy if tests pass

---

### **Security**

#### Q26: How is sensitive data protected?
**A**:
- **Passwords**: Hashed with bcrypt (salt + hash), never stored plain
- **API Keys**: Environment variables, not in code
- **JWT Tokens**: Signed with SECRET_KEY, expires in 30 mins
- **Database**: Encrypted connections (SSL), encrypted at rest (optional)
- **CORS**: Restricted to specified origins (production only)
- **SQL Injection**: Prevented by SQLAlchemy ORM (parameterized queries)
- **XSS**: React auto-escapes content (no innerHTML)

#### Q27: How can I reset the database?
**A**:
```bash
# Drop and recreate (development only!)
cd backend
python -c "from app.models.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"

# Seed demo data
python seed_demo.py
```

#### Q28: How do I add an API key for external services?
**A**:
1. Add to `.env`:
   ```
   FINNHUB_API_KEY=your_key_here
   ```
2. Access in code:
   ```python
   from app.core.config import settings
   api_key = settings.FINNHUB_API_KEY
   ```
3. Add to `.gitignore` to prevent committing secrets

---

### **Troubleshooting**

#### Q29: Backend won't start - "Port 8000 already in use"
**A**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python -m uvicorn app.main:app --reload --port 8001
```

#### Q30: Frontend can't connect to backend
**A**:
- Check backend is running: `http://localhost:8000` should show JSON
- Check CORS settings in `backend/app/core/config.py` includes frontend URL
- Check `NEXT_PUBLIC_API_URL` environment variable in frontend
- Check network tab in browser DevTools for failed requests
- Common fix: Restart both frontend and backend

#### Q31: Database migration failed
**A**:
```bash
# Check current schema
python -c "from app.models.database import engine; print(engine.table_names())"

# Reset and recreate (dev only)
dropdb moneymindset
createdb moneymindset
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### Q32: Market data not loading
**A**:
- Check internet connection
- Check yFinance working: `python -c "import yfinance as yf; print(yf.Ticker('RELIANCE.NS').info)"`
- Check Finnhub API key is valid (if using Finnhub)
- Fallback to mock data for testing

#### Q33: Game session lost after refresh
**A**:
- Session ID should be in database and URL
- If lost: User can view previous sessions in game history
- Future: Implement browser local storage backup of current session

---

## API Request Examples

### Create Game Session
```bash
# SIP Chronicles
POST /api/v1/games/sip-chronicles/create
{
  "investment_type": "nifty_50",
  "initial_sip": 500
}

# Paper Trading
POST /api/v1/games/paper-trading/create
{
  "market": "india",
  "starting_capital": 100000
}
```

### Make Game Decision
```bash
POST /api/v1/games/sip-chronicles/{session_id}/decision
{
  "month": 120,
  "interruption_type": "market_crash",
  "decision": "continue"
}
```

### Classify Transactions
```bash
POST /api/v1/analytics/classify/transaction
{
  "description": "Starbucks Coffee Shop",
  "amount": 450
}

# Response
{
  "success": true,
  "data": {
    "category": "Food & Dining",
    "confidence": 0.95
  }
}
```

### Simulate Investment
```bash
POST /api/v1/analytics/simulate/investment
{
  "initial_amount": 100000,
  "monthly_contribution": 5000,
  "years": 20,
  "asset_class": "balanced",
  "num_simulations": 1000
}

# Response
{
  "success": true,
  "data": {
    "p10": 1000000,      # 10% chance of reaching this
    "p50": 2500000,      # 50% chance (median)
    "p90": 5000000,      # 90% chance
    "mean": 2650000,
    "std_dev": 1200000
  }
}
```

---

## Key Concepts

### **Gamification**
- **XP**: Points earned from wise decisions in games
- **Badges**: Achievements unlocked (e.g., "Emergency Fund Hero", "Compound Interest Master")
- **Levels**: Progression based on total XP (Level 1-50)
- **Leaderboard**: Compare scores with friends/global community

### **Interruptions**
- Scheduled events in games that test decision-making
- Can increase/decrease wealth based on player choice
- Example: Market crash can be catastrophic (sell everything) or opportunity (buy more)

### **Monte Carlo Simulation**
- Statistical method to model uncertainty
- Generates many random scenarios to show probability distribution
- Used for: Investment forecasts, market simulations

### **Compound Interest**
- The "8th wonder of the world" (Einstein quote)
- Formula: A = P(1 + r)^t
- Key: Start early, stay invested, consistent contributions
- SIP game shows: ₹500/month × 38 years = ₹2.5M+ (not ₹500×12×38 = ₹228k)

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **yFinance**: https://github.com/ranaroussi/yfinance
- **React Query**: https://tanstack.com/query/latest

---

**Last Updated**: March 2026
**Version**: 1.0
