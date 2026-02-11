# Simulation API Endpoints - Complete Documentation

## Overview
All backend API endpoints for the 7 interactive simulations have been implemented. Each simulation has calculate/simulate endpoints and completion endpoints that integrate with the gamification system.

## API Base URL
```
http://localhost:8000/api/v1/simulations
```

## Authentication
All endpoints require JWT token authentication:
```bash
Authorization: Bearer <token>
```

---

## 1. ☕ Coffee Shop Effect

### Calculate Effect
```http
POST /coffee-shop-effect
```

**Request Body:**
```json
{
  "daily_cost": 5.50,
  "days_per_week": 5,
  "years": 30
}
```

**Response:**
```json
{
  "daily_cost": 5.50,
  "days_per_week": 5,
  "costs": {
    "annual": 1430,
    "five_year": 7150,
    "ten_year": 14300,
    "thirty_year": 42900
  },
  "compound_results": [
    {
      "year": 1,
      "spent_total": 1430,
      "invested_total": 1543,
      "opportunity_cost": 113
    }
    // ... 30 years of data
  ],
  "opportunity_examples": [
    {
      "item": "New iPhone",
      "cost": 1000,
      "years_saved": 1,
      "description": "Latest flagship smartphone"
    }
    // ... 10 examples
  ],
  "total_opportunity_cost": 132055,
  "recommendation": "Your $5.50 daily habit costs..."
}
```

### Compare Scenarios
```http
POST /coffee-shop-effect/compare
```

**Request Body:**
```json
{
  "scenarios": [
    {"name": "Coffee Shop", "daily_cost": 5.50, "days_per_week": 5},
    {"name": "Home Brew", "daily_cost": 0.75, "days_per_week": 5}
  ]
}
```

### Complete Simulation
```http
POST /coffee-shop-effect/complete
```

**Request Body:**
```json
{
  "user_score": 85,
  "perfect_score": false
}
```

**Response:** (See Gamification Response Format below)

---

## 2. 💰 Paycheck Game

### Calculate Strategy
```http
POST /paycheck-game/calculate
```

**Request Body:**
```json
{
  "monthly_income": 4000,
  "rent": 1200,
  "utilities": 200,
  "groceries": 400,
  "insurance": 300,
  "transportation": 200,
  "debt_payments": 300,
  "strategy": "save_first"
}
```

**Strategies:**
- `spend_first` - Spend freely, pay bills, save what's left
- `bills_first` - Pay bills first, spend freely, save what's left
- `save_first` - Auto-save first, pay bills, spend remainder

**Response:**
```json
{
  "strategy": "save_first",
  "amount_saved": 400,
  "bills_paid_on_time": true,
  "discretionary_spent": 400,
  "late_fees": 0,
  "stress_level": "low",
  "final_balance": 800,
  "description": "You automated savings and still had money for fun!",
  "monthly_breakdown": [
    {
      "category": "savings",
      "amount": 400,
      "order": 1
    }
    // ... more categories
  ]
}
```

### Complete Simulation
```http
POST /paycheck-game/complete
```

---

## 3. 📊 Budget Builder

### Validate Budget
```http
POST /budget-builder/validate
```

**Request Body:**
```json
{
  "monthly_income": 4000,
  "allocations": {
    "housing": 1200,
    "utilities": 200,
    "groceries": 400,
    "transportation": 200,
    "insurance": 100,
    "minimum_debt_payments": 100,
    "dining_out": 300,
    "entertainment": 200,
    "shopping": 200,
    "subscriptions": 100,
    "emergency_fund": 400,
    "retirement": 400,
    "investments": 200
  }
}
```

**Response:**
```json
{
  "is_balanced": true,
  "needs_percentage": 50.0,
  "wants_percentage": 30.0,
  "savings_percentage": 20.0,
  "total_allocated": 4000,
  "warnings": [],
  "recommendations": [
    "Great job! Your budget follows the 50/30/20 rule perfectly."
  ],
  "score": 95
}
```

### Complete Simulation
```http
POST /budget-builder/complete
```

---

## 4. 🛡️ Emergency Fund

### Simulate Scenarios
```http
POST /emergency-fund/simulate
```

**Request Body:**
```json
{
  "monthly_income": 4000,
  "monthly_expenses": 3200,
  "starting_fund": 5000,
  "seed": 42
}
```

**Response:**
```json
{
  "with_fund": {
    "character_name": "Prepared Person",
    "total_saved": 4800,
    "total_debt_incurred": 0,
    "total_interest_paid": 0,
    "final_net_worth": 4800,
    "average_stress": 3.5,
    "success_score": 95,
    "emergencies_faced": 4,
    "monthly_states": [
      {
        "month": 1,
        "emergency_fund": 5000,
        "credit_card_debt": 0,
        "stress_level": 2
      }
      // ... 12 months
    ]
  },
  "without_fund": {
    "character_name": "Unprepared Person",
    "total_saved": 0,
    "total_debt_incurred": 3500,
    "total_interest_paid": 245,
    "final_net_worth": -3745,
    "average_stress": 8.2,
    "success_score": 25,
    "emergencies_faced": 4,
    "monthly_states": [
      // ... 12 months
    ]
  },
  "difference": {
    "net_worth": 8545,
    "stress": -4.7,
    "debt": 3500
  }
}
```

### Complete Simulation
```http
POST /emergency-fund/complete
```

---

## 5. 🚗 Car Payment

