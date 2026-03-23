export const paycheckGameConfig = {
  intro: {
    title: 'The Paycheck Game',
    description: 'Master the most important financial decision: how to allocate your paycheck. Learn the difference between "save first" and "spend first" strategies that can transform your wealth over decades.',
    icon: '💰',
    whyItMatters: 'Your paycheck allocation strategy determines your financial future. The order in which you handle savings, bills, and spending can change your net worth by millions over 40 years.',
    highlightColor: 'green'
  },
  examples: [
    {
      name: 'Aman (Save First)',
      story: 'Earns ₹50,000/month. Saves 20% first (₹10,000), pays bills with 60% (₹30,000), spends remaining 20% (₹10,000) guilt-free.',
      outcome: 'Saved: ₹12 Lakh/year',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Monthly Income', value: '₹50,000' },
        { label: 'Monthly Savings', value: '₹10,000' },
        { label: 'Annual Savings', value: '₹1.2 Lakh' },
        { label: 'Stress Level', value: 'Low' },
        { label: '10-Year Wealth', value: '₹15+ Lakh' }
      ]
    },
    {
      name: 'Bhavna (Bills First)',
      story: 'Same ₹50,000 income. Pays bills first (₹30,000), then spends (₹15,000), saves what\'s left (₹5,000). Good discipline.',
      outcome: 'Saved: ₹6 Lakh/year',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Monthly Income', value: '₹50,000' },
        { label: 'Monthly Savings', value: '₹5,000' },
        { label: 'Annual Savings', value: '₹60,000' },
        { label: 'Stress Level', value: 'Medium' },
        { label: '10-Year Wealth', value: '₹7-8 Lakh' }
      ]
    },
    {
      name: 'Chitra (Spend First)',
      story: 'Same income but prioritizes spending (₹35,000), then bills (₹13,000). Rarely saves the remaining ₹2,000.',
      outcome: 'Saved: ₹1.2 Lakh/year',
      outcomeType: 'negative' as const,
      metrics: [
        { label: 'Monthly Income', value: '₹50,000' },
        { label: 'Monthly Savings', value: '₹1,000' },
        { label: 'Annual Savings', value: '₹12,000' },
        { label: 'Stress Level', value: 'High' },
        { label: '10-Year Wealth', value: '₹1-2 Lakh' }
      ]
    }
  ],
  insightTemplates: [
    {
      threshold: 'high',
      text: 'Excellent! You\'re saving {saved_amount}/month ({annual_saved}/year). In 5 years, you\'ll have {five_year_savings}. By increasing to {optimized_amount}/month, you could reach {recommended_amount} in the same period!'
    },
    {
      threshold: 'medium',
      text: 'Good effort. You\'re saving {saved_amount}/month. To accelerate wealth: try the "Save First" strategy to boost to {recommended_amount}/month and reach {five_year_savings} in 5 years.'
    },
    {
      threshold: 'low',
      text: 'Your current savings of {saved_amount}/month ({annual_saved}/year) won\'t build wealth fast. Switch to "Save First" to increase to {recommended_amount}/month and create {five_year_savings} in 5 years.'
    }
  ],
  fallbackInsights: [
    'Save First is powerful: psychology shows that money moved to savings immediately is rarely touched.',
    'The 50/30/20 rule: 50% needs (bills), 30% wants (spending), 20% savings. Adjust based on income.',
    '₹10,000/month saved = ₹12 Lakh/year = ₹1.2 Crore in 10 years at 12% growth.',
    'Most people stress about money because they spend first and save crumbs. Reverse this.',
    'Automate your savings: if money stays in your account, temptation wins. Move it to a separate account immediately.',
    'Your paycheck strategy compounds: small differences in saving rate = massive wealth differences by retirement.'
  ]
}
