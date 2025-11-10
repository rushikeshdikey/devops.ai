export interface Subscription {
  id: string
  user_id: string
  plan: 'FREE' | 'PREMIUM' | 'ENTERPRISE'
  status: 'ACTIVE' | 'CANCELED' | 'PAST_DUE'
  current_period_start?: string
  current_period_end?: string
  cancel_at_period_end: boolean
}

export interface CloudAccount {
  id: string
  user_id: string
  name: string
  provider: 'AWS' | 'GCP' | 'AZURE'
  region?: string
  is_active: boolean
  last_synced_at?: string
  created_at: string
}

export interface CostRecommendation {
  id: string
  resource_type: string
  resource_id: string
  recommendation_type: string
  title: string
  description: string
  current_cost: number
  estimated_new_cost: number
  monthly_savings: number
  annual_savings: number
  priority: 'HIGH' | 'MEDIUM' | 'LOW'
  implementation_effort: 'EASY' | 'MEDIUM' | 'HARD'
  status: 'PENDING' | 'APPLIED' | 'DISMISSED'
  metadata?: any
}

export interface CostAnalysis {
  id: string
  cloud_account_id: string
  analysis_date: string
  total_monthly_cost: number
  potential_savings: number
  savings_percentage: number
  resource_count: number
  cost_breakdown: {
    compute: number
    storage: number
    network: number
    database: number
    other: number
  }
  recommendations: CostRecommendation[]
}
