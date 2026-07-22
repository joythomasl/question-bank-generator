import { useState } from 'react'

// Mock gate only — this is a demo-scale check, not real authentication.
// Fine for a college project with no sensitive data behind it; swap for
// real auth (e.g. Firebase Authentication's free tier) if that ever changes.
const ADMIN_PASSWORD = 'admin123'

export default function LoginPage({ onLogin }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  function handleAdminSubmit(e) {
    e.preventDefault()
    if (password === ADMIN_PASSWORD) {
      onLogin('admin')
    } else {
      setError('Incorrect password')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-3xl">
        <p className="text-center text-muted font-mono text-xs uppercase tracking-widest mb-2">
          Question bank portal
        </p>
        <h1 className="text-center text-2xl font-semibold mb-10">
          Choose how you're signing in
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-surface border border-surfaceRaised rounded-xl p-6 flex flex-col gap-4">
            <div>
              <p className="font-mono text-xs text-muted uppercase tracking-widest">
                Standard access
              </p>
              <p className="text-lg font-medium mt-1">Continue as user</p>
              <p className="text-sm text-muted mt-2">
                Browse, filter, and download verified questions. No account needed.
              </p>
            </div>
            <button
              onClick={() => onLogin('user')}
              className="mt-auto bg-catTwoPointers text-ink font-medium rounded-lg py-2.5 hover:opacity-90 transition"
            >
              Enter portal
            </button>
          </div>

          <form
            onSubmit={handleAdminSubmit}
            className="bg-surface border border-surfaceRaised rounded-xl p-6 flex flex-col gap-4"
          >
            <div>
              <p className="font-mono text-xs text-muted uppercase tracking-widest">
                Restricted access
              </p>
              <p className="text-lg font-medium mt-1">Admin login</p>
              <p className="text-sm text-muted mt-2">
                Manage the question bank and view generation analytics.
              </p>
            </div>
            <input
              type="password"
              placeholder="Admin password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setError('')
              }}
              className="bg-ink border border-surfaceRaised rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-catDp"
            />
            {error && <p className="text-danger text-xs">{error}</p>}
            <button
              type="submit"
              className="mt-auto bg-transparent border border-surfaceRaised rounded-lg py-2.5 font-medium hover:bg-surfaceRaised transition"
            >
              Sign in as admin
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-muted mt-8">
          This is a demo-scale login for a college project, not a production auth system.
        </p>
      </div>
    </div>
  )
}
