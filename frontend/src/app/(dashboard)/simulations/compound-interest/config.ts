export const compoundInterestConfig = {
  intro: {
    title: 'The Power of Compound Interest',
    description: 'Compound interest is what turns small, consistent investments into massive wealth over time. Learn how time and consistency create exponential growth.',
    icon: '📈',
    whyItMatters: 'Time is your greatest asset in wealth building. Compound interest works harder the longer it runs. Starting early, even with small amounts, can result in extraordinary wealth.',
    highlightColor: 'blue'
  },
  examples: [
    {
      name: 'Emma',
      story: 'Started investing ₹5,000/month at age 25. Stayed consistent for 40 years until retirement at 65.',
      outcome: 'Wealth: ₹2 Crore+',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Monthly Investment', value: '₹5,000' },
        { label: 'Investment Period', value: '40 years' },
        { label: 'Total Contributed', value: '₹24 Lakh' },
        { label: 'Final Amount', value: '₹2.05 Cr' },
        { label: 'Pure Growth', value: '₹1.81 Cr' }
      ]
    },
    {
      name: 'Rajesh',
      story: 'Made the same monthly investment of ₹5,000 but started 10 years later at age 35. Still stayed consistent until 65.',
      outcome: 'Wealth: ₹92 Lakh',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Monthly Investment', value: '₹5,000' },
        { label: 'Investment Period', value: '30 years' },
        { label: 'Total Contributed', value: '₹18 Lakh' },
        { label: 'Final Amount', value: '₹92 Lakh' },
        { label: 'Pure Growth', value: '₹74 Lakh' }
      ]
    },
    {
      name: 'Priya',
      story: 'Invested the same ₹5,000/month but started late at age 45. Only had 20 years to invest before retirement.',
      outcome: 'Wealth: ₹38 Lakh',
      outcomeType: 'neutral' as const,
      metrics: [
        { label: 'Monthly Investment', value: '₹5,000' },
        { label: 'Investment Period', value: '20 years' },
        { label: 'Total Contributed', value: '₹12 Lakh' },
        { label: 'Final Amount', value: '₹38 Lakh' },
        { label: 'Pure Growth', value: '₹26 Lakh' }
      ]
    }
  ],
  insightTemplates: [
    {
      threshold: 'high',
      text: 'Excellent strategy! Your investment of {total} represents a {multiple}x multiple on your contributions. Your disciplined approach will generate {growth} in pure growth. Consider increasing to {increase_amount} monthly for {optimized} potential!'
    },
    {
      threshold: 'medium',
      text: 'Great start! Your {total} investment shows strong compound growth. You\'re building {growth} through the power of time. To accelerate: boost monthly to {increase_amount} for {potential} potential.'
    },
    {
      threshold: 'low',
      text: 'Good foundation! Your investment will grow to {total} with {growth} in returns. Remember: consistency beats perfect timing. Even this disciplined approach creates wealth over {pure_growth}!'
    }
  ],
  fallbackInsights: [
    'Time is more powerful than returns. A 5% return over 40 years beats a 20% return over 5 years.',
    'Consistency matters more than perfection. Missing one month is 8% less wealth over a 30-year period.',
    'The "1000x" phenomenon: ₹100/day for 40 years at 12% annual = ₹3.8 Crore',
    'Start with what you can afford today, not what you might afford tomorrow. Starting with ₹1000/month beats starting with ₹10,000/month 10 years later.',
    'SIP (Systematic Investment Plan) is the best tool for ordinary Indians to build wealth - removes timing risk and emotion.'
  ]
}
