import { useMemo, useState } from 'react'
import { useQuestions } from '../hooks/useQuestions.js'
import { editQuestion, getCuratedQuestions, removeQuestion, resetOverrides } from '../utils/overrides.js'

function Bar({ label, count, total, colorClass = 'bg-catDp' }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs w-40 text-muted truncate">{label}</span>
      <div className="flex-1 bg-ink rounded-full h-2">
        <div className={`${colorClass} h-2 rounded-full`} style={{ width: `${total ? (count / total) * 100 : 0}%` }} />
      </div>
      <span className="text-xs w-8 text-right">{count}</span>
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
    questions.forEach((q) => { counts[q.type || 'coding'] = (counts[q.type || 'coding'] || 0) + 1 })
    return counts
  }, [questions])

  const verifiedCount = questions.filter((q) => q.verified).length
  const unverifiedCount = questions.length - verifiedCount
  const verifiedPct = questions.length ? Math.round((verifiedCount / questions.length) * 100) : 0
  const uniqueCompanies = new Set(questions.map((q) => q.company).filter(Boolean)).size

  return (
    <div className="min-h-screen px-6 py-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="font-mono text-xs text-muted uppercase tracking-widest">Admin</p>
          <h1 className="text-xl font-semibold">Question bank management</h1>
        </div>
        <button onClick={onLogout} className="text-sm text-muted hover:text-bone border border-surfaceRaised rounded-lg px-3 py-1.5">
          Log out
        </button>
      </div>

      <div className="flex gap-2 mb-6">
        <button onClick={() => setTab('manage')} className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'manage' ? 'bg-surfaceRaised' : 'text-muted'}`}>
          Manage questions
        </button>
        <button onClick={() => setTab('analytics')} className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'analytics' ? 'bg-surfaceRaised' : 'text-muted'}`}>
          Analytics
        </button>
      </div>

      {tab === 'manage' && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-muted">{questions.length} questions in the curated set</p>
            <div className="flex gap-2">
              <button onClick={handleReset} className="text-xs text-muted border border-surfaceRaised rounded-lg px-3 py-1.5">
                Reset overrides
              </button>
              <button onClick={handleExport} className="text-xs bg-catTwoPointers text-ink font-medium rounded-lg px-3 py-1.5">
                Export questions.json
              </button>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            {questions.map((q) => (
              <div key={q.id} className="bg-surface border border-surfaceRaised rounded-lg px-4 py-3 flex items-center gap-4">
                <span className="font-mono text-xs text-muted w-16 truncate">{q.id}</span>
                <span className="flex-1 text-sm font-medium truncate">{q.title}</span>
                <span className="text-xs text-muted w-40 truncate">{q.category}</span>
                <span className="text-xs text-muted w-24 truncate">{q.company}</span>
                <select
                  value={q.difficulty}
                  onChange={(e) => handleEditDifficulty(q.id, e.target.value)}
                  className="bg-ink border border-surfaceRaised rounded-md text-xs px-2 py-1"
                >
                  <option>Easy</option>
                  <option>Medium</option>
                  <option>Hard</option>
                </select>
                <button onClick={() => handleRemove(q.id)} className="text-xs text-danger border border-surfaceRaised rounded-lg px-2 py-1">
                  Remove
                </button>
              </div>
            ))}
          </div>

          <p className="text-xs text-muted mt-6">
            Edits and removals here are stored in this browser only. Use export to bake the curated set into the questions.json shipped with the deployed site.
          </p>
        </div>
      )}

      {tab === 'analytics' && (
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-surface border border-surfaceRaised rounded-xl p-4">
              <p className="text-xs text-muted mb-1">Total questions</p>
              <p className="text-2xl font-semibold">{questions.length}</p>
            </div>
            <div className="bg-surface border border-surfaceRaised rounded-xl p-4">
              <p className="text-xs text-muted mb-1">Verified</p>
              <p className="text-2xl font-semibold text-verified">{verifiedPct}%</p>
              <p className="text-xs text-muted mt-1">{verifiedCount} of {questions.length}</p>
            </div>
            <div className="bg-surface border border-surfaceRaised rounded-xl p-4">
              <p className="text-xs text-muted mb-1">Categories</p>
              <p className="text-2xl font-semibold">{categoryCounts.length}</p>
            </div>
            <div className="bg-surface border border-surfaceRaised rounded-xl p-4">
              <p className="text-xs text-muted mb-1">Companies</p>
              <p className="text-2xl font-semibold">{uniqueCompanies}</p>
            </div>
          </div>

          <div className="bg-surface border border-surfaceRaised rounded-xl p-5">
            <p className="text-sm text-muted mb-3">Verified vs unverified</p>
            <div className="flex flex-col gap-2">
              <Bar label="Verified" count={verifiedCount} total={questions.length} colorClass="bg-verified" />
              <Bar label="Unverified" count={unverifiedCount} total={questions.length} colorClass="bg-danger" />
            </div>
          </div>

          <div className="bg-surface border border-surfaceRaised rounded-xl p-5">
            <p className="text-sm text-muted mb-3">By category</p>
            <div className="flex flex-col gap-2">
              {categoryCounts.map(([cat, count]) => (
                <Bar key={cat} label={cat} count={count} total={questions.length} colorClass="bg-catDp" />
              ))}
            </div>
          </div>

          <div className="bg-surface border border-surfaceRaised rounded-xl p-5">
            <p className="text-sm text-muted mb-3">By difficulty</p>
            <div className="flex flex-col gap-2">
              <Bar label="Easy" count={difficultyCounts.Easy} total={questions.length} colorClass="bg-verified" />
              <Bar label="Medium" count={difficultyCounts.Medium} total={questions.length} colorClass="bg-warn" />
              <Bar label="Hard" count={difficultyCounts.Hard} total={questions.length} colorClass="bg-danger" />
            </div>
          </div>

          <div className="bg-surface border border-surfaceRaised rounded-xl p-5">
            <p className="text-sm text-muted mb-3">Top companies</p>
            <div className="flex flex-col gap-2">
              {companyCounts.map(([company, count]) => (
                <Bar key={company} label={company} count={count} total={questions.length} colorClass="bg-catTwoPointers" />
              ))}
            </div>
          </div>

          <div className="bg-surface border border-surfaceRaised rounded-xl p-5">
            <p className="text-sm text-muted mb-3">By source</p>
            <div className="flex flex-col gap-2">
              {sourceCounts.map(([source, count]) => (
                <Bar key={source} label={source} count={count} total={questions.length} colorClass="bg-catBacktrack" />
              ))}
            </div>
          </div>

          <div className="bg-surface border border-surfaceRaised rounded-xl p-5">
            <p className="text-sm text-muted mb-3">Coding vs conceptual</p>
            <div className="flex flex-col gap-2">
              <Bar label="Coding" count={typeCounts.coding} total={questions.length} colorClass="bg-catGreedy" />
              <Bar label="Conceptual" count={typeCounts.conceptual} total={questions.length} colorClass="bg-catDc" />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}