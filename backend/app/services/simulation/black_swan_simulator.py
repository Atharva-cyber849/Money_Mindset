"""
Black Swan Crisis Simulation - Randomized financial crisis scenarios
Tests antifragility: wealth that thrives through chaos, not just survival
"""

import json
import random
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class CrisisType(str, Enum):
    DEMONETIZATION = "demonetization_2016"
    PANDEMIC = "covid_2020"
    IL_FS = "il_fs_2021"
    YES_BANK = "yes_bank_2021"
    CRYPTO_WINTER = "crypto_2022"
    SHADOW_BANKING = "shadow_banking_2023"
    RUPEE_CRISIS = "rupee_2024"
    # New Indian crisis scenarios
    LIQUIDITY_CRUNCH = "liquidity_crunch_2018"
    TECH_LAYOFFS = "tech_layoffs_2023"
    MONSOON_FAILURE = "monsoon_failure"
    CRUDE_OIL_SHOCK = "crude_oil_shock_2022"


class IncomeType(str, Enum):
    """Income source categories for vulnerability modeling"""
    SALARIED = "salaried"
    IT_PROFESSIONAL = "it_professional"
    AGRICULTURAL = "agricultural"
    BUSINESS = "business"
    GIG_ECONOMY = "gig_economy"


class PlayerProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    UNPREPARED = "unprepared"


class CrisisPhase(str, Enum):
    PRE_CRISIS = "pre_crisis"
    ONSET = "onset"
    TROUGH = "trough"
    RECOVERY = "recovery"


class DecisionType(str, Enum):
    REBALANCE = "rebalance"
    HOLD = "hold"
    SELL = "sell"
    BUY_DIP = "buy_dip"
    DEFAULT_LOAN = "default_loan"
    PAUSE_EMI = "pause_emi"


@dataclass
class FinancialProfile:
    """Starting financial state"""
    assets: Dict[str, float] = field(default_factory=dict)      # real_estate, equity, crypto, gold, fds, cash
    liabilities: Dict[str, float] = field(default_factory=dict)  # mortgage, personal_loans, credit_card_debt
    monthly_income: float = 50000
    monthly_expenses: float = 35000
    emergency_fund_months: float = 3

    def get_net_worth(self) -> float:
        total_assets = sum(self.assets.values())
        total_liabilities = sum(self.liabilities.values())
        return total_assets - total_liabilities

    def to_dict(self):
        return {
            "assets": self.assets,
            "liabilities": self.liabilities,
            "monthly_income": self.monthly_income,
            "monthly_expenses": self.monthly_expenses,
            "emergency_fund_months": self.emergency_fund_months,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            assets=data.get("assets", {}),
            liabilities=data.get("liabilities", {}),
            monthly_income=data.get("monthly_income", 50000),
            monthly_expenses=data.get("monthly_expenses", 35000),
            emergency_fund_months=data.get("emergency_fund_months", 3),
        )


@dataclass
class Decision:
    quarter: int
    decision_type: DecisionType
    asset_class: str
    amount: float
    outcome_wealth_change: float = 0
    optimal_action: str = ""
    cost_at_year_end: float = 0


