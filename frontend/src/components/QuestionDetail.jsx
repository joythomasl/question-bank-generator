import { useState, useEffect } from 'react'

const DIFFICULTY_ROLE = { Easy: 'verified', Medium: 'warn', Hard: 'danger' }
const DIFFICULTY_TEXT_CLASS = {
  verified: 'text-verified',
  warn: 'text-warn',
  danger: 'text-danger',
}

const ACCENT_COLORS = {
  'Dynamic Programming': '#7C9EFF',
  'Backtracking': '#F0806B',
  'Greedy': '#34D399',
  'Divide and Conquer': '#C084FC',
  'Two Pointers': '#38BDF8',
}

export default function QuestionDetail({ question, onClose }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (question) {
      requestAnimationFrame(() => setVisible(true))
      document.body.style.overflow = 'hidden'
    } else {
      setVisible(false)
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [question])

  if (!question) return null

  const diffClass = DIFFICULTY_TEXT_CLASS[DIFFICULTY_ROLE[question.difficulty]] || 'text-muted'
  const accentColor = ACCENT_COLORS[question.category] || '#7C9EFF'
  const sourceSite = question.source_site || question.source || 'codeforces'
  const sourceUrl = question.source_url || '#'
  const comps = question.companies || (question.company ? [question.company] : [])

  const pythonSol = question.solution_python || question.solutions?.python
  const javaSol = question.solution_java || question.solutions?.java

  function handleClose() {
    setVisible(false)
    setTimeout(onClose, 300)
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className={`absolute inset-0 bg-black/60 transition-opacity duration-300 ${
          visible ? 'opacity-100' : 'opacity-0'
        }`}
        style={{ backdropFilter: visible ? 'blur(4px)' : 'blur(0px)' }}
        onClick={handleClose}
      />

      {/* Panel */}
      <div
        className={`relative w-full max-w-xl bg-surface/95 h-full overflow-y-auto flex flex-col shadow-glass transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] terminal-window ${
          visible ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Futuristic Terminal Window Header */}
        <div className="terminal-header px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block"></span>
            <span className="w-3 h-3 rounded-full bg-yellow-500/80 inline-block"></span>
            <span className="w-3 h-3 rounded-full bg-green-500/80 inline-block"></span>
            <span className="font-mono text-xs text-muted ml-3 uppercase tracking-wider">guest@console:~/catalog$</span>
          </div>
          <button
            onClick={handleClose}
            className="text-muted hover:text-bone text-lg font-mono leading-none hover:bg-surfaceRaised/60 w-6 h-6 rounded flex items-center justify-center transition-all duration-200"
          >
            ESC
          </button>
        </div>

        {/* Content Box */}
        <div className="p-7 flex flex-col gap-7 overflow-y-auto">
          {/* Main Info */}
          <div>
            <span className="font-mono text-xs text-catDp uppercase tracking-widest">[{question.id.toUpperCase()}]</span>
            <h2 className="text-xl font-bold mt-2 font-display text-bone leading-snug">{question.title}</h2>
            
            <div className="flex flex-wrap gap-2 mt-4">
              {/* Source Badge with link */}
              <a
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] px-2.5 py-1 rounded bg-catDp/10 text-catDp border border-catDp/30 hover:bg-catDp/20 transition-colors font-mono uppercase tracking-wider"
              >
                {sourceSite} ↗
              </a>
              <span className="text-[10px] px-2.5 py-1 rounded bg-ink/60 text-muted border border-white/5 font-mono uppercase tracking-wider">
                {question.category}
              </span>
              <span className={`text-[10px] px-2.5 py-1 rounded bg-ink/60 ${diffClass} border border-white/5 font-mono uppercase tracking-wider`}>
                {question.difficulty}
              </span>
              {comps.map((c) => (
                <span key={c} className="text-[10px] px-2.5 py-1 rounded bg-ink/60 text-muted border border-white/5 font-mono uppercase tracking-wider">
                  🏢 {c}
                </span>
              ))}
              {question.is_new && (
                <span className="text-emerald-400 text-[9px] font-mono font-bold uppercase tracking-wider border border-emerald-500/50 rounded px-2 py-0.5 bg-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.3)] animate-pulse">
                  NEW
                </span>
              )}
              {question.verified && (
                <span className="text-emerald-400 text-[9px] font-mono uppercase tracking-wider border border-emerald-500/30 rounded px-2 py-0.5 bg-emerald-500/10">
                  VERIFIED
                </span>
              )}
            </div>
          </div>

        {question.type === 'conceptual' || question.item_type === 'conceptual' ? (
          <>
            <Section title="Question" accentColor={accentColor}>
              <p className="text-sm leading-relaxed">{question.question}</p>
            </Section>
            <Section title="Answer" accentColor={accentColor}>
              <p className="text-sm leading-relaxed text-muted">{question.answer}</p>
            </Section>
            {question.key_points?.length > 0 && (
              <Section title="Key points" accentColor={accentColor}>
                <ul className="text-sm text-muted flex flex-col gap-1.5">
                  {question.key_points.map((k, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-catDp mt-0.5 text-xs">▸</span>
                      <span>{k}</span>
                    </li>
                  ))}
                </ul>
              </Section>
            )}
          </>
        ) : (
          <>
            <Section title="Problem" accentColor={accentColor}>
              <p className="text-sm leading-relaxed">{question.problem_statement || 'No problem statement available.'}</p>
            </Section>

            {question.examples?.map((ex, i) => (
              <Section
                key={i}
                title={`Example${question.examples.length > 1 ? ` ${i + 1}` : ''}`}
                accentColor={accentColor}
              >
                <CodeBlock>
                  <p>
                    <span className="text-muted">Input: </span>
                    {typeof ex.input === 'object' ? JSON.stringify(ex.input) : ex.input}
                  </p>
                  <p>
                    <span className="text-muted">Output: </span>
                    {typeof ex.output === 'object' ? JSON.stringify(ex.output) : ex.output}
                  </p>
                </CodeBlock>
                {ex.explanation && <p className="text-sm text-muted mt-2">{ex.explanation}</p>}
              </Section>
            ))}

            {question.constraints?.length > 0 && (
              <Section title="Constraints" accentColor={accentColor}>
                <ul className="text-sm font-mono text-muted flex flex-col gap-1.5">
                  {question.constraints.map((c, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-catDp mt-0.5 text-xs">▸</span>
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </Section>
            )}

            {/* Test cases with Scraped vs Generated Origin Badges */}
            <Section title={`Test cases (${question.test_cases?.length ?? 0})`} accentColor={accentColor}>
              <div className="flex flex-col gap-2">
                {question.test_cases?.map((tc, i) => {
                  const origin = tc.origin || (i === 0 ? 'scraped' : 'generated')
                  return (
                    <div
                      key={i}
                      className="stagger-in bg-ink/60 rounded-xl p-3 font-mono text-xs flex flex-col gap-1 border border-white/5"
                      style={{ '--delay': `${i * 50}ms` }}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-muted text-[10px] uppercase tracking-wider">{tc.edge_case_type || 'case'}</span>
                        {/* Origin badge */}
                        <span
                          className={`text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded border ${
                            origin === 'scraped'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                              : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
                          }`}
                        >
                          {origin}
                        </span>
                      </div>
                      <span>in: {typeof tc.input === 'object' ? JSON.stringify(tc.input) : String(tc.input)}</span>
                      <span>out: {typeof tc.expected_output === 'object' ? JSON.stringify(tc.expected_output) : String(tc.expected_output)}</span>
                    </div>
                  )
                })}
              </div>
            </Section>

            <SolutionViewer pythonSol={pythonSol} javaSol={javaSol} accentColor={accentColor} />
          </>
        )}
        </div>
      </div>
    </div>
  )
}

function Section({ title, accentColor, children }) {
  return (
    <section className="relative pl-4">
      <div
        className="absolute left-0 top-0 bottom-0 w-[3px] rounded-full"
        style={{ backgroundColor: accentColor, opacity: 0.4 }}
      />
      <h3 className="font-mono text-xs text-muted uppercase tracking-widest mb-3">{title}</h3>
      {children}
    </section>
  )
}

function CodeBlock({ children, code }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    const text = code || ''
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      /* noop */
    }
  }

  return (
    <div className="code-block relative group">
      <div className="bg-ink/80 rounded-xl p-4 font-mono text-xs overflow-x-auto border border-white/5">
        {children}
      </div>
      {code && (
        <button
          onClick={handleCopy}
          className="copy-btn absolute top-2 right-2 text-[10px] font-mono text-muted bg-surfaceRaised/80 rounded-md px-2 py-1 hover:text-bone transition-colors"
        >
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      )}
    </div>
  )
}

function SolutionViewer({ pythonSol, javaSol, accentColor }) {
  const hasJava = Boolean(javaSol)
  const [lang, setLang] = useState('python')
  const code = lang === 'python' ? pythonSol : javaSol

  return (
    <Section title="Solution" accentColor={accentColor}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex gap-1 bg-ink/60 rounded-lg p-0.5 border border-white/5">
          <button
            onClick={() => setLang('python')}
            className={`text-xs px-3 py-1.5 rounded-md transition-all duration-200 ${
              lang === 'python' ? 'bg-surfaceRaised text-bone shadow-sm' : 'text-muted hover:text-bone'
            }`}
          >
            Python
          </button>
          <button
            onClick={() => hasJava && setLang('java')}
            disabled={!hasJava}
            className={`text-xs px-3 py-1.5 rounded-md transition-all duration-200 ${
              lang === 'java' ? 'bg-surfaceRaised text-bone shadow-sm' : 'text-muted hover:text-bone'
            } ${!hasJava ? 'opacity-40 cursor-not-allowed' : ''}`}
          >
            Java{!hasJava ? ' (pending)' : ''}
          </button>
        </div>
      </div>
      <CodeBlock code={code}>
        <pre className="whitespace-pre-wrap">{code || '// solution pending'}</pre>
      </CodeBlock>
    </Section>
  )
}