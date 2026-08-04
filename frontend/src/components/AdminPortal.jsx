import { useMemo, useState, useEffect, useRef } from 'react'
import { useQuestions } from '../hooks/useQuestions.js'
import { editQuestion, removeQuestion, resetOverrides } from '../utils/overrides.js'
import QuestionDetail from './QuestionDetail.jsx'
import ThemeToggle from './ThemeToggle.jsx'
import CompanyLogo from './CompanyLogo.jsx'
import HudCorners from './HudCorners.jsx'
import { LogOutIcon, DownloadIcon, EyeIcon } from './icons.jsx'
import { getCategoryColor, getCompanyColor, getSourceColor } from '../utils/colors.js'

// Competitive-programming questions are tagged with their own source site as a
// placeholder "company" when no real interview company is known — exclude those
// from company-facing analytics (source breakdown already covers that axis).
const PLACEHOLDER_COMPANY_NAMES = new Set([
  'codeforces', 'cses', 'geeksforgeeks', 'leetcode', 'hackerrank', 'general',
])
const isRealCompany = (name) => Boolean(name) && !PLACEHOLDER_COMPANY_NAMES.has(name.toLowerCase())

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
function Bar({ label, count, total, colorClass = 'bg-catDp', color }) {
  const pct = total ? (count / total) * 100 : 0

  return (
    <div className="flex items-center gap-3 group">
      <span className="text-xs w-40 text-muted truncate group-hover:text-bone transition-colors">{label}</span>
      <div className="flex-1 bg-veil/5 rounded-full h-2.5 overflow-hidden">
        <div
          className={`${color ? '' : colorClass} h-2.5 rounded-full bar-animate transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]`}
          style={{ width: `${pct}%`, backgroundColor: color, boxShadow: color ? `0 0 12px -2px ${color}99` : undefined }}
        />
      </div>
      <span className="data-readout text-xs w-8 text-right text-muted">{count}</span>
    </div>
  )
}

/* ── Stat card with gradient top glow ────────────────────────────────────── */
function StatCard({ label, value, color1, color2, suffix = '', textColor = '' }) {
  const animatedVal = useAnimatedCount(typeof value === 'number' ? value : 0)

  return (
    <div
      className="hud-tile stat-card-glow p-5 animate-scale-in relative"
      style={{ '--glow-start': color1, '--glow-end': color2 }}
    >
      <HudCorners color={color1} />
      <p className="text-[11px] text-muted mb-2 uppercase tracking-wide">{label}</p>
      <p className={`data-readout text-3xl font-bold ${textColor}`}>
        {typeof value === 'number' ? animatedVal : value}{suffix}
      </p>
    </div>
  )
}