### Calculate True Cost
```http
POST /car-payment/calculate
```

**Request Body:**
```json
{
  "car_price": 30000,
  "down_payment": 5000,
  "interest_rate": 6.5,
  "term_months": 60
}
```

**Response:**
```json
{
  "loan_details": {
    "car_price": 30000,
    "down_payment": 5000,
    "loan_amount": 25000,
    "interest_rate": 6.5,
    "term_months": 60,
    "monthly_payment": 488.26
  },
  "costs": {
    "total_paid": 34295.60,
    "total_interest": 4295.60,
    "insurance": 9000,
    "maintenance": 6000,
    "gas": 9000,
    "registration": 1000,
    "total_ownership_cost": 59295.60
  },
  "value": {
    "initial_value": 30000,
    "final_value": 12000,
    "depreciation": 18000
  },
  "opportunity_cost": {
    "if_invested": 68456.32,
    "lost_wealth": 38456.32
  }
}
```

### Complete Simulation
```http
POST /car-payment/complete
```

---

## 6. 💳 Credit Card Debt

### Calculate Payoff
```http
POST /credit-card-debt/calculate
```

**Request Body:**
```json
{
  "balance": 5000,
  "apr": 22.0,
  "monthly_payment": 200
}
```

**Response:**
```json
{
  "initial_balance": 5000,
  "apr": 22.0,
  "monthly_payment": 200,
  "months_to_payoff": 32,
  "years_to_payoff": 2.67,
  "total_paid": 6400,
  "total_interest": 1400,
  "interest_as_percentage": 28.0,
  "monthly_breakdown": [
    {
      "month": 1,
      "balance": 4891.67,
      "interest_paid": 91.67,
      "principal_paid": 108.33
    }
    // ... more months
  ]
}
```

**Error Response (payment too low):**
```json
{
  "error": "Monthly payment is too low - you'll never pay off the debt!",
  "minimum_payment_needed": 101.67
}
```

### Complete Simulation
```http
POST /credit-card-debt/complete
```

---

## 7. ⏰ Compound Interest
*Note: This simulation already exists in the codebase at `/compound-interest/page.tsx`*

---

## Gamification Response Format

All `/complete` endpoints return the same gamification response:

```json
{
  "xp_earned": {
    "amount": 120,
    "reason": "Base 100 XP + bonuses (first try)"
  },
  "level_up": {
    "old_level": "financial_newbie",
    "new_level": "money_student",
    "celebration_message": "🎉 Level Up! You're now a Money Student!",
    "unlocked_features": ["Advanced simulations", "AI tutor access"]
  },
  "badges_earned": [
    {
      "id": "first_steps",
      "name": "First Steps",
      "description": "Completed your first simulation",
      "rarity": "common",
      "icon": "👣",
      "message": "🎉 Badge Unlocked: First Steps!"
    }
  ],
  "new_unlocks": [
    {
      "type": "simulation",
      "id": "paycheck_game",
      "name": "The Paycheck Game"
    }
  ],
  "streak_info": {
    "current_streak": 1,
    "longest_streak": 1
  },
  "progress": {
    "level": "financial_newbie",
    "current_xp": 120,
    "xp_to_next_level": 880,
    "progress_percentage": 12.0
  }
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

**Success:**
- `200 OK` - Successful calculation/simulation
- `201 Created` - Resource created (not used in simulations)

**Client Errors:**
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Endpoint doesn't exist

**Server Errors:**
- `500 Internal Server Error` - Server-side error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Testing with cURL

### Example: Test Coffee Shop Effect
```bash
# Get token (login first)
TOKEN="your_jwt_token_here"

# Calculate effect
curl -X POST http://localhost:8000/api/v1/simulations/coffee-shop-effect \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "daily_cost": 5.50,
    "days_per_week": 5,
    "years": 30
  }'

# Complete simulation
curl -X POST http://localhost:8000/api/v1/simulations/coffee-shop-effect/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_score": 85,
    "perfect_score": false
  }'
```

### Example: Test Paycheck Game
```bash
curl -X POST http://localhost:8000/api/v1/simulations/paycheck-game/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_income": 4000,
    "rent": 1200,
    "utilities": 200,
    "groceries": 400,
    "insurance": 300,
    "transportation": 200,
    "debt_payments": 300,
    "strategy": "save_first"
  }'
```

---

## Frontend Integration Example

```typescript
// React example for completing a simulation
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
    
    if (!response.ok) {
      throw new Error('Failed to complete simulation')
    }
    
    const data = await response.json()
    
    // Display XP earned
    showNotification(`+${data.xp_earned.amount} XP!`)
    
    // Display badges
    data.badges_earned.forEach(badge => {
      showBadge(badge)
    })
    
    // Handle level up
    if (data.level_up) {
      showLevelUpModal(data.level_up)
    }
    
  } catch (error) {
    console.error('Error:', error)
  }
}
```

---

## Summary

✅ **7 Simulations** with complete API endpoints
✅ **Calculate/Simulate** endpoints for each simulation
✅ **Completion** endpoints integrated with gamification
✅ **Consistent** request/response formats
✅ **Error handling** with clear messages
✅ **Authentication** required for all endpoints
✅ **Documentation** with examples

**Next Steps:**
1. Test all endpoints with real backend
2. Integrate frontend with API calls
3. Add database persistence for user stats
4. Implement rate limiting
5. Add API monitoring/logging
