export const coffeeShopEffectConfig = {
  intro: {
    title: 'The Coffee Shop Effect',
    description: 'Small daily spending habits might seem harmless, but they compound into massive wealth leaks over time. Discover how ₹100/day becomes ₹3.6 Lakh/year—and what you could build instead.',
    icon: '☕',
    whyItMatters: 'Most people underestimate the power of small daily expenses. A coffee a day feels insignificant, but when invested instead, it could grow into lakhs over a decade. This simulation shows the hidden cost of micro-spending.'
  },
  examples: [
    {
      name: 'The Sippers',
      story: 'Spends ₹50/day on coffee and snacks. Annual expense: ₹18,250. Invested at 12% annually, could become ₹3.2 Lakh in 10 years.',
      outcome: 'Leaked: ₹1.82 Lakh',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Daily Spending', value: '₹50' },
        { label: 'Annual Cost', value: '₹18,250' },
        { label: '10-Year Cost', value: '₹1.82 Lakh' },
        { label: 'If Invested @ 12%', value: '₹3.2 Lakh' },
        { label: 'Opportunity Cost', value: '₹5.02 Lakh' }
      ]
    },
    {
      name: 'The Moderate',
      story: 'Spends ₹100/day on casual purchases. Annual expense: ₹36,500. Could accumulate to ₹6.4 Lakh if invested over 10 years.',
      outcome: 'Leaked: ₹3.65 Lakh',
      outcomeType: 'neutral' as const,
      metrics: [
        { label: 'Daily Spending', value: '₹100' },
        { label: 'Annual Cost', value: '₹36,500' },
        { label: '10-Year Cost', value: '₹3.65 Lakh' },
        { label: 'If Invested @ 12%', value: '₹6.4 Lakh' },
        { label: 'Opportunity Cost', value: '₹10.05 Lakh' }
      ]
    },
    {
      name: 'The Frequent',
      story: 'Spends ₹200/day on food, entertainment, and shopping. Annual expense: ₹73,000. This could transform into ₹12.8 Lakh with compound growth.',
      outcome: 'Leaked: ₹7.3 Lakh',
      outcomeType: 'negative' as const,
      metrics: [
        { label: 'Daily Spending', value: '₹200' },
        { label: 'Annual Cost', value: '₹73,000' },
        { label: '10-Year Cost', value: '₹7.3 Lakh' },
        { label: 'If Invested @ 12%', value: '₹12.8 Lakh' },
        { label: 'Opportunity Cost', value: '₹20.1 Lakh' }
      ]
    }
  ],
  insightTemplates: [
    {
      text: 'Your daily spending of {annual_amount}/year seems small, but here\'s the reality: if you invested that {annual_amount} annually for 10 years at 12%, it would grow to {invested_value}—that\'s the true cost of your habit.'
    }
  ],
  fallbackInsights: [
    'The coffee shop effect: Small daily expenses are invisible because they don\'t feel like debt, but they\'re just as damaging to wealth.',
    'Psychological blind spot: Your brain treats ₹50/day as "negligible," but ₹1.8 Lakh/year as "significant"—they\'re the same thing.',
    'Time multiplier: Money invested for 20 years grows 3-4x faster than money spent daily. Delay gratification = exponential wealth.',
    'The micro-spending trap: You think you\'re not a big spender, but micro-spending adds up to 30-40% of many household budgets.',
    'Habit design: Instead of willpower, redesign your habits. Pack lunch, brew coffee at home, unsubscribe from subscriptions you don\'t use.',
    'The 50% rule: If you can reduce daily spending by just 50%, you\'ll have enough to build a strong investment portfolio over 10 years.'
  ]
}
