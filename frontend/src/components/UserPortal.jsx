import { useState, useMemo } from 'react'
import { useQuestions } from '../hooks/useQuestions.js'
import { useLocalSet } from '../hooks/useLocalSet.js'
import QuestionDetail from './QuestionDetail.jsx'
import ThemeToggle from './ThemeToggle.jsx'
import CompanyLogo from './CompanyLogo.jsx'
import HudCorners from './HudCorners.jsx'
import DifficultyGauge from './DifficultyGauge.jsx'
import { SearchIcon, LogOutIcon, DownloadIcon, XIcon, LoaderIcon, StarIcon, CheckCircleIcon, SlidersIcon, ShieldCheckIcon } from './icons.jsx'
import { getCategoryColor, getSourceColor } from '../utils/colors.js'

const SOURCES = [
  { id: 'All', label: 'All sources' },
  { id: 'codeforces', label: 'Codeforces' },
  { id: 'cses', label: 'CSES' },
  { id: 'geeksforgeeks', label: 'GeeksforGeeks' },
  { id: 'leetcode', label: 'LeetCode' },
  { id: 'hackerrank', label: 'HackerRank' },
]

const DIFFICULTIES = ['Easy', 'Medium', 'Hard']
const DIFFICULTY_ORDER = { Easy: 0, Medium: 1, Hard: 2 }
const DIFFICULTY_TEXT_CLASS = { Easy: 'text-verified', Medium: 'text-warn', Hard: 'text-danger' }

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest first' },
  { value: 'title-asc', label: 'Title A–Z' },
  { value: 'difficulty-asc', label: 'Difficulty: easy first' },
  { value: 'difficulty-desc', label: 'Difficulty: hard first' },
  { value: 'companies-desc', label: 'Most companies' },
]

const ALL_COMPANIES = ['Google', 'Amazon', 'Microsoft', 'Meta', 'Apple', 'Bloomberg', 'Netflix', 'Adobe', 'Oracle', 'Uber']

const PLACEHOLDER_COMPANY_NAMES = new Set([
  ...SOURCES.map((s) => s.id.toLowerCase()),
  ...SOURCES.map((s) => s.label.toLowerCase()),
  'general',
])
const isRealCompany = (name) => Boolean(name) && !PLACEHOLDER_COMPANY_NAMES.has(name.toLowerCase())

function tintStyle(color, active) {
  if (!active) return undefined
  return {
    background: `linear-gradient(155deg, ${color}4D, ${color}22)`,
    borderColor: `${color}80`,
    color: 'rgb(var(--c-text))',
    boxShadow: `0 4px 14px ${color}33, inset 0 1px 0 rgba(255,255,255,0.15)`,
  }
}

