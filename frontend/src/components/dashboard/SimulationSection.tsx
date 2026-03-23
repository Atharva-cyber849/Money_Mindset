'use client';

import SimulationCard from './SimulationCard';

const SIMULATIONS_DATA = [
  {
    id: 'paycheck-game',
    icon: '💸',
    name: 'Paycheck Game',
    description: 'Learn how to budget your monthly income wisely',
    learningValue: 'Budgeting Basics',
    tags: ['Finance', 'Budgeting'],
    href: '/simulations/paycheck-game',
    accentColor: 'green',
  },
  {
    id: 'coffee-shop-effect',
    icon: '☕',
    name: 'Coffee Shop Effect',
    description: 'See how small daily expenses compound into big money leaks',
    learningValue: 'Micro-spending Impact',
    tags: ['Spending', 'Growth'],
    new: true,
    href: '/simulations/coffee-shop-effect',
    accentColor: 'amber',
  },
  {
    id: 'compound-interest',
    icon: '📈',
    name: 'Compound Interest',
    description: 'Watch your money grow exponentially through investing',
    learningValue: 'Power of Compounding',
    tags: ['Investing', 'Growth'],
    featured: true,
    href: '/simulations/compound-interest',
    accentColor: 'teal',
  },
  {
    id: 'emergency-fund',
    icon: '🆘',
    name: 'Emergency Fund',
    description: 'Build your financial safety net step by step',
    learningValue: 'Financial Security',
    tags: ['Safety', 'Planning'],
    href: '/simulations/emergency-fund',
    accentColor: 'purple',
  },
  {
    id: 'credit-card-debt',
    icon: '💳',
    name: 'Credit Card Debt',
    description: 'Understand how credit card interest spirals out of control',
    learningValue: 'Debt Management',
    tags: ['Debt', 'Interest'],
    trending: true,
    href: '/simulations/credit-card-debt',
    accentColor: 'pink',
  },
  {
    id: 'budget-builder',
    icon: '📊',
    name: 'Budget Builder',
    description: 'Create an optimal budget for your income and goals',
    learningValue: 'Budget Planning',
    tags: ['Planning', 'Analysis'],
    href: '/simulations/budget-builder',
    accentColor: 'green',
  },
  {
    id: 'car-payment',
    icon: '🚗',
    name: 'Car Payment',
    description: 'See the true cost of buying vs leasing a vehicle',
    learningValue: 'Major Purchases',
    tags: ['Decisions', 'Planning'],
    href: '/simulations/car-payment',
    accentColor: 'amber',
  },
];

export default function SimulationSection() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">🔬 Simulations</h2>
          <p className="text-sm text-gray-600 mt-1">Interactive scenarios to explore financial concepts</p>
        </div>
        <div className="text-sm font-semibold px-3 py-1 bg-cyan-100 text-cyan-700 rounded-full">
          {SIMULATIONS_DATA.length} Available
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {SIMULATIONS_DATA.map((simulation) => (
          <SimulationCard
            key={simulation.id}
            {...simulation}
          />
        ))}
      </div>
    </div>
  );
}
