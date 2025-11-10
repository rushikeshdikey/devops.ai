import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import CostOptimizerPage from './pages/CostOptimizerPage'
import CloudAccountsPage from './pages/CloudAccountsPage'
import CostAnalysisDetailPage from './pages/CostAnalysisDetailPage'
import PricingPage from './pages/PricingPage'
import Layout from './components/Layout'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="cost-optimizer" element={<CostOptimizerPage />} />
          <Route path="cost-optimizer/accounts" element={<CloudAccountsPage />} />
          <Route path="cost-optimizer/analysis/:analysisId" element={<CostAnalysisDetailPage />} />
          <Route path="pricing" element={<PricingPage />} />
        </Route>
      </Routes>
      <Toaster />
    </>
  )
}

export default App