export default function AdminPortal({ onLogout }) {
  const [tab, setTab] = useState('manage')
  const [openQuestion, setOpenQuestion] = useState(null)
  const [mutationError, setMutationError] = useState('')
  // No source/category/etc filters here — admin manages the whole catalog,
  // so just ask for everything (backend caps at 1000 per request).
  const { questions, loading, refetch } = useQuestions({ limit: 1000 })

  async function handleRemove(id) {
    setMutationError('')
    try {
      await removeQuestion(id)
      await refetch()
    } catch (err) {
      setMutationError(`Couldn't remove question: ${err.message}`)
    }
  }

  async function handleEditDifficulty(id, difficulty) {
    setMutationError('')
    try {
      await editQuestion(id, { difficulty })
      await refetch()
    } catch (err) {
      setMutationError(`Couldn't update difficulty: ${err.message}`)
    }
  }

  async function handleReset() {
    setMutationError('')
    try {
      await resetOverrides()
      await refetch()
    } catch (err) {
      setMutationError(`Couldn't reset overrides: ${err.message}`)
    }
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
      const c = q.company
      if (!isRealCompany(c)) return
      counts[c] = (counts[c] || 0) + 1
    })
    return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 10)
  }, [questions])

  const sourceCounts = useMemo(() => {
    const counts = {}
    questions.forEach((q) => {
      const s = q.source_site || q.source || 'unknown'
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
  const uniqueCompanies = new Set(questions.map((q) => q.company).filter(isRealCompany)).size

  return (
    <div className="min-h-screen relative">
      <div className="bg-grid" />
      <div className="bg-particles" />
      <div className="bg-orbs" />
      <div className="px-6 py-8 max-w-5xl mx-auto relative z-10">
        {/* ── Header ── */}
        <div className="flex items-center justify-between mb-8 opacity-0 animate-slide-up">
          <div>
            <p className="text-xs text-muted font-medium uppercase tracking-[0.2em]">Admin</p>
            <h1 className="text-2xl font-semibold font-display bg-gradient-to-r from-bone to-catDc bg-clip-text text-transparent">
              Question bank management
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <button
              id="admin-logout-btn"
              onClick={onLogout}
              className="hud-btn-ghost flex items-center gap-2 text-sm px-4 py-2.5"
            >
              <LogOutIcon /> Log out
            </button>
          </div>
        </div>

        {/* ── Tab selector with sliding indicator ── */}
        <div className="relative flex gap-1 mb-8 bg-veil/[0.03] rounded-full p-1 w-fit border border-line/8 opacity-0 animate-slide-up-delay-1">
          <button
            id="tab-manage"
            onClick={() => setTab('manage')}
            className={`relative z-10 px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-200 ${
              tab === 'manage' ? 'text-bone' : 'text-muted hover:text-bone'
            }`}
          >
            Manage questions
          </button>
          <button
            id="tab-analytics"
            onClick={() => setTab('analytics')}
            className={`relative z-10 px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-200 ${
              tab === 'analytics' ? 'text-bone' : 'text-muted hover:text-bone'
            }`}
          >
            Analytics
          </button>
          {/* Sliding background */}
          <div
            className="absolute top-1 bottom-1 rounded-full transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
            style={{
              left: tab === 'manage' ? '4px' : '50%',
              width: 'calc(50% - 4px)',
              background: 'linear-gradient(155deg, rgba(255,255,255,0.16), rgba(255,255,255,0.04))',
              boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.25), 0 4px 14px rgba(0,0,0,0.3)',
              border: '1px solid rgba(255,255,255,0.1)',
            }}
          />
        </div>

        {/* ── Manage tab ── */}
        {tab === 'manage' && (
          <div className="opacity-0 animate-fade-in" style={{ animationDelay: '0.15s', animationFillMode: 'forwards' }}>
            <div className="flex items-center justify-between mb-5">
              <p className="text-sm text-muted">
                <span className="text-bone font-semibold">{questions.length}</span> questions in the catalog
              </p>
              <div className="flex gap-2">
                <button
                  id="reset-overrides-btn"
                  onClick={handleReset}
                  className="hud-btn-ghost text-xs px-4 py-2 hover:!text-danger hover:!border-danger/30"
                >
                  Reset overrides
                </button>
                <button
                  id="export-btn"
                  onClick={handleExport}
                  className="hud-btn-primary flex items-center gap-2 text-xs px-4 py-2"
                >
                  <DownloadIcon /> Export questions.json
                </button>
              </div>
            </div>

            {mutationError && (
              <p className="text-xs text-danger bg-danger/10 border border-danger/20 rounded-xl px-4 py-2.5 mb-4">
                {mutationError}
              </p>
            )}

            {loading && questions.length === 0 && (
              <p className="text-sm text-muted py-8 text-center">Loading questions…</p>
            )}

            <div className="flex flex-col gap-2">
              {questions.map((q, i) => (
                <div
                  key={q.id}
                  className="stagger-in hud-tile hud-tile-interactive px-5 py-3.5 flex items-center gap-4 relative"
                  style={{ '--delay': `${i * 30}ms` }}
                >
                  <span className="data-readout text-xs text-muted/70 w-16 truncate">{q.id}</span>
                  <span className="flex-1 text-sm font-medium truncate">{q.title}</span>
                  <span
                    className="text-xs w-40 truncate hidden md:block font-medium"
                    style={{ color: getCategoryColor(q.category) }}
                  >
                    {q.category}
                  </span>
                  <span className="text-xs text-muted w-24 truncate hidden md:flex items-center gap-1.5">
                    {isRealCompany(q.company) && <CompanyLogo name={q.company} size={14} />}
                    <span className="truncate">{q.company}</span>
                  </span>
                  <button
                    onClick={() => setOpenQuestion(q)}
                    aria-label={`View ${q.title}`}
                    title="View question"
                    className="hud-btn-ghost text-xs px-2.5 py-1.5"
                  >
                    <EyeIcon />
                  </button>
                  <select
                    value={q.difficulty}
                    onChange={(e) => handleEditDifficulty(q.id, e.target.value)}
                    className="rounded-full text-xs px-3 py-1.5 hud-input cursor-pointer"
                  >
                    <option>Easy</option>
                    <option>Medium</option>
                    <option>Hard</option>
                  </select>
                  <button
                    onClick={() => handleRemove(q.id)}
                    className="hud-btn-ghost text-xs px-3 py-1.5 hover:!text-danger hover:!border-danger/40"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>

            <p className="text-xs text-muted/60 mt-8">
              Edits and removals here update the live catalog immediately — every visitor sees the change. Export downloads a snapshot of the current curated set.
            </p>

            <QuestionDetail question={openQuestion} onClose={() => setOpenQuestion(null)} />
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
            <div className="hud-tile rounded-3xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">Verified vs unverified</p>
              <div className="flex flex-col gap-3">
                <Bar label="Verified" count={verifiedCount} total={questions.length} colorClass="bg-verified" />
                <Bar label="Unverified" count={unverifiedCount} total={questions.length} colorClass="bg-danger" />
              </div>
              {/* Mini verified breakdown */}
              <div className="mt-4 pt-4 border-t border-line/5">
                <p className="text-xs text-muted">
                  <span className="text-bone font-semibold">{verifiedCount}</span> of {questions.length} verified ({verifiedPct}%)
                </p>
              </div>
            </div>

            {/* By category */}
            <div className="hud-tile rounded-3xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">By category</p>
              <div className="flex flex-col gap-3">
                {categoryCounts.map(([cat, count]) => (
                  <Bar key={cat} label={cat} count={count} total={questions.length} color={getCategoryColor(cat)} />
                ))}
              </div>
            </div>

            {/* By difficulty */}
            <div className="hud-tile rounded-3xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">By difficulty</p>
              <div className="flex flex-col gap-3">
                <Bar label="Easy" count={difficultyCounts.Easy} total={questions.length} colorClass="bg-verified" />
                <Bar label="Medium" count={difficultyCounts.Medium} total={questions.length} colorClass="bg-warn" />
                <Bar label="Hard" count={difficultyCounts.Hard} total={questions.length} colorClass="bg-danger" />
              </div>
            </div>

            {/* Top companies */}
            <div className="hud-tile rounded-3xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">Top companies</p>
              <div className="flex flex-col gap-3">
                {companyCounts.map(([company, count]) => (
                  <Bar key={company} label={company} count={count} total={questions.length} color={getCompanyColor(company)} />
                ))}
              </div>
            </div>

            {/* By source */}
            <div className="hud-tile rounded-3xl p-6">
              <p className="text-sm text-muted mb-4 font-medium">By source</p>
              <div className="flex flex-col gap-3">
                {sourceCounts.map(([source, count]) => (
                  <Bar key={source} label={source} count={count} total={questions.length} color={getSourceColor(source)} />
                ))}
              </div>
            </div>

            {/* Coding vs conceptual */}
            <div className="hud-tile rounded-3xl p-6">
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