export const creditCardDebtConfig = {
  intro: {
    title: 'The Credit Card Debt Trap',
    description: 'Credit card debt is one of the fastest drains on wealth. At 24% annual interest, your debt compounds against you. Learn how minimum payments trap you for years.',
    icon: '💳',
    whyItMatters: 'Credit cards promise convenience but deliver financial slavery. A ₹1 Lakh debt at 24% interest could take 30+ months to clear if you only pay minimum. The interest you pay could have been invested.'
  },
  examples: [
    {
      name: 'Arun (Minimum Payment)',
      story: 'Borrowed ₹1 Lakh on CC at 24% annual (~2% monthly). Pays only minimum (3% of balance). Takes 63 months to clear debt.',
      outcome: 'Trapped: ₹63,200 interest paid',
      outcomeType: 'negative' as const,
      metrics: [
        { label: 'Initial Debt', value: '₹1,00,000' },
        { label: 'Interest Rate', value: '24% p.a. (2%/month)' },
        { label: 'Monthly Payment', value: '₹3,000 (minimum)' },
        { label: 'Months to Clear', value: '63' },
        { label: 'Total Interest Paid', value: '₹63,200' }
      ]
    },
    {
      name: 'Divya (Aggressive Payoff)',
      story: 'Same ₹1 Lakh debt. Pays ₹10,000/month aggressively. Clears in 11 months.',
      outcome: 'Free: ₹11,500 interest paid',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Initial Debt', value: '₹1,00,000' },
        { label: 'Interest Rate', value: '24% p.a.' },
        { label: 'Monthly Payment', value: '₹10,000' },
        { label: 'Months to Clear', value: '11' },
        { label: 'Total Interest Paid', value: '₹11,500' }
      ]
    },
    {
      name: 'Elena (Complete Avoidance)',
      story: 'Never borrows. Buys gadgets using saved money. No interest, no debt trap. Saves ₹1 Lakh in 10 months.',
      outcome: 'Wealthy: ₹1 Lakh saved',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Monthly Savings', value: '₹10,000' },
        { label: 'Annual Savings Goal', value: '₹1,20,000' },
        { label: 'Time to ₹1,00,000', value: '10 months' },
        { label: 'Interest Paid', value: '₹0' },
        { label: 'Net Wealth Gain', value: '₹1,00,000' }
      ]
    }
  ],
  insightTemplates: [
    {
      threshold: 'high',
      text: 'You\'re paying {monthly_payment}/month on {debt_amount} debt @ 24% interest. At this rate, you\'ll be debt-free in {months_to_clear} months and save {interest_saved} in interest. Keep pushing!'
    },
    {
      threshold: 'medium',
      text: 'Your {monthly_payment}/month payment will take {months_to_clear} months to clear {debt_amount}. You\'ll pay {total_interest} in interest. Try increasing to {aggressive_payment}/month to save {interest_saved}.'
    },
    {
      threshold: 'low',
      text: 'At your current {monthly_payment}/month, you\'ll pay off {debt_amount} in {months_to_clear} months, paying {total_interest} in interest—that\'s more than your principal! Increase payments urgently.'
    }
  ],
  fallbackInsights: [
    'Credit card interest compounds against you: A ₹50,000 debt at 24% becomes ₹56,244 in just 6 months of only minimum payments.',
    'The minimum payment trap: Credit card companies set minimums so low that you\'re mostly paying interest, not principal.',
    'Every ₹1,000 you add to your payment saves months and thousands in interest. ₹5,000/month vs ₹3,000/month saves ₹30,000+.',
    'The true cost of CC debt: A ₹1 Lakh purchase on CC for 5 years costs ₹1.63 Lakh total (63% premium!).',
    'Debt trap mechanics: 24% interest means you need to pay 24% every year just to stay even. Paying minimums means you\'re losing.',
    'Pro tip: If you must use CC, pay full balance every month. Use CC rewards only if you can afford to clear it immediately.'
  ]
}
