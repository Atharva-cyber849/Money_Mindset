"use client";

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { ArrowRight, Gamepad2, Calculator, PiggyBank, CreditCard, TrendingUp, Home, DollarSign, Zap } from 'lucide-react';

const simulations = [
  {
    title: 'Coffee Shop Effect',
    description: 'See how small daily purchases compound over time',
    href: '/simulations/coffee-shop-effect',
    icon: Zap,
    color: 'bg-amber-500',
  },
  {
    title: 'Compound Interest',
    description: 'Watch your investments grow exponentially',
    href: '/simulations/compound-interest',
    icon: TrendingUp,
    color: 'bg-green-500',
  },
  {
    title: 'Emergency Fund',
    description: 'Build financial resilience step by step',
    href: '/simulations/emergency-fund',
    icon: PiggyBank,
    color: 'bg-blue-500',
  },
  {
    title: 'Credit Card Debt',
    description: 'Understand the true cost of revolving debt',
    href: '/simulations/credit-card-debt',
    icon: CreditCard,
    color: 'bg-red-500',
  },
  {
    title: 'Budget Builder',
    description: 'Create a personalized spending plan',
    href: '/simulations/budget-builder',
    icon: Calculator,
    color: 'bg-purple-500',
  },
  {
    title: 'Car Payment Simulator',
    description: 'Compare lease vs buy vs cash',
    href: '/simulations/car-payment',
    icon: Home,
    color: 'bg-indigo-500',
  },
  {
    title: 'Paycheck Game',
    description: 'Learn to allocate your income wisely',
    href: '/simulations/paycheck-game',
    icon: DollarSign,
    color: 'bg-emerald-500',
  },
];

export default function SimulationsPage() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Financial Simulations</h1>
        <p className="text-muted-foreground text-lg">
          Interactive experiences to master money management
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {simulations.map((simulation) => {
          const Icon = simulation.icon;
          return (
            <Card key={simulation.title} hover animate className="p-6">
              <div className={`w-12 h-12 ${simulation.color} rounded-lg flex items-center justify-center mb-4`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">{simulation.title}</h3>
              <p className="text-muted-foreground mb-4">{simulation.description}</p>
              <Link href={simulation.href}>
                <Button className="w-full group">
                  Start Simulation
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </Card>
          );
        })}
      </div>

      <div className="mt-12 p-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg text-white">
        <div className="flex items-center gap-4">
          <Gamepad2 className="w-12 h-12" />
          <div className="flex-1">
            <h2 className="text-2xl font-bold mb-2">New to Simulations?</h2>
            <p className="opacity-90">
              Start with the Coffee Shop Effect to see how small changes make a big impact on your financial future.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
