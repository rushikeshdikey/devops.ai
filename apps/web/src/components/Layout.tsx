import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from './ui/Button'
import { Home, Cloud, DollarSign, LogOut, Zap } from 'lucide-react'

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
            <Link to="/" className="flex items-center space-x-2">
              <DollarSign className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">Cloud Cost Optimizer</h1>
            </Link>
            <div className="flex space-x-2 ml-8">
              <Link to="/">
                <Button variant="ghost" size="sm">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Button>
              </Link>
              <Link to="/cost-optimizer">
                <Button variant="ghost" size="sm">
                  <Cloud className="h-4 w-4 mr-2" />
                  Cost Analysis
                </Button>
              </Link>
              <Link to="/pricing">
                <Button variant="ghost" size="sm">
                  <Zap className="h-4 w-4 mr-2" />
                  Pricing
                </Button>
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm">
              <p className="font-medium">{user?.name}</p>
              <p className="text-muted-foreground text-xs">{user?.email}</p>
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