class BlackSwanSimulator:
    """Crisis simulation with randomized profiles and antifragility scoring"""

    CRISIS_CONFIGS = {
        CrisisType.DEMONETIZATION: {
            "name": "₹2000 Demonetization",
            "year": 2016,
            "onset_quarter": 11,
            "duration_quarters": 2,
            "description": "86% of currency invalidated overnight. Cash holdings lose 86% value.",
            "asset_impacts": {
                "cash": -0.86,
                "equity": -0.10,
                "gold": 0.05,  # Benefits as hedge
                "fds": 0,
                "real_estate": 0.02,
                "crypto": 0,  # Didn't exist meaningfully yet
            },
            "income_impact_multiplier": 0.95,  # Slight income impact
            "severity": 0.7,
        },
        CrisisType.PANDEMIC: {
            "name": "COVID-19 Pandemic",
            "year": 2020,
            "onset_quarter": 11,
            "duration_quarters": 8,
            "description": "Global pandemic causes market crash and unemployment surge.",
            "asset_impacts": {
                "cash": 0,
                "equity": -0.35,
                "gold": 0.15,  # Safe haven
                "fds": 0.02,  # Rates fall
                "real_estate": -0.08,  # Rental income drop
                "crypto": -0.50,  # Speculative asset hit hard
            },
            "income_impact_multiplier": 0.65,  # 35% income loss
            "severity": 0.75,
        },
        CrisisType.IL_FS: {
            "name": "IL&FS Credit Crisis",
            "year": 2021,
            "onset_quarter": 12,
            "duration_quarters": 4,
            "description": "Shadow banking system freezes. High-yield papers worthless.",
            "asset_impacts": {
                "cash": 0,
                "equity": -0.18,
                "gold": 0.02,
                "fds": -0.30,  # Bank deposits at risk
                "real_estate": 0,
                "crypto": 0.20,  # Crypto partly benefits
            },
            "income_impact_multiplier": 0.80,  # 20% income impact
            "severity": 0.6,
        },
        CrisisType.YES_BANK: {
            "name": "Yes Bank Crisis",
            "year": 2021,
            "onset_quarter": 13,
            "duration_quarters": 3,
            "description": "Major bank faces liquidity crisis. Depositor fears escalate.",
            "asset_impacts": {
                "cash": -0.10,  # Cash in Yes Bank at risk
                "equity": -0.12,
                "gold": 0.03,
                "fds": -0.15,  # Deposits frozen temporarily
                "real_estate": 0,
                "crypto": 0.10,
            },
            "income_impact_multiplier": 0.85,
            "severity": 0.5,
        },
        CrisisType.CRYPTO_WINTER: {
            "name": "Crypto Market Collapse",
            "year": 2022,
            "onset_quarter": 14,
            "duration_quarters": 6,
            "description": "Cryptocurrency bubble bursts. Digital assets plummet.",
            "asset_impacts": {
                "cash": 0,
                "equity": -0.25,  # Contagion
                "gold": 0,
                "fds": 0.05,  # Flight to safety
                "real_estate": 0,
                "crypto": -0.80,  # Catastrophic
            },
            "income_impact_multiplier": 0.90,  # Mild income impact
            "severity": 0.5,
        },
        CrisisType.SHADOW_BANKING: {
            "name": "NBFC Cascade Crisis",
            "year": 2023,
            "onset_quarter": 15,
            "duration_quarters": 5,
            "description": "NBFC defaults trigger chain reaction. Credit freeze.",
            "asset_impacts": {
                "cash": 0,
                "equity": -0.40,
                "gold": 0.08,
                "fds": -0.25,
                "real_estate": -0.15,
                "crypto": 0.30,
            },
            "income_impact_multiplier": 0.60,  # 40% income loss
            "severity": 0.7,
        },
        CrisisType.RUPEE_CRISIS: {
            "name": "Rupee Depreciation Crisis",
            "year": 2024,
            "onset_quarter": 16,
            "duration_quarters": 4,
            "description": "Rupee crashes against dollar. Imports shock economy.",
            "asset_impacts": {
                "cash": -0.15,  # Purchasing power erodes
                "equity": -0.20,
                "gold": 0.25,  # Priced in rupees, appreciates
                "fds": -0.05,  # Real returns negative
                "real_estate": 0.10,  # Asset inflation
                "crypto": 0.40,  # Dollar hedge
            },
            "income_impact_multiplier": 0.70,  # 30% impact
            "severity": 0.6,
        },
        CrisisType.LIQUIDITY_CRUNCH: {
            "name": "Banking Liquidity Crunch",
            "year": 2018,
            "onset_quarter": 9,
            "duration_quarters": 4,
            "description": "Credit freeze: Banks restrict withdrawals, FD yields drop sharply.",
            "asset_impacts": {
                "cash": -0.20,  # Withdrawal restrictions
                "equity": -0.12,
                "gold": 0.05,
                "fds": -0.15,  # Lower yields
                "real_estate": 0,
                "crypto": 0,
            },
            "income_impact_multiplier": 0.80,  # 20% income impact
            "severity": 0.55,
            "employment_risk": 0.05,  # 5% unemployment risk
        },
        CrisisType.TECH_LAYOFFS: {
            "name": "Tech Sector Layoffs",
            "year": 2023,
            "onset_quarter": 15,
            "duration_quarters": 6,
            "description": "Major tech companies cut 25% workforce. IT sector turbulence.",
            "asset_impacts": {
                "cash": 0,
                "equity": -0.25,  # IT stocks hit
                "gold": 0.08,
                "fds": 0.02,
                "real_estate": 0,
                "crypto": 0,
            },
            "income_impact_multiplier": 0.75,  # 25% income loss impact
            "severity": 0.65,
            "employment_risk": 0.30,  # 30% unemployment for IT professionals
        },
        CrisisType.MONSOON_FAILURE: {
            "name": "Monsoon Failure - Drought",
            "year": 2015,
            "onset_quarter": 7,
            "duration_quarters": 4,
            "description": "Agricultural drought: Rural income plummets 40-80%.",
            "asset_impacts": {
                "cash": 0,
                "equity": -0.15,  # Agri exposure
                "gold": 0,
                "fds": 0,
                "real_estate": -0.08,  # Rural property
                "crypto": 0,
            },
            "income_impact_multiplier": 0.20,  # 80% income loss for agricultural
            "severity": 0.6,
            "employment_risk": 0.60,  # Severe for agricultural regions
        },
        CrisisType.CRUDE_OIL_SHOCK: {
            "name": "Crude Oil Price Spike",
            "year": 2022,
            "onset_quarter": 16,
            "duration_quarters": 3,
            "description": "Oil import costs spike: inflation rises, rupee depreciates.",
            "asset_impacts": {
                "cash": -0.03,  # Inflation erodes purchasing power
                "equity": -0.08,
                "gold": 0.10,
                "fds": -0.02,  # Real returns negative
                "real_estate": 0.05,  # Asset prices inflate
                "crypto": 0.05,
            },
            "income_impact_multiplier": 0.97,  # 3% income impact
            "severity": 0.45,
            "employment_risk": 0.08,
        },
    }

    def __init__(
        self,
        crisis_type: CrisisType,
        player_profile: PlayerProfile,
        random_seed: Optional[int] = None,
        difficulty: str = "medium",
    ):
        self.crisis_type = crisis_type
        self.player_profile = player_profile
        self.difficulty = difficulty
        self.random_seed = random_seed or random.randint(100000, 999999)

        # Set random seed for reproducibility
        random.seed(self.random_seed)

        # Game state
        self.current_quarter = 0
        self.current_phase = CrisisPhase.PRE_CRISIS
        self.decisions_made: List[Decision] = []
        self.quarterly_wealth_history: List[float] = []

        # Crisis configuration
        self.crisis_config = self.CRISIS_CONFIGS[crisis_type]

        # Adjust crisis timeline by difficulty
        if difficulty == "easy":
            self.pre_crisis_quarters = 12
            self.crisis_trough_offset = 2
        elif difficulty == "hard":
            self.pre_crisis_quarters = 6
            self.crisis_trough_offset = 1
        else:  # medium
            self.pre_crisis_quarters = 10
            self.crisis_trough_offset = 2

        # Market index tracking
        self.market_index_history = [100.0]

    def advance_quarter(self) -> Dict:
        """Progress one quarter through the game"""
        self.current_quarter += 1

        # Determine current phase
        crisis_start = self.pre_crisis_quarters
        crisis_end = crisis_start + self.crisis_config["duration_quarters"]
        trough_quarter = crisis_start + self.crisis_trough_offset

        if self.current_quarter < crisis_start:
            self.current_phase = CrisisPhase.PRE_CRISIS
        elif self.current_quarter == crisis_start:
            self.current_phase = CrisisPhase.ONSET
        elif self.current_quarter == trough_quarter:
            self.current_phase = CrisisPhase.TROUGH
        elif self.current_quarter > crisis_end:
            self.current_phase = CrisisPhase.RECOVERY
        else:
            self.current_phase = CrisisPhase.ONSET

        # Apply market movement
        market_return = self._calculate_market_return()
        new_market_index = self.market_index_history[-1] * (1 + market_return)
        self.market_index_history.append(new_market_index)

        # Apply asset impacts
        self._update_portfolio_values(market_return)

        # Calculate current wealth
        current_wealth = self.player_profile.get_net_worth()
        self.quarterly_wealth_history.append(current_wealth)

        return {
            "quarter": self.current_quarter,
            "phase": self.current_phase.value,
            "wealth": current_wealth,
            "market_index": new_market_index,
            "market_return": market_return,
            "portfolio": self.player_profile.assets.copy(),
        }

    def _calculate_market_return(self) -> float:
        """Calculate quarterly market return based on phase"""
        if self.current_phase == CrisisPhase.PRE_CRISIS:
            # Normal 2-3% quarterly return
            return random.gauss(0.02, 0.01)
        elif self.current_phase == CrisisPhase.ONSET:
            # Sharp decline at crisis onset
            severity = self.crisis_config["severity"]
            return -severity * random.uniform(0.05, 0.15)
        elif self.current_phase == CrisisPhase.TROUGH:
            # Worst phase - deep decline
            severity = self.crisis_config["severity"]
            return -severity * random.uniform(0.10, 0.20)
        elif self.current_phase == CrisisPhase.RECOVERY:
            # Recovery with volatility
            return random.gauss(0.01, 0.02)
        return 0

    def _update_portfolio_values(self, market_return: float) -> None:
        """Update asset values based on market return and crisis impacts"""
        if self.current_phase == CrisisPhase.PRE_CRISIS:
            # Pre-crisis: normal market returns
            for asset in self.player_profile.assets:
                self.player_profile.assets[asset] *= (1 + market_return * 0.8)
        else:
            # Crisis period: apply specific asset impacts
            impacts = self.crisis_config["asset_impacts"]
            for asset, value in self.player_profile.assets.items():
                if asset in impacts:
                    impact = impacts.get(asset, 0)
                    # Crisis impact + normal market movement
                    total_impact = impact + (market_return * 0.3)
                    self.player_profile.assets[asset] *= (1 + total_impact)

    def make_decision(
        self,
        decision_type: DecisionType,
        asset_class: str,
        amount: float,
    ) -> Tuple[bool, str]:
        """Record a decision made by player"""
        if asset_class not in self.player_profile.assets:
            return False, f"Asset class {asset_class} not available"

        current_balance = self.player_profile.assets[asset_class]

        if decision_type in [DecisionType.SELL, DecisionType.BUY_DIP]:
            if decision_type == DecisionType.SELL and current_balance < amount:
                return False, f"Insufficient {asset_class} to sell"

            if decision_type == DecisionType.SELL:
                self.player_profile.assets[asset_class] -= amount
                self.player_profile.assets["cash"] += amount
            elif decision_type == DecisionType.BUY_DIP:
                if self.player_profile.assets["cash"] < amount:
                    return False, "Insufficient cash to buy"
                self.player_profile.assets["cash"] -= amount
                self.player_profile.assets[asset_class] += amount

        decision = Decision(
            quarter=self.current_quarter,
            decision_type=decision_type,
            asset_class=asset_class,
            amount=amount,
        )
        self.decisions_made.append(decision)

        action_text = f"{decision_type.value} {asset_class}: ₹{amount:.0f}"
        return True, action_text

    def calculate_antifragility_score(self) -> Dict:
        """Calculate antifragility metrics"""
        if not self.quarterly_wealth_history or len(self.quarterly_wealth_history) < 2:
            return {"antifragility_score": 0, "survival": True, "analysis": ""}

        starting_wealth = self.quarterly_wealth_history[0]
        final_wealth = self.quarterly_wealth_history[-1]
        min_wealth = min(self.quarterly_wealth_history)

        # Calculate what wealth would be with no change
        baseline_wealth = starting_wealth

        # Antifragility = (final - baseline) / |min - baseline|
        # Positive: opportunistic (bought dips, grew despite crisis)
        # Negative: defensive (held cash, hedged, minimized losses)
        # Zero: broke even

        if min_wealth < baseline_wealth:
            drawdown = baseline_wealth - min_wealth
            recovery = final_wealth - min_wealth
            antifragility = (recovery / drawdown) if drawdown > 0 else 0
        else:
            # Min wealth above baseline (strong defensive positioning)
            antifragility = (final_wealth - baseline_wealth) / baseline_wealth if baseline_wealth > 0 else 0

        # Normalize to -100 to +100
        antifragility_score = max(-100, min(100, antifragility * 50))

        # Survival check
        survival = final_wealth > 0

        return {
            "antifragility_score": antifragility_score,
            "starting_wealth": starting_wealth,
            "trough_wealth": min_wealth,
            "final_wealth": final_wealth,
            "survival": survival,
            "max_drawdown_pct": ((starting_wealth - min_wealth) / starting_wealth * 100) if starting_wealth > 0 else 0,
        }

    def get_recommendations(self) -> List[Dict]:
        """Educational recommendations for pre-crisis positioning"""
        recommendations = []

        if self.difficulty == "easy":
            recommendations.append({
                "action": "Build emergency fund",
                "reason": "Convert 20% of equity to cash",
                "impact": "Dry powder to buy dips during crisis",
            })
            recommendations.append({
                "action": "Hedge with gold",
                "reason": "Gold tends to appreciate during crises",
                "impact": "+5-25% return during downturn",
            })

        if self.crisis_type == CrisisType.CRYPTO_WINTER:
            recommendations.append({
                "action": "Reduce crypto exposure",
                "reason": "Crypto is speculative and crash-prone",
                "impact": "Avoid 80% losses",
            })

        if self.crisis_type == CrisisType.DEMONETIZATION:
            recommendations.append({
                "action": "Limit cash holdings",
                "reason": "86% of notes will be invalidated",
                "impact": "Don't lose 86% of cash",
            })

        return recommendations

    def serialize_state(self) -> str:
        """Serialize full game state to JSON"""
        return json.dumps({
            "crisis_type": self.crisis_type.value,
            "current_quarter": self.current_quarter,
            "current_phase": self.current_phase.value,
            "random_seed": self.random_seed,
            "difficulty": self.difficulty,
            "player_profile": self.player_profile.to_dict(),
            "decisions_made": [
                {
                    "quarter": d.quarter,
                    "decision_type": d.decision_type.value,
                    "asset_class": d.asset_class,
                    "amount": d.amount,
                }
                for d in self.decisions_made
            ],
            "quarterly_wealth_history": self.quarterly_wealth_history,
            "market_index_history": self.market_index_history,
        })

    @classmethod
    def deserialize_state(cls, state_json: str):
        """Restore game from serialized state"""
        data = json.loads(state_json)
        crisis_type = CrisisType(data["crisis_type"])
        profile = FinancialProfile.from_dict(data["player_profile"])

        simulator = cls(
            crisis_type=crisis_type,
            player_profile=profile,
            random_seed=data["random_seed"],
            difficulty=data["difficulty"],
        )

        simulator.current_quarter = data["current_quarter"]
        simulator.current_phase = CrisisPhase(data["current_phase"])
        simulator.quarterly_wealth_history = data["quarterly_wealth_history"]
        simulator.market_index_history = data["market_index_history"]

        return simulator


