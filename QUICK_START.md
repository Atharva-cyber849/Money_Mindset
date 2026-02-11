# Quick Start Guide - Money Mindset Developer Reference

## 🚀 Quick Commands

### Start Development Servers
```bash
# Backend (FastAPI)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend (Next.js)
cd frontend
npm run dev
# Opens at http://localhost:3000
```

### Run Tests
```bash
# Coffee Shop Integration Tests
python tests/test_coffee_shop_integration.py

# All Tests (when implemented)
pytest tests/
```

---

## 📂 Project Structure - Quick Reference

```
Money Mindset/
├── frontend/src/app/simulations/
│   ├── coffee-shop-effect/page.tsx       # ✅ 557 lines
│   ├── paycheck-game/page.tsx            # ✅ 700 lines (NEW)
│   ├── budget-builder/page.tsx           # ✅ 850 lines (NEW)
│   ├── emergency-fund/page.tsx           # ✅ 900 lines (NEW)
│   ├── car-payment/page.tsx              # ✅ 800 lines (NEW)
│   ├── credit-card-debt/page.tsx         # ✅ 850 lines (NEW)
│   └── compound-interest/page.tsx        # ✅ 778 lines
│
├── backend/app/
│   ├── api/v1/simulations.py             # ✅ 15 endpoints
│   ├── services/simulation/              # ✅ 7 engines
│   │   ├── coffee_shop_simulator.py
│   │   ├── paycheck_game.py
│   │   ├── budget_builder.py
│   │   ├── emergency_fund.py
│   │   └── ... (others)
│   └── services/gamification/            # ✅ Complete system
│       ├── progress_tracker.py
│       ├── badge_system.py
│       ├── achievement_engine.py
│       └── gamification_service.py
│
└── docs/                                 # ✅ 4 docs
    ├── FRONTEND_SIMULATIONS_COMPLETE.md
    ├── API_DOCUMENTATION.md
    ├── IMPLEMENTATION_SUMMARY.md
    └── PROJECT_ROADMAP.md
```

---

## 🔌 API Endpoints - Quick Reference

### Base URL
```
http://localhost:8000/api/v1/simulations
```

### Headers (All Requests)
```json
{
  "Authorization": "Bearer <jwt_token>",
  "Content-Type": "application/json"
}
```

### Quick Test (Coffee Shop)
```bash
TOKEN="your_token_here"

# Calculate
curl -X POST http://localhost:8000/api/v1/simulations/coffee-shop-effect \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"daily_cost": 5.50, "days_per_week": 5, "years": 30}'

# Complete
curl -X POST http://localhost:8000/api/v1/simulations/coffee-shop-effect/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_score": 85, "perfect_score": false}'
```

---

## 🎨 Frontend Components - Quick Reference

### Standard 4-Step Pattern
Every simulation follows this structure:

```tsx
// Step 1: Setup/Intro
function StepSetup({ onNext }: { onNext: (data) => void }) { ... }

// Step 2: Main Calculation/Interaction
function StepCalculate({ data, onNext }: { ... }) { ... }

// Step 3: Results/Visualization
function StepResults({ data, onNext }: { ... }) { ... }

// Step 4: Complete/Rewards
function StepComplete() { ... }

// Main Component
export default function SimulationPage() {
  const [currentStep, setCurrentStep] = useState(1)
  // ... manage state and step navigation
}
```

### Common Imports
```tsx
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Slider } from '@/components/ui/Slider'
import { formatCurrency } from '@/lib/utils'
import { BarChart, Bar, PieChart, Pie, AreaChart, Area, ... } from 'recharts'
```

---

## 📊 Chart Types - Quick Reference

### Area Chart (Compound Growth)
```tsx
<ResponsiveContainer width="100%" height={300}>
  <AreaChart data={data}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="year" />
    <YAxis tickFormatter={(value) => formatCurrency(value)} />
    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
    <Area type="monotone" dataKey="spending" stroke="#ef4444" fill="url(#colorSpending)" />
    <Area type="monotone" dataKey="invested" stroke="#10b981" fill="url(#colorInvested)" />
  </AreaChart>
</ResponsiveContainer>
```

### Bar Chart (Comparisons)
```tsx
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={data}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="name" />
    <YAxis tickFormatter={(value) => `$${value}`} />
    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
    <Bar dataKey="amount" fill="#3b82f6" />
  </BarChart>
</ResponsiveContainer>
```

### Pie Chart (Distribution)
```tsx
<ResponsiveContainer width="100%" height={300}>
  <PieChart>
    <Pie
      data={data}
      cx="50%"
      cy="50%"
      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
      outerRadius={80}
      dataKey="value"
    >
      {data.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={entry.color} />
      ))}
    </Pie>
    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
  </PieChart>
</ResponsiveContainer>
```

---

## 🎮 Gamification - Quick Reference

