import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Shield } from 'lucide-react'
import { formatDate } from '@/lib/utils'
import api from '@/services/api'

export default function PoliciesPage() {
  const { data: policies, isLoading } = useQuery({
    queryKey: ['policies'],
    queryFn: async () => {
      const response = await api.get('/policies')
      return response.data
    },
  })

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Policies</h1>
        <p className="text-muted-foreground">Manage validation policies</p>
      </div>

      <div className="grid gap-4">
        {policies?.map((policy: any) => (
          <Card key={policy.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <CardTitle className="text-lg">{policy.name}</CardTitle>
                </div>
                <span className="text-xs bg-secondary px-2 py-1 rounded">{policy.scope}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Rule: </span>
                  <code className="text-xs bg-muted px-2 py-1 rounded">{policy.rule}</code>
                </div>
                <p className="text-xs text-muted-foreground">
                  Created {formatDate(policy.created_at)}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
