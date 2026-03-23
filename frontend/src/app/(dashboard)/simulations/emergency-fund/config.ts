export const emergencyFundConfig = {
  intro: {
    title: 'Emergency Fund: Your Financial Parachute',
    description: 'An emergency fund is your safety net against life\'s unexpected events. Learn how building 3-6 months of expenses can save you from debt and financial stress.',
    icon: '🆘',
    whyItMatters: 'Without an emergency fund, unexpected expenses (job loss, medical emergency, car breakdown) force you into debt. An emergency fund lets you face crises without panic—it\'s financial peace of mind.'
  },
  examples: [
    {
      name: 'Rohan (No Emergency Fund)',
      story: 'Monthly expenses: ₹50,000. Car breaks down (₹80,000 repair). Has to use credit card at 24% annual interest. Takes 18 months to pay off.',
      outcome: 'Debt Trapped: ₹21,600 interest paid',
      outcomeType: 'negative' as const,
      metrics: [
        { label: 'Monthly Expenses', value: '₹50,000' },
        { label: 'Emergency Cost', value: '₹80,000' },
        { label: 'CC Interest 24% p.a.', value: '₹21,600' },
        { label: 'Total Paid Back', value: '₹1,01,600' },
        { label: 'Months to Clear', value: '18' }
      ]
    },
    {
      name: 'Shruti (3 Months Fund)',
      story: 'Monthly expenses: ₹50,000. Saved ₹1.5 Lakh (3 months fund). Same emergency costs cash. No debt, stress-free recovery.',
      outcome: 'Safe: ₹1.5 Lakh Emergency Buffer',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Monthly Expenses', value: '₹50,000' },
        { label: 'Emergency Fund (3 mo)', value: '₹1.5 Lakh' },
        { label: 'Emergency Cost', value: '₹80,000' },
        { label: 'Fund Remaining', value: '₹70,000' },
        { label: 'Interest Paid', value: '₹0' }
      ]
    },
    {
      name: 'Vikram (6 Months Fund)',
      story: 'Monthly expenses: ₹50,000. Built ₹3 Lakh fund over 18 months. Lost job for 3 months while finding work. Fund covered everything.',
      outcome: 'Secure: ₹3 Lakh Emergency Buffer',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Monthly Expenses', value: '₹50,000' },
        { label: 'Emergency Fund (6 mo)', value: '₹3 Lakh' },
        { label: 'Job Loss Period', value: '3 months' },
        { label: 'Total Covered', value: '₹1.5 Lakh' },
        { label: 'Fund Remaining', value: '₹1.5 Lakh' }
      ]
    }
  ],
  insightTemplates: [
    {
      threshold: 'low',
      text: 'You have a target of {target_months} months ({target_amount}). You\'ve saved {saved_amount} so far. At {monthly_rate}/month, you\'ll reach your goal in {months_needed} months. One emergency could ruin you now—accelerate!'
    },
    {
      threshold: 'medium',
      text: 'Great progress! You\'ve saved {saved_amount} toward {target_amount}. You\'re {percent_complete}% there. Keep building—this fund will save you from debt in emergencies.'
    },
    {
      threshold: 'high',
      text: 'Excellent! You\'ve fully funded your {target_months}-month emergency fund ({target_amount}). You\'re now protected against unexpected events. Consider building additional investments with surplus income.'
    }
  ],
  fallbackInsights: [
    'Emergency funds save lives: 60% of Indians have zero emergency savings. A ₹50,000 emergency becomes ₹1 Lakh debt without a fund.',
    'The 3-month minimum: Your fund should cover 3 months of essential expenses (rent, food, utilities, transport only—not wants).',
    'Build fast with automation: ₹5,000/month = ₹60,000/year = ₹1.8 Lakh in 3 years (3 months for ₹50,000 expenses).',
    'Keep it accessible: Your emergency fund should be in savings account or liquid mutual funds (not stocks that might crash).',
    'One thing at a time: Build emergency fund first, then invest. A loan at 15% interest destroys investment gains.',
    'The ₹3 Lakh rule: If your monthly expenses are ₹50,000, build ₹3 Lakh (6 months). This covers job loss, health crisis, everything.'
  ]
}
