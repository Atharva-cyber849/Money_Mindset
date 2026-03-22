# 💹 Paper Trading Platform

**Learn stock trading with virtual money. Real prices, zero risk.**

## Overview

Paper Trading is a complete **stock market simulation game** integrated into the Money Mindset platform. Users can practice trading in Indian markets (NSE/BSE) or US markets (S&P 500) with virtual capital, learning portfolio diversification, market timing, and risk management.

### Key Features

✅ **Dual-Market Support** - Trade Indian stocks, US stocks, or both
✅ **Real Market Data** - Live prices via yfinance + historical backtesting
✅ **Multiple Strategies** - Portfolio Builder, Day Trader, Value Investor, ETF Investor
✅ **Multi-Dimensional Scoring** - 5-part assessment (wealth, diversification, risk, timing, adherence)
✅ **Historical Backtesting** - Replay past market periods (2020-2024 available)
✅ **Educational Focus** - Teaches real-world trading principles

---

## Architecture

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI + SQLAlchemy + PostgreSQL |
| **Frontend** | Next.js 14 + React + Tailwind CSS |
| **Market Data** | yfinance (real) + mock data (fallback) |
| **News** | NewsAPI + Finnhub (optional) |

### System Design

```
┌─────────────────────────────────────┐
│   Frontend (React/Next.js)          │
│  - Setup screen                     │
│  - Game loop (trade execution)      │
│  - Results page                     │
└──────────────┬──────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│   API Layer (FastAPI)               │
│  - /paper-trading/create            │
│  - /paper-trading/{id}/trade        │
│  - /paper-trading/{id}/complete     │
└──────────────┬──────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│   Business Logic                    │
│  - PaperTradingSimulator            │
│  - Portfolio calculations           │
│  - Scoring engine                   │
│  - Market events                    │
└──────────────┬──────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│   Data Layer                        │
│  - yfinance (real prices)           │
│  - Mock prices (fallback)           │
│  - PostgreSQL (sessions, trades)    │
└──────────────────────────────────────┘
```

---

## Getting Started

### 1. Installation

```bash
# Clone repo (if not already)
git clone <repo>
cd Money\ Mindset

# Backend setup
cd backend/
pip install -r requirements.txt

# Frontend setup
cd ../frontend/
npm install
```

### 2. Run Application

```bash
# Terminal 1: Backend
cd backend/
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend/
npm run dev
```

Visit: `http://localhost:3000/games/paper-trading`

### 3. First Game

1. **Choose Market**: India / US / Both
2. **Pick Strategy**: Portfolio Builder, Day Trader, etc.
3. **Set Capital**: ₹50K-₹10L (India) or $1K-$100K (US)
4. **Pick Period**: Live market or historical dates
5. **Start Trading**
   - Search stocks (RELIANCE.NS, TCS.NS, AAPL, MSFT, etc.)
   - Enter quantity and price
   - Click BUY/SELL
6. **Complete Session** and view scores

---

## Game Mechanics

### Trade Execution

```
User selects: RELIANCE.NS, Qty=10, Price=₹2,850
Commission: 0.1% = ₹28.50
Total cost: ₹28,528.50
```

### Portfolio Calculation

```
Entry: RELIANCE.NS 10 @ ₹2,850 = ₹28,500
Current: RELIANCE.NS 10 @ ₹2,900 = ₹29,000
P&L: +₹500 (+1.75%)
```

### Scoring System (0-100)

| Component | Max | Criteria |
|-----------|-----|----------|
| **Portfolio Score** | 30 | Wealth vs initial capital |
| **Diversification** | 25 | Sector balance, allocation spread |
| **Risk-Adjusted** | 20 | Sharpe ratio, max drawdown |
| **Timing** | 15 | Win rate on profitable trades |
| **Adherence** | 10 | Consistency with strategy choice |

Example: Good diversified portfolio builder
```
Portfolio: 25/30 (80% return)
Diversification: 23/25 (5 sectors)
Risk-Adjusted: 18/20 (good Sharpe)
Timing: 12/15 (80% win rate)
Adherence: 10/10 (consistent)
━━━━━━━━━━━━━━━━━
Total: 88/100 (Expert)
```

### Market Events

During gameplay, random market events occur:
- **Market Crash**: -5% to -15% market-wide
- **Earnings Season**: Sector-specific volatility
- **Fed Decision**: ±1-2% US market impact
- **RBI Policy**: ±2-3% India market impact
- **Sector Rotation**: Cap size rotation

---

## Supported Markets

### Indian Stocks (NSE/BSE)

**NIFTY 50 Sample:**
- Reliance Industries (RELIANCE.NS)
- Tata Consultancy Services (TCS.NS)
- Infosys (INFY.NS)
- Wipro (WIPRO.NS)
- HDFC Bank (HDFCBANK.NS)
- ICICI Bank (ICICIBANK.NS)
- Maruti Suzuki (MARUTI.NS)
- State Bank of India (SBIN.NS)
- SBI Cards (SBICARD.NS)
- Bharti Airtel (BHARTIARTL.NS)

**Indices:**
- NIFTY 50 (^NSEI)
- SENSEX (^BSESN)
- NIFTY IT (^CNXIT)
- NIFTY BANK (^CNXBN)

### US Stocks (S&P 500)

**Major Stocks:**
- Apple (AAPL)
- Microsoft (MSFT)
- Alphabet (GOOGL)
- Amazon (AMZN)
- Meta (META)
- NVIDIA (NVDA)
- Tesla (TSLA)
- JPMorgan Chase (JPM)
- Visa (V)
- Johnson & Johnson (JNJ)

**Indices:**
- S&P 500 (SPY)
- NASDAQ 100 (QQQ)
- Dow Jones (DIA)
- Russell 2000 (IWM)

---

