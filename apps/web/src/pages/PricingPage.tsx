import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Check, Zap, Crown } from 'lucide-react'
import { subscriptionAPI } from '@/services/costOptimizer'

export default function PricingPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedPlan, setSelectedPlan] = useState<'FREE' | 'PREMIUM' | null>(null)

  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: async () => {
      const response = await subscriptionAPI.getCurrent()
      return response.data
    },
  })

  const upgradeMutation = useMutation({
    mutationFn: async (plan: string) => {
      const response = await subscriptionAPI.upgrade(plan)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] })
      toast.success('Subscription updated successfully!')
      navigate('/cost-optimizer')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update subscription')
    },
  })

  const handleUpgrade = (plan: 'FREE' | 'PREMIUM') => {
    setSelectedPlan(plan)

    if (plan === 'PREMIUM') {
      // In production, integrate with Stripe Checkout here
      // For now, just simulate the upgrade
      upgradeMutation.mutate(plan)
    } else {
      upgradeMutation.mutate(plan)
    }
  }

  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for trying out the platform',
      features: [
        '1 cloud account',
        'Basic cost analysis',
        'Monthly savings reports',
        'Email support',
        'Cost breakdown by service',
        'Basic recommendations',
      ],
      cta: 'Get Started',
      plan: 'FREE' as const,
      icon: Check,
      popular: false,
    },
    {
      name: 'Premium',
      price: '$29',
      period: 'per month',
      description: 'Unlimited cost optimization',
      features: [
        'Unlimited cloud accounts',
        'Advanced AI recommendations',
        'Priority support',
        'Auto-apply optimizations',
        'Weekly detailed reports',
        'Cost trends & forecasting',
        'Multi-cloud comparison',
        'Custom alerts & notifications',
        'API access',
      ],
      cta: 'Upgrade to Premium',
      plan: 'PREMIUM' as const,
      icon: Crown,
      popular: true,
    },
  ]

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold">Simple, Transparent Pricing</h1>
        <p className="text-xl text-muted-foreground">
          Start saving on cloud costs today
        </p>
      </div>

      {subscription?.plan && (
        <Card className="border-primary">
          <CardContent className="pt-6 text-center">
            <p className="text-sm">
              Your current plan:{' '}
              <span className="font-bold">{subscription.plan}</span>
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid md:grid-cols-2 gap-6 mt-8">
        {plans.map((plan) => (
          <Card
            key={plan.name}
            className={`relative ${
              plan.popular ? 'border-primary shadow-lg scale-105' : ''
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="bg-primary text-primary-foreground text-xs font-bold px-3 py-1 rounded-full">
                  MOST POPULAR
                </div>
              </div>
            )}

            <CardHeader>
              <div className="flex items-center space-x-2 mb-2">
                <plan.icon className="h-6 w-6" />
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
              </div>
              <div className="space-y-1">
                <div className="flex items-baseline">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground ml-2">/{plan.period}</span>
                </div>
                <p className="text-sm text-muted-foreground">{plan.description}</p>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              <ul className="space-y-3">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <Check className="h-5 w-5 text-green-600 mr-2 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                className="w-full"
                variant={plan.popular ? 'default' : 'outline'}
                onClick={() => handleUpgrade(plan.plan)}
                disabled={
                  upgradeMutation.isPending || subscription?.plan === plan.plan
                }
              >
                {subscription?.plan === plan.plan
                  ? 'Current Plan'
                  : upgradeMutation.isPending && selectedPlan === plan.plan
                  ? 'Processing...'
                  : plan.cta}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ROI Calculator */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Return on Investment</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">40%</div>
              <div className="text-sm text-muted-foreground">Average savings</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary">$14,000</div>
              <div className="text-sm text-muted-foreground">Avg. annual savings per customer</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">48x</div>
              <div className="text-sm text-muted-foreground">ROI on Premium plan</div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-secondary rounded-lg">
            <p className="text-sm text-center">
              <strong>Example:</strong> If you're spending $3,500/month on cloud costs,
              Premium could save you ~$1,400/month ($16,800/year) for just $29/month
              ($348/year). That's a <strong className="text-green-600">48x return</strong> on
              investment!
            </p>
          </div>
        </CardContent>
      </Card>

      {/* FAQ */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium mb-1">Can I cancel anytime?</h4>
            <p className="text-sm text-muted-foreground">
              Yes! You can cancel your Premium subscription at any time. Your access will
              continue until the end of your billing period.
            </p>
          </div>
          <div>
            <h4 className="font-medium mb-1">What cloud providers do you support?</h4>
            <p className="text-sm text-muted-foreground">
              We currently support AWS, Google Cloud Platform (GCP), and Microsoft Azure.
            </p>
          </div>
          <div>
            <h4 className="font-medium mb-1">Is my data secure?</h4>
            <p className="text-sm text-muted-foreground">
              Absolutely. We use read-only credentials and encrypt all sensitive data. We never
              make changes to your infrastructure without your explicit approval.
            </p>
          </div>
          <div>
            <h4 className="font-medium mb-1">Do you offer refunds?</h4>
            <p className="text-sm text-muted-foreground">
              Yes! If you're not satisfied within the first 30 days, we'll provide a full refund,
              no questions asked.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
