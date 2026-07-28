import { useState, useMemo } from 'react'
import { useQuestions } from '../hooks/useQuestions.js'
import QuestionDetail from './QuestionDetail.jsx'

const SOURCES = [
  { id: 'All', label: 'All Sources' },
  { id: 'codeforces', label: 'Codeforces' },
  { id: 'cses', label: 'CSES' },
  { id: 'geeksforgeeks', label: 'GeeksforGeeks' },
  { id: 'leetcode', label: 'LeetCode' },
  { id: 'hackerrank', label: 'HackerRank' },
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
    if (!stats?.last_successful_run) return 'Scheduled every 3 days'
    try {
      const date = new Date(stats.last_successful_run)
      return `Last updated: ${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
    } catch {
      return 'Scheduled every 3 days'
    }
  }, [stats])

  return (
    <div className="bg-orbs min-h-screen px-6 py-8 max-w-6xl mx-auto pb-28 relative">
      <div className="relative z-10">
        {/* ── Header ── */}
        <div className="flex items-center justify-between mb-6 opacity-0 animate-slide-up">
          <div>
            <div className="flex items-center gap-3">
              <p className="font-mono text-xs text-muted uppercase tracking-[0.2em]">Autonomous Question Bank</p>
              <span className="text-[10px] font-mono text-muted bg-surfaceRaised/60 px-2 py-0.5 rounded-full border border-white/5">
                {lastUpdatedText}
              </span>
            </div>
            <h1 className="text-2xl font-bold font-display bg-gradient-to-r from-bone to-catDp bg-clip-text text-transparent mt-1">
              Browse verified questions
            </h1>
          </div>
          <button
            id="user-logout-btn"
            onClick={onLogout}
            className="text-sm text-muted hover:text-bone border border-surfaceRaised/60 rounded-xl px-4 py-2 hover:border-catDp/30 hover:bg-catDp/5 transition-all duration-200"
          >
            Log out
          </button>
        </div>

        {/* ── Cold Start Warning Banner ── */}
        {isWakingUp && (
          <div className="mb-6 bg-amber-500/10 border border-amber-500/30 text-amber-200 rounded-2xl p-4 flex items-center gap-3 text-sm animate-fade-in">
            <span className="animate-spin text-lg">⏳</span>
            <div>
              <p className="font-semibold">Waking up the server...</p>
              <p className="text-xs text-amber-300/80">
                The free-tier backend is cold-starting. This usually takes 20-40 seconds on initial load. Retrying automatically...
              </p>
            </div>
          </div>
        )}

        {/* ── Source filter bar ── */}
        <div className="mb-4 overflow-x-auto opacity-0 animate-slide-up-delay-1">
          <div className="flex gap-2 pb-1 w-max">
            {SOURCES.map((s) => (
              <button
                key={s.id}
                onClick={() => setActiveSource(s.id)}
                className={`whitespace-nowrap px-4 py-2 rounded-full text-xs font-mono border transition-all duration-200 ${
                  activeSource === s.id ? 'pill-active' : 'pill-inactive'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* ── Company Filter Bar ── */}
        <div className="mb-5 overflow-x-auto opacity-0 animate-slide-up-delay-1">
          <div className="flex items-center gap-2 pb-1 w-max">
            <span className="text-xs font-mono text-muted uppercase tracking-wider mr-1">🏢 Companies:</span>
            <button
              onClick={() => setActiveCompany('All')}
              className={`whitespace-nowrap px-4 py-2 rounded-full text-xs font-mono border transition-all duration-200 ${
                activeCompany === 'All' ? 'pill-active' : 'pill-inactive'
              }`}
            >
              All Companies
            </button>
            {companies.map((c) => (
              <button
                key={c}
                onClick={() => setActiveCompany(c)}
                className={`whitespace-nowrap px-4 py-2 rounded-full text-xs font-mono border transition-all duration-200 ${
                  activeCompany === c ? 'pill-active' : 'pill-inactive'
                }`}
              >
                🏢 {c}
              </button>
            ))}
          </div>
        </div>

        {/* ── Search + Company Select + Sort ── */}
        <div className="flex flex-col md:flex-row gap-3 mb-5 opacity-0 animate-slide-up-delay-2">
          <div className="flex-1 relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-muted text-sm pointer-events-none">🔍</span>
            <input
              id="search-input"
              type="text"
              placeholder="Search title or problem text..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full glass-card rounded-xl pl-10 pr-4 py-3 text-sm input-glow"
            />
          </div>

          {/* Company Quick Dropdown */}
          <select
            id="company-select"
            value={activeCompany}
            onChange={(e) => setActiveCompany(e.target.value)}
            className="glass-card rounded-xl px-4 py-3 text-sm text-muted cursor-pointer input-glow"
          >
            <option value="All">All Companies</option>
            {companies.map((c) => (
              <option key={c} value={c}>
                🏢 {c}
              </option>
            ))}
          </select>

          {/* Sort dropdown */}
          <select
            id="sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="glass-card rounded-xl px-4 py-3 text-sm text-muted cursor-pointer input-glow"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* ── Category pills ── */}
        <div className="flex flex-wrap gap-2 mb-4 opacity-0 animate-slide-up-delay-2">
          <button
            onClick={() => setActiveCategory('All')}
            className={`px-4 py-2 rounded-full text-xs font-medium border transition-all duration-200 ${
              activeCategory === 'All' ? 'pill-active' : 'pill-inactive'
            }`}
          >
            All categories
          </button>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-4 py-2 rounded-full text-xs font-medium border transition-all duration-200 ${
                activeCategory === cat ? 'pill-active' : 'pill-inactive'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* ── Difficulty pills ── */}
        <div className="flex flex-wrap gap-2 mb-6 opacity-0 animate-slide-up-delay-3">
          <button
            onClick={() => setActiveDifficulty('All')}
            className={`px-4 py-2 rounded-full text-xs font-medium border transition-all duration-200 ${
              activeDifficulty === 'All' ? 'pill-active' : 'pill-inactive'
            }`}
          >
            All difficulties
          </button>
          {DIFFICULTIES.map((d) => (
            <button
              key={d}
              onClick={() => setActiveDifficulty(d)}
              className={`px-4 py-2 rounded-full text-xs font-medium border transition-all duration-200 ${
                activeDifficulty === d ? 'pill-active' : 'pill-inactive'
              }`}
            >
              {d}
            </button>
          ))}
        </div>

        {/* ── Loading state ── */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* ── Results counter ── */}
        {!loading && (
          <p className="text-xs text-muted mb-4 animate-fade-in flex items-center gap-2">
            <span>
              Showing <span className="text-bone font-semibold">{sortedQuestions.length}</span> of{' '}
              <span className="text-bone font-semibold">{total}</span> total questions
            </span>
            {activeCompany !== 'All' && (
              <span className="bg-catDp/10 border border-catDp/30 text-catDp px-2.5 py-0.5 rounded-full font-mono text-[11px]">
                Company: {activeCompany}
              </span>
            )}
          </p>
        )}

        {/* ── Question grid ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedQuestions.map((q, i) => {
            const sourceSite = q.source_site || q.source || 'codeforces'
            const sourceUrl = q.source_url || '#'
            const comps = q.companies || (q.company ? [q.company] : [])

            return (
              <div
                key={q.id}
                onClick={() => setOpenQuestion(q)}
                className="stagger-in glass-card glass-card-hover rounded-2xl p-5 flex flex-col gap-3 cursor-pointer"
                style={{ '--delay': `${(i % 12) * 40}ms` }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selected.has(q.id)}
                      onChange={() => toggle(q.id)}
                      className="styled-checkbox"
                    />
                    <span className="font-mono text-xs text-muted truncate max-w-[120px]">{q.id}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {/* Source badge with external link */}
                    <a
                      href={sourceUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="text-[10px] font-mono text-catDp uppercase tracking-wider border border-catDp/30 rounded-md px-2 py-0.5 bg-catDp/10 hover:bg-catDp/20 transition-colors"
                    >
                      {sourceSite} ↗
                    </a>
                    {q.is_new && (
                      <span className="text-emerald-400 text-[10px] font-mono font-bold uppercase tracking-widest border border-emerald-500/50 rounded-md px-2 py-0.5 bg-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.3)] animate-pulse">
                        ⚡ NEW
                      </span>
                    )}
                    {q.verified && (
                      <span className="text-verified text-[10px] font-mono uppercase tracking-widest border border-verified/40 rounded-md px-2 py-0.5 bg-verified/10">
                        Verified
                      </span>
                    )}
                  </div>
                </div>

                <p className="font-medium text-sm leading-snug">{q.title}</p>

                <div className="flex flex-wrap gap-2">
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full bg-gradient-to-r ${
                      CATEGORY_COLORS[q.category] || 'from-ink to-ink'
                    } text-muted border border-white/5`}
                  >
                    {q.category}
                  </span>
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full bg-ink/60 ${
                      DIFFICULTY_TEXT_CLASS[DIFFICULTY_ROLE[q.difficulty]] || 'text-muted'
                    } border border-white/5`}
                  >
                    {q.difficulty}
                  </span>
                </div>

                {/* Company badges */}
                {comps.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-auto pt-1">
                    {comps.map((c) => (
                      <span
                        key={c}
                        onClick={(e) => {
                          e.stopPropagation()
                          setActiveCompany(c)
                        }}
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border transition-colors ${
                          activeCompany === c
                            ? 'bg-catDp text-bone border-catDp'
                            : 'text-muted/80 bg-ink/40 border-white/5 hover:border-catDp/40 hover:text-bone'
                        }`}
                      >
                        🏢 {c}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* ── Frosted bottom bar ── */}
        <div className="fixed bottom-0 left-0 right-0 frosted-bar px-6 py-4 flex items-center justify-between z-40">
          <span className="text-sm font-medium">
            <span className="text-catDp font-bold">{selected.size}</span> <span className="text-muted">selected</span>
          </span>
          <button id="download-btn" onClick={handleDownload} className="btn-gradient px-5 py-2.5 text-sm">
            ↓ Download selected
          </button>
        </div>

        <QuestionDetail question={openQuestion} onClose={() => setOpenQuestion(null)} />
      </div>
    </div>
  )
}