### Complete Simulation (Frontend)
```tsx
const handleComplete = async () => {
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await fetch('/api/v1/simulations/coffee-shop-effect/complete', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_score: calculateScore(),
        perfect_score: score >= 95
      })
    })
    
    const data = await response.json()
    
    // Display XP
    showNotification(`+${data.xp_earned.amount} XP!`)
    
    // Display badges
    data.badges_earned.forEach(badge => showBadge(badge))
    
    // Handle level up
    if (data.level_up) showLevelUpModal(data.level_up)
    
  } catch (error) {
    console.error('Error:', error)
  }
}
```

### Response Format
```json
{
  "xp_earned": { "amount": 120, "reason": "Base 100 XP + bonuses" },
  "level_up": { "old_level": "financial_newbie", "new_level": "money_student" },
  "badges_earned": [{ "name": "First Steps", "icon": "👣" }],
  "new_unlocks": [{ "type": "simulation", "id": "paycheck_game" }],
  "progress": { "current_xp": 120, "xp_to_next_level": 880 }
}
```

---

## 🐛 Common Issues & Solutions

### Issue: Charts not rendering
**Solution:** Ensure ResponsiveContainer has explicit height
```tsx
<ResponsiveContainer width="100%" height={300}> // ← Add height!
```

### Issue: Slider not updating calculations
**Solution:** Add slider value to useEffect dependencies
```tsx
useEffect(() => {
  // recalculate...
}, [sliderValue]) // ← Add dependency
```

### Issue: API CORS errors
**Solution:** Add CORS middleware in FastAPI
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: 401 Unauthorized
**Solution:** Check JWT token is being sent
```tsx
headers: {
  'Authorization': `Bearer ${token}`, // ← Ensure token exists
}
```

---

## 📝 Code Snippets - Copy/Paste

### Progress Bar
```tsx
<div className="h-2 bg-gray-300 rounded-full overflow-hidden">
  <div
    className="h-full bg-blue-600 transition-all duration-500"
    style={{ width: `${(currentStep / 4) * 100}%` }}
  />
</div>
```

### Step Navigation
```tsx
const [currentStep, setCurrentStep] = useState(1)

<AnimatePresence mode="wait">
  {currentStep === 1 && <StepOne key="one" onNext={() => setCurrentStep(2)} />}
  {currentStep === 2 && <StepTwo key="two" onNext={() => setCurrentStep(3)} />}
</AnimatePresence>
```

### Loading State
```tsx
const [loading, setLoading] = useState(false)

{loading ? (
  <div className="animate-spin">⏳</div>
) : (
  <Button onClick={handleSubmit}>Calculate</Button>
)}
```

### Error Handling
```tsx
const [error, setError] = useState<string | null>(null)

{error && (
  <div className="p-4 bg-red-50 text-red-600 rounded">
    {error}
  </div>
)}
```

---

## 🎯 Testing Checklist

Before committing:
- [ ] Run `npm run build` (frontend) - no errors
- [ ] Test on mobile viewport (Chrome DevTools)
- [ ] Check all sliders work
- [ ] Verify charts render
- [ ] Test step navigation
- [ ] Check console for errors
- [ ] Test API endpoints (Postman)

---

## 📦 Dependencies

### Frontend
```json
{
  "react": "^18.2.0",
  "next": "^14.0.0",
  "framer-motion": "^10.0.0",
  "recharts": "^2.10.0",
  "tailwindcss": "^3.3.0"
}
```

### Backend
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-jose[cryptography]==3.3.0
```

---

## 🚀 Deployment Quick Steps

1. **Build frontend:**
   ```bash
   cd frontend && npm run build
   ```

2. **Start backend:**
   ```bash
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Environment variables:**
   ```bash
   # .env
   DATABASE_URL=postgresql://...
   SECRET_KEY=your_secret_key
   FRONTEND_URL=https://yourdomain.com
   ```

---

## 📚 Documentation Files

- **API_DOCUMENTATION.md** - All API endpoints with examples
- **FRONTEND_SIMULATIONS_COMPLETE.md** - Frontend details
- **IMPLEMENTATION_SUMMARY.md** - Complete project summary
- **PROJECT_ROADMAP.md** - Visual roadmap and next steps
- **QUICK_START.md** - This file

---

## 💡 Pro Tips

1. **Hot Reload:** Both frontend and backend support hot reload - changes reflect immediately
2. **Debugging:** Use browser DevTools Network tab to inspect API calls
3. **State Management:** Keep simulation state in parent component, pass to steps
4. **Performance:** Memoize expensive calculations with `useMemo`
5. **Accessibility:** Add aria-labels to sliders and buttons
6. **Mobile First:** Test on mobile early, not as an afterthought

---

## 🆘 Need Help?

1. Check relevant documentation file
2. Review existing simulation code (Coffee Shop is well-documented)
3. Check backend simulation engines for calculation logic
4. Review API endpoint responses in Postman
5. Use browser DevTools console for frontend errors

---

**Last Updated:** February 7, 2026
**Status:** ✅ All 7 Simulations Complete
**Next:** Database Integration + Authentication
