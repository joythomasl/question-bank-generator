import { useState } from 'react'
import LoginPage from './components/LoginPage.jsx'
import UserPortal from './components/UserPortal.jsx'
import AdminPortal from './components/AdminPortal.jsx'

const SESSION_KEY = 'session_role_v1'

export default function App() {
  const [role, setRole] = useState(() => localStorage.getItem(SESSION_KEY) || null)

  function handleLogin(nextRole) {
    localStorage.setItem(SESSION_KEY, nextRole)
    setRole(nextRole)
  }

  function handleLogout() {
    localStorage.removeItem(SESSION_KEY)
    setRole(null)
  }

  if (!role) return <LoginPage onLogin={handleLogin} />
  if (role === 'admin') return <AdminPortal onLogout={handleLogout} />
  return <UserPortal onLogout={handleLogout} />
}
