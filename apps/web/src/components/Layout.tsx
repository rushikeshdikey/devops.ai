import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from './ui/Button'
import { Home, FolderGit2, Shield, FileText, LogOut } from 'lucide-react'

export default function Layout() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b">
        <div className="flex h-16 items-center px-4 container mx-auto">
          <div className="flex items-center space-x-4 flex-1">
            <h1 className="text-xl font-bold">DevOps Automation</h1>
            <div className="flex space-x-2 ml-8">
              <Link to="/">
                <Button variant="ghost" size="sm">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Button>
              </Link>
              <Link to="/projects">
                <Button variant="ghost" size="sm">
                  <FolderGit2 className="h-4 w-4 mr-2" />
                  Projects
                </Button>
              </Link>
              <Link to="/policies">
                <Button variant="ghost" size="sm">
                  <Shield className="h-4 w-4 mr-2" />
                  Policies
                </Button>
              </Link>
              <Link to="/audit">
                <Button variant="ghost" size="sm">
                  <FileText className="h-4 w-4 mr-2" />
                  Audit Logs
                </Button>
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm">
              <p className="font-medium">{user?.name}</p>
              <p className="text-muted-foreground text-xs">{user?.role}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </nav>
      <main className="container mx-auto py-6">
        <Outlet />
      </main>
    </div>
  )
}
