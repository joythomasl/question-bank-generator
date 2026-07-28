import { useState, useMemo } from 'react'
import { useQuestions } from '../hooks/useQuestions.js'
import QuestionDetail from './QuestionDetail.jsx'

const SOURCES = [
  { id: 'All', label: 'ALL SOURCES' },
  { id: 'codeforces', label: 'CODEFORCES' },
  { id: 'cses', label: 'CSES' },
  { id: 'geeksforgeeks', label: 'GEEKSFORGEEKS' },
  { id: 'leetcode', label: 'LEETCODE' },
  { id: 'hackerrank', label: 'HACKERRANK' },
]

const CATEGORIES = [
  'Dynamic Programming',
  'Backtracking',
  'Greedy',
  'Divide and Conquer',
  'Two Pointers',
]

const DIFFICULTIES = ['Easy', 'Medium', 'Hard']
const DIFFICULTY_ORDER = { Easy: 0, Medium: 1, Hard: 2 }
const DIFFICULTY_ROLE = { Easy: 'verified', Medium: 'warn', Hard: 'danger' }
const DIFFICULTY_TEXT_CLASS = {
  verified: 'text-verified',
  warn: 'text-warn',
  danger: 'text-danger',
}

const CATEGORY_COLORS = {
  'Dynamic Programming': 'from-catDp/20 to-catDp/5',
  'Backtracking': 'from-catBacktrack/20 to-catBacktrack/5',
  'Greedy': 'from-catGreedy/20 to-catGreedy/5',
  'Divide and Conquer': 'from-catDc/20 to-catDc/5',
  'Two Pointers': 'from-catTwoPointers/20 to-catTwoPointers/5',
}

const SORT_OPTIONS = [
  { value: 'newest', label: '⚡ Newest First (Default)' },
  { value: 'title-asc', label: 'Title A-Z' },
  { value: 'difficulty-asc', label: 'Difficulty: Easy first' },
  { value: 'difficulty-desc', label: 'Difficulty: Hard first' },
]

const ALL_COMPANIES = [
  'Google',
  'Amazon',
  'Microsoft',
  'Meta',
  'Apple',
  'Bloomberg',
  'Netflix',
  'Adobe',
  'Oracle',
  'Uber',
]

function SkeletonCard() {
  return (
    <div className="glass-card rounded-2xl p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="skeleton h-4 w-16" />
        <div className="skeleton h-5 w-14 rounded-full" />
      </div>
      <div className="skeleton h-5 w-3/4" />
      <div className="flex gap-2">
        <div className="skeleton h-5 w-24 rounded-full" />
        <div className="skeleton h-5 w-16 rounded-full" />
      </div>
      <div className="skeleton h-4 w-20" />
    </div>
  )
}

