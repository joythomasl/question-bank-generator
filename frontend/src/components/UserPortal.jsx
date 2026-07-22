import { useMemo, useState } from 'react'
import { useQuestions } from '../hooks/useQuestions.js'
import { getCuratedQuestions } from '../utils/overrides.js'
import QuestionDetail from './QuestionDetail.jsx'

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

const SORT_OPTIONS = [
  { value: 'title-asc', label: 'Title A-Z' },
  { value: 'difficulty-asc', label: 'Difficulty: Easy first' },
  { value: 'difficulty-desc', label: 'Difficulty: Hard first' },
]

export default function UserPortal({ onLogout }) {
  const { questions: rawQuestions, loading } = useQuestions()
  const allQuestions = useMemo(
    () => (rawQuestions ? getCuratedQuestions(rawQuestions) : []),
    [rawQuestions],
  )

  const [activeCategory, setActiveCategory] = useState('All')
  const [activeDifficulty, setActiveDifficulty] = useState('All')
  const [activeCompany, setActiveCompany] = useState('All')
  const [sortBy, setSortBy] = useState('title-asc')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(new Set())
  const [openQuestion, setOpenQuestion] = useState(null)

  useMemo(() => {
    if (rawQuestions) setSelected(new Set(allQuestions.map((q) => q.id)))
  }, [rawQuestions]) // eslint-disable-line react-hooks/exhaustive-deps

  const companies = useMemo(() => {
    const set = new Set()
    allQuestions.forEach((q) => {
      if (q.company) set.add(q.company)
    })
    return Array.from(set).sort()
  }, [allQuestions])

  const filtered = useMemo(() => {
    let result = allQuestions.filter(
      (q) =>
        (activeCategory === 'All' || q.category === activeCategory) &&
        (activeDifficulty === 'All' || q.difficulty === activeDifficulty) &&
        (activeCompany === 'All' || q.company === activeCompany) &&
        q.title.toLowerCase().includes(query.toLowerCase()),
    )

    result = [...result].sort((a, b) => {
      if (sortBy === 'title-asc') return a.title.localeCompare(b.title)
      const da = DIFFICULTY_ORDER[a.difficulty] ?? 1
      const db = DIFFICULTY_ORDER[b.difficulty] ?? 1
      return sortBy === 'difficulty-asc' ? da - db : db - da
    })

    return result
  }, [allQuestions, activeCategory, activeDifficulty, activeCompany, query, sortBy])

  function toggle(id) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  function handleDownload() {
    const data = allQuestions.filter((q) => selected.has(q.id))
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'questions.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen px-6 py-8 max-w-6xl mx-auto pb-24">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="font-mono text-xs text-muted uppercase tracking-widest">Question bank</p>
          <h1 className="text-xl font-semibold">Browse verified questions</h1>
        </div>
        <button
          onClick={onLogout}
          className="text-sm text-muted hover:text-bone border border-surfaceRaised rounded-lg px-3 py-1.5"
        >
          Log out
        </button>
      </div>

      {companies.length > 0 && (
        <div className="mb-4 overflow-x-auto">
          <div className="flex gap-2 pb-1 w-max">
            <button
              onClick={() => setActiveCompany('All')}
              className={`whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-mono border ${
                activeCompany === 'All' ? 'border-bone' : 'border-surfaceRaised text-muted'
              }`}
            >
              All companies
            </button>
            {companies.map((c) => (
              <button
                key={c}
                onClick={() => setActiveCompany(c)}
                className={`whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-mono border ${
                  activeCompany === c ? 'border-bone' : 'border-surfaceRaised text-muted'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-3 mb-4">
        <input
          type="text"
          placeholder="Search by title"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 bg-surface border border-surfaceRaised rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-catDp"
        />
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-surface border border-surfaceRaised rounded-lg px-3 py-2.5 text-sm text-muted"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        <button
          onClick={() => setActiveCategory('All')}
          className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
            activeCategory === 'All' ? 'border-bone' : 'border-surfaceRaised text-muted'
          }`}
        >
          All categories
        </button>
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
              activeCategory === cat ? 'border-bone' : 'border-surfaceRaised text-muted'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setActiveDifficulty('All')}
          className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
            activeDifficulty === 'All' ? 'border-bone' : 'border-surfaceRaised text-muted'
          }`}
        >
          All difficulties
        </button>
        {DIFFICULTIES.map((d) => (
          <button
            key={d}
            onClick={() => setActiveDifficulty(d)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
              activeDifficulty === d ? 'border-bone' : 'border-surfaceRaised text-muted'
            }`}
          >
            {d}
          </button>
        ))}
      </div>

      {loading && <p className="text-muted text-sm mb-4">Loading questions…</p>}
      {!loading && (
        <p className="text-xs text-muted mb-4">{filtered.length} of {allQuestions.length} questions shown</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((q) => (
          <div
            key={q.id}
            onClick={() => setOpenQuestion(q)}
            className="bg-surface border border-surfaceRaised rounded-xl p-4 flex flex-col gap-3 cursor-pointer hover:border-catDp transition"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                <input type="checkbox" checked={selected.has(q.id)} onChange={() => toggle(q.id)} />
                <span className="font-mono text-xs text-muted">{q.id}</span>
              </div>
              {q.verified && (
                <span className="text-verified text-xs font-mono uppercase tracking-wide border border-verified rounded px-1.5 py-0.5 -rotate-2">
                  Verified
                </span>
              )}
            </div>
            <p className="font-medium text-sm">{q.title}</p>
            <div className="flex flex-wrap gap-2">
              <span className="text-xs px-2 py-0.5 rounded-full bg-ink text-muted">{q.category}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full bg-ink ${DIFFICULTY_TEXT_CLASS[DIFFICULTY_ROLE[q.difficulty]] || 'text-muted'}`}>
                {q.difficulty}
              </span>
            </div>
            <span className="text-xs text-muted">{q.company}</span>
          </div>
        ))}
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-surface border-t border-surfaceRaised px-6 py-4 flex items-center justify-between">
        <span className="text-sm font-medium">{selected.size} selected</span>
        <button
          onClick={handleDownload}
          className="bg-catTwoPointers text-ink font-medium rounded-lg px-4 py-2 text-sm"
        >
          Download selected
        </button>
      </div>

      <QuestionDetail question={openQuestion} onClose={() => setOpenQuestion(null)} />
    </div>
  )
}