## Data Sources

### Real-Time Prices

**Primary:** yfinance
- ✅ Free access to all NSE/BSE stocks
- ✅ Free access to all US stocks
- ✅ 20+ years of historical data
- ⚠️ Unofficial (scrapes Yahoo Finance)
- ⚠️ May break occasionally

**Fallback:** Mock prices
- ✅ Guaranteed to work
- ⚠️ Not real market data

### Historical Data

**For Backtesting:**
- 5-year daily OHLCV data available
- Pre-fetch with `python scripts/prefetch_data.py`
- Stored as static JSON (zero API dependency)

### News Events

**Optional Integration:**
- NewsAPI: 100 requests/day free
- Finnhub: 60 requests/min free
- Used for market event triggers

---

## API Endpoints

### Sessions

| Endpoint | Method | Description |
|----------|--------|------------|
| `/paper-trading/create` | POST | Start new session |
| `/paper-trading/{id}` | GET | Get session details |
| `/paper-trading/{id}/complete` | POST | Finish & calculate scores |
| `/paper-trading/user/sessions` | GET | List user's sessions |

### Trading

| Endpoint | Method | Description |
|----------|--------|------------|
| `/paper-trading/{id}/trade` | POST | Execute BUY/SELL |
| `/paper-trading/{id}/holdings` | GET | View current holdings |
| `/paper-trading/{id}/history` | GET | Trade history |

### Market Data

| Endpoint | Method | Description |
|----------|--------|------------|
| `/market/indices?market=india\|us\|both` | GET | Get indices |
| `/market/combined?market=india\|us\|both` | GET | Indices + news |

---

## File Structure

```
Money Mindset/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── games.py (7 new endpoints)
│   │   │   └── market.py (updated for dual-market)
│   │   ├── models/
│   │   │   └── finance.py (4 new models)
│   │   ├── services/
│   │   │   ├── market_data_service.py (enhanced)
│   │   │   ├── ai_analysis.py (asset classes + Monte Carlo)
│   │   │   └── simulation/
│   │   │       └── paper_trading_simulator.py (NEW - 650 lines)
│   │   └── main.py
│   ├── scripts/
│   │   └── prefetch_data.py (NEW - data pre-fetcher)
│   └── requirements.txt (updated)
│
├── frontend/
│   └── src/app/(dashboard)/games/
│       └── paper-trading/
│           ├── page.tsx (NEW - 450 lines)
│           └── results/
│               └── page.tsx (NEW - 150 lines)
│
└── TESTING_GUIDE.md (NEW - comprehensive testing)
```

---

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for:
- End-to-end test workflows
- API testing with curl
- Performance benchmarks
- Validation checklist
- Common issues & fixes
- Load testing guide

Quick test:
```bash
# Run backend tests
cd backend/
pytest

# Run frontend tests
cd frontend/
npm run test
```

---

## Production Deployment

### Pre-flight

1. Ensure `yfinance` in `requirements.txt` ✅
2. Run database migrations
3. Set environment variables (.env)
4. Run data pre-fetching script (optional)

### Environment Variables

```bash
# .env
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ANTHROPIC_API_KEY=...
news_api_key=...  # Optional
finhub_api_key=... # Optional
```

### Scale Considerations

| Metric | Target | Notes |
|--------|--------|-------|
| Concurrent Users | 1000+ | Use load balancer |
| Database | PostgreSQL | With connection pooling |
| Cache | Redis (optional) | 5-min TTL for market data |
| API Rate Limit | 1000/min | Per user or IP |

---

## Roadmap

### Phase 1 ✅ (Complete)
- ✅ Paper Trading simulator
- ✅ Dual-market support
- ✅ Multi-dimensional scoring
- ✅ Real data integration (yfinance)
- ✅ Historical backtesting

### Phase 2 (Planned)
- [ ] Advanced orders (limit, stop-loss)
- [ ] Dividend tracking
- [ ] Tax calculation
- [ ] Portfolio rebalancing suggestions
- [ ] Achievements & badges
- [ ] Leaderboards

### Phase 3 (Future)
- [ ] Mobile app
- [ ] Real brokerage integration
- [ ] News sentiment analysis
- [ ] ML-driven recommendations

---

## Support & Troubleshooting

### Common Issues

**Q: "yfinance not found"**
A: Run `pip install yfinance`

**Q: "No price data for symbol X"**
A: Fall back to mock prices will activate automatically

**Q: "Scores don't look right"**
A: See scoring algorithm in `/backend/app/services/simulation/paper_trading_simulator.py`

**Q: "Performance is slow"**
A: Check market data cache TTL, enable Redis, use pre-fetched data

### Getting Help

- Check [TESTING_GUIDE.md](TESTING_GUIDE.md)
- Review source code comments
- Run in debug mode: `DEBUG=True`
- Check logs: `tail -f backend.log`

---

## Contributing

To add new stocks:
1. Update `INDIA_STOCKS` or `US_STOCKS` in simulator
2. Test with `yfinance` to verify symbols
3. Run `scripts/prefetch_data.py` to cache data
4. Update documentation

---

## License

Part of Money Mindset platform. See root LICENSE file.

---

## Credits

**Data Sources:**
- yfinance: Historical & real-time stock data
- NewsAPI: Financial news
- Finnhub: Company insights

**Framework:**
- FastAPI: Backend framework
- Next.js 14: Frontend framework
- SQLAlchemy: ORM

---

## Quick Links

- 🎮 **Play Demo**: `/games/paper-trading`
- 📊 **Analytics**: `/analytics`
- 🔧 **Testing**: `TESTING_GUIDE.md`
- 💾 **API Docs**: `http://localhost:8000/docs`
- 📘 **Storybook**: `frontend: npm run storybook`

---

**Made with ❤️ for financial literacy**
