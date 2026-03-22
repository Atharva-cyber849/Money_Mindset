# Paper Trading Platform - Testing & Validation Guide

## Quick Start

### 1. Backend Setup
```bash
cd backend/
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend/
npm install
npm run dev
```

Visit: `http://localhost:3000/dashboard/games/paper-trading`

---

## End-to-End Test Workflow

### Test Case 1: India Market Trading (Real Data)

**Setup:**
1. Navigate to `/games/paper-trading`
2. Select: Market = "India", Strategy = "Portfolio Builder", Capital = ₹100,000
3. Click "Start Trading"

**Expected:**
- ✅ Session created successfully
- ✅ Portfolio shows ₹100,000 cash
- ✅ Holdings table empty

**Trading:**
1. Enter symbol: `RELIANCE.NS`
2. Quantity: 10
3. Enter current price: (fetch from yfinance or use mock)
4. Click BUY

**Expected:**
- ✅ Trade executes with commission (~0.1%)
- ✅ Cash decreases by (qty × price + commission)
- ✅ Holdings shows RELIANCE.NS
- ✅ Entry price recorded

**Complete Session:**
1. Click "Complete Session"
2. View Results

**Expected:**
- ✅ Final wealth calculated
- ✅ P&L displayed (may be negative if price dropped)
- ✅ 5-part score breakdown visible
- ✅ Scores sum to 100 or less

---

### Test Case 2: US Market Trading (Mock Data)

**Setup:**
1. Select: Market = "US", Strategy = "Day Trader", Capital = $50,000
2. Start game

**Trading:**
```
Symbol: AAPL
Quantity: 5
Price: 180.00
Side: BUY
```

**Expected:**
- ✅ Trade succeeds
- ✅ Total: $900 + ~$0.90 commission
- ✅ Cash remaining: $49,099

---

### Test Case 3: Historical Backtesting

**Setup:**
1. Select: Market = "India", Historical = checked
2. Start date: 2023-01-01, End date: 2023-12-31
3. Start game

**Expected:**
- ✅ Session created with historical period
- ✅ Can trade with historical prices

---

## API Testing

### Create Session
```bash
curl -X POST http://localhost:8000/api/v1/paper-trading/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "market": "india",
    "strategy": "portfolio_builder",
    "initial_capital": 500000,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid-string",
  "market": "india",
  "strategy": "portfolio_builder",
  "initial_capital": 500000,
  "status": "active"
}
```

### Execute Trade
```bash
curl -X POST http://localhost:8000/api/v1/paper-trading/{session_id}/trade \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "symbol": "RELIANCE.NS",
    "quantity": 10,
    "price": 2850.50,
    "side": "BUY"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "trade": {
    "trade_id": "uuid",
    "symbol": "RELIANCE.NS",
    "quantity": 10,
    "price": 2850.50,
    "total_value": 28505.00,
    "commission": 28.50,
    "cash_remaining": 471466.50
  },
  "portfolio": { ... }
}
```

### Get Session
```bash
curl http://localhost:8000/api/v1/paper-trading/{session_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Complete Session
```bash
curl -X POST http://localhost:8000/api/v1/paper-trading/{session_id}/complete \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "session_id": "uuid",
  "status": "completed",
  "final_wealth": 512500,
  "total_pnl": 12500,
  "pnl_percentage": 2.5,
  "scores": {
    "portfolio_score": 25,
    "diversification_score": 20,
    "risk_adjusted_score": 18,
    "timing_score": 12,
    "adherence_score": 10,
    "total_score": 85
  }
}
```

---

## Data Source Verification

### 1. Real-Time Prices (yfinance)
```python
import yfinance as yf

# India
nifty = yf.Ticker("^NSEI")
print(nifty.info['regularMarketPrice'])

# US
spy = yf.Ticker("SPY")
print(spy.info['regularMarketPrice'])

# Stock
reliance = yf.Ticker("RELIANCE.NS")
print(reliance.history(period="1d")["Close"].iloc[-1])
```

### 2. Historical Data (yfinance)
```python
import yfinance as yf

