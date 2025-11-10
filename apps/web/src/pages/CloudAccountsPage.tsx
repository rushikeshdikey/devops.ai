import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Plus, Trash2, Cloud, Play } from 'lucide-react'
import { cloudAccountAPI, costAnalysisAPI, subscriptionAPI } from '@/services/costOptimizer'
import { formatDate } from '@/lib/utils'
import { useNavigate } from 'react-router-dom'

export default function CloudAccountsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    provider: 'AWS',
    region: '',
    accessKeyId: '',
    secretAccessKey: '',
  })

  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: async () => {
      const response = await subscriptionAPI.getCurrent()
      return response.data
    },
  })

  const { data: accounts, isLoading } = useQuery({
    queryKey: ['cloud-accounts'],
    queryFn: async () => {
      const response = await cloudAccountAPI.list()
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await cloudAccountAPI.create({
        name: data.name,
        provider: data.provider,
        region: data.region || undefined,
        credentials: {
          access_key_id: data.accessKeyId,
          secret_access_key: data.secretAccessKey,
        },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cloud-accounts'] })
      toast.success('Cloud account connected successfully')
      setShowAddForm(false)
      setFormData({
        name: '',
        provider: 'AWS',
        region: '',
        accessKeyId: '',
        secretAccessKey: '',
      })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to connect cloud account')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => cloudAccountAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cloud-accounts'] })
      toast.success('Cloud account disconnected')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to disconnect account')
    },
  })

  const analyzeMutation = useMutation({
    mutationFn: async (accountId: string) => {
      const response = await costAnalysisAPI.run(accountId)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['cost-analyses'] })
      toast.success('Cost analysis completed')
      navigate(`/cost-optimizer/analysis/${data.id}`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Analysis failed')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const canAddAccount = subscription?.plan !== 'FREE' || !accounts || accounts.length === 0

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Cloud Accounts</h1>
          <p className="text-muted-foreground">Connect and manage your cloud accounts</p>
        </div>
        <Button onClick={() => setShowAddForm(!showAddForm)} disabled={!canAddAccount}>
          <Plus className="h-4 w-4 mr-2" />
          Add Account
        </Button>
      </div>

      {!canAddAccount && (
        <Card className="border-yellow-300 bg-yellow-50">
          <CardContent className="pt-6">
            <p className="text-sm">
              You've reached the limit for Free tier (1 account). Upgrade to Premium for unlimited
              cloud accounts.
            </p>
            <Button
              size="sm"
              className="mt-2"
              onClick={() => navigate('/pricing')}
            >
              Upgrade to Premium
            </Button>
          </CardContent>
        </Card>
      )}

      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>Connect Cloud Account</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Account Name</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Production AWS Account"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">Cloud Provider</label>
                <select
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="AWS">Amazon Web Services (AWS)</option>
                  <option value="GCP">Google Cloud Platform (GCP)</option>
                  <option value="AZURE">Microsoft Azure</option>
                </select>
              </div>

              <div>
                <label className="text-sm font-medium">Region (optional)</label>
                <Input
                  value={formData.region}
                  onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                  placeholder="us-east-1"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Access Key ID / Client ID</label>
                <Input
                  value={formData.accessKeyId}
                  onChange={(e) => setFormData({ ...formData, accessKeyId: e.target.value })}
                  placeholder="AKIA..."
                  required
                />
                <p className="text-xs text-muted-foreground mt-1">
                  For demo purposes, any value works. In production, use read-only IAM credentials.
                </p>
              </div>

              <div>
                <label className="text-sm font-medium">Secret Access Key</label>
                <Input
                  type="password"
                  value={formData.secretAccessKey}
                  onChange={(e) =>
                    setFormData({ ...formData, secretAccessKey: e.target.value })
                  }
                  placeholder="•••••••••••••"
                  required
                />
              </div>

              <div className="flex space-x-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Connecting...' : 'Connect Account'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowAddForm(false)}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {accounts?.map((account: any) => (
          <Card key={account.id}>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-3">
                  <Cloud className="h-5 w-5" />
                  <div>
                    <CardTitle className="text-lg">{account.name}</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {account.provider} {account.region && `• ${account.region}`}
                    </p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    onClick={() => analyzeMutation.mutate(account.id)}
                    disabled={analyzeMutation.isPending}
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Run Analysis
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => deleteMutation.mutate(account.id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-sm space-y-1">
                <p>
                  <span className="text-muted-foreground">Status: </span>
                  <span className="text-green-600">● Active</span>
                </p>
                <p>
                  <span className="text-muted-foreground">Added: </span>
                  {formatDate(account.created_at)}
                </p>
                {account.last_synced_at && (
                  <p>
                    <span className="text-muted-foreground">Last analyzed: </span>
                    {formatDate(account.last_synced_at)}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {accounts?.length === 0 && !showAddForm && (
        <Card>
          <CardContent className="py-8 text-center">
            <Cloud className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">No cloud accounts connected</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Connect your first cloud account to start optimizing costs
            </p>
            <Button onClick={() => setShowAddForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Cloud Account
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