export default function UserPortal({ onLogout }) {
  const [activeSource, setActiveSource] = useState('All')
  const [activeCategory, setActiveCategory] = useState('All')
  const [activeDifficulty, setActiveDifficulty] = useState('All')
  const [activeCompany, setActiveCompany] = useState('All')
  const [sortBy, setSortBy] = useState('newest')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(new Set())
  const [openQuestion, setOpenQuestion] = useState(null)

  const { questions, total, stats, loading, isWakingUp } = useQuestions({
    sourceSite: activeSource,
    category: activeCategory,
    difficulty: activeDifficulty,
    company: activeCompany,
    search: query,
    limit: 100,
    offset: 0,
  })

  // Extract unique companies from fetched stats/questions
  const companies = useMemo(() => {
    const set = new Set(ALL_COMPANIES)
    questions.forEach((q) => {
      const comps = q.companies || (q.company ? [q.company] : [])
      comps.forEach((c) => set.add(c))
    })
    return Array.from(set).sort()
  }, [questions])

  const sortedQuestions = useMemo(() => {
    return [...questions].sort((a, b) => {
      if (sortBy === 'newest') {
        const aNew = a.is_new || false
        const bNew = b.is_new || false
        if (aNew !== bNew) return bNew ? 1 : -1
        return (a.id || '').localeCompare(b.id || '')
      }
      if (sortBy === 'title-asc') return (a.title || '').localeCompare(b.title || '')
      const da = DIFFICULTY_ORDER[a.difficulty] ?? 1
      const db = DIFFICULTY_ORDER[b.difficulty] ?? 1
      return sortBy === 'difficulty-asc' ? da - db : db - da
    })
  }, [questions, sortBy])

  function toggle(id) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  function handleDownload() {
    const data = sortedQuestions.filter((q) => selected.has(q.id))
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'questions.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  const lastUpdatedText = useMemo(() => {
    if (!stats?.last_successful_run) return 'SYNC OK (30m Interval)'
    try {
      const date = new Date(stats.last_successful_run)
      return `SYNC: ${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
    } catch {
      return 'SYNC OK (30m Interval)'
    }
  }, [stats])

  return (
    <div className="min-h-screen relative pb-28">
      {/* Hex grid backdrop */}
      <div className="bg-cyber-grid" />
      <div className="bg-orbs" />

      <div className="relative z-10 px-6 py-8 max-w-6xl mx-auto">
        {/* ── Top Header Bar ── */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8 opacity-0 animate-slide-up">
          <div>
            <p className="font-mono text-xs text-catDp uppercase tracking-[0.25em]">SYSTEM CATALOG</p>
            <h1 className="text-3xl font-bold font-display bg-gradient-to-r from-bone via-bone to-catDp bg-clip-text text-transparent mt-1.5">
              Verified Algorithmic Repository
            </h1>
          </div>
          <button
            id="user-logout-btn"
            onClick={onLogout}
            className="text-xs font-mono text-muted hover:text-bone border border-white/10 rounded-lg px-4 py-2 hover:border-catDp/40 hover:bg-catDp/5 transition-all duration-200"
          >
            DISCONNECT_SESSION
          </button>
        </div>

        {/* ── System Stats Display HUD ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8 opacity-0 animate-slide-up-delay-1">
          {/* Stat 1 */}
          <div className="glass-card stat-card-glow rounded-xl p-5 flex flex-col justify-between min-h-[110px]" style={{ '--glow-start': '#7c9eff', '--glow-end': '#38bdf8' }}>
            <span className="font-mono text-[10px] text-muted tracking-widest uppercase">DATABANK SIZE</span>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-4xl font-extrabold font-display text-bone">{stats?.total || total}</span>
              <span className="text-xs font-mono text-muted">VERIFIED RECORDS</span>
            </div>
            <div className="w-full bg-ink/40 h-1.5 rounded-full mt-3 overflow-hidden border border-white/5">
              <div className="h-full bg-gradient-to-r from-[#7c9eff] to-[#38bdf8] rounded-full bar-animate" style={{ width: '100%' }} />
            </div>
          </div>

          {/* Stat 2 */}
          <div className="glass-card stat-card-glow rounded-xl p-5 flex flex-col justify-between min-h-[110px]" style={{ '--glow-start': '#c084fc', '--glow-end': '#f0806b' }}>
            <span className="font-mono text-[10px] text-muted tracking-widest uppercase">QUALITY RATIO</span>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-4xl font-extrabold font-display text-gradient bg-gradient-to-r from-bone to-catDc bg-clip-text text-transparent">
                {stats?.verified_percentage || 100.0}%
              </span>
              <span className="text-xs font-mono text-muted">PASS RATE</span>
            </div>
            <div className="w-full bg-ink/40 h-1.5 rounded-full mt-3 overflow-hidden border border-white/5">
              <div className="h-full bg-gradient-to-r from-[#c084fc] to-[#f0806b] rounded-full bar-animate" style={{ width: '100%' }} />
            </div>
          </div>

          {/* Stat 3 */}
          <div className="glass-card stat-card-glow rounded-xl p-5 flex flex-col justify-between min-h-[110px]" style={{ '--glow-start': '#34d399', '--glow-end': '#38bdf8' }}>
            <span className="font-mono text-[10px] text-muted tracking-widest uppercase">BACKGROUND RUNNER</span>
            <div className="flex items-center gap-2.5 mt-2.5">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              <span className="text-sm font-mono font-medium text-emerald-400">{lastUpdatedText}</span>
            </div>
            <div className="text-[10px] font-mono text-muted mt-auto pt-2 border-t border-white/5">
              AUTONOMOUS SCRAPER STATUS: ACTIVE
            </div>
          </div>
        </div>

        {/* ── Cold Start Warning Banner ── */}
        {isWakingUp && (
          <div className="mb-6 bg-amber-500/10 border border-amber-500/20 text-amber-200 rounded-xl p-4 flex items-center gap-3 text-sm animate-fade-in shadow-glow">
            <span className="animate-spin text-lg">⏳</span>
            <div>
              <p className="font-mono font-bold text-xs uppercase tracking-wider text-amber-400">CONNECTING INSTANCE</p>
              <p className="text-xs text-amber-300/80 mt-0.5">
                The database server instance is cold-starting. Retrying connection automatically...
              </p>
            </div>
          </div>
        )}

        {/* ── Control Center (Filters & Search) ── */}
        <div className="glass-panel rounded-2xl p-6 mb-8 opacity-0 animate-slide-up-delay-2">
          <div className="border-b border-white/5 pb-4 mb-5 flex items-center justify-between">
            <span className="font-mono text-xs text-muted uppercase tracking-widest">[ SYSTEM FILTERS ]</span>
            <span className="text-[10px] font-mono text-muted uppercase bg-ink/60 border border-white/5 px-2.5 py-0.5 rounded">AUTO_SYNC</span>
          </div>

          {/* Source Filter Tabs */}
          <div className="mb-5 overflow-x-auto">
            <div className="flex gap-2 pb-1.5 w-max">
              {SOURCES.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setActiveSource(s.id)}
                  className={`whitespace-nowrap px-4 py-2.5 rounded-lg text-xs font-mono border transition-all duration-200 ${
                    activeSource === s.id ? 'pill-active' : 'pill-inactive'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Search + Dropdowns Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-muted text-xs pointer-events-none">🔍</span>
              <input
                id="search-input"
                type="text"
                placeholder="Search title, statement..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full glass-card rounded-xl pl-10 pr-4 py-3 text-xs input-glow font-mono"
              />
            </div>

            <select
              id="company-select"
              value={activeCompany}
              onChange={(e) => setActiveCompany(e.target.value)}
              className="glass-card rounded-xl px-4 py-3 text-xs text-muted cursor-pointer input-glow font-mono"
            >
              <option value="All">All Companies (🏢)</option>
              {companies.map((c) => (
                <option key={c} value={c}>
                  🏢 {c}
                </option>
              ))}
            </select>

            <select
              id="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="glass-card rounded-xl px-4 py-3 text-xs text-muted cursor-pointer input-glow font-mono"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Sub-Filters Row (Categories & Difficulties) */}
          <div className="flex flex-col gap-4 pt-4 border-t border-white/5">
            {/* Categories */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] font-mono text-muted uppercase tracking-wider mr-2">CATEGORIES:</span>
              <button
                onClick={() => setActiveCategory('All')}
                className={`px-3 py-1.5 rounded-md text-[11px] font-mono border transition-all duration-200 ${
                  activeCategory === 'All' ? 'pill-active' : 'pill-inactive'
                }`}
              >
                ALL
              </button>
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-3 py-1.5 rounded-md text-[11px] font-mono border transition-all duration-200 ${
                    activeCategory === cat ? 'pill-active' : 'pill-inactive'
                  }`}
                >
                  {cat.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Difficulties */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] font-mono text-muted uppercase tracking-wider mr-2">DIFFICULTY:</span>
              <button
                onClick={() => setActiveDifficulty('All')}
                className={`px-3 py-1.5 rounded-md text-[11px] font-mono border transition-all duration-200 ${
                  activeDifficulty === 'All' ? 'pill-active' : 'pill-inactive'
                }`}
              >
                ALL
              </button>
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  onClick={() => setActiveDifficulty(d)}
                  className={`px-3 py-1.5 rounded-md text-[11px] font-mono border transition-all duration-200 ${
                    activeDifficulty === d ? 'pill-active' : 'pill-inactive'
                  }`}
                >
                  {d.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ── Results Info Line ── */}
        {!loading && (
          <p className="text-[11px] font-mono text-muted mb-4 animate-fade-in flex items-center gap-2">
            <span>
              CATALOG MATCH: <span className="text-catDp font-semibold">{sortedQuestions.length}</span> /{' '}
              <span className="text-muted font-semibold">{total}</span> ITEMS
            </span>
            {activeCompany !== 'All' && (
              <span className="bg-catDp/10 border border-catDp/30 text-catDp px-2.5 py-0.5 rounded font-mono text-[9px]">
                TAG: {activeCompany.toUpperCase()}
              </span>
            )}
          </p>
        )}

        {/* ── Loading Skeleton Grid ── */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* ── Question Grid list ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {sortedQuestions.map((q, i) => {
            const sourceSite = q.source_site || q.source || 'codeforces'
            const sourceUrl = q.source_url || '#'
            const comps = q.companies || (q.company ? [q.company] : [])

            return (
              <div
                key={q.id}
                onClick={() => setOpenQuestion(q)}
                className="stagger-in glass-card glass-card-hover rounded-xl p-5 flex flex-col gap-4 cursor-pointer relative overflow-hidden"
                style={{ '--delay': `${(i % 12) * 35}ms` }}
              >
                {/* Cyber accent glow lines */}
                {q.is_new && (
                  <div className="absolute top-0 left-0 right-0 h-[2px] bg-emerald-500 shadow-[0_1px_8px_rgba(52,211,153,0.6)]" />
                )}

                <div className="flex items-center justify-between border-b border-white/5 pb-2.5">
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selected.has(q.id)}
                      onChange={() => toggle(q.id)}
                      className="styled-checkbox"
                    />
                    <span className="font-mono text-[10px] text-muted truncate max-w-[120px]">{q.id.toUpperCase()}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {/* Source label */}
                    <a
                      href={sourceUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="text-[9px] font-mono text-catDp uppercase tracking-widest border border-catDp/20 rounded px-1.5 py-0.5 bg-catDp/5 hover:bg-catDp/15 transition-all"
                    >
                      [{sourceSite.toUpperCase()}]
                    </a>
                  </div>
                </div>

                {/* Problem Title */}
                <div>
                  <h4 className="font-medium text-sm leading-snug font-display text-bone hover:text-catDp transition-colors">
                    {q.title}
                  </h4>
                </div>

                <div className="flex flex-wrap gap-1.5 mt-auto">
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded bg-ink/60 border border-white/5 text-muted`}>
                    {q.category.toUpperCase()}
                  </span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded bg-ink/60 border border-white/5 ${DIFFICULTY_TEXT_CLASS[DIFFICULTY_ROLE[q.difficulty]] || 'text-muted'}`}>
                    {q.difficulty.toUpperCase()}
                  </span>
                  {q.is_new && (
                    <span className="text-emerald-400 text-[9px] font-mono font-bold uppercase tracking-wider border border-emerald-500/30 rounded px-1.5 py-0.5 bg-emerald-500/10 shadow-[0_0_8px_rgba(52,211,153,0.15)] animate-pulse">
                      NEW
                    </span>
                  )}
                  {q.verified && (
                    <span className="text-emerald-400 text-[9px] font-mono uppercase tracking-wider border border-emerald-500/20 rounded px-1.5 py-0.5 bg-emerald-500/5">
                      VERIFIED
                    </span>
                  )}
                </div>

                {/* Company Tag Pills */}
                {comps.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1.5 border-t border-white/5">
                    {comps.slice(0, 4).map((c) => (
                      <span
                        key={c}
                        onClick={(e) => {
                          e.stopPropagation()
                          setActiveCompany(c)
                        }}
                        className={`text-[9px] font-mono px-1.5 py-0.5 rounded border transition-colors ${
                          activeCompany === c
                            ? 'bg-catDp text-ink border-catDp font-bold'
                            : 'text-muted bg-ink/40 border-white/5 hover:border-catDp/40 hover:text-bone'
                        }`}
                      >
                        🏢 {c.toUpperCase()}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* ── Floating Futuristic HUD Action Bar ── */}
        {selected.size > 0 && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-lg rounded-2xl frosted-bar px-6 py-4 flex items-center justify-between z-40 border border-white/10 shadow-glow animate-slide-up">
            <span className="text-xs font-mono">
              SELECTED_RECORDS: <span className="text-catDp font-bold">{selected.size}</span>
            </span>
            <button
              id="download-btn"
              onClick={handleDownload}
              className="btn-gradient px-5 py-2.5 text-xs font-mono uppercase tracking-wider"
            >
              DOWNLOAD_CATALOG
            </button>
          </div>
        )}

        <QuestionDetail question={openQuestion} onClose={() => setOpenQuestion(null)} />
      </div>
    </div>
  )
}