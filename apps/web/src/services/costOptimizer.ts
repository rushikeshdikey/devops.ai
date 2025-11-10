import api from './api'

// Subscription APIs
export const subscriptionAPI = {
  getCurrent: () => api.get('/billing/subscription'),
  upgrade: (plan: string, paymentMethodId?: string) =>
    api.post('/billing/subscription', { plan, payment_method_id: paymentMethodId }),
  cancel: () => api.post('/billing/subscription/cancel'),
}

// Cloud Account APIs
export const cloudAccountAPI = {
  list: () => api.get('/cost-optimizer/cloud-accounts'),
  create: (data: { name: string; provider: string; credentials: any; region?: string }) =>
    api.post('/cost-optimizer/cloud-accounts', data),
  get: (id: string) => api.get(`/cost-optimizer/cloud-accounts/${id}`),
  delete: (id: string) => api.delete(`/cost-optimizer/cloud-accounts/${id}`),
}

// Cost Analysis APIs
export const costAnalysisAPI = {
  run: (cloudAccountId: string) =>
    api.post('/cost-optimizer/analyze', { cloud_account_id: cloudAccountId }),
  list: (cloudAccountId?: string) => {
    const params = cloudAccountId ? `?cloud_account_id=${cloudAccountId}` : ''
    return api.get(`/cost-optimizer/analyses${params}`)
  },
  get: (id: string) => api.get(`/cost-optimizer/analyses/${id}`),
}

// Recommendation APIs
export const recommendationAPI = {
  updateStatus: (id: string, action: 'APPLY' | 'DISMISS') =>
    api.patch(`/cost-optimizer/recommendations/${id}`, { action }),
}
