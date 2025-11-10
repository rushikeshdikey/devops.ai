import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { toast } from 'sonner'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import {
  DollarSign,
  TrendingDown,
  CheckCircle,
  XCircle,
  AlertCircle,
  Zap,
} from 'lucide-react'
import { costAnalysisAPI, recommendationAPI } from '@/services/costOptimizer'
import { formatDate } from '@/lib/utils'
import type { CostRecommendation } from '@/types/costOptimizer'

export default function CostAnalysisDetailPage() {
  const { analysisId } = useParams()
  const queryClient = useQueryClient()

  const { data: analysis, isLoading } = useQuery({
    queryKey: ['cost-analysis', analysisId],
    queryFn: async () => {
      const response = await costAnalysisAPI.get(analysisId!)
      return response.data
    },
  })

  const updateRecommendationMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'APPLY' | 'DISMISS' }) =>
      recommendationAPI.updateStatus(id, action),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['cost-analysis', analysisId] })
      toast.success(
        variables.action === 'APPLY'
          ? 'Recommendation marked as applied'
          : 'Recommendation dismissed'
      )
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update recommendation')
    },
  })

  if (isLoading) return <div>Loading...</div>

  if (!analysis) return <div>Analysis not found</div>

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH':
        return 'text-red-600 bg-red-50'
      case 'MEDIUM':
        return 'text-yellow-600 bg-yellow-50'
      case 'LOW':
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getEffortIcon = (effort: string) => {
    switch (effort) {
      case 'EASY':
        return '🟢'
      case 'MEDIUM':
        return '🟡'
      case 'HARD':
        return '🔴'
      default:
        return '⚪'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Cost Analysis Results</h1>
        <p className="text-muted-foreground">{formatDate(analysis.analysis_date)}</p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Monthly Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${analysis.total_monthly_cost.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">{analysis.resource_count} resources</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potential Savings</CardTitle>
            <TrendingDown className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${analysis.potential_savings.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              {analysis.savings_percentage.toFixed(1)}% reduction
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Annual Savings</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${(analysis.potential_savings * 12).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">If all applied</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recommendations</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analysis.recommendations.length}</div>
            <p className="text-xs text-muted-foreground">Optimization opportunities</p>
          </CardContent>
        </Card>
      </div>

      {/* Cost Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Cost Breakdown by Service</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(analysis.cost_breakdown).map(([service, cost]) => {
              const percentage = ((cost as number) / analysis.total_monthly_cost) * 100
              return (
                <div key={service} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="capitalize font-medium">{service}</span>
                    <span>${(cost as number).toFixed(2)}</span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <div className="text-xs text-muted-foreground">{percentage.toFixed(1)}%</div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Cost Optimization Recommendations</h2>
        <div className="space-y-4">
          {analysis.recommendations
            .sort((a: CostRecommendation, b: CostRecommendation) => {
              const priorityOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 }
              return (
                priorityOrder[a.priority as keyof typeof priorityOrder] -
                priorityOrder[b.priority as keyof typeof priorityOrder]
              )
            })
            .map((rec: CostRecommendation) => (
              <Card
                key={rec.id}
                className={rec.status === 'APPLIED' ? 'opacity-60' : ''}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span
                          className={`text-xs px-2 py-1 rounded ${getPriorityColor(rec.priority)}`}
                        >
                          {rec.priority}
                        </span>
                        <span className="text-xs px-2 py-1 rounded bg-secondary">
                          {rec.recommendation_type.replace(/_/g, ' ')}
                        </span>
                        <span className="text-xs">{getEffortIcon(rec.implementation_effort)} {rec.implementation_effort}</span>
                        {rec.status === 'APPLIED' && (
                          <span className="text-xs text-green-600 flex items-center">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Applied
                          </span>
                        )}
                        {rec.status === 'DISMISSED' && (
                          <span className="text-xs text-gray-600 flex items-center">
                            <XCircle className="h-3 w-3 mr-1" />
                            Dismissed
                          </span>
                        )}
                      </div>
                      <CardTitle className="text-lg">{rec.title}</CardTitle>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        ${rec.monthly_savings.toFixed(0)}
                      </div>
                      <div className="text-xs text-muted-foreground">/month</div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">{rec.description}</p>

                  <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Current Cost:</span>
                      <div className="font-medium">${rec.current_cost.toFixed(2)}/mo</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">New Cost:</span>
                      <div className="font-medium">${rec.estimated_new_cost.toFixed(2)}/mo</div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Annual Savings:</span>
                      <div className="font-medium text-green-600">
                        ${rec.annual_savings.toFixed(0)}
                      </div>
                    </div>
                  </div>

                  {rec.metadata && Object.keys(rec.metadata).length > 0 && (
                    <div className="bg-secondary p-3 rounded text-sm">
                      <div className="font-medium mb-2">Technical Details:</div>
                      <div className="space-y-1">
                        {Object.entries(rec.metadata).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-muted-foreground">
                              {key.replace(/_/g, ' ')}:
                            </span>
                            <span>{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {rec.status === 'PENDING' && (
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        onClick={() =>
                          updateRecommendationMutation.mutate({ id: rec.id, action: 'APPLY' })
                        }
                        disabled={updateRecommendationMutation.isPending}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Mark as Applied
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          updateRecommendationMutation.mutate({ id: rec.id, action: 'DISMISS' })
                        }
                        disabled={updateRecommendationMutation.isPending}
                      >
                        <XCircle className="h-4 w-4 mr-2" />
                        Dismiss
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
        </div>
      </div>
    </div>
  )
}
