"""
Tax-Advantaged Account Optimizer
Simulation 12: Compare 401k, IRA, Roth IRA, and HSA strategies
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import random


class AccountType(Enum):
    """Tax-advantaged account types"""
    TRADITIONAL_401K = "traditional_401k"
    ROTH_401K = "roth_401k"
    TRADITIONAL_IRA = "traditional_ira"
    ROTH_IRA = "roth_ira"
    HSA = "hsa"
    TAXABLE = "taxable"


class TaxBracket(Enum):
    """Federal tax brackets (2024 approximation)"""
    LOW = "low"      # 12% (income < $44,725)
    MEDIUM = "medium"  # 22% (income $44,726-$95,375)
    HIGH = "high"    # 24-32% (income $95,376-$182,100)
    VERY_HIGH = "very_high"  # 35-37% (income > $182,100)


@dataclass
class AccountContribution:
    """Annual contribution to an account"""
    year: int
    account_type: AccountType
    contribution: float
    employer_match: float
    tax_saved_now: float  # Tax deduction for traditional accounts
    account_balance: float


@dataclass
class WithdrawalResult:
    """Retirement withdrawal analysis"""
    year: int
    withdrawal_amount: float
    taxes_owed: float
    net_withdrawal: float
    remaining_balance: float


@dataclass
class AccountStrategy:
    """Complete tax-advantaged account strategy"""
    strategy_name: str
    accounts: Dict[AccountType, List[AccountContribution]]
    total_contributed: float
    total_employer_match: float
    total_tax_saved: float
    final_balance: float
    withdrawal_analysis: List[WithdrawalResult]
    net_after_tax: float
    effective_tax_rate: float


class TaxAdvantagedOptimizer:
    """
    Simulates different tax-advantaged account strategies
    Demonstrates tax benefits and optimal allocation
    """
    
    # 2024 Contribution limits
    CONTRIBUTION_LIMITS = {
        AccountType.TRADITIONAL_401K: 23000,
        AccountType.ROTH_401K: 23000,
        AccountType.TRADITIONAL_IRA: 7000,
        AccountType.ROTH_IRA: 7000,
        AccountType.HSA: 4150  # Individual coverage
    }
    
    # Tax rates by bracket
    TAX_RATES = {
        TaxBracket.LOW: 0.12,
        TaxBracket.MEDIUM: 0.22,
        TaxBracket.HIGH: 0.28,
        TaxBracket.VERY_HIGH: 0.35
    }
    
    # Investment assumptions
    ANNUAL_RETURN = 0.08
    EMPLOYER_MATCH_RATE = 0.50  # 50% match up to 6% of salary
    EMPLOYER_MATCH_CAP = 0.06   # Match up to 6% of salary
    
    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
    
    def compare_strategies(
        self,
        annual_income: float,
        years_until_retirement: int,
        current_age: int,
        current_tax_bracket: TaxBracket,
        retirement_tax_bracket: TaxBracket
    ) -> Dict[str, AccountStrategy]:
        """
        Compare different tax-advantaged account strategies
        
        Args:
            annual_income: Current annual income
            years_until_retirement: Years until retirement
            current_age: Current age
            current_tax_bracket: Current tax bracket
            retirement_tax_bracket: Expected retirement tax bracket
        
        Returns:
            Dictionary of strategy results
        """
        strategies = {}
        
        # Strategy 1: All Traditional 401k (max tax deduction now)
        strategies["all_traditional"] = self._simulate_all_traditional(
            annual_income,
            years_until_retirement,
            current_tax_bracket,
            retirement_tax_bracket
        )
        
        # Strategy 2: All Roth (pay taxes now, tax-free later)
        strategies["all_roth"] = self._simulate_all_roth(
            annual_income,
            years_until_retirement,
            current_tax_bracket,
            retirement_tax_bracket
        )
        
        # Strategy 3: Balanced (mix of traditional and Roth)
        strategies["balanced"] = self._simulate_balanced(
            annual_income,
            years_until_retirement,
            current_tax_bracket,
            retirement_tax_bracket
        )
        
        # Strategy 4: HSA First (triple tax advantage)
        strategies["hsa_first"] = self._simulate_hsa_first(
            annual_income,
            years_until_retirement,
            current_tax_bracket,
            retirement_tax_bracket
        )
        
        # Strategy 5: No retirement accounts (taxable only)
        strategies["taxable_only"] = self._simulate_taxable_only(
            annual_income,
            years_until_retirement,
            current_tax_bracket,
            retirement_tax_bracket
        )
        
        return strategies
    
    def _simulate_all_traditional(
        self,
        income: float,
        years: int,
        current_bracket: TaxBracket,
        retirement_bracket: TaxBracket
    ) -> AccountStrategy:
        """Simulate maxing out traditional 401k"""
        # Calculate annual contribution (up to limit)
        annual_contribution = min(
            income * 0.15,  # 15% of income
            self.CONTRIBUTION_LIMITS[AccountType.TRADITIONAL_401K]
        )
        
        # Employer match
        match_eligible = min(income * self.EMPLOYER_MATCH_CAP, annual_contribution)
        employer_match = match_eligible * self.EMPLOYER_MATCH_RATE
        
        # Accumulation phase
        contributions = []
        balance = 0
        total_tax_saved = 0
        
        for year in range(1, years + 1):
            # Tax savings from deduction
            tax_saved = annual_contribution * self.TAX_RATES[current_bracket]
            total_tax_saved += tax_saved
            
            # Add contributions
            balance += annual_contribution + employer_match
            
            # Investment growth
            balance *= (1 + self.ANNUAL_RETURN)
            
            contributions.append(AccountContribution(
                year=year,
                account_type=AccountType.TRADITIONAL_401K,
                contribution=annual_contribution,
                employer_match=employer_match,
                tax_saved_now=tax_saved,
                account_balance=balance
            ))
        
        # Withdrawal phase (30 years of retirement)
        withdrawal_analysis = self._simulate_withdrawals(
            balance,
            retirement_bracket,
            30,
            is_roth=False
        )
        
        return AccountStrategy(
            strategy_name="All Traditional 401k",
            accounts={AccountType.TRADITIONAL_401K: contributions},
            total_contributed=annual_contribution * years,
            total_employer_match=employer_match * years,
            total_tax_saved=total_tax_saved,
            final_balance=balance,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=withdrawal_analysis[-1].remaining_balance if withdrawal_analysis else balance,
            effective_tax_rate=self._calculate_effective_rate(withdrawal_analysis)
        )
    
    def _simulate_all_roth(
        self,
        income: float,
        years: int,
        current_bracket: TaxBracket,
        retirement_bracket: TaxBracket
    ) -> AccountStrategy:
        """Simulate Roth 401k + Roth IRA strategy"""
        # Roth 401k contribution
        roth_401k_contribution = min(
            income * 0.10,
            self.CONTRIBUTION_LIMITS[AccountType.ROTH_401K]
        )
        
        # Roth IRA contribution
        roth_ira_contribution = self.CONTRIBUTION_LIMITS[AccountType.ROTH_IRA]
        
        # Employer match (always goes to traditional)
        match_eligible = min(income * self.EMPLOYER_MATCH_CAP, roth_401k_contribution)
        employer_match = match_eligible * self.EMPLOYER_MATCH_RATE
        
        # Accumulation
        contributions_401k = []
        contributions_ira = []
        balance_401k = 0
        balance_ira = 0
        
        for year in range(1, years + 1):
            # Roth 401k
            balance_401k += roth_401k_contribution + employer_match
            balance_401k *= (1 + self.ANNUAL_RETURN)
            
            contributions_401k.append(AccountContribution(
                year=year,
                account_type=AccountType.ROTH_401K,
                contribution=roth_401k_contribution,
                employer_match=employer_match,
                tax_saved_now=0,  # No tax savings with Roth
                account_balance=balance_401k
            ))
            
            # Roth IRA
            balance_ira += roth_ira_contribution
            balance_ira *= (1 + self.ANNUAL_RETURN)
            
            contributions_ira.append(AccountContribution(
                year=year,
                account_type=AccountType.ROTH_IRA,
                contribution=roth_ira_contribution,
                employer_match=0,
                tax_saved_now=0,
                account_balance=balance_ira
            ))
        
        total_balance = balance_401k + balance_ira
        
        # Roth withdrawals are tax-free!
        withdrawal_analysis = self._simulate_withdrawals(
            total_balance,
            retirement_bracket,
            30,
            is_roth=True
        )
        
        return AccountStrategy(
            strategy_name="All Roth (401k + IRA)",
            accounts={
                AccountType.ROTH_401K: contributions_401k,
                AccountType.ROTH_IRA: contributions_ira
            },
            total_contributed=(roth_401k_contribution + roth_ira_contribution) * years,
            total_employer_match=employer_match * years,
            total_tax_saved=0,
            final_balance=total_balance,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=total_balance,  # Tax-free!
            effective_tax_rate=0.0
        )
    
    def _simulate_balanced(
        self,
        income: float,
        years: int,
        current_bracket: TaxBracket,
        retirement_bracket: TaxBracket
    ) -> AccountStrategy:
        """Simulate balanced traditional/Roth mix"""
        # 60% traditional 401k, 40% Roth IRA
        trad_401k = min(income * 0.09, self.CONTRIBUTION_LIMITS[AccountType.TRADITIONAL_401K] * 0.6)
        roth_ira = min(income * 0.06, self.CONTRIBUTION_LIMITS[AccountType.ROTH_IRA])
        
        match_eligible = min(income * self.EMPLOYER_MATCH_CAP, trad_401k)
        employer_match = match_eligible * self.EMPLOYER_MATCH_RATE
        
        contributions_401k = []
        contributions_ira = []
        balance_401k = 0
        balance_ira = 0
        total_tax_saved = 0
        
        for year in range(1, years + 1):
            # Traditional 401k
            tax_saved = trad_401k * self.TAX_RATES[current_bracket]
            total_tax_saved += tax_saved
            
            balance_401k += trad_401k + employer_match
            balance_401k *= (1 + self.ANNUAL_RETURN)
            
            contributions_401k.append(AccountContribution(
                year=year,
                account_type=AccountType.TRADITIONAL_401K,
                contribution=trad_401k,
                employer_match=employer_match,
                tax_saved_now=tax_saved,
                account_balance=balance_401k
            ))
            
            # Roth IRA
            balance_ira += roth_ira
            balance_ira *= (1 + self.ANNUAL_RETURN)
            
            contributions_ira.append(AccountContribution(
                year=year,
                account_type=AccountType.ROTH_IRA,
                contribution=roth_ira,
                employer_match=0,
                tax_saved_now=0,
                account_balance=balance_ira
            ))
        
        # Mixed withdrawals (strategic)
        withdrawal_analysis = self._simulate_mixed_withdrawals(
            balance_401k,
            balance_ira,
            retirement_bracket,
            30
        )
        
        return AccountStrategy(
            strategy_name="Balanced (60% Traditional, 40% Roth)",
            accounts={
                AccountType.TRADITIONAL_401K: contributions_401k,
                AccountType.ROTH_IRA: contributions_ira
            },
            total_contributed=(trad_401k + roth_ira) * years,
            total_employer_match=employer_match * years,
            total_tax_saved=total_tax_saved,
            final_balance=balance_401k + balance_ira,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=sum(w.net_withdrawal for w in withdrawal_analysis),
            effective_tax_rate=self._calculate_effective_rate(withdrawal_analysis)
        )
    
    def _simulate_hsa_first(
        self,
        income: float,
        years: int,
        current_bracket: TaxBracket,
        retirement_bracket: TaxBracket
    ) -> AccountStrategy:
        """Simulate HSA-first strategy (triple tax advantage)"""
        # Max HSA first (best tax advantage)
        hsa_contribution = self.CONTRIBUTION_LIMITS[AccountType.HSA]
        
        # Then traditional 401k
        trad_401k = min(income * 0.10, self.CONTRIBUTION_LIMITS[AccountType.TRADITIONAL_401K])
        
        match_eligible = min(income * self.EMPLOYER_MATCH_CAP, trad_401k)
        employer_match = match_eligible * self.EMPLOYER_MATCH_RATE
        
        contributions_hsa = []
        contributions_401k = []
        balance_hsa = 0
        balance_401k = 0
        total_tax_saved = 0
        
        for year in range(1, years + 1):
            # HSA: Triple tax advantage
            # 1. Tax-deductible contributions
            # 2. Tax-free growth
            # 3. Tax-free withdrawals for medical expenses
            hsa_tax_saved = hsa_contribution * self.TAX_RATES[current_bracket]
            
            balance_hsa += hsa_contribution
            balance_hsa *= (1 + self.ANNUAL_RETURN)
            
            contributions_hsa.append(AccountContribution(
                year=year,
                account_type=AccountType.HSA,
                contribution=hsa_contribution,
                employer_match=0,
                tax_saved_now=hsa_tax_saved,
                account_balance=balance_hsa
            ))
            
            # Traditional 401k
            trad_tax_saved = trad_401k * self.TAX_RATES[current_bracket]
            total_tax_saved += hsa_tax_saved + trad_tax_saved
            
            balance_401k += trad_401k + employer_match
            balance_401k *= (1 + self.ANNUAL_RETURN)
            
            contributions_401k.append(AccountContribution(
                year=year,
                account_type=AccountType.TRADITIONAL_401K,
                contribution=trad_401k,
                employer_match=employer_match,
                tax_saved_now=trad_tax_saved,
                account_balance=balance_401k
            ))
        
        # Assume 50% of HSA used for medical (tax-free), 50% withdrawn (taxed)
        hsa_medical_expenses = balance_hsa * 0.5
        hsa_taxable = balance_hsa * 0.5
        
        withdrawal_analysis = self._simulate_withdrawals(
            balance_401k + hsa_taxable,
            retirement_bracket,
            30,
            is_roth=False
        )
        
        # Add back tax-free HSA medical withdrawals
        net_after_tax = sum(w.net_withdrawal for w in withdrawal_analysis) + hsa_medical_expenses
        
        return AccountStrategy(
            strategy_name="HSA First (Triple Tax Advantage)",
            accounts={
                AccountType.HSA: contributions_hsa,
                AccountType.TRADITIONAL_401K: contributions_401k
            },
            total_contributed=(hsa_contribution + trad_401k) * years,
            total_employer_match=employer_match * years,
            total_tax_saved=total_tax_saved,
            final_balance=balance_hsa + balance_401k,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=net_after_tax,
            effective_tax_rate=self._calculate_effective_rate(withdrawal_analysis) * 0.5  # Reduced by HSA
        )
    
    def _simulate_taxable_only(
        self,
        income: float,
        years: int,
        current_bracket: TaxBracket,
        retirement_bracket: TaxBracket
    ) -> AccountStrategy:
        """Simulate no retirement accounts (baseline comparison)"""
        # Same contribution amount, but in taxable account
        annual_contribution = income * 0.15
        
        # Must pay taxes on income first
        after_tax_contribution = annual_contribution * (1 - self.TAX_RATES[current_bracket])
        
        contributions = []
        balance = 0
        
        for year in range(1, years + 1):
            balance += after_tax_contribution
            
            # Growth is taxed annually (capital gains)
            growth = balance * self.ANNUAL_RETURN
            capital_gains_tax = growth * 0.15  # 15% long-term capital gains
            net_growth = growth - capital_gains_tax
            
            balance += net_growth
            
            contributions.append(AccountContribution(
                year=year,
                account_type=AccountType.TAXABLE,
                contribution=after_tax_contribution,
                employer_match=0,
                tax_saved_now=0,
                account_balance=balance
            ))
        
        # Already paid taxes, so no additional tax on withdrawal
        withdrawal_analysis = self._simulate_withdrawals(
            balance,
            retirement_bracket,
            30,
            is_roth=True  # Treat as tax-free since already taxed
        )
        
        return AccountStrategy(
            strategy_name="Taxable Account Only (No Retirement Accounts)",
            accounts={AccountType.TAXABLE: contributions},
            total_contributed=annual_contribution * years,
            total_employer_match=0,
            total_tax_saved=0,
            final_balance=balance,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=balance,
            effective_tax_rate=self.TAX_RATES[current_bracket]  # Paid upfront
        )
    
    def _simulate_withdrawals(
        self,
        starting_balance: float,
        tax_bracket: TaxBracket,
        years: int,
        is_roth: bool
    ) -> List[WithdrawalResult]:
        """Simulate retirement withdrawals"""
        balance = starting_balance
        withdrawals = []
        
        # 4% rule: withdraw 4% per year
        annual_withdrawal = balance * 0.04
        
        for year in range(1, years + 1):
            if is_roth:
                taxes_owed = 0
                net_withdrawal = annual_withdrawal
            else:
                taxes_owed = annual_withdrawal * self.TAX_RATES[tax_bracket]
                net_withdrawal = annual_withdrawal - taxes_owed
            
            balance -= annual_withdrawal
            
            # Remaining balance continues to grow
            if balance > 0:
                balance *= (1 + self.ANNUAL_RETURN * 0.6)  # More conservative in retirement
            
            withdrawals.append(WithdrawalResult(
                year=year,
                withdrawal_amount=annual_withdrawal,
                taxes_owed=taxes_owed,
                net_withdrawal=net_withdrawal,
                remaining_balance=max(balance, 0)
            ))
        
        return withdrawals
    
    def _simulate_mixed_withdrawals(
        self,
        traditional_balance: float,
        roth_balance: float,
        tax_bracket: TaxBracket,
        years: int
    ) -> List[WithdrawalResult]:
        """Strategically withdraw from traditional and Roth to minimize taxes"""
        withdrawals = []
        trad_balance = traditional_balance
        roth_bal = roth_balance
        
        total_balance = trad_balance + roth_bal
        annual_need = total_balance * 0.04
        
        for year in range(1, years + 1):
            # Withdraw from traditional up to lower tax brackets
            # Then supplement with Roth (tax-free)
            
            # Assume we want to stay in lower bracket
            trad_withdrawal = min(annual_need * 0.6, trad_balance)
            roth_withdrawal = min(annual_need - trad_withdrawal, roth_bal)
            
            trad_taxes = trad_withdrawal * self.TAX_RATES[tax_bracket]
            roth_taxes = 0
            
            total_withdrawal = trad_withdrawal + roth_withdrawal
            total_taxes = trad_taxes
            net_withdrawal = total_withdrawal - total_taxes
            
            trad_balance -= trad_withdrawal
            roth_bal -= roth_withdrawal
            
            # Growth on remaining
            if trad_balance > 0:
                trad_balance *= (1 + self.ANNUAL_RETURN * 0.6)
            if roth_bal > 0:
                roth_bal *= (1 + self.ANNUAL_RETURN * 0.6)
            
            withdrawals.append(WithdrawalResult(
                year=year,
                withdrawal_amount=total_withdrawal,
                taxes_owed=total_taxes,
                net_withdrawal=net_withdrawal,
                remaining_balance=trad_balance + roth_bal
            ))
        
        return withdrawals
    
    def _calculate_effective_rate(self, withdrawals: List[WithdrawalResult]) -> float:
        """Calculate effective tax rate over retirement"""
        if not withdrawals:
            return 0.0
        
        total_withdrawn = sum(w.withdrawal_amount for w in withdrawals)
        total_taxes = sum(w.taxes_owed for w in withdrawals)
        
        if total_withdrawn == 0:
            return 0.0
        
        return total_taxes / total_withdrawn
    
    def generate_recommendation(
        self,
        current_age: int,
        income: float,
        current_bracket: TaxBracket,
        expected_retirement_bracket: TaxBracket
    ) -> Dict:
        """Generate personalized recommendation"""
        recommendations = []
        
        # HSA: Always recommend if eligible
        recommendations.append({
            "priority": 1,
            "account": "HSA",
            "reason": "Triple tax advantage: deductible, tax-free growth, tax-free withdrawals for medical",
            "action": f"Max out HSA: ${self.CONTRIBUTION_LIMITS[AccountType.HSA]:,.0f}/year"
        })
        
        # Employer match: Free money
        match_amount = min(income * self.EMPLOYER_MATCH_CAP, 
                          self.CONTRIBUTION_LIMITS[AccountType.TRADITIONAL_401K]) * self.EMPLOYER_MATCH_RATE
        recommendations.append({
            "priority": 2,
            "account": "401k (Traditional or Roth)",
            "reason": f"Employer match is free money: ${match_amount:,.0f}/year",
            "action": f"Contribute at least {self.EMPLOYER_MATCH_CAP*100:.0f}% to get full match"
        })
        
        # Traditional vs Roth decision
        if self.TAX_RATES[current_bracket] > self.TAX_RATES[expected_retirement_bracket]:
            recommendations.append({
                "priority": 3,
                "account": "Roth IRA/401k",
                "reason": f"You're in a higher bracket now ({self.TAX_RATES[current_bracket]*100:.0f}%) than expected in retirement ({self.TAX_RATES[expected_retirement_bracket]*100:.0f}%). Pay taxes now with Roth.",
                "action": "Prioritize Roth contributions"
            })
        else:
            recommendations.append({
                "priority": 3,
                "account": "Traditional IRA/401k",
                "reason": f"You're in a lower bracket now ({self.TAX_RATES[current_bracket]*100:.0f}%). Get the deduction now, pay taxes later.",
                "action": "Prioritize Traditional contributions"
            })
        
        # Age-based advice
        if current_age < 40:
            recommendations.append({
                "priority": 4,
                "account": "Roth IRA",
                "reason": "You're young - decades of tax-free growth ahead. Time is on your side.",
                "action": "Consider maxing Roth IRA for long-term tax-free gains"
            })
        
        return {
            "recommendations": recommendations,
            "key_insight": self._generate_key_insight(current_age, current_bracket, expected_retirement_bracket)
        }
    
    def _generate_key_insight(
        self,
        age: int,
        current: TaxBracket,
        retirement: TaxBracket
    ) -> str:
        """Generate key insight based on situation"""
        if age < 30:
            return "Youth is your superpower! Focus on Roth accounts - you'll thank yourself in 40 years when you withdraw hundreds of thousands tax-free."
        elif current == TaxBracket.HIGH or current == TaxBracket.VERY_HIGH:
            return f"You're in the {self.TAX_RATES[current]*100:.0f}% bracket. Traditional accounts give you immediate tax relief. Every $1,000 contributed saves ${self.TAX_RATES[current]*1000:.0f} in taxes!"
        elif current < retirement:
            return "Your income is likely to rise. Lock in your current low tax rate with Roth contributions now."
        else:
            return "Balance is key. Split between Traditional (tax deduction now) and Roth (tax-free later) gives you flexibility in retirement."
