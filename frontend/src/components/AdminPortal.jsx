import { useMemo, useState, useEffect, useRef } from 'react'
import { useQuestions } from '../hooks/useQuestions.js'
import { editQuestion, getCuratedQuestions, removeQuestion, resetOverrides } from '../utils/overrides.js'

/* ── Animated counter hook ──────────────────────────────────────────────── */
function useAnimatedCount(target, duration = 600) {
  const [count, setCount] = useState(0)
  const prevRef = useRef(0)

  useEffect(() => {
    const start = prevRef.current
    const diff = target - start
    if (diff === 0) return
    const startTime = performance.now()

    function step(now) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.round(start + diff * eased))
      if (progress < 1) requestAnimationFrame(step)
      else prevRef.current = target
    }
    requestAnimationFrame(step)
  }, [target, duration])

  return count
}

/* ── Animated bar with fill ─────────────────────────────────────────────── */
function Bar({ label, count, total, colorClass = 'bg-catDp' }) {
  const pct = total ? (count / total) * 100 : 0

  return (
    <div className="flex items-center gap-3 group">
      <span className="text-xs w-40 text-muted truncate group-hover:text-bone transition-colors">{label}</span>
      <div className="flex-1 bg-ink/60 rounded-full h-2.5 overflow-hidden">
        <div
          className={`${colorClass} h-2.5 rounded-full bar-animate transition-all duration-300`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs w-8 text-right font-mono text-muted">{count}</span>
    </div>
  )
}

/* ── Stat card with gradient top border ─────────────────────────────────── */
function StatCard({ label, value, color1, color2, suffix = '', textColor = '' }) {
  const animatedVal = useAnimatedCount(typeof value === 'number' ? value : 0)

  return (
    <div
      className="stat-card glass-card rounded-2xl p-5 animate-scale-in"
      style={{ '--stat-color-1': color1, '--stat-color-2': color2 }}
    >
      <p className="text-xs text-muted mb-2">{label}</p>
      <p className={`text-3xl font-bold font-display ${textColor}`}>
        {typeof value === 'number' ? animatedVal : value}{suffix}
      </p>
    </div>
  )
}

export default function AdminPortal({ onLogout }) {
  const [tab, setTab] = useState('manage')
  const [refreshKey, setRefreshKey] = useState(0)
  const { questions: rawQuestions } = useQuestions()

  const questions = useMemo(
    () => (rawQuestions ? getCuratedQuestions(rawQuestions) : []),
    [refreshKey, rawQuestions],
  )

  function handleRemove(id) {
    removeQuestion(id)
    setRefreshKey((k) => k + 1)
  }

  function handleEditDifficulty(id, difficulty) {
    editQuestion(id, { difficulty })
    setRefreshKey((k) => k + 1)
  }

  function handleReset() {
    resetOverrides()
    setRefreshKey((k) => k + 1)
  }

  function handleExport() {
    const blob = new Blob([JSON.stringify(questions, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'questions.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  const categoryCounts = useMemo(() => {
    const counts = {}
    questions.forEach((q) => { counts[q.category] = (counts[q.category] || 0) + 1 })
    return Object.entries(counts).sort((a, b) => b[1] - a[1])
  }, [questions])

  const difficultyCounts = useMemo(() => {
    const counts = { Easy: 0, Medium: 0, Hard: 0 }
    questions.forEach((q) => { counts[q.difficulty] = (counts[q.difficulty] || 0) + 1 })
    return counts
  }, [questions])

  const companyCounts = useMemo(() => {
    const counts = {}
    questions.forEach((q) => {
      const c = q.company || 'General'
      counts[c] = (counts[c] || 0) + 1
    })
    return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 10)
  }, [questions])

  const sourceCounts = useMemo(() => {
    const counts = {}
    questions.forEach((q) => {
      const s = q.source || 'unknown'
      counts[s] = (counts[s] || 0) + 1
    })
    return Object.entries(counts).sort((a, b) => b[1] - a[1])
  }, [questions])

  const typeCounts = useMemo(() => {
    const counts = { coding: 0, conceptual: 0 }
    questions.forEach((q) => { counts[q.type || q.item_type || 'coding'] = (counts[q.type || q.item_type || 'coding'] || 0) + 1 })
    return counts
  }, [questions])

  const verifiedCount = questions.filter((q) => q.verified).length
  const unverifiedCount = questions.length - verifiedCount
  const verifiedPct = questions.length ? Math.round((verifiedCount / questions.length) * 100) : 0
  const uniqueCompanies = new Set(questions.map((q) => q.company).filter(Boolean)).size

  return (
    <div className="bg-orbs min-h-screen px-6 py-8 max-w-5xl mx-auto relative">
      <div className="relative z-10">
        {/* ── Header ── */}
        <div className="flex items-center justify-between mb-8 opacity-0 animate-slide-up">
          <div>
            <p className="font-mono text-xs text-muted uppercase tracking-[0.2em]">Admin</p>
            <h1 className="text-2xl font-bold font-display bg-gradient-to-r from-bone to-catDc bg-clip-text text-transparent">
              Question bank management
            </h1>
          </div>
          <button
            id="admin-logout-btn"
            onClick={onLogout}
            className="text-sm text-muted hover:text-bone border border-surfaceRaised/60 rounded-xl px-4 py-2 hover:border-catDc/30 hover:bg-catDc/5 transition-all duration-200"
          >
            Log out
          </button>
        </div>

        {/* ── Tab selector with sliding indicator ── */}
        <div className="relative flex gap-1 mb-8 bg-ink/40 rounded-xl p-1 w-fit border border-white/5 opacity-0 animate-slide-up-delay-1">
          <button
            id="tab-manage"
            onClick={() => setTab('manage')}
            className={`relative z-10 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
              tab === 'manage' ? 'text-bone' : 'text-muted hover:text-bone'
            }`}
          >
            Manage questions
          </button>
          <button
            id="tab-analytics"
            onClick={() => setTab('analytics')}
            className={`relative z-10 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
              tab === 'analytics' ? 'text-bone' : 'text-muted hover:text-bone'
            }`}
          >
            Analytics
          </button>
          {/* Sliding background */}
          <div
            className="absolute top-1 bottom-1 rounded-lg bg-surfaceRaised/80 shadow-sm transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
            style={{
              left: tab === 'manage' ? '4px' : '50%',
              width: 'calc(50% - 4px)',
            }}
          />
        </div>

        {/* ── Manage tab ── */}
        {tab === 'manage' && (
          <div className="opacity-0 animate-fade-in" style={{ animationDelay: '0.15s', animationFillMode: 'forwards' }}>
            <div className="flex items-center justify-between mb-5">
              <p className="text-sm text-muted">
                <span className="text-bone font-semibold">{questions.length}</span> questions in the curated set
              </p>
              <div className="flex gap-2">
                <button
                  id="reset-overrides-btn"
                  onClick={handleReset}
                  className="text-xs text-muted border border-surfaceRaised/60 rounded-xl px-4 py-2 hover:border-danger/30 hover:text-danger hover:bg-danger/5 transition-all duration-200"
                >
                  Reset overrides
                </button>
                <button
                  id="export-btn"
                  onClick={handleExport}
                  className="text-xs btn-gradient px-4 py-2"
                >
                  ↓ Export questions.json
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              {questions.map((q, i) => (
                <div
                  key={q.id}
                  className="stagger-in glass-card glass-card-hover rounded-xl px-5 py-3.5 flex items-center gap-4"
                  style={{ '--delay': `${i * 30}ms` }}
                >
                  <span className="font-mono text-xs text-muted w-16 truncate">{q.id}</span>
                  <span className="flex-1 text-sm font-medium truncate">{q.title}</span>
                  <span className="text-xs text-muted w-40 truncate hidden md:block">{q.category}</span>
                  <span className="text-xs text-muted w-24 truncate hidden md:block">{q.company}</span>
                  <select
                    value={q.difficulty}
                    onChange={(e) => handleEditDifficulty(q.id, e.target.value)}
                    className="bg-ink/60 border border-surfaceRaised/60 rounded-lg text-xs px-3 py-1.5 input-glow cursor-pointer"
                  >
                    <option>Easy</option>
                    <option>Medium</option>
                    <option>Hard</option>
                  </select>
                  <button
                    onClick={() => handleRemove(q.id)}
                    className="text-xs text-muted border border-surfaceRaised/60 rounded-lg px-3 py-1.5 hover:text-danger hover:border-danger/40 hover:bg-danger/5 transition-all duration-200"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>

            <p className="text-xs text-muted/60 mt-8">
              Edits and removals here are stored in this browser only. Use export to bake the curated set into the questions.json shipped with the deployed site.
            </p>
          </div>
        )}

        {/* ── Analytics tab ── */}
        {tab === 'analytics' && (
          <div className="flex flex-col gap-6 opacity-0 animate-fade-in" style={{ animationDelay: '0.15s', animationFillMode: 'forwards' }}>
            {/* Stat cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Total questions" value={questions.length} color1="#7C9EFF" color2="#38BDF8" />
              <StatCard label="Verified" value={verifiedPct} suffix="%" color1="#4ADE80" color2="#34D399" textColor="text-verified" />
              <StatCard label="Categories" value={categoryCounts.length} color1="#C084FC" color2="#7C9EFF" />
              <StatCard label="Companies" value={uniqueCompanies} color1="#F5B942" color2="#F0806B" />
            </div>

            {/* Verified vs unverified */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">Verified vs unverified</p>
              <div className="flex flex-col gap-3">
                <Bar label="Verified" count={verifiedCount} total={questions.length} colorClass="bg-verified" />
                <Bar label="Unverified" count={unverifiedCount} total={questions.length} colorClass="bg-danger" />
              </div>
              {/* Mini verified breakdown */}
              <div className="mt-4 pt-4 border-t border-white/5">
                <p className="text-xs text-muted">
                  <span className="text-bone font-semibold">{verifiedCount}</span> of {questions.length} verified ({verifiedPct}%)
                </p>
              </div>
            </div>

            {/* By category */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">By category</p>
              <div className="flex flex-col gap-3">
                {categoryCounts.map(([cat, count]) => (
                  <Bar key={cat} label={cat} count={count} total={questions.length} colorClass="bg-catDp" />
                ))}
              </div>
            </div>

            {/* By difficulty */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">By difficulty</p>
              <div className="flex flex-col gap-3">
                <Bar label="Easy" count={difficultyCounts.Easy} total={questions.length} colorClass="bg-verified" />
                <Bar label="Medium" count={difficultyCounts.Medium} total={questions.length} colorClass="bg-warn" />
                <Bar label="Hard" count={difficultyCounts.Hard} total={questions.length} colorClass="bg-danger" />
              </div>
            </div>

            {/* Top companies */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">Top companies</p>
              <div className="flex flex-col gap-3">
                {companyCounts.map(([company, count]) => (
                  <Bar key={company} label={company} count={count} total={questions.length} colorClass="bg-catTwoPointers" />
                ))}
              </div>
            </div>

            {/* By source */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">By source</p>
              <div className="flex flex-col gap-3">
                {sourceCounts.map(([source, count]) => (
                  <Bar key={source} label={source} count={count} total={questions.length} colorClass="bg-catBacktrack" />
                ))}
              </div>
            </div>

            {/* Coding vs conceptual */}
            <div className="glass-card rounded-2xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">Coding vs conceptual</p>
              <div className="flex flex-col gap-3">
                <Bar label="Coding" count={typeCounts.coding} total={questions.length} colorClass="bg-catGreedy" />
                <Bar label="Conceptual" count={typeCounts.conceptual} total={questions.length} colorClass="bg-catDc" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}