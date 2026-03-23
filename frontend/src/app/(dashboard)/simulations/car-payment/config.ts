export const carPaymentConfig = {
  intro: {
    title: 'The Car Payment Decision',
    description: 'Buying a car is often the second-largest expense after housing. Learn the 3 paths: Buy Cash, Finance, or Lease—and which kills your wealth the slowest.',
    icon: '🚗',
    whyItMatters: 'A ₹15 Lakh car decision today impacts your wealth for 7-10 years. Choose wisely: financing at 8% interest + insurance means you\'re paying ₹25,000/month for a depreciating asset that loses 50% value in 5 years.'
  },
  examples: [
    {
      name: 'Harsh (Buy Cash)',
      story: 'Saved ₹15 Lakh, bought car outright. Monthly insurance: ₹3,000. After 7 years, car worth ₹7.5 Lakh. Sold it, recovered half investment.',
      outcome: 'Total Cost: ₹15 Lakh → ₹7.5 Lakh',
      outcomeType: 'positive' as const,
      metrics: [
        { label: 'Upfront Cost', value: '₹15,00,000' },
        { label: 'Monthly Insurance', value: '₹3,000' },
        { label: 'Maintenance (7 yrs)', value: '₹2,00,000' },
        { label: 'Total Cost', value: '₹17,52,000' },
        { label: 'Resale Value', value: '₹7,50,000' },
        { label: 'Net Cost', value: '₹10,02,000' }
      ]
    },
    {
      name: 'Isha (Finance)',
      story: '₹3 Lakh down payment, financed ₹12 Lakh @ 8% for 60 months. EMI: ₹23,300 + insurance ₹3,000. Total cost including interest: ₹17.8 Lakh.',
      outcome: 'Monthly Burden: ₹26,300',
      outcomeType: 'neutral' as const,
      metrics: [
        { label: 'Down Payment', value: '₹3,00,000' },
        { label: 'Loan Amount', value: '₹12,00,000' },
        { label: 'Monthly EMI', value: '₹23,300' },
        { label: 'Monthly Insurance', value: '₹3,000' },
        { label: 'Total Monthly Cost', value: '₹26,300' },
        { label: 'Interest Paid Over 5 Yrs', value: '₹2,67,000' }
      ]
    },
    {
      name: 'Ravi (Lease)',
      story: 'Leases ₹15 Lakh car for 36 months. Monthly payment: ₹25,000. After 3 years, returns car—no residual value worry.',
      outcome: 'Monthly Payment: ₹25,000',
      outcomeType: 'negative' as const,
      metrics: [
        { label: 'Monthly Lease', value: '₹25,000' },
        { label: 'Lease Duration', value: '36 months' },
        { label: 'Processing Fee', value: '₹1,00,000' },
        { label: 'Total Cost (3 Yrs)', value: '₹10,00,000' },
        { label: 'Own Anything?', value: 'No' },
        { label: 'After 3 Yrs', value: 'Start Over' }
      ]
    }
  ],
  insightTemplates: [
    {
      threshold: 'high',
      text: 'Buying cash is wealth-smart: Your ₹{car_price} car costs ₹{total_cost_cash} over 7 years. You keep ₹{resale_value} in residual value. Compare: Financing costs ₹{total_cost_financed} (interest!) and Leasing costs ₹{total_cost_lease} with zero ownership.'
    },
    {
      threshold: 'medium',
      text: 'Financing ₹{car_price}: Your EMI ₹{monthly_emi} + insurance seems "affordable" but it\'s ₹{yearly_cost}/year for 5 years. That\'s ₹{total_cost_financed} total—only possible if your income > ₹{min_income}/month.'
    },
    {
      threshold: 'low',
      text: 'Leasing ₹{car_price} at ₹{monthly_lease}/month means ₹{total_lease_cost} every 3 years forever. After 20 years, you\'ll have paid ₹{total_20_years}—enough to own 2-3 cars outright!'
    }
  ],
  fallbackInsights: [
    'The car affordability rule: Your car EMI should not exceed 15-20% of monthly income. Higher = wealth destruction.',
    'Depreciation kills wealth: Cars lose 20% value year 1, 15% year 2, then 10% annually. Your ₹15 Lakh car = ₹7.5 Lakh in 5 years.',
    'Interest on depreciating assets is dangerous: You\'re paying 8% interest on an asset losing 15% value = 23% annual wealth loss.',
    'Lease trap: Every 3 years you restart with no equity. After 15 years of leasing, you\'ve paid ₹50 Lakh but own zero.',
    'The smart move: Save ₹15 Lakh, buy used car (5 years old) for ₹7.5 Lakh, invest remaining ₹7.5 Lakh = own asset + growing portfolio.',
    'Total cost of ownership includes: EMI/lease, insurance (₹3-8K/month), fuel (₹3-5K/month), maintenance (₹2-3K/month). Real monthly cost = ₹40K+ even after EMI ends.'
  ]
}
