import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { useState } from 'react'
import { toast } from 'sonner'
import Editor from '@monaco-editor/react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Save, CheckCircle, Play, AlertCircle } from 'lucide-react'
import { formatDate } from '@/lib/utils'
import api from '@/services/api'

export default function ConfigWorkspacePage() {
  const { configId } = useParams()
  const queryClient = useQueryClient()
  const [content, setContent] = useState('')
  const [validationResult, setValidationResult] = useState<any>(null)

  const { data: config } = useQuery({
    queryKey: ['config', configId],
    queryFn: async () => {
      const response = await api.get(`/configs/${configId}`)
      return response.data
    },
  })

  const { data: versions } = useQuery({
    queryKey: ['versions', configId],
    queryFn: async () => {
      const response = await api.get(`/configs/${configId}/versions`)
      return response.data
    },
  })

  const { data: latestVersion } = useQuery({
    queryKey: ['version', config?.latest_version_id],
    queryFn: async () => {
      if (!config?.latest_version_id) return null
      const response = await api.get(`/versions/${config.latest_version_id}`)
      setContent(response.data.content)
      return response.data
    },
    enabled: !!config?.latest_version_id,
  })

  const createVersionMutation = useMutation({
    mutationFn: async (data: { content: string }) => {
      const response = await api.post(`/configs/${configId}/versions`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['versions', configId] })
      queryClient.invalidateQueries({ queryKey: ['config', configId] })
      toast.success('Version created successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create version')
    },
  })

  const validateMutation = useMutation({
    mutationFn: async (versionId: string) => {
      const response = await api.post(`/versions/${versionId}/validate`)
      return response.data
    },
    onSuccess: (data) => {
      setValidationResult(data)
      toast.success('Validation complete')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Validation failed')
    },
  })

  const handleSave = () => {
    createVersionMutation.mutate({ content })
  }

  const handleValidate = () => {
    if (latestVersion?.id) {
      validateMutation.mutate(latestVersion.id)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{config?.title}</h1>
        <p className="text-muted-foreground">{config?.type}</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Editor</CardTitle>
                <div className="space-x-2">
                  <Button size="sm" onClick={handleValidate} disabled={!latestVersion}>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Validate
                  </Button>
                  <Button size="sm" onClick={handleSave}>
                    <Save className="h-4 w-4 mr-2" />
                    Save Version
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="border rounded-md overflow-hidden">
                <Editor
                  height="500px"
                  language={config?.type === 'TERRAFORM' ? 'hcl' : 'yaml'}
                  value={content}
                  onChange={(value) => setContent(value || '')}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                  }}
                />
              </div>
            </CardContent>
          </Card>

          {validationResult && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  {validationResult.status === 'PASS' ? (
                    <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 mr-2 text-red-500" />
                  )}
                  Validation Result: {validationResult.status}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {validationResult.report.issues?.length > 0 ? (
                  <div className="space-y-2">
                    {validationResult.report.issues.map((issue: any, idx: number) => (
                      <div key={idx} className="text-sm">
                        <span
                          className={`font-medium ${
                            issue.level === 'ERROR'
                              ? 'text-red-500'
                              : issue.level === 'WARN'
                              ? 'text-yellow-500'
                              : 'text-blue-500'
                          }`}
                        >
                          [{issue.level}]
                        </span>{' '}
                        {issue.message}
                        {issue.path && <span className="text-muted-foreground"> - {issue.path}</span>}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No issues found</p>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Versions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {versions?.map((version: any) => (
                  <div
                    key={version.id}
                    className="p-2 border rounded hover:bg-accent cursor-pointer text-sm"
                  >
                    <div className="font-medium">v{version.version_number}</div>
                    <div className="text-xs text-muted-foreground">
                      {formatDate(version.created_at)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
