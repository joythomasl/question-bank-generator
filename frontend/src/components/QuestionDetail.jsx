import { useState, useEffect } from 'react'
import { XIcon, CopyIcon, CheckIcon, StarIcon, CheckCircleIcon } from './icons.jsx'
import CompanyLogo from './CompanyLogo.jsx'
import { getCategoryColor, getSourceColor } from '../utils/colors.js'

const DIFFICULTY_ROLE = { Easy: 'verified', Medium: 'warn', Hard: 'danger' }
const DIFFICULTY_TEXT_CLASS = {
  verified: 'text-verified',
  warn: 'text-warn',
  danger: 'text-danger',
}

// Mirrors UserPortal's filter — competitive-programming questions are tagged
// with their own source site as a placeholder "company" when none is known.
const PLACEHOLDER_COMPANY_NAMES = new Set([
  'codeforces', 'cses', 'geeksforgeeks', 'leetcode', 'hackerrank', 'general',
])
const isRealCompany = (name) => Boolean(name) && !PLACEHOLDER_COMPANY_NAMES.has(name.toLowerCase())

export default function QuestionDetail({ question, onClose, bookmarked, solved, onToggleBookmark, onToggleSolved }) {
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
  const accentColor = getCategoryColor(question.category)
  const sourceSite = question.source_site || question.source || 'codeforces'
  const sourceUrl = question.source_url || '#'
  const sourceColor = getSourceColor(sourceSite)
  const comps = (question.companies || (question.company ? [question.company] : [])).filter(isRealCompany)

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
        className={`absolute inset-0 bg-black/50 transition-opacity duration-300 ${
          visible ? 'opacity-100' : 'opacity-0'
        }`}
        style={{ backdropFilter: visible ? 'blur(6px)' : 'blur(0px)' }}
        onClick={handleClose}
      />

      {/* Panel */}
      <div
        className={`hud-sheet relative w-full max-w-xl h-full overflow-y-auto flex flex-col transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
          visible ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Panel header */}
        <div className="hud-sheet-header sticky top-0 z-10 px-7 py-5 flex items-center justify-between">
          <span className="data-readout text-xs text-muted font-medium uppercase tracking-wide">
            Question details
          </span>
          <div className="flex items-center gap-1">
            {onToggleSolved && (
              <button
                onClick={onToggleSolved}
                title={solved ? 'Marked solved' : 'Mark as solved'}
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 ${solved ? 'text-verified' : 'text-muted hover:text-verified'}`}
              >
                <CheckCircleIcon filled={solved} />
              </button>
            )}
            {onToggleBookmark && (
              <button
                onClick={onToggleBookmark}
                title={bookmarked ? 'Bookmarked' : 'Bookmark'}
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 ${bookmarked ? 'text-warn' : 'text-muted hover:text-warn'}`}
              >
                <StarIcon filled={bookmarked} />
              </button>
            )}
            <button
              onClick={handleClose}
              aria-label="Close"
              className="text-muted hover:text-bone w-8 h-8 rounded-full flex items-center justify-center hover:bg-veil/8 transition-all duration-200"
            >
              <XIcon />
            </button>
          </div>
        </div>

        {/* Content Box */}
        <div className="p-7 pt-2 flex flex-col gap-7 overflow-y-auto">
          {/* Main Info */}
          <div>
            <h2 className="text-xl font-semibold mt-2 font-display text-bone leading-snug">{question.title}</h2>

            <div className="flex flex-wrap gap-2 mt-4">
              {/* Source Badge with link */}
              <a
                href={sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-[11px] font-medium pl-1.5 pr-2.5 py-1 rounded-full border transition-colors capitalize"
                style={{ color: sourceColor, borderColor: `${sourceColor}4D`, background: `${sourceColor}1A` }}
              >
                <CompanyLogo name={sourceSite} color={sourceColor} size={15} />
                {sourceSite} ↗
              </a>
              <span
                className="text-[11px] font-medium px-2.5 py-1 rounded-full border"
                style={{ color: accentColor, borderColor: `${accentColor}4D`, background: `${accentColor}1A` }}
              >
                {question.category}
              </span>
              <span className={`text-[11px] font-medium px-2.5 py-1 rounded-full bg-veil/5 ${diffClass} border border-line/8`}>
                {question.difficulty}
              </span>
              {comps.map((c) => (
                <span key={c} className="flex items-center gap-1.5 text-[11px] font-medium pl-1.5 pr-2.5 py-1 rounded-full bg-veil/5 text-muted border border-line/8">
                  <CompanyLogo name={c} size={15} />
                  {c}
                </span>
              ))}
              {question.is_new && (
                <span className="text-emerald-400 text-[11px] font-semibold rounded-full px-2.5 py-1 bg-emerald-500/15 border border-emerald-500/40">
                  New
                </span>
              )}
              {question.verified && (
                <span className="text-emerald-400 text-[11px] font-medium rounded-full px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/30">
                  Verified
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
                      className="stagger-in hud-code rounded-2xl p-3 font-mono text-xs flex flex-col gap-1"
                      style={{ '--delay': `${i * 50}ms` }}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-muted text-[10px] uppercase tracking-wider">{tc.edge_case_type || 'case'}</span>
                        {/* Origin badge */}
                        <span
                          className={`text-[9px] font-mono uppercase tracking-wider px-1.5 py-0.5 rounded-full border ${
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
        style={{ backgroundColor: accentColor, opacity: 0.45 }}
      />
      <h3 className="text-xs text-muted font-semibold uppercase tracking-wide mb-3">{title}</h3>
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
    <div className="relative group">
      <div className="hud-code rounded-2xl p-4 font-mono text-xs overflow-x-auto">
        {children}
      </div>
      {code && (
        <button
          onClick={handleCopy}
          className="absolute top-2.5 right-2.5 flex items-center gap-1.5 text-[10px] font-medium text-muted bg-veil/8 border border-line/10 rounded-full px-2.5 py-1 hover:text-bone hover:bg-veil/12 transition-colors"
        >
          {copied ? <CheckIcon /> : <CopyIcon />}
          {copied ? 'Copied' : 'Copy'}
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
        <div className="flex gap-1 bg-veil/5 rounded-full p-1 border border-line/8">
          <button
            onClick={() => setLang('python')}
            className={`text-xs px-3 py-1.5 rounded-full transition-all duration-200 ${
              lang === 'python' ? 'bg-veil/12 text-bone' : 'text-muted hover:text-bone'
            }`}
          >
            Python
          </button>
          <button
            onClick={() => hasJava && setLang('java')}
            disabled={!hasJava}
            className={`text-xs px-3 py-1.5 rounded-full transition-all duration-200 ${
              lang === 'java' ? 'bg-veil/12 text-bone' : 'text-muted hover:text-bone'
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
