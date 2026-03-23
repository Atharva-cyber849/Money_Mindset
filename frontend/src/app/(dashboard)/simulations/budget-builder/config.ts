export const budgetBuilderConfig = {
  intro: {
    title: 'The 50/30/20 Budget Framework',
    description: 'The most effective budget splits your income into three categories: 50% Needs (essentials), 30% Wants (lifestyle), 20% Savings. Learn to build wealth every month without feeling deprived.',
    icon: '📊',
    whyItMatters: 'Most people fail at budgeting because it feels restrictive. The 50/30/20 framework is designed for both responsibility AND happiness. It ensures you save for future while enjoying life today.'
  },
  examples: [
    {
      name: 'Meera (50/30/20 Perfect)',
      story: 'Monthly income: ₹1,00,000. Allocates ₹50K to needs (rent, food, bills), ₹30K to wants (dining, entertainment), ₹20K to savings. Lifestyle: Comfortable. Savings: ₹2.4 Lakh/year.',
      outcome: 'Balanced: ₹2.4 Lakh/year saved',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Monthly Income', value: '₹1,00,000' },
        { label: 'Needs (50%)', value: '₹50,000' },
        { label: 'Wants (30%)', value: '₹30,000' },
        { label: 'Savings (20%)', value: '₹20,000' },
        { label: 'Annual Savings', value: '₹2,40,000' },
        { label: '10-Year Wealth @ 12%', value: '₹40+ Lakh' }
      ]
    },
    {
      name: 'Arjun (70/25/5 Reality)',
      story: 'Same ₹1,00,000 income. Actually spends ₹70K on needs (high rent) + ₹25K on wants, leaving only ₹5K savings. Savings: ₹60K/year. Feels poor despite good income.',
      outcome: 'Imbalanced: Only ₹60K/year',
      outcomeType: 'neutral' as const,
      metrics: [
        { label: 'Monthly Income', value: '₹1,00,000' },
        { label: 'Needs (70%)', value: '₹70,000' },
        { label: 'Wants (25%)', value: '₹25,000' },
        { label: 'Savings (5%)', value: '₹5,000' },
        { label: 'Annual Savings', value: '₹60,000' },
        { label: '10-Year Wealth @ 12%', value: '₹10 Lakh only' }
      ]
    },
    {
      name: 'Priya (80/15/5 Disaster)',
      story: 'Same ₹1,00,000 but lives beyond means: ₹80K needs (expensive area), ₹15K wants, saves ₹5K. Adding to debt. Savings: ₹60K/year but growing debt = negative net worth.',
      outcome: 'Crisis: Going into debt',
      outcomeType: 'negative' as const,
      metrics: [
        { label: 'Monthly Income', value: '₹1,00,000' },
        { label: 'Needs (80%)', value: '₹80,000' },
        { label: 'Wants (15%)', value: '₹15,000' },
        { label: 'Savings (5%)', value: '₹5,000' },
        { label: 'Actually Saves', value: '-₹10,000 (borrows!)' },
        { label: 'Annual Debt Increase', value: '₹1,20,000' }
      ]
    }
  ],
  insightTemplates: [
    {
      threshold: 'high',
      text: 'Perfect 50/30/20! Your ₹{income}/month budget: ₹{needs} needs, ₹{wants} wants, ₹{savings} savings. Annual wealth: ₹{annual_savings}. In 10 years @ 12% = ₹{ten_year_wealth}. You\'re on track to become wealthy.'
    },
    {
      threshold: 'medium',
      text: 'Your actual split: {actual_needs}% needs, {actual_wants}% wants, {actual_savings}% savings. You\'re oversaving on needs or spending too much on wants. Adjust: move ₹{adjustment_amount} from wants to savings to reach 20% target.'
    },
    {
      threshold: 'low',
      text: 'Alert: Your {actual_savings}% savings rate is unsustainable wealth-wise. You\'re saving only ₹{actual_savings_amount}/month = ₹{annual_savings} yearly. Target 20% = ₹{target_savings}/month for ₹{target_annual}/year wealth building.'
    }
  ],
  fallbackInsights: [
    'The 50% needs ceiling: If your needs exceed 50%, consider downsizing home or changing location. Housing is the biggest wealth killer.',
    'The 30% wants trap: Most people allocate 50-60% to wants because they blur the line between "needs" and "wants". Food = need. Dining out = want.',
    'The 20% savings minimum: Anything less than 20% savings won\'t build wealth. Most Indians save <5% and stay poor forever.',
    'Adjust for life stage: Young? Can do 40% needs / 20% wants / 40% savings. Retired? Can shift to 50% needs / 30% wants / 20% leisure.',
    'The compound effect: ₹20K/month @ 12% annual growth = ₹2.4 Lakh/year = ₹40 Lakh in 10 years. That\'s your retirement fund.',
    'Psychological hack: The 50/30/20 framework removes guilt. You ALWAYS have 30% for wants without feeling bad. Most strict budgets fail because people deny themselves.'
  ]
}
