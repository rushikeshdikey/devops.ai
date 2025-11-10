import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { DollarSign, TrendingDown, Cloud, Zap, ArrowRight } from 'lucide-react'
import { subscriptionAPI, cloudAccountAPI, costAnalysisAPI } from '@/services/costOptimizer'
import type { CostAnalysis } from '@/types/costOptimizer'

export default function CostOptimizerPage() {
  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: async () => {
      const response = await subscriptionAPI.getCurrent()
      return response.data
    },
  })

  const { data: cloudAccounts } = useQuery({
    queryKey: ['cloud-accounts'],
    queryFn: async () => {
      const response = await cloudAccountAPI.list()
      return response.data
    },
  })

  const { data: analyses } = useQuery({
    queryKey: ['cost-analyses'],
    queryFn: async () => {
      const response = await costAnalysisAPI.list()
      return response.data
    },
  })

  const latestAnalysis: CostAnalysis | undefined = analyses?.[0]

  const totalSavings = analyses?.reduce(
    (sum: number, analysis: CostAnalysis) => sum + analysis.potential_savings,
    0
  ) || 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Cost Optimizer</h1>
          <p className="text-muted-foreground">
            AI-powered cloud cost optimization and savings recommendations
          </p>
        </div>
        <div className="flex space-x-2">
          <Link to="/cost-optimizer/accounts">
            <Button>
              <Cloud className="h-4 w-4 mr-2" />
              Manage Accounts
            </Button>
          </Link>
          {subscription?.plan === 'FREE' && (
            <Link to="/pricing">
              <Button variant="default">
                <Zap className="h-4 w-4 mr-2" />
                Upgrade to Premium
              </Button>
            </Link>
          )}
        </div>
      </div>

      {/* Subscription Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Current Plan: {subscription?.plan || 'FREE'}</span>
            {subscription?.plan === 'FREE' && (
              <span className="text-sm font-normal text-muted-foreground">
                Limited to 1 cloud account
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {subscription?.plan === 'FREE' ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Upgrade to Premium for unlimited cloud accounts, advanced AI recommendations, and
                priority support.
              </p>
              <Link to="/pricing">
                <Button size="sm">
                  View Pricing <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </div>
          ) : (
            <p className="text-sm text-green-600">
              ✓ Unlimited cloud accounts • Advanced AI • Priority support
            </p>
          )}
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Connected Accounts</CardTitle>
            <Cloud className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{cloudAccounts?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {subscription?.plan === 'FREE' ? 'Max 1 on Free' : 'Unlimited'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Monthly Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${latestAnalysis?.total_monthly_cost.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-muted-foreground">Across all accounts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potential Savings</CardTitle>
            <TrendingDown className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${latestAnalysis?.potential_savings.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-muted-foreground">
              {latestAnalysis?.savings_percentage.toFixed(1) || '0'}% reduction
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Recommendations</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {latestAnalysis?.recommendations.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">Optimization opportunities</p>
          </CardContent>
        </Card>
      </div>

      {/* Latest Analysis */}
      {latestAnalysis ? (
        <Card>
          <CardHeader>
            <CardTitle>Latest Cost Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium mb-2">Cost Breakdown</h4>
                <div className="space-y-2">
                  {Object.entries(latestAnalysis.cost_breakdown).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="capitalize">{key}</span>
                      <span className="font-medium">${(value as number).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">Top Recommendations</h4>
                <div className="space-y-2">
                  {latestAnalysis.recommendations.slice(0, 3).map((rec) => (
                    <div key={rec.id} className="text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">{rec.title}</span>
                        <span className="font-medium text-green-600">
                          ${rec.monthly_savings.toFixed(0)}/mo
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <Link to={`/cost-optimizer/analysis/${latestAnalysis.id}`}>
              <Button variant="outline" className="w-full">
                View Full Analysis <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-8 text-center">
            <Cloud className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">No cost analyses yet</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Connect a cloud account and run your first cost analysis
            </p>
            <Link to="/cost-optimizer/accounts">
              <Button>Get Started</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-4">
        <Link to="/cost-optimizer/accounts">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardContent className="pt-6">
              <Cloud className="h-8 w-8 mb-2" />
              <h3 className="font-medium mb-1">Connect Cloud Account</h3>
              <p className="text-sm text-muted-foreground">
                Add AWS, GCP, or Azure accounts for analysis
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link to="/pricing">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardContent className="pt-6">
              <Zap className="h-8 w-8 mb-2" />
              <h3 className="font-medium mb-1">Upgrade to Premium</h3>
              <p className="text-sm text-muted-foreground">
                Unlock unlimited accounts and advanced features
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link to="/cost-optimizer/analyses">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardContent className="pt-6">
              <TrendingDown className="h-8 w-8 mb-2" />
              <h3 className="font-medium mb-1">View All Analyses</h3>
              <p className="text-sm text-muted-foreground">
                Browse historical cost analyses and trends
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  )
}
