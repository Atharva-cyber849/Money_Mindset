'use client'

import { useState } from 'react'
import {
  DollarSign,
  TrendingUp,
  Target,
  Zap,
  Search,
  Mail,
  CheckCircle,
  AlertTriangle,
  Info,
  Plus,
  Download,
  Trash2,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, StatCard } from '@/components/ui/Card'
import { Input, CurrencyInput, Textarea } from '@/components/ui/Input'
import { Badge, PillButton, CountBadge, Status } from '@/components/ui/Pill'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { SimpleTooltip } from '@/components/ui/Tooltip'
import {
  Container,
  PageHeader,
  Section,
  Grid,
  Stack,
} from '@/components/ui/Layout'

export default function DesignSystemDemo() {
  const [inputValue, setInputValue] = useState('')
  const [currencyValue, setCurrencyValue] = useState(1000)
  const [activeTab, setActiveTab] = useState('all')

  return (
    <Container size="xl" padding>
      <PageHeader
        title="Design System Showcase"
        subtitle="Complete UI Component Library for Money Mindset"
        backLink={{ href: '/dashboard', label: 'Back to Dashboard' }}
      />

      {/* Buttons */}
      <Section title="Buttons" subtitle="All button variants and sizes">
        <Stack direction="vertical" gap={6}>
          {/* Primary Buttons */}
          <div>
            <h4 className="text-sm font-semibold text-text-secondary mb-3 uppercase">
              Primary Buttons
            </h4>
            <Stack direction="horizontal" gap={3}>
              <Button variant="primary" size="sm">
                Small
              </Button>
              <Button variant="primary" size="md">
                Medium
              </Button>
              <Button variant="primary" size="lg">
                Large
              </Button>
              <Button variant="primary" icon={Plus}>
                With Icon
              </Button>
              <Button variant="primary" isLoading>
                Loading
              </Button>
            </Stack>
          </div>

          {/* Secondary Buttons */}
          <div>
            <h4 className="text-sm font-semibold text-text-secondary mb-3 uppercase">
              Secondary & Other Variants
            </h4>
            <Stack direction="horizontal" gap={3}>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="danger" icon={Trash2}>
                Delete
              </Button>
              <Button variant="primary" disabled>
                Disabled
              </Button>
            </Stack>
          </div>
        </Stack>
      </Section>

      {/* Stat Cards */}
      <Section title="Stat Cards" subtitle="Animated statistic displays">
        <Grid cols={4} gap={6}>
          <StatCard
            title="Total Balance"
            value="$5,432"
            icon={DollarSign}
            iconColor="bg-wealth-green"
            trend="up"
            change={12.5}
            animate={true}
          />
          <StatCard
            title="Monthly Savings"
            value="$1,234"
            icon={Target}
            iconColor="bg-blue-500"
            trend="up"
            change={8}
            animate={true}
          />
          <StatCard
            title="Investments"
            value="$12,450"
            icon={TrendingUp}
            iconColor="bg-purple-500"
            trend="up"
            change={15.2}
            animate={true}
          />
          <StatCard
            title="XP Points"
            value={1250}
            icon={Zap}
            iconColor="bg-yellow-500"
            animate={true}
          />
        </Grid>
      </Section>

      {/* Inputs */}
      <Section title="Form Inputs" subtitle="Text inputs, currency, and more">
        <Grid cols={2} gap={6}>
          <Card>
            <Stack direction="vertical" gap={4}>
              <Input
                label="Email Address"
                type="email"
                placeholder="you@example.com"
                icon={Mail}
              />

              <Input
                label="Search"
                placeholder="Search transactions..."
                icon={Search}
              />

              <CurrencyInput
                label="Transaction Amount"
                value={currencyValue}
                onValueChange={setCurrencyValue}
              />

              <Input
                label="With Error"
                error="This field is required"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
            </Stack>
          </Card>

          <Card>
            <Stack direction="vertical" gap={4}>
              <Textarea
                label="Notes"
                placeholder="Add transaction notes..."
                rows={6}
              />

              <Stack direction="horizontal" gap={3} justify="end">
                <Button variant="ghost">Cancel</Button>
                <Button variant="primary">Save Changes</Button>
              </Stack>
            </Stack>
          </Card>
        </Grid>
      </Section>

      {/* Badges & Pills */}
      <Section title="Badges & Pills" subtitle="Status indicators and filters">
        <Grid cols={2} gap={6}>
          <Card>
            <h4 className="text-lg font-semibold mb-4">Status Badges</h4>
            <Stack direction="horizontal" gap={3}>
              <Badge variant="success" icon={CheckCircle}>
                Success
              </Badge>
              <Badge variant="warning" icon={AlertTriangle}>
                Warning
              </Badge>
              <Badge variant="danger" icon={AlertTriangle}>
                Danger
              </Badge>
              <Badge variant="info" icon={Info}>
                Info
              </Badge>
              <Badge variant="neutral">Neutral</Badge>
            </Stack>

            <div className="mt-6">
              <h5 className="text-sm font-semibold mb-3">Sizes</h5>
              <Stack direction="horizontal" gap={3}>
                <Badge size="sm">Small</Badge>
                <Badge size="md">Medium</Badge>
                <Badge size="lg">Large</Badge>
              </Stack>
            </div>
          </Card>

          <Card>
            <h4 className="text-lg font-semibold mb-4">Pill Buttons & Indicators</h4>
            <Stack direction="horizontal" gap={3}>
              <PillButton
                variant="info"
                active={activeTab === 'all'}
                onClick={() => setActiveTab('all')}
              >
                All
              </PillButton>
              <PillButton
                variant="success"
                active={activeTab === 'completed'}
                onClick={() => setActiveTab('completed')}
              >
                Completed
              </PillButton>
              <PillButton
                variant="warning"
                active={activeTab === 'pending'}
                onClick={() => setActiveTab('pending')}
              >
                Pending
              </PillButton>
            </Stack>

            <div className="mt-6">
              <h5 className="text-sm font-semibold mb-3">Special Badges</h5>
              <Stack direction="horizontal" gap={4}>
                <div className="flex items-center gap-2">
                  <span>Notifications</span>
                  <CountBadge count={5} variant="danger" />
                </div>
                <div className="flex items-center gap-2">
                  <span>New Messages</span>
                  <CountBadge count={99} variant="info" />
                </div>
                <Status status="online" showLabel />
              </Stack>
            </div>
          </Card>
        </Grid>
      </Section>

      {/* Progress Bars */}
      <Section title="Progress Bars" subtitle="Various progress indicators">
        <Card>
          <Stack direction="vertical" gap={6}>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Budget Progress</span>
                <span className="text-sm font-mono font-bold">75%</span>
              </div>
              <ProgressBar percent={75} color="green" animate={true} />
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Savings Goal</span>
                <span className="text-sm font-mono font-bold">$3,000 / $5,000</span>
              </div>
              <ProgressBar percent={60} color="blue" height="h-4" animate={true} />
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Warning Level</span>
                <span className="text-sm font-mono font-bold">85%</span>
              </div>
              <ProgressBar percent={85} color="yellow" animate={true} />
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Over Budget</span>
                <span className="text-sm font-mono font-bold text-danger-red">
                  110%
                </span>
              </div>
              <ProgressBar percent={110} color="red" animate={true} />
            </div>
          </Stack>
        </Card>
      </Section>

      {/* Cards */}
      <Section title="Cards" subtitle="Content containers with hover effects">
        <Grid cols={3} gap={6}>
          <Card hover>
            <h3 className="text-lg font-bold mb-2">Hoverable Card</h3>
            <p className="text-text-secondary">
              Hover over this card to see the lift effect with shadow.
            </p>
          </Card>

          <Card animate>
            <h3 className="text-lg font-bold mb-2">Animated Card</h3>
            <p className="text-text-secondary">
              This card fades in on page load with GSAP animation.
            </p>
          </Card>

          <Card className="bg-gradient-wealth text-white">
            <h3 className="text-lg font-bold mb-2">Gradient Card</h3>
            <p className="text-white/90">
              Custom styled card with gradient background.
            </p>
          </Card>
        </Grid>
      </Section>

      {/* Tooltips */}
      <Section title="Tooltips" subtitle="Helpful hover information">
        <Card>
          <Stack direction="horizontal" gap={6}>
            <SimpleTooltip content="This is a helpful tooltip">
              <Button variant="primary">Hover for tooltip</Button>
            </SimpleTooltip>

            <SimpleTooltip content="Additional information about this feature">
              <Badge variant="info" icon={Info}>
                Info Badge
              </Badge>
            </SimpleTooltip>

            <SimpleTooltip content="Click to download your report">
              <Button variant="secondary" icon={Download}>
                Download Report
              </Button>
            </SimpleTooltip>
          </Stack>
        </Card>
      </Section>

      {/* Color Palette */}
      <Section title="Color Palette" subtitle="Design system colors">
        <Grid cols={4} gap={6}>
          <Card>
            <h4 className="text-sm font-semibold mb-3">Wealth Green</h4>
            <div className="space-y-2">
              <div className="h-12 bg-wealth-green rounded flex items-center justify-center text-white font-mono text-sm">
                #10B981
              </div>
              <div className="h-12 bg-wealth-green-light rounded flex items-center justify-center text-wealth-green-dark font-mono text-sm">
                Light
              </div>
              <div className="h-12 bg-wealth-green-dark rounded flex items-center justify-center text-white font-mono text-sm">
                Dark
              </div>
            </div>
          </Card>

          <Card>
            <h4 className="text-sm font-semibold mb-3">Warning Amber</h4>
            <div className="space-y-2">
              <div className="h-12 bg-warning-amber rounded flex items-center justify-center text-white font-mono text-sm">
                #F59E0B
              </div>
              <div className="h-12 bg-warning-amber-light rounded flex items-center justify-center text-amber-800 font-mono text-sm">
                Light
              </div>
            </div>
          </Card>

          <Card>
            <h4 className="text-sm font-semibold mb-3">Danger Red</h4>
            <div className="space-y-2">
              <div className="h-12 bg-danger-red rounded flex items-center justify-center text-white font-mono text-sm">
                #EF4444
              </div>
              <div className="h-12 bg-danger-red-light rounded flex items-center justify-center text-red-800 font-mono text-sm">
                Light
              </div>
            </div>
          </Card>

          <Card>
            <h4 className="text-sm font-semibold mb-3">Info Blue</h4>
            <div className="space-y-2">
              <div className="h-12 bg-info-blue rounded flex items-center justify-center text-white font-mono text-sm">
                #3B82F6
              </div>
              <div className="h-12 bg-info-blue-light rounded flex items-center justify-center text-blue-800 font-mono text-sm">
                Light
              </div>
            </div>
          </Card>
        </Grid>
      </Section>

      {/* Typography */}
      <Section title="Typography" subtitle="Font families and sizes">
        <Card>
          <Stack direction="vertical" gap={4}>
            <div>
              <p className="text-sm text-text-secondary mb-2">Display Font (Poppins)</p>
              <h1 className="font-display text-4xl font-bold">
                The quick brown fox jumps over the lazy dog
              </h1>
            </div>

            <div>
              <p className="text-sm text-text-secondary mb-2">Primary Font (Inter)</p>
              <p className="font-primary text-lg">
                The quick brown fox jumps over the lazy dog
              </p>
            </div>

            <div>
              <p className="text-sm text-text-secondary mb-2">Mono Font (JetBrains Mono)</p>
              <p className="font-mono text-lg">
                $1,234.56 • 2024-02-07 • ABC123
              </p>
            </div>
          </Stack>
        </Card>
      </Section>

      {/* Footer */}
      <div className="mt-12 text-center text-sm text-text-muted">
        <p className="mb-2">
          💡 This design system provides a consistent UI foundation for Money Mindset
        </p>
        <p>
          See <code className="bg-background px-2 py-1 rounded text-text-primary">
            DESIGN_SYSTEM.md
          </code>{' '}
          for complete documentation
        </p>
      </div>
    </Container>
  )
}
