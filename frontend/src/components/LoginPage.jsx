import { useState } from 'react'

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
    <div className="bg-orbs min-h-screen flex items-center justify-center px-6 relative">
      <div className="w-full max-w-3xl relative z-10">
        {/* ── Header ── */}
        <div className="opacity-0 animate-slide-up text-center mb-10">
          <p className="text-muted font-mono text-xs uppercase tracking-[0.25em] mb-3">
            Question Bank Portal
          </p>
          <h1 className="font-display text-3xl md:text-4xl font-bold bg-gradient-to-r from-bone via-catDp to-catDc bg-clip-text text-transparent">
            Choose how you're signing in
          </h1>
        </div>

        {/* ── Cards ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* User card */}
          <div className="opacity-0 animate-slide-up-delay-1 glass-card glass-card-hover rounded-2xl p-7 flex flex-col gap-5 group">
            <div>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-catTwoPointers/20 to-catTwoPointers/5 flex items-center justify-center text-lg mb-4 group-hover:animate-float">
                ⚡
              </div>
              <p className="font-mono text-xs text-muted uppercase tracking-widest">
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
              className="mt-auto btn-gradient py-3 text-sm rounded-xl"
            >
              Enter portal →
            </button>
          </div>

          {/* Admin card */}
          <form
            onSubmit={handleAdminSubmit}
            className="opacity-0 animate-slide-up-delay-2 glass-card glass-card-hover rounded-2xl p-7 flex flex-col gap-5 group"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-catDc/20 to-catDc/5 flex items-center justify-center text-lg mb-4 group-hover:animate-float">
                🔒
              </div>
              <p className="font-mono text-xs text-muted uppercase tracking-widest">
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
              className="bg-ink/60 border border-surfaceRaised rounded-xl px-4 py-3 text-sm input-glow"
            />
            {error && (
              <p
                className={`text-danger text-xs transition-transform ${shakeError ? 'animate-[shake_0.3s_ease-in-out]' : ''}`}
                style={shakeError ? { animation: 'shake 0.3s ease-in-out' } : {}}
              >
                {error}
              </p>
            )}
            <button
              id="login-admin-btn"
              type="submit"
              className="mt-auto bg-transparent border border-surfaceRaised/60 rounded-xl py-3 font-medium text-sm text-muted hover:text-bone hover:border-catDc/40 hover:bg-catDc/5 transition-all duration-200"
            >
              Sign in as admin
            </button>
          </form>
        </div>

        <p className="opacity-0 animate-slide-up-delay-3 text-center text-xs text-muted/60 mt-10">
          This is a demo-scale login for a college project, not a production auth system.
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
