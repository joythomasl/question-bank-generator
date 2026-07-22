import { useMemo, useState } from 'react'
import { MOCK_QUESTIONS } from '../data/mockQuestions.js'
import { getCuratedQuestions } from '../utils/overrides.js'

const CATEGORIES = [
  'Dynamic Programming',
  'Backtracking',
  'Greedy',
  'Divide and Conquer',
  'Two Pointers',
]

// Written as literal class names (not template-interpolated) so Tailwind's
// build-time scanner can actually find and keep them.
const DIFFICULTY_TEXT_CLASS = {
  verified: 'text-verified',
  warn: 'text-warn',
  danger: 'text-danger',
}

export default function UserPortal({ onLogout }) {
  const allQuestions = useMemo(() => getCuratedQuestions(MOCK_QUESTIONS), [])
  const [activeCategory, setActiveCategory] = useState('All')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(() => new Set(allQuestions.map((q) => q.id)))

  const filtered = allQuestions.filter(
    (q) =>
      (activeCategory === 'All' || q.category === activeCategory) &&
      q.title.toLowerCase().includes(query.toLowerCase()),
  )

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

      <input
        type="text"
        placeholder="Search by title"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full bg-surface border border-surfaceRaised rounded-lg px-4 py-2.5 text-sm mb-4 focus:outline-none focus:border-catDp"
      />

      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setActiveCategory('All')}
          className={`px-3 py-1.5 rounded-full text-xs font-medium border ${
            activeCategory === 'All' ? 'border-bone' : 'border-surfaceRaised text-muted'
          }`}
        >
          All
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

      {/* NOTE: swap this grid for react-window / @tanstack/react-virtual once
          the real questions.json (700-1200+ rows) replaces mock data — plain
          .map() will start to feel janky well before that scale. */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((q) => (
          <div
            key={q.id}
            className="bg-surface border border-surfaceRaised rounded-xl p-4 flex flex-col gap-3"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
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
              <span className="text-xs px-2 py-0.5 rounded-full bg-ink text-muted">
                {q.category}
              </span>
              <span
                className={`text-xs px-2 py-0.5 rounded-full bg-ink ${DIFFICULTY_TEXT_CLASS[q.difficultyColor]}`}
              >
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
    </div>
  )
}