def generate_random_profile(profile_type: PlayerProfile, random_seed: int) -> FinancialProfile:
    """Generate realistic random profile based on type"""
    random.seed(random_seed)

    profile = FinancialProfile()

    if profile_type == PlayerProfile.CONSERVATIVE:
        profile.assets = {
            "cash": random.randint(100000, 300000),
            "fds": random.randint(500000, 1500000),
            "gold": random.randint(50000, 200000),
            "real_estate": random.randint(2000000, 5000000),
            "equity": random.randint(100000, 300000),
            "crypto": random.randint(0, 50000),
        }
        profile.liabilities = {
            "mortgage": random.randint(0, 1000000),
            "personal_loans": 0,
            "credit_card_debt": random.randint(0, 50000),
        }
        profile.monthly_income = random.randint(40000, 80000)
        profile.emergency_fund_months = random.uniform(8, 12)

    elif profile_type == PlayerProfile.MODERATE:
        profile.assets = {
            "cash": random.randint(200000, 500000),
            "equity": random.randint(500000, 1500000),
            "fds": random.randint(300000, 800000),
            "gold": random.randint(50000, 150000),
            "real_estate": random.randint(1500000, 4000000),
            "crypto": random.randint(50000, 300000),
        }
        profile.liabilities = {
            "mortgage": random.randint(500000, 2000000),
            "personal_loans": random.randint(0, 300000),
            "credit_card_debt": random.randint(0, 100000),
        }
        profile.monthly_income = random.randint(60000, 120000)
        profile.emergency_fund_months = random.uniform(5, 8)

    elif profile_type == PlayerProfile.AGGRESSIVE:
        profile.assets = {
            "equity": random.randint(2000000, 5000000),
            "crypto": random.randint(500000, 2000000),
            "real_estate": random.randint(1000000, 3000000),
            "gold": random.randint(50000, 100000),
            "fds": random.randint(100000, 300000),
            "cash": random.randint(50000, 200000),
        }
        profile.liabilities = {
            "mortgage": random.randint(1000000, 3000000),
            "personal_loans": random.randint(200000, 800000),
            "credit_card_debt": random.randint(50000, 200000),
        }
        profile.monthly_income = random.randint(100000, 200000)
        profile.emergency_fund_months = random.uniform(2, 4)

    elif profile_type == PlayerProfile.UNPREPARED:
        profile.assets = {
            "cash": random.randint(50000, 200000),
            "real_estate": random.randint(500000, 1500000),
            "fds": random.randint(0, 100000),
            "gold": random.randint(10000, 50000),
            "equity": random.randint(0, 100000),
            "crypto": 0,
        }
        profile.liabilities = {
            "mortgage": random.randint(300000, 1500000),
            "personal_loans": random.randint(200000, 800000),
            "credit_card_debt": random.randint(100000, 300000),
        }
        profile.monthly_income = random.randint(25000, 50000)
        profile.emergency_fund_months = random.uniform(1, 2)

    profile.monthly_expenses = profile.monthly_income * random.uniform(0.6, 0.8)

    return profile