# 2023 data
sensex = yf.download("^BSESN", start="2023-01-01", end="2023-12-31")
print(sensex.shape)  # Should be ~250 records
```

### 3. NewsAPI Integration
```bash
curl "https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=YOUR_KEY"
```

---

## Performance Benchmarks

| Operation | Target | Actual |
|-----------|--------|--------|
| Create session | < 500ms | ? |
| Execute trade | < 1000ms | ? |
| Get holdings | < 500ms | ? |
| Complete session | < 2000ms | ? |
| Fetch historical data | < 5000ms (cached) | ? |

---

## Validation Checklist

### Backend
- [ ] Market data service returns India indices
- [ ] Market data service returns US indices
- [ ] Paper trading simulator initializes correctly
- [ ] Trade execution validates cash
- [ ] Trade execution validates shares
- [ ] Portfolio P&L calculates accurately
- [ ] Scores calculate 0-100 range
- [ ] Database models create tables
- [ ] API endpoints return 200 on success
- [ ] API endpoints return 400 on bad input
- [ ] API endpoints return 404 on missing session
- [ ] yfinance integration works
- [ ] Mock data fallback works

### Frontend
- [ ] Setup screen loads
- [ ] Market selector works
- [ ] Strategy selector works
- [ ] Capital input accepts numbers
- [ ] Historical date picker works
- [ ] Game creates session
- [ ] Portfolio displays cash
- [ ] Trade executor accepts input
- [ ] Trade confirmation modal appears
- [ ] Holdings table updates
- [ ] Results page displays scores
- [ ] Results page shows P&L
- [ ] Games hub includes Paper Trading entry
- [ ] Navigation links work

### Integration
- [ ] Frontend → API → Backend flow works
- [ ] Session persists in database
- [ ] Multiple trades in one session
- [ ] Session completion saves scores
- [ ] Results page loads completed session
- [ ] Historical backtesting works
- [ ] Real-time trading works

---

## Common Issues & Fixes

### Issue: "yfinance not found"
**Fix:**
```bash
pip install yfinance
```

### Issue: "No data returned for symbol"
**Fix:**
- Check symbol format (use `.NS` for India)
- yfinance may be blocked temporarily
- Mock data fallback should activate
- Check `/backend/.env` for API keys

### Issue: API returns 401 Unauthorized
**Fix:**
- Ensure user is logged in
- Check authentication token in request
- Verify JWT secret key in `.env`

### Issue: Portfolio calculation looks wrong
**Fix:**
- Verify commission is 0.1%
- Check entry price = weighted average
- Verify current price used for calculation
- Test with simple math: qty × price + commission

### Issue: Scores don't add up to 100
**Fix:**
- Check scoring algorithm constraints
- Max total should be 100 (30+25+20+15+10)
- Verify percentile calculations
- Test with known inputs

---

## Data Pre-fetching for Competition

Run before competition to cache all historical data:

```bash
cd backend/scripts/
python prefetch_data.py
```

This creates:
- `data/paper_trading/india_*.json` - Historical India data
- `data/paper_trading/us_*.json` - Historical US data
- `data/paper_trading/latest_prices.json` - Current prices

**Benefit:** Zero API calls during demo (100% reliable)

---

## Load Testing

Test with multiple concurrent users:

```bash
# Install locust
pip install locust

# Create loadtest.py and run
locust -f loadtest.py --host=http://localhost:8000
```

---

## Production Deployment Checklist

- [ ] `yfinance` in `requirements.txt`
- [ ] NewsAPI key in `.env`
- [ ] Database migrations run
- [ ] API tests pass
- [ ] Frontend tests pass
- [ ] Load test passes (100+ users)
- [ ] Data pre-fetching script runs successfully
- [ ] Logging configured
- [ ] Error handling verified
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Caching enabled (5-min TTL for market data)
- [ ] Database backups configured
- [ ] Monitoring setup

---

## Success Criteria

- ✅ Create session with any market/strategy
- ✅ Execute BUY and SELL trades correctly
- ✅ Portfolio calculates P&L accurately
- ✅ Scoring produces meaningful results
- ✅ Historical backtesting works
- ✅ Results page displays all scores
- ✅ All tests pass
- ✅ Load test shows acceptable performance
- ✅ No API errors during demo
- ✅ Real data (yfinance) OR mock data (fallback)

---

## Support Resources

- **yfinance docs:** https://github.com/ranaroussi/yfinance
- **NewsAPI docs:** https://newsapi.org/docs
- **FastAPI docs:** https://fastapi.tiangolo.com
- **React Hook Form:** https://react-hook-form.com

---