function SkeletonTile() {
  return (
    <div className="hud-tile rounded-none p-5 flex flex-col gap-4">
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

// Toggle switch row used by the new verified/bookmarked/solved filters
function SwitchRow({ label, checked, onChange, icon }) {
  return (
    <label className="flex items-center justify-between gap-3 cursor-pointer group">
      <span className="flex items-center gap-2 text-xs text-muted group-hover:text-bone transition-colors">
        {icon}
        {label}
      </span>
      <input type="checkbox" className="hud-switch" checked={checked} onChange={onChange} />
    </label>
  )
}

export default function UserPortal({ onLogout }) {
  const [activeSource, setActiveSource] = useState('All')
  const [activeCategories, setActiveCategories] = useState(new Set())
  const [activeDifficulties, setActiveDifficulties] = useState(new Set())
  const [activeCompany, setActiveCompany] = useState('All')
  const [verifiedOnly, setVerifiedOnly] = useState(false)
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false)
  const [hideSolved, setHideSolved] = useState(false)
  const [sortBy, setSortBy] = useState('newest')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(new Set())
  const [openQuestion, setOpenQuestion] = useState(null)

  const { set: bookmarks, toggle: toggleBookmark } = useLocalSet('bookmarked_questions_v1')
  const { set: solved, toggle: toggleSolved } = useLocalSet('solved_questions_v1')

  // Category/difficulty/verified/bookmarked/solved are filtered client-side
  // (multi-select — the API only supports one value per field) since the
  // catalog is small enough that this stays instant either way.
  const { questions: serverQuestions, total, stats, loading, isWakingUp } = useQuestions({
    sourceSite: activeSource,
    company: activeCompany,
    search: query,
    limit: 200,
    offset: 0,
  })

  const categories = useMemo(() => {
    const set = new Set()
    serverQuestions.forEach((q) => { if (q.category) set.add(q.category) })
    return Array.from(set).sort()
  }, [serverQuestions])

  const companies = useMemo(() => {
    const set = new Set(ALL_COMPANIES)
    serverQuestions.forEach((q) => {
      const comps = q.companies || (q.company ? [q.company] : [])
      comps.filter(isRealCompany).forEach((c) => set.add(c))
    })
    return Array.from(set).sort()
  }, [serverQuestions])

  const questions = useMemo(() => {
    return serverQuestions.filter((q) => {
      if (activeCategories.size > 0 && !activeCategories.has(q.category)) return false
      if (activeDifficulties.size > 0 && !activeDifficulties.has(q.difficulty)) return false
      if (verifiedOnly && !q.verified) return false
      if (bookmarkedOnly && !bookmarks.has(q.id)) return false
      if (hideSolved && solved.has(q.id)) return false
      return true
    })
  }, [serverQuestions, activeCategories, activeDifficulties, verifiedOnly, bookmarkedOnly, hideSolved, bookmarks, solved])

  const sortedQuestions = useMemo(() => {
    return [...questions].sort((a, b) => {
      if (sortBy === 'newest') {
        const aNew = a.is_new || false
        const bNew = b.is_new || false
        if (aNew !== bNew) return bNew ? 1 : -1
        return (a.id || '').localeCompare(b.id || '')
      }
      if (sortBy === 'title-asc') return (a.title || '').localeCompare(b.title || '')
      if (sortBy === 'companies-desc') {
        const ca = (a.companies || []).length
        const cb = (b.companies || []).length
        return cb - ca
      }
      const da = DIFFICULTY_ORDER[a.difficulty] ?? 1
      const db = DIFFICULTY_ORDER[b.difficulty] ?? 1
      return sortBy === 'difficulty-asc' ? da - db : db - da
    })
  }, [questions, sortBy])

  function toggleCategory(cat) {
    setActiveCategories((prev) => {
      const next = new Set(prev)
      if (next.has(cat)) next.delete(cat)
      else next.add(cat)
      return next
    })
  }

  function toggleDifficulty(d) {
    setActiveDifficulties((prev) => {
      const next = new Set(prev)
      if (next.has(d)) next.delete(d)
      else next.add(d)
      return next
    })
  }

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
    if (!stats?.last_successful_run) return 'Auto-syncs every 30 min'
    try {
      const date = new Date(stats.last_successful_run)
      return `Synced ${date.toLocaleDateString()} · ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
    } catch {
      return 'Auto-syncs every 30 min'
    }
  }, [stats])

  const hardCount = serverQuestions.filter((q) => q.difficulty === 'Hard').length
  const activeFilterCount = activeCategories.size + activeDifficulties.size + (verifiedOnly ? 1 : 0) + (bookmarkedOnly ? 1 : 0) + (hideSolved ? 1 : 0)

  return (
    <div className="min-h-screen relative pb-28">
      <div className="bg-grid" />
      <div className="bg-particles" />
      <div className="bg-orbs" />

      <div className="relative z-10 px-6 py-8 max-w-6xl mx-auto">
        {/* ── Top Header Bar ── */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8 opacity-0 animate-slide-up">
          <div>
            <p className="data-readout text-xs text-catDp font-medium uppercase tracking-[0.3em]">// Question Library</p>
            <h1 className="text-3xl font-bold font-display bg-gradient-to-r from-bone via-bone to-catDp bg-clip-text text-transparent mt-1.5 tracking-tight">
              Verified Question Bank
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <button id="user-logout-btn" onClick={onLogout} className="hud-btn-ghost flex items-center gap-2 text-xs font-medium px-4 py-2.5">
              <LogOutIcon /> Sign out
            </button>
          </div>
        </div>

        {/* ── Bento stat deck ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 opacity-0 animate-slide-up-delay-1" style={{ gridAutoRows: 'minmax(90px, auto)' }}>
          {/* Hero tile */}
          <div className="hud-tile stat-card-glow col-span-2 row-span-2 p-6 flex flex-col justify-between relative" style={{ '--glow-start': '#7c9eff', '--glow-end': '#2dd4bf' }}>
            <HudCorners color="#7c9eff" />
            <div className="flex items-start justify-between">
              <span className="text-[11px] text-muted tracking-[0.2em] uppercase font-medium">Total catalog</span>
              <DifficultyDonut verifiedPct={stats?.verified_percentage ?? 100} />
            </div>
            <div>
              <div className="flex items-baseline gap-2">
                <span className="data-readout text-6xl font-bold text-bone leading-none">{stats?.total || total}</span>
                <span className="text-sm text-muted">questions</span>
              </div>
              <p className="text-xs text-muted mt-3">
                <span className="text-verified font-semibold">{stats?.verified_percentage ?? 100}%</span> verified · auto-synced from the live pipeline
              </p>
            </div>
          </div>

          <MiniStat label="Hard mode" value={hardCount} accent="#F43F5E" sub="high-difficulty picks" />
          <MiniStat label="Categories" value={categories.length} accent="#C084FC" sub="topics covered" />
          <MiniStat label="Bookmarked" value={bookmarks.size} accent="#F59E0B" sub="saved for later" />
          <div className="hud-tile p-5 flex flex-col justify-between relative">
            <HudCorners color="#2dd4bf" />
            <span className="text-[11px] text-muted tracking-[0.2em] uppercase font-medium">Sync status</span>
            <div>
              <div className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-60" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
                <span className="data-readout text-xs font-medium text-emerald-400">{lastUpdatedText}</span>
              </div>
            </div>
          </div>
        </div>

        {/* ── Cold Start Warning Banner ── */}
        {isWakingUp && (
          <div className="mb-6 bg-amber-500/10 border border-amber-500/20 text-amber-200 rounded-xl p-4 flex items-center gap-3 text-sm animate-fade-in">
            <span className="text-amber-400"><LoaderIcon /></span>
            <div>
              <p className="font-semibold text-xs text-amber-400">Waking up the server</p>
              <p className="text-xs text-amber-300/80 mt-0.5">Our free-tier database is cold-starting. Reconnecting automatically…</p>
            </div>
          </div>
        )}

        {/* ── Control Center (Filters & Search) ── */}
        <div className="hud-tile hud-tile-lg p-6 mb-8 opacity-0 animate-slide-up-delay-2 relative">
          <HudCorners />
          <div className="flex items-center justify-between border-b border-line/5 pb-4 mb-5">
            <span className="flex items-center gap-2 text-sm font-semibold text-bone">
              <SlidersIcon /> Filters
            </span>
            {activeFilterCount > 0 && (
              <button
                onClick={() => { setActiveCategories(new Set()); setActiveDifficulties(new Set()); setVerifiedOnly(false); setBookmarkedOnly(false); setHideSolved(false) }}
                className="text-[11px] text-muted hover:text-danger transition-colors flex items-center gap-1"
              >
                Clear {activeFilterCount} <XIcon />
              </button>
            )}
          </div>

          {/* Source Filter Tabs */}
          <div className="mb-5 overflow-x-auto">
            <div className="flex gap-2 pb-1.5 w-max">
              {SOURCES.map((s) => {
                const active = activeSource === s.id
                const color = getSourceColor(s.id)
                return (
                  <button
                    key={s.id}
                    onClick={() => setActiveSource(s.id)}
                    className={`whitespace-nowrap px-4 py-2.5 rounded-full text-xs font-medium border transition-all duration-200 ${active ? '' : 'hud-chip-inactive'}`}
                    style={tintStyle(color, active)}
                  >
                    {s.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Search + Dropdowns Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-muted pointer-events-none">
                <SearchIcon />
              </span>
              <input
                id="search-input"
                type="text"
                placeholder="Search title, statement..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full rounded-xl pl-10 pr-4 py-3 text-sm hud-input"
              />
            </div>

            <select id="company-select" value={activeCompany} onChange={(e) => setActiveCompany(e.target.value)} className="rounded-xl px-4 py-3 text-sm text-muted cursor-pointer hud-input">
              <option value="All">All companies</option>
              {companies.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>

            <select id="sort-select" value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="rounded-xl px-4 py-3 text-sm text-muted cursor-pointer hud-input">
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Sub-Filters Row (multi-select Categories & Difficulties) */}
          <div className="flex flex-col gap-4 pt-4 border-t border-line/5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] text-muted uppercase tracking-wide font-medium mr-1">Category (multi-select)</span>
              {categories.map((cat) => {
                const active = activeCategories.has(cat)
                const color = getCategoryColor(cat)
                return (
                  <button
                    key={cat}
                    onClick={() => toggleCategory(cat)}
                    className={`px-3 py-1.5 rounded-full text-[11px] font-medium border transition-all duration-200 ${active ? '' : 'hud-chip-inactive'}`}
                    style={tintStyle(color, active)}
                  >
                    {cat}
                  </button>
                )
              })}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] text-muted uppercase tracking-wide font-medium mr-1">Difficulty (multi-select)</span>
              {DIFFICULTIES.map((d) => {
                const active = activeDifficulties.has(d)
                const color = { Easy: '#22C55E', Medium: '#F59E0B', Hard: '#F43F5E' }[d]
                return (
                  <button
                    key={d}
                    onClick={() => toggleDifficulty(d)}
                    className={`px-3 py-1.5 rounded-full text-[11px] font-medium border transition-all duration-200 ${active ? '' : 'hud-chip-inactive'}`}
                    style={tintStyle(color, active)}
                  >
                    {d}
                  </button>
                )
              })}
            </div>

            {/* New: toggle-style filters */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-line/5">
              <SwitchRow label="Verified only" checked={verifiedOnly} onChange={(e) => setVerifiedOnly(e.target.checked)} icon={<ShieldCheckIcon />} />
              <SwitchRow label="Bookmarked only" checked={bookmarkedOnly} onChange={(e) => setBookmarkedOnly(e.target.checked)} icon={<StarIcon />} />
              <SwitchRow label="Hide solved" checked={hideSolved} onChange={(e) => setHideSolved(e.target.checked)} icon={<CheckCircleIcon />} />
            </div>
          </div>
        </div>

        {/* ── Results Info Line ── */}
        {!loading && (
          <p className="text-xs text-muted mb-4 animate-fade-in flex items-center gap-2">
            <span className="data-readout">
              Showing <span className="text-catDp font-semibold">{sortedQuestions.length}</span> of{' '}
              <span className="text-muted font-semibold">{total}</span> questions
            </span>
            {activeCompany !== 'All' && (
              <button onClick={() => setActiveCompany('All')} className="flex items-center gap-1.5 bg-catDp/10 border border-catDp/30 text-catDp px-2.5 py-0.5 rounded-full text-[11px] hover:bg-catDp/20 transition-colors">
                {activeCompany} <XIcon />
              </button>
            )}
          </p>
        )}

        {/* ── Loading Skeleton Grid ── */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-4">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonTile key={i} />)}
          </div>
        )}

        {/* ── Question Grid list ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {sortedQuestions.map((q, i) => {
            const sourceSite = q.source_site || q.source || 'codeforces'
            const sourceUrl = q.source_url || '#'
            const comps = (q.companies || (q.company ? [q.company] : [])).filter(isRealCompany)
            const sourceLabel = SOURCES.find((s) => s.id === sourceSite)?.label || sourceSite
            const sourceColor = getSourceColor(sourceSite)
            const categoryColor = getCategoryColor(q.category)
            const isBookmarked = bookmarks.has(q.id)
            const isSolved = solved.has(q.id)

            return (
              <div
                key={q.id}
                onClick={() => setOpenQuestion(q)}
                className="stagger-in hud-tile hud-tile-interactive p-5 flex flex-col gap-4 relative"
                style={{ '--delay': `${(i % 12) * 30}ms` }}
              >
                <HudCorners color={categoryColor} />
                <div className="absolute left-0 top-3 bottom-3 w-[3px] rounded-r-full" style={{ background: `linear-gradient(180deg, ${categoryColor}, ${categoryColor}00)` }} />

                <div className="flex items-center justify-between border-b border-line/5 pb-2.5">
                  <div className="flex items-center gap-2.5" onClick={(e) => e.stopPropagation()}>
                    <input type="checkbox" checked={selected.has(q.id)} onChange={() => toggle(q.id)} className="styled-checkbox" />
                    <span className="data-readout text-[10px] text-muted/70 truncate max-w-[90px]">{q.id}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={(e) => { e.stopPropagation(); toggleSolved(q.id) }}
                      className={`p-1 rounded-md transition-colors ${isSolved ? 'text-verified' : 'text-muted/50 hover:text-verified'}`}
                      title={isSolved ? 'Marked solved' : 'Mark as solved'}
                    >
                      <CheckCircleIcon filled={isSolved} />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); toggleBookmark(q.id) }}
                      className={`p-1 rounded-md transition-colors ${isBookmarked ? 'text-warn' : 'text-muted/50 hover:text-warn'}`}
                      title={isBookmarked ? 'Bookmarked' : 'Bookmark'}
                    >
                      <StarIcon filled={isBookmarked} />
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <a
                    href={sourceUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="flex items-center gap-1.5 text-[10px] font-medium rounded-full pl-1 pr-2.5 py-0.5 border transition-all"
                    style={{ color: sourceColor, borderColor: `${sourceColor}40`, background: `${sourceColor}14` }}
                  >
                    <CompanyLogo name={sourceLabel} color={sourceColor} size={14} />
                    {sourceLabel}
                  </a>
                  <DifficultyGauge difficulty={q.difficulty} size={26} />
                </div>

                <h4 className="font-semibold text-sm leading-snug font-display text-bone hover:text-catDp transition-colors">
                  {q.title}
                </h4>

                <div className="flex flex-wrap gap-1.5 mt-auto">
                  <span className="text-[10px] font-medium px-2.5 py-0.5 rounded-full border" style={{ color: categoryColor, borderColor: `${categoryColor}40`, background: `${categoryColor}14` }}>
                    {q.category}
                  </span>
                  {q.is_new && (
                    <span className="text-emerald-400 text-[10px] font-semibold border border-emerald-500/30 rounded-full px-2.5 py-0.5 bg-emerald-500/10">New</span>
                  )}
                  {q.verified && (
                    <span className="text-emerald-400 text-[10px] font-medium border border-emerald-500/20 rounded-full px-2.5 py-0.5 bg-emerald-500/5">Verified</span>
                  )}
                </div>

                {comps.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1.5 border-t border-line/5">
                    {comps.slice(0, 4).map((c) => {
                      const active = activeCompany === c
                      return (
                        <span
                          key={c}
                          onClick={(e) => { e.stopPropagation(); setActiveCompany(c) }}
                          className={`flex items-center gap-1 text-[10px] font-medium pl-1 pr-2 py-0.5 rounded-full border transition-colors ${active ? 'text-ink font-semibold' : 'text-muted hover:text-bone'}`}
                          style={active ? { background: 'linear-gradient(135deg, #7c9eff, #2dd4bf)', borderColor: 'transparent' } : { borderColor: 'rgb(var(--c-veil) / 0.08)', background: 'rgb(var(--c-veil) / 0.03)' }}
                        >
                          <CompanyLogo name={c} size={13} />
                          {c}
                        </span>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* ── Floating selection bar ── */}
        {selected.size > 0 && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-lg rounded-full frosted-bar px-6 py-3.5 flex items-center justify-between z-40 animate-slide-up">
            <span className="text-sm">
              <span className="text-catDp font-semibold">{selected.size}</span> selected
            </span>
            <button id="download-btn" onClick={handleDownload} className="hud-btn-primary flex items-center gap-2 px-5 py-2.5 text-xs font-semibold">
              <DownloadIcon /> Download selected
            </button>
          </div>
        )}

        <QuestionDetail question={openQuestion} onClose={() => setOpenQuestion(null)} bookmarked={openQuestion && bookmarks.has(openQuestion.id)} solved={openQuestion && solved.has(openQuestion.id)} onToggleBookmark={() => openQuestion && toggleBookmark(openQuestion.id)} onToggleSolved={() => openQuestion && toggleSolved(openQuestion.id)} />
      </div>
    </div>
  )
}

function MiniStat({ label, value, accent, sub }) {
  return (
    <div className="hud-tile p-5 flex flex-col justify-between relative">
      <HudCorners color={accent} />
      <span className="text-[11px] text-muted tracking-[0.2em] uppercase font-medium">{label}</span>
      <div>
        <span className="data-readout text-3xl font-bold" style={{ color: accent }}>{value}</span>
        <p className="text-[11px] text-muted mt-1">{sub}</p>
      </div>
    </div>
  )
}

function DifficultyDonut({ verifiedPct }) {
  const size = 44
  const r = 17
  const circumference = 2 * Math.PI * r
  const offset = circumference * (1 - verifiedPct / 100)
  return (
    <span className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgb(var(--c-veil))" strokeOpacity="0.1" strokeWidth="3" />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none" stroke="url(#donut-gradient)" strokeWidth="3" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.16,1,0.3,1)' }}
        />
        <defs>
          <linearGradient id="donut-gradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#7c9eff" />
            <stop offset="100%" stopColor="#2dd4bf" />
          </linearGradient>
        </defs>
      </svg>
      <span className="absolute data-readout text-[10px] font-bold text-bone">{Math.round(verifiedPct)}%</span>
    </span>
  )
}
