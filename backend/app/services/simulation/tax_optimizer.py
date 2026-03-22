"""
Indian Tax-Advantaged Account Optimizer
Simulation: Compare NPS, PPF, ELSS, SSY, and EPF retirement strategies
Optimizes for Section 80C deductions, capital gains, and retirement outcomes
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import random


class IndianAccountType(Enum):
    """Indian tax-advantaged account types"""
    NPS_TIER1 = "nps_tier1"           # National Pension System - Tier 1 (locked till 60)
    NPS_TIER2 = "nps_tier2"           # NPS Tier 2 (flexible withdrawal)
    PPF = "ppf"                        # Public Provident Fund (15-year maturity)
    ELSS = "elss"                      # Equity Linked Saving Scheme (3-year lock)
    SSY = "ssy"                        # Sukanya Samriddhi Yojana (daughter education)
    TAXABLE = "taxable"                # Regular taxable investment


class IncomeTaxBracketIndia(Enum):
    """Indian income tax brackets (FY 2024-25)"""
    EXEMPT = "exempt"        # < ₹2.5L (below exemption limit)
    FIVE_PERCENT = "5%"      # ₹2.5L - ₹5L
    TWENTY_PERCENT = "20%"   # ₹5L - ₹10L
    THIRTY_PERCENT = "30%"   # > ₹10L


@dataclass
class TaxDeduction:
    """Indian tax deduction details"""
    section: str              # Section 80C, 80D, 80E, etc.
    category: str             # PPF, Life Insurance, Home Loan Principal, etc.
    amount: float
    limit: float
    description: str


@dataclass
class IndianAccountContribution:
    """Annual contribution to Indian tax account"""
    year: int
    account_type: IndianAccountType
    contribution: float
    employer_contribution: float  # EPF match from employer
    tax_deduction: float                  # Tax saved this year
    account_balance: float
    applicable_tax_bracket: IncomeTaxBracketIndia


@dataclass
class WithdrawalResultIndia:
    """Indian withdrawal analysis with capital gains tax"""
    year: int
    withdrawal_amount: float
    capital_gains: float
    capital_gains_tax: float              # LTCG/STCG
    total_taxes_owed: float
    net_withdrawal: float
    remaining_balance: float


@dataclass
class IndianTaxOptimizationStrategy:
    """Complete Indian tax optimization strategy"""
    strategy_name: str
    accounts: Dict[IndianAccountType, List[IndianAccountContribution]]
    total_contributed: float
    total_employer_contribution: float
    total_tax_deductions: float           # Total under Section 80C, 80D, etc.
    final_balance: float
    withdrawal_analysis: List[WithdrawalResultIndia]
    net_after_tax: float
    effective_tax_rate: float
    annual_tax_savings: float


class IndianTaxOptimizer:
    """
    Simulates Indian tax-advantaged account strategies
    Focuses on Section 80C deductions, NPS, PPF, ELSS, EPF
    Includes capital gains taxation and HRA benefits
    """

    # 2024-25 FY Contribution limits (in Indian Rupees)
    CONTRIBUTION_LIMITS = {
        IndianAccountType.NPS_TIER1: 250000,      # Can contribute more, but only ₹2.5L gets 80CCD deduction
        IndianAccountType.NPS_TIER2: 200000,      # Flexible, but no guarantee
        IndianAccountType.PPF: 150000,             # ₹1.5L per financial year
        IndianAccountType.ELSS: 999999999,         # Can go higher, only ₹1.5L gets 80C benefit
        IndianAccountType.SSY: 150000              # Up to ₹1.5L/year
    }

    # Indian tax rates by bracket (FY 2024-25)
    TAX_RATES = {
        IncomeTaxBracketIndia.EXEMPT: 0.00,
        IncomeTaxBracketIndia.FIVE_PERCENT: 0.05,
        IncomeTaxBracketIndia.TWENTY_PERCENT: 0.20,
        IncomeTaxBracketIndia.THIRTY_PERCENT: 0.30
    }

    # Applicable Surcharge and Education Cess
    SURCHARGE_RATES = {
        IncomeTaxBracketIndia.EXEMPT: 0.00,
        IncomeTaxBracketIndia.FIVE_PERCENT: 0.00,
        IncomeTaxBracketIndia.TWENTY_PERCENT: 0.05,        # 5% surcharge above ₹50L
        IncomeTaxBracketIndia.THIRTY_PERCENT: 0.25         # 25% surcharge above ₹1Cr
    }

    EDUCATION_CESS = 0.04                                   # 4% education cess on tax

    # Section 80 Deduction limits
    SECTION_80_LIMITS = {
        "80C": 150000,            # PPF, ELSS, Life Ins, Home Loan Principal, etc. → ₹1.5L combined limit
        "80CCD": 50000,           # Additional NPS contribution → ₹50K limit
        "80D": 150000,             # Medical insurance (increases with age)
        "80E": 999999999,          # Education loan interest → No limit
        "80G": 500000              # Charitable donation → 50% or 100% deduction
    }

    # Investment returns (Indian market assumptions)
    NPS_RETURN = 0.09             # 9% CAGR (conservative estimate)
    PPF_RETURN = 0.075            # 7.5% CAGR (government backed)
    ELSS_RETURN = 0.12            # 12% CAGR (equity-heavy)
    TAXABLE_RETURN = 0.10         # 10% CAGR

    # EPF contribution (Employee + Employer)
    EPF_EMPLOYEE_RATE = 0.12      # 12% of basic salary
    EPF_EMPLOYER_RATE = 0.12      # 12% employer match

    # Capital gains tax rates
    LTCG_EQUITY = 0.20            # 20% Long-term capital gains on equity (with indexation)
    STCG_EQUITY = 0.15            # 15% Slab rate (short-term)
    LTCG_PROPERTY = 0.20           # 20% Long-term capital gains on real estate

    # Investment holding periods
    PPF_HOLDING_YEARS = 15        # Maturity period
    ELSS_LOCK_IN = 3              # Lock-in period
    NPS_LOCK_TILL_60 = True        # Locked till 60 for Tier-1

    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)

    def determine_tax_bracket(self, annual_income: float, age: int = 60) -> IncomeTaxBracketIndia:
        """Determine tax bracket based on income (simplified for age 60+)"""
        if annual_income < 250000:
            return IncomeTaxBracketIndia.EXEMPT
        elif annual_income < 500000:
            return IncomeTaxBracketIndia.FIVE_PERCENT
        elif annual_income < 1000000:
            return IncomeTaxBracketIndia.TWENTY_PERCENT
        else:
            return IncomeTaxBracketIndia.THIRTY_PERCENT

    def calculate_income_tax(self, gross_income: float, age: int = 60, has_hra: bool = False,
                            has_children: bool = False) -> Dict:
        """Calculate Indian income tax with deductions and surcharge"""
        taxable_income = gross_income

        # HRA exemption (rough estimate: 40-50% of basic in metros)
        hra_exemption = gross_income * 0.40 if has_hra else 0
        taxable_income -= hra_exemption

        # Standard deduction
        if gross_income <= 5000000:
            standard_deduction = min(75000, gross_income)
        else:
            standard_deduction = 75000
        taxable_income -= standard_deduction

        if taxable_income < 0:
            taxable_income = 0

        tax_bracket = self.determine_tax_bracket(taxable_income, age)
        base_tax = taxable_income * self.TAX_RATES[tax_bracket]

        # Calculate surcharge (only if gross > certain thresholds)
        surcharge = 0
        if gross_income > 5000000:
            surcharge_rate = 0.25 if gross_income > 10000000 else 0.15
            surcharge = base_tax * surcharge_rate

        # Education cess
        education_cess = (base_tax + surcharge) * self.EDUCATION_CESS

        total_tax = base_tax + surcharge + education_cess

        return {
            "gross_income": gross_income,
            "hra_exemption": hra_exemption,
            "standard_deduction": standard_deduction,
            "taxable_income": taxable_income,
            "base_tax": base_tax,
            "surcharge": surcharge,
            "education_cess": education_cess,
            "total_tax": total_tax,
            "tax_bracket": tax_bracket
        }

    def compare_strategies(
        self,
        annual_income: float,
        years_until_retirement: int,
        current_age: int,
        has_dependents: bool = True
    ) -> Dict[str, IndianTaxOptimizationStrategy]:
        """
        Compare different Indian tax optimization strategies

        Args:
            annual_income: Current annual income (₹)
            years_until_retirement: Years until retirement (age 60)
            current_age: Current age
            has_dependents: Whether player has family/dependents

        Returns:
            Dictionary of strategy results
        """
        strategies = {}

        # Strategy 1: Maximum Section 80C + PPF (Conservative, Safe)
        strategies["max_80c_ppf"] = self._simulate_max_80c_ppf(
            annual_income,
            years_until_retirement,
            current_age,
            has_dependents
        )

        # Strategy 2: NPS + ELSS (Growth-oriented, Tax-efficient)
        strategies["nps_elss"] = self._simulate_nps_elss(
            annual_income,
            years_until_retirement,
            current_age,
            has_dependents
        )

        # Strategy 3: Balanced Portfolio (Mixed approach)
        strategies["balanced"] = self._simulate_balanced(
            annual_income,
            years_until_retirement,
            current_age,
            has_dependents
        )

        # Strategy 4: Aggressive Growth (High risk, high return)
        strategies["aggressive"] = self._simulate_aggressive(
            annual_income,
            years_until_retirement,
            current_age,
            has_dependents
        )

        # Strategy 5: Minimal Tax Planning (Taxable only - baseline)
        strategies["taxable_only"] = self._simulate_taxable_only(
            annual_income,
            years_until_retirement,
            current_age,
            has_dependents
        )

        return strategies

    def _simulate_max_80c_ppf(
        self,
        income: float,
        years: int,
        current_age: int,
        has_dependents: bool
    ) -> IndianTaxOptimizationStrategy:
        """Maximize Section 80C with PPF + ELSS"""
        # Allocate ₹1.5L to Section 80C (PPF + ELSS)
        section_80c_limit = self.SECTION_80_LIMITS["80C"]
        ppf_contribution = section_80c_limit * 0.70  # ₹1.05L to PPF
        elss_contribution = section_80c_limit * 0.30  # ₹45K to ELSS

        # EPF deduction (already deducted from salary by employer)
        epf_contribution = income * self.EPF_EMPLOYEE_RATE
        epf_employer = income * self.EPF_EMPLOYER_RATE

        contributions_ppf = []
        contributions_elss = []
        balance_ppf = 0
        balance_elss = 0
        total_tax_saved = 0

        tax_bracket = self.determine_tax_bracket(income)
        tax_rate = self.TAX_RATES[tax_bracket]

        for year in range(1, years + 1):
            # PPF contribution with tax benefit
            tax_saved_ppf = ppf_contribution * tax_rate
            total_tax_saved += tax_saved_ppf

            balance_ppf += ppf_contribution
            balance_ppf *= (1 + self.PPF_RETURN)

            contributions_ppf.append(IndianAccountContribution(
                year=year,
                account_type=IndianAccountType.PPF,
                contribution=ppf_contribution,
                employer_contribution=0,
                tax_deduction=tax_saved_ppf,
                account_balance=balance_ppf,
                applicable_tax_bracket=tax_bracket
            ))

            # ELSS contribution (3-year lock-in)
            if year >= self.ELSS_LOCK_IN:
                tax_saved_elss = elss_contribution * tax_rate
                total_tax_saved += tax_saved_elss
            else:
                tax_saved_elss = 0

            balance_elss += elss_contribution
            balance_elss *= (1 + self.ELSS_RETURN)

            contributions_elss.append(IndianAccountContribution(
                year=year,
                account_type=IndianAccountType.ELSS,
                contribution=elss_contribution,
                employer_contribution=0,
                tax_deduction=tax_saved_elss,
                account_balance=balance_elss,
                applicable_tax_bracket=tax_bracket
            ))

        # PPF matures after 15 years (tax-free withdrawal)
        # ELSS after lock-in becomes taxable on gains
        total_balance = balance_ppf + balance_elss
        ppf_withdrawal_analysis = self._simulate_ppf_withdrawals(balance_ppf, 30)
        elss_withdrawal_analysis = self._simulate_capital_gains_withdrawals(balance_elss, 30)

        return IndianTaxOptimizationStrategy(
            strategy_name="Maximum Section 80C (PPF + ELSS + EPF)",
            accounts={
                IndianAccountType.PPF: contributions_ppf,
                IndianAccountType.ELSS: contributions_elss
            },
            total_contributed=(ppf_contribution + elss_contribution) * years,
            total_employer_contribution=epf_employer * years,
            total_tax_deductions=total_tax_saved,
            final_balance=total_balance,
            withdrawal_analysis=ppf_withdrawal_analysis,
            net_after_tax=sum(w.net_withdrawal for w in ppf_withdrawal_analysis),
            effective_tax_rate=self._calculate_effective_rate(ppf_withdrawal_analysis),
            annual_tax_savings=total_tax_saved / years
        )

    def _simulate_nps_elss(
        self,
        income: float,
        years: int,
        current_age: int,
        has_dependents: bool
    ) -> IndianTaxOptimizationStrategy:
        """NPS Tier-1 + ELSS strategy (Growth-oriented)"""
        section_80c = self.SECTION_80_LIMITS["80C"]
        section_80ccd = self.SECTION_80_LIMITS["80CCD"]

        # NPS Tier-1: ₹1.5L under 80C + ₹50K under 80CCD = ₹2L total
        nps_contribution = min(section_80c + section_80ccd, income * 0.20)
        elss_contribution = 0  # All 80C goes to NPS

        # EPF
        epf_contribution = income * self.EPF_EMPLOYEE_RATE
        epf_employer = income * self.EPF_EMPLOYER_RATE

        contributions_nps = []
        balance_nps = 0
        total_tax_saved = 0

        tax_bracket = self.determine_tax_bracket(income)
        tax_rate = self.TAX_RATES[tax_bracket]

        for year in range(1, years + 1):
            # NPS contributions get 80C + 80CCD deection
            tax_saved_nps = nps_contribution * tax_rate
            total_tax_saved += tax_saved_nps

            balance_nps += nps_contribution
            balance_nps *= (1 + self.NPS_RETURN)

            contributions_nps.append(IndianAccountContribution(
                year=year,
                account_type=IndianAccountType.NPS_TIER1,
                contribution=nps_contribution,
                employer_contribution=0,
                tax_deduction=tax_saved_nps,
                account_balance=balance_nps,
                applicable_tax_bracket=tax_bracket
            ))

        # NPS maturity after 60 - 40% lumpsum withdrawal (taxable), 60% annuity (taxed as income)
        withdrawal_analysis = self._simulate_nps_withdrawals(balance_nps, 30)

        return IndianTaxOptimizationStrategy(
            strategy_name="NPS Tier-1 (80C + 80CCD) + ELSS",
            accounts={IndianAccountType.NPS_TIER1: contributions_nps},
            total_contributed=nps_contribution * years,
            total_employer_contribution=epf_employer * years,
            total_tax_deductions=total_tax_saved,
            final_balance=balance_nps,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=sum(w.net_withdrawal for w in withdrawal_analysis),
            effective_tax_rate=self._calculate_effective_rate(withdrawal_analysis),
            annual_tax_savings=total_tax_saved / years
        )

    def _simulate_balanced(
        self,
        income: float,
        years: int,
        current_age: int,
        has_dependents: bool
    ) -> IndianTaxOptimizationStrategy:
        """Balanced: Split between NPS and PPF"""
        section_80c = self.SECTION_80_LIMITS["80C"]

        # 60% to PPF, 40% to ELSS for diversification
        ppf_contribution = section_80c * 0.60
        elss_contribution = section_80c * 0.40
        epf_contribution = income * self.EPF_EMPLOYEE_RATE
        epf_employer = income * self.EPF_EMPLOYER_RATE

        contributions_ppf = []
        contributions_elss = []
        balance_ppf = 0
        balance_elss = 0
        total_tax_saved = 0

        tax_bracket = self.determine_tax_bracket(income)
        tax_rate = self.TAX_RATES[tax_bracket]

        for year in range(1, years + 1):
            # PPF
            tax_saved_ppf = ppf_contribution * tax_rate
            total_tax_saved += tax_saved_ppf
            balance_ppf += ppf_contribution
            balance_ppf *= (1 + self.PPF_RETURN)

            contributions_ppf.append(IndianAccountContribution(
                year=year,
                account_type=IndianAccountType.PPF,
                contribution=ppf_contribution,
                employer_contribution=0,
                tax_deduction=tax_saved_ppf,
                account_balance=balance_ppf,
                applicable_tax_bracket=tax_bracket
            ))

            # ELSS
            tax_saved_elss = elss_contribution * tax_rate if year >= self.ELSS_LOCK_IN else 0
            total_tax_saved += tax_saved_elss
            balance_elss += elss_contribution
            balance_elss *= (1 + self.ELSS_RETURN)

            contributions_elss.append(IndianAccountContribution(
                year=year,
                account_type=IndianAccountType.ELSS,
                contribution=elss_contribution,
                employer_contribution=0,
                tax_deduction=tax_saved_elss,
                account_balance=balance_elss,
                applicable_tax_bracket=tax_bracket
            ))

        total_balance = balance_ppf + balance_elss
        withdrawal_analysis = self._simulate_balanced_withdrawals(balance_ppf, balance_elss, 30)

        return IndianTaxOptimizationStrategy(
            strategy_name="Balanced (PPF 60% + ELSS 40%)",
            accounts={
                IndianAccountType.PPF: contributions_ppf,
                IndianAccountType.ELSS: contributions_elss
            },
            total_contributed=(ppf_contribution + elss_contribution) * years,
            total_employer_contribution=epf_employer * years,
            total_tax_deductions=total_tax_saved,
            final_balance=total_balance,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=sum(w.net_withdrawal for w in withdrawal_analysis),
            effective_tax_rate=self._calculate_effective_rate(withdrawal_analysis),
            annual_tax_savings=total_tax_saved / years
        )

    def _simulate_aggressive(
        self,
        income: float,
        years: int,
        current_age: int,
        has_dependents: bool
    ) -> IndianTaxOptimizationStrategy:
        """Aggressive: High ELSS allocation for long-term capital appreciation"""
        section_80c = self.SECTION_80_LIMITS["80C"]
        section_80ccd = self.SECTION_80_LIMITS["80CCD"]

        # Allocate more to ELSS and NPS for growth
        elss_contribution = section_80c * 0.70
        nps_contribution = (section_80c + section_80ccd) * 0.30
        epf_contribution = income * self.EPF_EMPLOYEE_RATE
        epf_employer = income * self.EPF_EMPLOYER_RATE

        contributions_elss = []
        contributions_nps = []
        balance_elss = 0
        balance_nps = 0
        total_tax_saved = 0

        tax_bracket = self.determine_tax_bracket(income)
        tax_rate = self.TAX_RATES[tax_bracket]

        for year in range(1, years + 1):
            # ELSS (equity allocation)
            tax_saved_elss = elss_contribution * tax_rate if year >= self.ELSS_LOCK_IN else 0
            total_tax_saved += tax_saved_elss
            balance_elss += elss_contribution
            balance_elss *= (1 + self.ELSS_RETURN)

            contributions_elss.append(IndianAccountContribution(
                year=year,
                account_type=IndianAccountType.ELSS,
                contribution=elss_contribution,
                employer_contribution=0,
                tax_deduction=tax_saved_elss,
                account_balance=balance_elss,
                applicable_tax_bracket=tax_bracket
            ))

            # NPS (balanced growth)
            tax_saved_nps = nps_contribution * tax_rate
            total_tax_saved += tax_saved_nps
            balance_nps += nps_contribution
            balance_nps *= (1 + self.NPS_RETURN)

            contributions_nps.append(IndianAccountContribution(
                year=year,
                account_type=IndianAccountType.NPS_TIER1,
                contribution=nps_contribution,
                employer_contribution=0,
                tax_deduction=tax_saved_nps,
                account_balance=balance_nps,
                applicable_tax_bracket=tax_bracket
            ))

        total_balance = balance_elss + balance_nps
        withdrawal_analysis = self._simulate_capital_gains_withdrawals(balance_elss + balance_nps, 30)

        return IndianTaxOptimizationStrategy(
            strategy_name="Aggressive Growth (ELSS 70% + NPS 30%)",
            accounts={
                IndianAccountType.ELSS: contributions_elss,
                IndianAccountType.NPS_TIER1: contributions_nps
            },
            total_contributed=(elss_contribution + nps_contribution) * years,
            total_employer_contribution=epf_employer * years,
            total_tax_deductions=total_tax_saved,
            final_balance=total_balance,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=sum(w.net_withdrawal for w in withdrawal_analysis),
            effective_tax_rate=self._calculate_effective_rate(withdrawal_analysis),
            annual_tax_savings=total_tax_saved / years
        )

    def _simulate_taxable_only(
        self,
        income: float,
        years: int,
        current_age: int,
        has_dependents: bool
    ) -> IndianTaxOptimizationStrategy:
        """No tax planning - baseline comparison"""
        contribution = income * 0.10

        # Pay full income tax upfront
        tax_bracket = self.determine_tax_bracket(income)
        tax_rate = self.TAX_RATES[tax_bracket]
        after_tax_contribution = contribution * (1 - tax_rate)

        contributions = []
        balance = 0
        total_tax_paid = 0

        for year in range(1, years + 1):
            balance += after_tax_contribution
            balance *= (1 + self.TAXABLE_RETURN)
            total_tax_paid += contribution * tax_rate

            contributions.append(IndianAccountContribution(
                year=year,
                account_type=IndianAccountType.TAXABLE,
                contribution=after_tax_contribution,
                employer_contribution=0,
                tax_deduction=0,
                account_balance=balance,
                applicable_tax_bracket=tax_bracket
            ))

        # Capital gains tax on appreciation
        withdrawal_analysis = self._simulate_capital_gains_withdrawals(balance, 30)

        return IndianTaxOptimizationStrategy(
            strategy_name="Taxable Account Only (No Deductions)",
            accounts={IndianAccountType.TAXABLE: contributions},
            total_contributed=contribution * years,
            total_employer_contribution=0,
            total_tax_deductions=0,
            final_balance=balance,
            withdrawal_analysis=withdrawal_analysis,
            net_after_tax=sum(w.net_withdrawal for w in withdrawal_analysis),
            effective_tax_rate=self._calculate_effective_rate(withdrawal_analysis),
            annual_tax_savings=0
        )

    def _simulate_ppf_withdrawals(
        self,
        starting_balance: float,
        years: int
    ) -> List[WithdrawalResultIndia]:
        """PPF maturity withdrawals are TAX-FREE"""
        balance = starting_balance
        withdrawals = []
        annual_withdrawal = balance * 0.04  # 4% rule

        for year in range(1, years + 1):
            # PPF withdrawals after maturity are 100% tax-free
            taxes_owed = 0
            capital_gains = 0
            net_withdrawal = annual_withdrawal
            balance -= annual_withdrawal

            if balance > 0:
                balance *= (1 + self.PPF_RETURN * 0.6)

            withdrawals.append(WithdrawalResultIndia(
                year=year,
                withdrawal_amount=annual_withdrawal,
                capital_gains=0,
                capital_gains_tax=0,
                total_taxes_owed=0,
                net_withdrawal=net_withdrawal,
                remaining_balance=max(balance, 0)
            ))

        return withdrawals

    def _simulate_nps_withdrawals(
        self,
        starting_balance: float,
        years: int
    ) -> List[WithdrawalResultIndia]:
        """NPS withdrawal: 40% lumpsum (tax-free) + 60% annuity (taxed as income)"""
        balance = starting_balance
        withdrawals = []

        # At maturity (age 60):
        lumpsum = balance * 0.40  # Tax-free lumpsum
        annuity_corpus = balance * 0.60  # Taxed as income
        annual_annuity = annuity_corpus / years

        for year in range(1, years + 1):
            # Mix of tax-free lumpsum and taxable annuity
            if year == 1:
                withdrawal = lumpsum / years + annual_annuity
            else:
                withdrawal = lumpsum / years + annual_annuity

            # Annuity taxed at income tax rates (30% assumed for retiree)
            taxes_owed = annual_annuity * 0.30
            net_withdrawal = withdrawal - taxes_owed

            balance -= withdrawal
            if balance > 0:
                balance *= (1 + 0.05)  # Conservative growth in retirement

            withdrawals.append(WithdrawalResultIndia(
                year=year,
                withdrawal_amount=withdrawal,
                capital_gains=0,
                capital_gains_tax=taxes_owed,
                total_taxes_owed=taxes_owed,
                net_withdrawal=net_withdrawal,
                remaining_balance=max(balance, 0)
            ))

        return withdrawals

    def _simulate_capital_gains_withdrawals(
        self,
        starting_balance: float,
        years: int
    ) -> List[WithdrawalResultIndia]:
        """ELSS withdrawals with capital gains tax (20% LTCG after 3 years)"""
        balance = starting_balance
        cost_basis = starting_balance * 0.6  # Assume 40% gains
        withdrawals = []
        annual_withdrawal = balance * 0.04

        for year in range(1, years + 1):
            capital_gains = annual_withdrawal * 0.40
            capital_gains_tax = capital_gains * self.LTCG_EQUITY  # 20% LTCG
            taxes_owed = capital_gains_tax
            net_withdrawal = annual_withdrawal - taxes_owed

            balance -= annual_withdrawal
            if balance > 0:
                balance *= (1 + 0.08)

            withdrawals.append(WithdrawalResultIndia(
                year=year,
                withdrawal_amount=annual_withdrawal,
                capital_gains=capital_gains,
                capital_gains_tax=capital_gains_tax,
                total_taxes_owed=taxes_owed,
                net_withdrawal=net_withdrawal,
                remaining_balance=max(balance, 0)
            ))

        return withdrawals

    def _simulate_balanced_withdrawals(
        self,
        ppf_balance: float,
        elss_balance: float,
        years: int
    ) -> List[WithdrawalResultIndia]:
        """Mixed withdrawal: PPF (tax-free) + ELSS (capital gains tax)"""
        withdrawals = []
        ppf_bal = ppf_balance
        elss_bal = elss_balance
        total = ppf_bal + elss_bal
        annual_need = total * 0.04

        for year in range(1, years + 1):
            # Draw 60% from PPF (tax-free), 40% from ELSS (taxable)
            ppf_withdrawal = min(annual_need * 0.60, ppf_bal)
            elss_withdrawal = min(annual_need * 0.40, elss_bal)

            # PPF tax-free
            ppf_tax = 0

            # ELSS with capital gains tax
            capital_gains = elss_withdrawal * 0.40
            elss_tax = capital_gains * self.LTCG_EQUITY

            total_withdrawal = ppf_withdrawal + elss_withdrawal
            total_taxes = ppf_tax + elss_tax
            net_withdrawal = total_withdrawal - total_taxes

            ppf_bal -= ppf_withdrawal
            elss_bal -= elss_withdrawal

            if ppf_bal > 0:
                ppf_bal *= 1.075
            if elss_bal > 0:
                elss_bal *= 1.08

            withdrawals.append(WithdrawalResultIndia(
                year=year,
                withdrawal_amount=total_withdrawal,
                capital_gains=capital_gains if elss_withdrawal > 0 else 0,
                capital_gains_tax=elss_tax,
                total_taxes_owed=total_taxes,
                net_withdrawal=net_withdrawal,
                remaining_balance=ppf_bal + elss_bal
            ))

        return withdrawals

    def _calculate_effective_rate(self, withdrawals: List[WithdrawalResultIndia]) -> float:
        """Calculate effective tax rate over retirement"""
        if not withdrawals:
            return 0.0

        total_withdrawn = sum(w.withdrawal_amount for w in withdrawals)
        total_taxes = sum(w.total_taxes_owed for w in withdrawals)

        if total_withdrawn == 0:
            return 0.0

        return total_taxes / total_withdrawn

    def generate_recommendation(
        self,
        current_age: int,
        income: float,
        has_dependents: bool = True
    ) -> Dict:
        """Generate personalized Indian tax optimization recommendation"""
        years_to_60 = 60 - current_age
        recommendations = []

        # Priority 1: EPF (automatic, employer match is free money)
        epf_amount = income * self.EPF_EMPLOYEE_RATE
        epf_employer_match = income * self.EPF_EMPLOYER_RATE

        recommendations.append({
            "priority": 1,
            "strategy": "Maximize EPF (Employee Provident Fund)",
            "amount": f"₹{epf_amount:,.0f}/year (Employee) + ₹{epf_employer_match:,.0f} (Employer match)",
            "benefit": f"Builds retirement corpus of ₹{epf_amount * years_to_60 * 1.08:,.0f}+ tax-free",
            "tax_saved": f"₹{epf_amount * 0.30:,.0f}/year (at 30% bracket)"
        })

        # Priority 2: Section 80C optimization
        section_80c = self.SECTION_80_LIMITS["80C"]
        tax_bracket = self.determine_tax_bracket(income)
        tax_rate = self.TAX_RATES[tax_bracket]

        recommendations.append({
            "priority": 2,
            "strategy": "Max Section 80C (₹1.5L limit)",
            "options": "PPF + ELSS + Life Insurance + Home Loan Principal",
            "tax_saved": f"₹{section_80c * tax_rate:,.0f}/year at your {tax_bracket.value} bracket"
        })

        # Priority 3: Additional NPS (80CCD)
        if income > 500000:
            section_80ccd = self.SECTION_80_LIMITS["80CCD"]
            recommendations.append({
                "priority": 3,
                "strategy": "NPS Tier-1 + Section 80CCD (Extra ₹50K deduction)",
                "amount": f"₹{section_80ccd:,.0f}/year additional",
                "benefit": "Long-term locked corpus + tax-free at maturity (40% lumpsum + 60% annuity)",
                "tax_saved": f"₹{section_80ccd * tax_rate:,.0f}/year"
            })

        # Priority 4: Tax-free investments
        recommendations.append({
            "priority": 4,
            "strategy": "Health Insurance (Section 80D)",
            "amount": "₹25,000-₹1,50,000/year depending on age/family",
            "benefit": "Essential protection + tax deduction + returns usually tax-free"
        })

        # Age-specific advice
        if current_age < 35:
            recommendations.append({
                "priority": 5,
                "strategy": "Aggressive Growth Strategy (You have 25-30 years!)",
                "tips": "Maximize ELSS (equity funds), NPS, long-term holdings for C APital gains optimization",
                "insight": "Time is your best asset - compound growth on ₹2-3L/year can create ₹4-5 Cr corpus"
            })
        elif current_age < 50:
            recommendations.append({
                "priority": 5,
                "strategy": "Balanced Approach recommended",
                "tips": "Mix of PPF (safe) + ELSS/NPS (growth) + Insurance",
                "insight": f"You have ~{60-current_age} years - balance growth with stability"
            })
        else:
            recommendations.append({
                "priority": 5,
                "strategy": "Conservative Approach for retirement planning",
                "tips": "Shift to safe PPF, focus on steady income sources",
                "insight": f"Only {60-current_age} years to retirement - preserve capital while securing income"
            })

        return {
            "recommendations": recommendations,
            "current_bracket": tax_bracket,
            "tax_rate": f"{tax_rate*100:.0f}%",
            "annual_tax_optimization_potential": f"₹{section_80c * tax_rate + (section_80ccd * tax_rate if income > 500000 else 0):,.0f}"
        }
