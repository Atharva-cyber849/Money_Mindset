"""
SIP Chronicles Game Simulator
An idle game teaching the power of compound interest and investment discipline.

Players start a ₹500/month SIP at age 22 and watch wealth compound over 38 years
with periodic life interruptions testing their investment discipline.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import random
import json


class SIPType(str, Enum):
    """Investment types with different historical returns"""
    NIFTY_50 = "nifty_50"           # Standard equity index
    MIDCAP_150 = "midcap_150"       # Higher volatility, higher returns
    GOLD = "gold"                   # Inflation hedge
    ELSS = "elss"                   # Tax-advantaged equity (80C benefit)
    LIQUID_FUND = "liquid_fund"     # Quick access, low returns
    ARBITRAGE_FUND = "arbitrage_fund"  # Tax-efficient fund rotation
    DIVIDEND_FUND = "dividend_fund"    # Regular payout allocation


class InterruptionType(str, Enum):
    """Life events that interrupt SIP discipline"""
    SALARY_INCREASE = "salary_increase"        # Opportunity to upgrade
    MARKET_CRASH = "market_crash"              # Test of staying invested
    EMERGENCY_WITHDRAWAL = "emergency_withdrawal"  # Financial crisis
    PAUSE_SIP = "pause_sip"                    # Can't afford SIP
    JOB_LOSS = "job_loss"                      # Income interruption
    BULL_RUN = "bull_run"                      # Market acceleration
    # New Indian market events
    BUDGET_ANNOUNCEMENT = "budget_announcement"    # Feb 1 policy changes
    RBI_RATE_DECISION = "rbi_rate_decision"        # Quarterly MPC decisions
    CIRCUIT_BREAKER = "circuit_breaker"            # Market halt
    IPO_OPPORTUNITY = "ipo_opportunity"            # Hot IPO disruption
    DIVIDEND_PAYOUT = "dividend_payout"            # Quarterly/annual payouts
    SECTOR_ROTATION = "sector_rotation"            # Sector-specific changes
    INDEX_REBALANCING = "index_rebalancing"        # Mar/Jun/Sep/Dec rebalancing
    FINANCIAL_YEAR_END = "financial_year_end"      # Mar 31 tax loss harvesting


class InterruptionResponse(str, Enum):
    """Decision options for each interruption"""
    CONTINUE = "continue"                      # Stick with plan
    PAUSE = "pause"                            # Temporarily stop
    UPGRADE = "upgrade"                        # Increase SIP amount
    WITHDRAW = "withdraw"                      # Take money out


@dataclass
class InterruptionEvent:
    """An interruption in the game"""
    month: int
    age: int
    interruption_type: InterruptionType
    description: str
    options: List[Dict]  # [{action, consequence_description}]


@dataclass
class MonthlySnapshot:
    """State at each month"""
    month: int
    age: int
    accumulated_wealth: float
    total_contributions: float
    monthly_sip: float
    monthly_return: float
    interruption: Optional[InterruptionEvent] = None


@dataclass
class Decision:
    """A decision made during the game"""
    month: int
    age: int
    decision_type: str
    wealth_at_decision: float
    optimalwealth_at_decision: float
    cost_at_closure: float


class SIPChroniclesSimulator:
    """Main SIP Chronicles game engine"""

    # Historical returns (annual CAGR with volatility)
    RETURNS = {
        SIPType.NIFTY_50: {"avg": 0.10, "volatility": 0.02},
        SIPType.MIDCAP_150: {"avg": 0.12, "volatility": 0.03},
        SIPType.GOLD: {"avg": 0.05, "volatility": 0.01},
        SIPType.ELSS: {"avg": 0.10, "volatility": 0.02},  # Same as equity
        SIPType.LIQUID_FUND: {"avg": 0.02, "volatility": 0.001},  # 1-2% safe returns
        SIPType.ARBITRAGE_FUND: {"avg": 0.08, "volatility": 0.005},  # Tax-efficient
        SIPType.DIVIDEND_FUND: {"avg": 0.09, "volatility": 0.015},  # Regular payouts
    }

    # Indian portfolio milestones (achievements)
    MILESTONES = [100000, 2500000, 5000000, 10000000, 20000000]  # ₹1L, 25L, 50L, 1Cr, 2Cr

    def __init__(
        self,
        monthly_sip: float = 500,
        sip_type: SIPType = SIPType.NIFTY_50,
        starting_age: int = 22,
    ):
        self.monthly_sip = monthly_sip
        self.sip_type = sip_type
        self.starting_age = starting_age
        self.current_month = 0
        self.current_age = starting_age
        self.accumulated_wealth = 0
        self.total_contributions = 0

        # Tracking
        self.history: List[MonthlySnapshot] = []
        self.optimal_history: List[MonthlySnapshot] = []  # For hindsight
        self.decisions_made: List[Decision] = []
        self.interruptions_encountered: List[InterruptionEvent] = []
        self.milestones_achieved: List[Dict] = []  # Track milestone achievements with month/age

    def get_monthly_return_rate(self, year: int) -> float:
        """
        Get monthly return rate with variance based on year.
        Returns vary year to year to simulate market conditions.
        """
        returns_data = self.RETURNS[self.sip_type]
        avg_annual = returns_data["avg"]
        volatility = returns_data["volatility"]

        # Add random variance to annual rate (-volatility to +volatility)
        annual_rate = avg_annual + random.uniform(-volatility, volatility)

        # Convert to monthly rate
        # Monthly rate = (1 + annual)^(1/12) - 1
        monthly_rate = (1 + annual_rate) ** (1 / 12) - 1
        return monthly_rate

    def accumulate_wealth(
        self,
        current_wealth: float,
        sip_amount: float,
        monthly_rate: float,
    ) -> Tuple[float, float]:
        """
        Apply monthly compound growth.
        Returns: (new_wealth, monthly_gain)
        """
        # Apply return first to existing wealth
        growth = current_wealth * monthly_rate
        new_wealth = current_wealth + growth + sip_amount
        return new_wealth, growth

    def generate_interruption(self, month: int) -> Optional[InterruptionEvent]:
        """Generate an interruption at specific months or randomly"""
        age = self.starting_age + (month // 12)

        # Predefined interruptions at key months
        if month == 12:  # 1 year in
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.SALARY_INCREASE,
                description="Congratulations on your first annual raise! Your salary increased by ₹10K/month.",
                options=[
                    {
                        "action": "UPGRADE",
                        "description": "Upgrade SIP from ₹500 to ₹1000/month",
                        "consequence": "Extra ₹5.4L compounded over next 37 years",
                    },
                    {
                        "action": "CONTINUE",
                        "description": "Keep SIP at ₹500, spend the raise",
                        "consequence": "Miss acceleration but simpler to manage",
                    },
                ],
            )

        if month == 48:  # 4 years in
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.MARKET_CRASH,
                description="Market crash! Your portfolio down 30%. Markets always recover, but psychologically it's hard.",
                options=[
                    {
                        "action": "CONTINUE",
                        "description": "Continue SIP, buy more at discount",
                        "consequence": "You buy units at 30% discount - recovery amplifies gains",
                    },
                    {
                        "action": "PAUSE",
                        "description": "Pause SIP for 6 months",
                        "consequence": "Miss the lowest prices - costs ₹50K at age 60",
                    },
                ],
            )

        if month == 84:  # 7 years in
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.JOB_LOSS,
                description="Job market turned down - you got laid off. 6 months to find new job.",
                options=[
                    {
                        "action": "PAUSE",
                        "description": "Pause SIP for 6 months",
                        "consequence": "Preserve cash but lose ₹3K contribution. Resume after",
                    },
                    {
                        "action": "CONTINUE",
                        "description": "Keep investing - stay disciplined",
                        "consequence": "Risky but SIP continues. You'll recover the 6 months income",
                    },
                ],
            )

        if month == 180:  # ~15 years in
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.EMERGENCY_WITHDRAWAL,
                description="Medical emergency: family member needs ₹2 lakhs",
                options=[
                    {
                        "action": "WITHDRAW",
                        "description": "Withdraw ₹2L from SIP corpus",
                        "consequence": "Interrupt 15 years of compounding - costs ₹50L at age 60",
                    },
                    {
                        "action": "CONTINUE",
                        "description": "Don't touch SIP - find funds elsewhere",
                        "consequence": "Preserve SIP, maintain compound trajectory",
                    },
                ],
            )

        if month == 360:  # ~30 years in
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.BULL_RUN,
                description="10-year bull market: assets surge 100%+. Confidence everywhere.",
                options=[
                    {
                        "action": "UPGRADE",
                        "description": "Upgrade to ₹2000/month (confidence high)",
                        "consequence": "Extra ₹30L gains in final stretch. But risky if market turns",
                    },
                    {
                        "action": "CONTINUE",
                        "description": "Stick with plan",
                        "consequence": "Steady as she goes. Reduced regret risk",
                    },
                ],
            )

        # Indian market events - cyclical and random
        # Budget Announcement (Feb 1 - month % 12 == 1)
        if month > 12 and month % 12 == 1 and random.random() < 0.3:
            market_reaction = random.choice([-0.05, 0, 0.05])
            direction = "+↑" if market_reaction > 0 else ("-↓" if market_reaction < 0 else "→")
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.BUDGET_ANNOUNCEMENT,
                description=f"Budget announcement {direction} {abs(market_reaction)*100:.0f}% market reaction",
                options=[
                    {"action": "CONTINUE", "description": "Stay invested", "consequence": "Ride the wave"},
                    {"action": "PAUSE", "description": "Wait it out", "consequence": "Miss potential gains"},
                ],
            )

        # RBI Rate Decision (3-month intervals)
        if month > 12 and month % 3 == 0 and random.random() < 0.25:
            rate_change = random.choice([-0.02, 0, 0.02])
            direction = "hike" if rate_change > 0 else ("cut" if rate_change < 0 else "hold")
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.RBI_RATE_DECISION,
                description=f"RBI rate {direction}: Affects growth assets",
                options=[
                    {"action": "CONTINUE", "description": "Stick to SIP", "consequence": "Disciplined approach"},
                    {"action": "UPGRADE", "description": "Increase SIP 20%", "consequence": "Capitalize on rates"},
                ],
            )

        # Circuit Breaker (Market halt - rare)
        if month > 24 and random.random() < 0.001:
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.CIRCUIT_BREAKER,
                description="Market circuit breaker triggered! Trading halted for 15 minutes.",
                options=[
                    {"action": "CONTINUE", "description": "Resume trading", "consequence": "Markets stabilize"},
                    {"action": "PAUSE", "description": "Wait 1 day", "consequence": "Miss recovery bounce"},
                ],
            )

        # IPO Opportunity (Hot IPOs disrupt attention)
        if month > 36 and random.random() < 0.008:
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.IPO_OPPORTUNITY,
                description="Hot IPO listing! Potential 20% day-1 gain (or crash).",
                options=[
                    {"action": "CONTINUE", "description": "Ignore hype, stay in SIP", "consequence": "Avoid FOMO losses"},
                    {"action": "WITHDRAW", "description": "Allocate ₹1L to IPO", "consequence": "Risky but exciting"},
                ],
            )

        # Dividend Payout (Regular income)
        if month % 3 == 0 and month > 24 and random.random() < 0.4:
            dividend_amount = self.accumulated_wealth * 0.01
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.DIVIDEND_PAYOUT,
                description=f"Dividend payout: ₹{dividend_amount:,.0f} received",
                options=[
                    {"action": "CONTINUE", "description": "Reinvest dividend", "consequence": "Compound faster"},
                    {"action": "PAUSE", "description": "Take as income", "consequence": "Break compounding"},
                ],
            )

        # Sector Rotation (Specific sector changes)
        if month > 12 and random.random() < 0.15:
            sector = random.choice(["IT", "Pharma", "Banking", "Telecom"])
            rotation = random.choice(["bullish", "bearish"])
            impact = 0.12 if rotation == "bullish" else -0.08
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.SECTOR_ROTATION,
                description=f"{sector} sector becomes {rotation}",
                options=[
                    {"action": "CONTINUE", "description": "Index hedges sector risk", "consequence": "Balanced exposure"},
                ],
            )

        # Index Rebalancing (Mar/Jun/Sep/Dec)
        rebalancing_months = [2, 5, 8, 11]  # 0-indexed months
        if month > 12 and (month % 12) in rebalancing_months and random.random() < 0.3:
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.INDEX_REBALANCING,
                description="Index rebalancing: Stock additions/removals happening",
                options=[
                    {"action": "CONTINUE", "description": "Let fund manager rebalance", "consequence": "Professional management"},
                ],
            )

        # Financial Year End (Mar 31 - tax loss harvesting window)
        if month > 12 and month % 12 == 3 and random.random() < 0.25:
            return InterruptionEvent(
                month=month,
                age=age,
                interruption_type=InterruptionType.FINANCIAL_YEAR_END,
                description="FY end: Tax-loss harvesting window opens",
                options=[
                    {"action": "CONTINUE", "description": "Let mutual fund handle it", "consequence": "No action needed"},
                    {"action": "UPGRADE", "description": "Max out 80C: ₹1.5L/year in ELSS", "consequence": "Tax savings"},
                ],
            )

        # Random interruptions (lower probability)
        if random.random() < 0.01:  # 1% per month
            if random.random() < 0.5:
                return InterruptionEvent(
                    month=month,
                    age=age,
                    interruption_type=InterruptionType.PAUSE_SIP,
                    description="Unexpected expense. Can you pause SIP for a month?",
                    options=[
                        {"action": "PAUSE", "description": "Pause 1 month", "consequence": "Miss ₹500"},
                        {"action": "CONTINUE", "description": "Adjust elsewhere", "consequence": "Maintain discipline"},
                    ],
                )

        return None

    def apply_interruption_response(
        self,
        interruption: InterruptionEvent,
        response: InterruptionResponse,
        current_wealth: float,
    ) -> Tuple[float, str, float]:
        """
        Apply the consequence of a decision.
        Returns: (wealth_impact, description, new_monthly_sip)
        """
        if interruption.interruption_type == InterruptionType.SALARY_INCREASE:
            if response == InterruptionResponse.UPGRADE:
                return 0, "SIP upgraded to ₹1000/month", 1000
            return 0, "Kept SIP at ₹500", self.monthly_sip

        elif interruption.interruption_type == InterruptionType.MARKET_CRASH:
            if response == InterruptionResponse.CONTINUE:
                return 0, "Continued investing at discount prices", self.monthly_sip
            elif response == InterruptionResponse.PAUSE:
                return -50000, "Paused for 6 months, missed recovery", self.monthly_sip
            return 0, "", self.monthly_sip

        elif interruption.interruption_type == InterruptionType.JOB_LOSS:
            if response == InterruptionResponse.PAUSE:
                return -3000, "Paused for 6 months", self.monthly_sip
            return 0, "Continued despite job loss", self.monthly_sip

        elif interruption.interruption_type == InterruptionType.EMERGENCY_WITHDRAWAL:
            if response == InterruptionResponse.WITHDRAW:
                return -200000, "Withdrew ₹2L for emergency", self.monthly_sip
            return 0, "Preserved SIP despite emergency", self.monthly_sip

        elif interruption.interruption_type == InterruptionType.BULL_RUN:
            if response == InterruptionResponse.UPGRADE:
                return 0, "Upgraded SIP to ₹2000", 2000
            return 0, "Maintained discipline", self.monthly_sip

        return 0, "", self.monthly_sip

    def simulate_month(
        self,
        month: int,
        interruption_response: Optional[InterruptionResponse] = None,
    ) -> MonthlySnapshot:
        """Simulate one month of SIP"""
        self.current_month = month
        self.current_age = self.starting_age + (month // 12)
        year = month // 12

        # Step 1: Add monthly SIP contribution
        self.total_contributions += self.monthly_sip

        # Step 2: Apply monthly returns
        monthly_rate = self.get_monthly_return_rate(year)
        self.accumulated_wealth, monthly_return = self.accumulate_wealth(
            self.accumulated_wealth,
            self.monthly_sip,
            monthly_rate,
        )

        # Step 3: Check for interruption
        interruption = self.generate_interruption(month)
        if interruption and interruption_response:
            wealth_impact, description, new_sip = self.apply_interruption_response(
                interruption, interruption_response, self.accumulated_wealth
            )
            self.accumulated_wealth += wealth_impact
            if new_sip != self.monthly_sip:
                self.monthly_sip = new_sip
            self.interruptions_encountered.append(interruption)

        # Step 4: Create snapshot
        snapshot = MonthlySnapshot(
            month=month,
            age=self.current_age,
            accumulated_wealth=max(0, self.accumulated_wealth),
            total_contributions=self.total_contributions,
            monthly_sip=self.monthly_sip,
            monthly_return=monthly_return,
            interruption=interruption,
        )

        self.history.append(snapshot)
        return snapshot

    def calculate_hindsight_costs(self) -> List[Dict]:
        """
        After game ends, calculate the cost of each decision in hindsight.
        Returns top 3 most expensive mistakes.
        """
        if not self.interruptions_encountered:
            return []

        costs = []
        for interrupt in self.interruptions_encountered:
            # Rough estimate: each decision costs X% of 30 years compounding
            # Better: Would need to re-simulate with optimal choices
            estimated_cost = {"month": interrupt.month, "type": interrupt.interruption_type, "cost": 0}
            costs.append(estimated_cost)

        # Sort by estimated cost and return top 3
        return sorted(costs, key=lambda x: x["cost"], reverse=True)[:3]

    def check_milestone_achievement(self, wealth: float, month: int) -> Optional[Dict]:
        """Check if wealth has crossed an Indian portfolio milestone"""
        for milestone in self.MILESTONES:
            # Check if this is a new milestone achievement
            previous_wealth = self.history[-2].accumulated_wealth if len(self.history) > 1 else 0
            if previous_wealth < milestone <= wealth:
                age = self.starting_age + (month // 12)
                milestone_dict = {
                    "month": month,
                    "age": age,
                    "wealth": wealth,
                    "milestone": milestone,
                    "milestone_label": self._format_milestone(milestone),
                }
                self.milestones_achieved.append(milestone_dict)
                return milestone_dict
        return None

    def _format_milestone(self, amount: float) -> str:
        """Format milestone amount in Indian notation (₹)"""
        if amount >= 10000000:
            return f"₹{amount/10000000:.0f}Cr"
        elif amount >= 100000:
            return f"₹{amount/100000:.0f}L"
        else:
            return f"₹{amount:,.0f}"

    def get_final_corpus(self) -> float:
        """Get final wealth at age 60"""
        return self.accumulated_wealth

    def get_tax_benefit(self) -> float:
        """Calculate tax benefit if using ELSS"""
        if self.sip_type == SIPType.ELSS:
            # 30% tax savings on first year contribution
            return self.monthly_sip * 12 * self.ELSS_TAX_BENEFIT
        return 0

    def get_game_summary(self) -> Dict:
        """Get complete game summary"""
        final_wealth = self.get_final_corpus()
        multiplier = final_wealth / self.total_contributions if self.total_contributions > 0 else 1

        return {
            "final_corpus": final_wealth,
            "final_age": self.current_age,
            "total_contributions": self.total_contributions,
            "total_months": self.current_month,
            "SIP_type": self.sip_type.value,
            "multiplier": multiplier,
            "interruptions_count": len(self.interruptions_encountered),
            "tax_savings": self.get_tax_benefit(),
            "milestones_achieved": self.milestones_achieved,
            "milestones_count": len(self.milestones_achieved),
            "interruptions_log": [
                {
                    "month": i.month,
                    "age": i.age,
                    "type": i.interruption_type.value,
                    "description": i.description,
                }
                for i in self.interruptions_encountered
            ],
        }
