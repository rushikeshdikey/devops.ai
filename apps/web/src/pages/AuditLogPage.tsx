import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { formatDate } from '@/lib/utils'
import api from '@/services/api'

export default function AuditLogPage() {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['audit'],
    queryFn: async () => {
      const response = await api.get('/audit')
      return response.data
    },
  })

  if (isLoading) return <div>Loading...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audit Logs</h1>
        <p className="text-muted-foreground">Track all system activities</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {logs?.map((log: any) => (
              <div key={log.id} className="flex items-center justify-between p-3 border rounded">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm">{log.action}</span>
                    <span className="text-xs text-muted-foreground">{log.subject_type}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatDate(log.created_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
