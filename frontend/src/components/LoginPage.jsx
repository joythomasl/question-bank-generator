import { useState } from 'react'
import { BoltIcon, LockIcon } from './icons.jsx'
import ThemeToggle from './ThemeToggle.jsx'
import HudCorners from './HudCorners.jsx'

// Mock gate only — this is a demo-scale check, not real authentication.
// Fine for a college project with no sensitive data behind it; swap for
// real auth (e.g. Firebase Authentication's free tier) if that ever changes.
const ADMIN_PASSWORD = 'admin123'

export default function LoginPage({ onLogin }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [shakeError, setShakeError] = useState(false)

  function handleAdminSubmit(e) {
    e.preventDefault()
    if (password === ADMIN_PASSWORD) {
      onLogin('admin')
    } else {
      setError('Incorrect password')
      setShakeError(true)
      setTimeout(() => setShakeError(false), 500)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6 relative">
      <div className="bg-grid" />
      <div className="bg-particles" />
      <div className="bg-orbs" />
      <div className="fixed top-6 right-6 z-20">
        <ThemeToggle />
      </div>
      <div className="w-full max-w-3xl relative z-10">
        {/* ── Header ── */}
        <div className="opacity-0 animate-slide-up text-center mb-10">
          <p className="text-muted text-xs font-medium uppercase tracking-[0.25em] mb-3">
            Question Bank Portal
          </p>
          <h1 className="font-display text-3xl md:text-4xl font-semibold bg-gradient-to-r from-bone via-catDp to-catDc bg-clip-text text-transparent">
            Choose how you're signing in
          </h1>
        </div>

        {/* ── Cards ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* User card */}
          <div className="opacity-0 animate-slide-up-delay-1 hud-tile hud-tile-interactive p-7 flex flex-col gap-5 group relative">
            <HudCorners color="#22D3EE" />
            <div>
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-catTwoPointers/25 to-catTwoPointers/5 border border-line/10 flex items-center justify-center text-catTwoPointers mb-4 group-hover:animate-float">
                <BoltIcon />
              </div>
              <p className="text-xs text-muted font-medium uppercase tracking-widest">
                Standard access
              </p>
              <p className="text-lg font-semibold mt-1 font-display">Continue as user</p>
              <p className="text-sm text-muted mt-2 leading-relaxed">
                Browse, filter, and download verified questions. No account needed.
              </p>
            </div>
            <button
              id="login-user-btn"
              onClick={() => onLogin('user')}
              className="mt-auto hud-btn-primary py-3 text-sm"
            >
              Enter portal →
            </button>
          </div>

          {/* Admin card */}
          <form
            onSubmit={handleAdminSubmit}
            className="opacity-0 animate-slide-up-delay-2 hud-tile hud-tile-interactive p-7 flex flex-col gap-5 group relative"
          >
            <HudCorners color="#C084FC" />
            <div>
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-catDc/25 to-catDc/5 border border-line/10 flex items-center justify-center text-catDc mb-4 group-hover:animate-float">
                <LockIcon />
              </div>
              <p className="text-xs text-muted font-medium uppercase tracking-widest">
                Restricted access
              </p>
              <p className="text-lg font-semibold mt-1 font-display">Admin login</p>
              <p className="text-sm text-muted mt-2 leading-relaxed">
                Manage the question bank and view generation analytics.
              </p>
            </div>
            <input
              id="admin-password-input"
              type="password"
              placeholder="Admin password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setError('')
              }}
              className="rounded-2xl px-4 py-3 text-sm hud-input"
            />
            {error && (
              <p
                className="text-danger text-xs"
                style={shakeError ? { animation: 'shake 0.3s ease-in-out' } : {}}
              >
                {error}
              </p>
            )}
            <button
              id="login-admin-btn"
              type="submit"
              className="mt-auto hud-btn-ghost py-3 font-medium text-sm"
            >
              Sign in as admin
            </button>
          </form>
        </div>

        <p className="opacity-0 animate-slide-up-delay-3 text-center text-xs text-muted/70 mt-10">
          Guest browsing requires no account. Admin access is limited to maintainers.
        </p>
      </div>

      {/* Shake keyframes (inline for the error animation) */}
      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          20% { transform: translateX(-6px); }
          40% { transform: translateX(6px); }
          60% { transform: translateX(-4px); }
          80% { transform: translateX(4px); }
        }
      `}</style>
    </div>
  )
}
