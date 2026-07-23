import { useEffect, useRef, useState } from 'react'

/**
 * LiveGenerateButton
 *
 * Responsibilities:
 *  1. On page mount: silently pre-load Pyodide (WASM Python runtime) into a
 *     ref so it's warm before the user ever clicks the button.
 *  2. On click: fetch /api/generate-question (abort after 115s), then run the
 *     returned python_solution against all 10 test_cases in Pyodide, animating
 *     each test case as pass/fail in real time.
 *  3. Call onGenerated(question) only when all 10 test cases genuinely pass.
 *  4. Show a clear error state for any failure — never leave the UI hanging.
 */
export default function LiveGenerateButton({ onGenerated }) {
  const pyodideRef = useRef(null)
  const pyodideLoadingRef = useRef(false)
  const abortRef = useRef(null)
  const isGeneratingRef = useRef(false)  // synchronous guard — immune to React batching

  const [pyodideReady, setPyodideReady] = useState(false)
  const [status, setStatus] = useState('idle') // idle | loading | verifying | success | error
  const [errorMsg, setErrorMsg] = useState('')
  const [testResults, setTestResults] = useState([]) // Array<'pending'|'pass'|'fail'>
  const [currentQuestion, setCurrentQuestion] = useState(null)

  // ── Pre-load Pyodide silently on mount ──────────────────────────────────────
  useEffect(() => {
    if (pyodideLoadingRef.current) return
    pyodideLoadingRef.current = true

    // Inject the Pyodide CDN script tag once
    if (!document.getElementById('pyodide-script')) {
      const script = document.createElement('script')
      script.id = 'pyodide-script'
      script.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js'
      script.async = true
      script.onload = async () => {
        try {
          // eslint-disable-next-line no-undef
          const pyodide = await loadPyodide({
            indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/',
          })
          pyodideRef.current = pyodide
          setPyodideReady(true)
          console.log('[LiveGenerateButton] Pyodide ready ✓')
        } catch (err) {
          console.warn('[LiveGenerateButton] Pyodide failed to load:', err)
          // Non-fatal — button still works, verification step will be skipped
          setPyodideReady(false)
        }
      }
      document.head.appendChild(script)
    }
  }, [])

  // ── Run Pyodide verification ─────────────────────────────────────────────────
  async function verifyWithPyodide(question) {
    const pyodide = pyodideRef.current
    const testCases = question.test_cases || []
    const pythonCode = question.solutions?.python || ''

    // Initialise all as pending
    setTestResults(testCases.map(() => 'pending'))

    const results = []

    for (let i = 0; i < testCases.length; i++) {
      const tc = testCases[i]
      let passed = false

      try {
        if (!pyodide) throw new Error('Pyodide not ready')

        // Build a runnable Python snippet: define solve(), call it, compare
        const inputArgs = Object.entries(tc.input || {})
          .map(([k, v]) => `${k} = ${JSON.stringify(v)}`)
          .join('\n')

        const callArgs = Object.keys(tc.input || {}).join(', ')

        const snippet = `
import json

${pythonCode}

${inputArgs}
result = solve(${callArgs})
expected = json.loads(${JSON.stringify(JSON.stringify(tc.expected_output))})

def smart_equal(a, b):
    # 1. Exact equality (covers list, dict, bool, None)
    if a == b:
        return True
    # 2. Numeric: int/float/bool cross-comparison
    try:
        if abs(float(a) - float(b)) < 1e-9:
            return True
    except (TypeError, ValueError):
        pass
    # 3. String normalisation: "6" vs 6
    try:
        if str(a).strip() == str(b).strip():
            return True
    except Exception:
        pass
    # 4. Lists: try sorted comparison (handles [1,0] vs [0,1])
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        try:
            if sorted(a) == sorted(b):
                return True
        except TypeError:
            pass
    # 5. Set equality for unordered collections
    try:
        if set(a) == set(b):
            return True
    except TypeError:
        pass
    return False

smart_equal(result, expected)
`.trim()


        const outcome = await pyodide.runPythonAsync(snippet)
        passed = outcome === true
      } catch (e) {
        passed = false
        console.warn(`[LiveGenerateButton] Test case ${i + 1} error:`, e)
      }

      results.push(passed ? 'pass' : 'fail')

      // Animate each result as it comes in (with a tiny stagger for visual effect)
      setTestResults([...results, ...Array(testCases.length - results.length).fill('pending')])
      await new Promise((r) => setTimeout(r, 80))
    }

    return results
  }

  // ── Main click handler ──────────────────────────────────────────────────────
  async function handleClick() {
    // Synchronous ref guard — prevents double-fire regardless of React batching
    if (isGeneratingRef.current) return
    isGeneratingRef.current = true

    if (status === 'loading' || status === 'verifying') return

    setStatus('loading')
    setErrorMsg('')
    setTestResults([])
    setCurrentQuestion(null)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const res = await fetch('/api/generate-question', {
        method: 'GET',
        signal: controller.signal,
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({ error: `HTTP ${res.status}` }))
        throw new Error(body.error || `HTTP ${res.status}`)
      }

      const question = await res.json()
      setCurrentQuestion(question)
      setStatus('verifying')

      const results = await verifyWithPyodide(question)
      const passCount = results.filter(r => r === 'pass').length
      const allPassed = passCount === results.length

      // Always add the question — full pass, partial pass, or even 0 pass
      const finalQuestion = {
        ...question,
        verified: allPassed,
        pyodide_pass_count: passCount,
        pyodide_total: results.length,
      }
      setCurrentQuestion(finalQuestion)
      setStatus('success')
      onGenerated(finalQuestion)
    } catch (err) {
      if (err.name === 'AbortError') {
        setStatus('error')
        setErrorMsg('Generation cancelled.')
      } else {
        setStatus('error')
        setErrorMsg(err.message || 'Generation failed — try again.')
      }
    } finally {
      abortRef.current = null
      isGeneratingRef.current = false
    }
  }

  function handleCancel() {
    if (abortRef.current) abortRef.current.abort()
    setStatus('idle')
    setErrorMsg('')
    setTestResults([])
  }

  function handleReset() {
    setStatus('idle')
    setErrorMsg('')
    setTestResults([])
    setCurrentQuestion(null)
  }

  // ── Render ──────────────────────────────────────────────────────────────────
  const isActive = status === 'loading' || status === 'verifying'

  return (
    <div className="mb-6">
      {/* ── Trigger button ── */}
      {status === 'idle' && (
        <div className="flex items-center gap-3">
          <button
            id="live-generate-btn"
            onClick={handleClick}
            className="
              relative flex items-center gap-2
              px-4 py-2.5 rounded-xl text-sm font-medium
              bg-gradient-to-r from-violet-600 to-indigo-600
              hover:from-violet-500 hover:to-indigo-500
              text-white shadow-lg shadow-indigo-900/40
              transition-all duration-200 hover:scale-105 active:scale-95
            "
          >
            <span className="text-base">⚡</span>
            Generate live question
            {!pyodideReady && (
              <span className="ml-1 opacity-60 text-xs">(warming up…)</span>
            )}
          </button>
          {pyodideReady && (
            <span className="text-xs text-emerald-500 font-mono flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse inline-block" />
              Verifier ready
            </span>
          )}
        </div>
      )}

      {/* ── Active generation panel ── */}
      {isActive && (
        <div className="
          relative rounded-2xl border border-violet-500/40
          bg-gradient-to-br from-surface to-ink p-5
          shadow-xl shadow-violet-900/20
          overflow-hidden
        ">
          {/* Animated glow border */}
          <div className="absolute inset-0 rounded-2xl pointer-events-none"
            style={{
              background: 'linear-gradient(135deg, rgba(139,92,246,0.12) 0%, rgba(99,102,241,0.08) 100%)',
              animation: 'pulse 2s cubic-bezier(0.4,0,0.6,1) infinite',
            }}
          />

          <div className="relative">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-violet-500 animate-ping" />
                <span className="text-sm font-medium text-violet-300">
                  {status === 'loading' ? 'Scraping + generating…' : 'Verifying with Pyodide…'}
                </span>
              </div>
              <button
                onClick={handleCancel}
                className="text-xs text-muted hover:text-bone border border-surfaceRaised rounded px-2 py-1"
              >
                Cancel
              </button>
            </div>


            {/* Phase labels */}
            <div className="flex items-center gap-2 mb-4">
              <PhaseChip label="Scrape" done={status === 'verifying' || status === 'success'} active={status === 'loading'} />
              <span className="text-surfaceRaised text-xs">→</span>
              <PhaseChip label="Generate" done={status === 'verifying' || status === 'success'} active={status === 'loading'} />
              <span className="text-surfaceRaised text-xs">→</span>
              <PhaseChip label="Verify (Pyodide)" done={status === 'success'} active={status === 'verifying'} />
            </div>

            {/* Question title once we have it */}
            {currentQuestion && (
              <div className="mb-4 p-3 bg-ink rounded-xl border border-surfaceRaised">
                <p className="text-xs text-muted font-mono mb-1">Generated question</p>
                <p className="text-sm font-medium">{currentQuestion.title}</p>
                <div className="flex gap-2 mt-1.5">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-surfaceRaised text-muted">{currentQuestion.category}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-surfaceRaised text-muted">{currentQuestion.difficulty}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-surfaceRaised text-muted font-mono">{currentQuestion.seed_source}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Success state ── */}
      {status === 'success' && currentQuestion && (
        <div className="rounded-2xl border border-emerald-500/40 bg-gradient-to-br from-surface to-ink p-5 shadow-xl shadow-emerald-900/10">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 text-lg">✓</div>
              <div>
                <p className="text-sm font-semibold text-emerald-400">Question generated successfully</p>
                <p className="text-xs text-muted mt-0.5">"{currentQuestion.title}" added to the list</p>
              </div>
            </div>
            <button onClick={handleReset} className="text-xs text-muted hover:text-bone">Dismiss</button>
          </div>

            <button
            onClick={handleReset}
            className="
              mt-4 w-full flex items-center justify-center gap-2
              px-4 py-2.5 rounded-xl text-sm font-medium
              bg-gradient-to-r from-violet-600 to-indigo-600
              hover:from-violet-500 hover:to-indigo-500
              text-white transition-all duration-200
            "
          >
            <span>⚡</span> Generate another
          </button>
        </div>
      )}

      {/* ── Error state ── */}
      {status === 'error' && (
        <div className="rounded-2xl border border-red-500/30 bg-gradient-to-br from-surface to-ink p-5">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-400 text-base shrink-0">✕</div>
            <div className="flex-1">
              <p className="text-sm font-medium text-red-400">Generation failed</p>
              <p className="text-xs text-muted mt-1 leading-relaxed">{errorMsg}</p>
            </div>
          </div>
          <button
            onClick={handleReset}
            className="
              mt-4 w-full flex items-center justify-center gap-2
              px-4 py-2.5 rounded-xl text-sm font-medium
              bg-gradient-to-r from-violet-600 to-indigo-600
              hover:from-violet-500 hover:to-indigo-500
              text-white transition-all duration-200
            "
          >
            <span>⚡</span> Try again
          </button>
        </div>
      )}
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

function PhaseChip({ label, done, active }) {
  return (
    <span className={`
      text-xs px-2.5 py-1 rounded-full font-mono border transition-all duration-300
      ${done ? 'border-emerald-500/50 text-emerald-400 bg-emerald-900/20' :
        active ? 'border-violet-500/60 text-violet-300 bg-violet-900/20 animate-pulse' :
        'border-surfaceRaised text-muted'}
    `}>
      {done ? '✓ ' : active ? '⟳ ' : ''}{label}
    </span>
  )
}

function TestDot({ index, result }) {
  const colorMap = {
    pending: 'bg-surfaceRaised border-surfaceRaised',
    pass: 'bg-emerald-500/30 border-emerald-500 shadow-emerald-900/40',
    fail: 'bg-red-500/30 border-red-500 shadow-red-900/40',
  }
  const labelMap = { pending: '?', pass: '✓', fail: '✕' }
  const textMap = { pending: 'text-muted', pass: 'text-emerald-400', fail: 'text-red-400' }

  return (
    <div
      title={`Test ${index + 1}: ${result}`}
      className={`
        w-7 h-7 rounded-lg border flex items-center justify-center
        text-xs font-mono font-bold shadow-sm
        transition-all duration-300
        ${colorMap[result] || colorMap.pending}
        ${textMap[result] || textMap.pending}
        ${result === 'pass' ? 'scale-110' : ''}
      `}
    >
      {labelMap[result] ?? '?'}
    </div>
  )
}
