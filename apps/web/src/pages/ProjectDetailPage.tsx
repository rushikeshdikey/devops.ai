import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { useState } from 'react'
import { toast } from 'sonner'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Plus, FileCode } from 'lucide-react'
import { formatDate } from '@/lib/utils'
import api from '@/services/api'

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [title, setTitle] = useState('')
  const [type, setType] = useState('K8S_YAML')

  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const response = await api.get(`/projects/${projectId}`)
      return response.data
    },
  })

  const { data: configs } = useQuery({
    queryKey: ['configs', projectId],
    queryFn: async () => {
      const response = await api.get(`/projects/${projectId}/configs`)
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: { title: string; type: string }) => {
      const response = await api.post(`/projects/${projectId}/configs`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configs', projectId] })
      toast.success('Configuration created successfully')
      setShowCreate(false)
      setTitle('')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create configuration')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({ title, type })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{project?.name}</h1>
        <p className="text-muted-foreground">{project?.description}</p>
      </div>

      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Configurations</h2>
        <Button onClick={() => setShowCreate(!showCreate)}>
          <Plus className="h-4 w-4 mr-2" />
          New Config
        </Button>
      </div>

      {showCreate && (
        <Card>
          <CardHeader>
            <CardTitle>Create Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Title</label>
                <Input value={title} onChange={(e) => setTitle(e.target.value)} required />
              </div>
              <div>
                <label className="text-sm font-medium">Type</label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="K8S_YAML">Kubernetes YAML</option>
                  <option value="TERRAFORM">Terraform</option>
                  <option value="GENERIC_YAML">Generic YAML</option>
                </select>
              </div>
              <div className="flex space-x-2">
                <Button type="submit" disabled={createMutation.isPending}>
                  Create
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowCreate(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {configs?.map((config: any) => (
          <Link key={config.id} to={`/configs/${config.id}`}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <FileCode className="h-5 w-5" />
                    <CardTitle className="text-lg">{config.title}</CardTitle>
                  </div>
                  <span className="text-xs bg-secondary px-2 py-1 rounded">{config.type}</span>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  Created {formatDate(config.created_at)}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
