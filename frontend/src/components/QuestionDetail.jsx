import { useState } from 'react'

const DIFFICULTY_ROLE = { Easy: 'verified', Medium: 'warn', Hard: 'danger' }
const DIFFICULTY_TEXT_CLASS = {
  verified: 'text-verified',
  warn: 'text-warn',
  danger: 'text-danger',
}

export default function QuestionDetail({ question, onClose }) {
  if (!question) return null

  const diffClass = DIFFICULTY_TEXT_CLASS[DIFFICULTY_ROLE[question.difficulty]] || 'text-muted'

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-xl bg-surface h-full overflow-y-auto p-6 flex flex-col gap-6">
        <div className="flex items-start justify-between">
          <div>
            <span className="font-mono text-xs text-muted">{question.id}</span>
            <h2 className="text-xl font-semibold mt-1">{question.title}</h2>
            <div className="flex flex-wrap gap-2 mt-2">
              <span className="text-xs px-2 py-0.5 rounded-full bg-ink text-muted">{question.category}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full bg-ink ${diffClass}`}>
                {question.difficulty}
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-ink text-muted">{question.company}</span>
              {question.verified && (
                <span className="text-verified text-xs font-mono uppercase tracking-wide border border-verified rounded px-1.5 py-0.5 -rotate-2">
                  Verified
                </span>
              )}
            </div>
          </div>
          <button onClick={onClose} className="text-muted hover:text-bone text-xl leading-none">×</button>
        </div>

        {question.type === 'conceptual' ? (
          <>
            <section>
              <h3 className="font-mono text-xs text-muted uppercase tracking-widest mb-2">Question</h3>
              <p className="text-sm leading-relaxed">{question.question}</p>
            </section>
            <section>
              <h3 className="font-mono text-xs text-muted uppercase tracking-widest mb-2">Answer</h3>
              <p className="text-sm leading-relaxed text-muted">{question.answer}</p>
            </section>
            {question.key_points?.length > 0 && (
              <section>
                <h3 className="font-mono text-xs text-muted uppercase tracking-widest mb-2">Key points</h3>
                <ul className="text-sm text-muted flex flex-col gap-1">
                  {question.key_points.map((k, i) => <li key={i}>• {k}</li>)}
                </ul>
              </section>
            )}
          </>
        ) : (
          <>
            <section>
              <h3 className="font-mono text-xs text-muted uppercase tracking-widest mb-2">Problem</h3>
              <p className="text-sm leading-relaxed">{question.problem_statement}</p>
            </section>

            {question.examples?.map((ex, i) => (
              <section key={i}>
                <h3 className="font-mono text-xs text-muted uppercase tracking-widest mb-2">
                  Example{question.examples.length > 1 ? ` ${i + 1}` : ''}
                </h3>
                <div className="bg-ink rounded-lg p-3 font-mono text-xs flex flex-col gap-1">
                  <p><span className="text-muted">Input: </span>{ex.input}</p>
                  <p><span className="text-muted">Output: </span>{ex.output}</p>
                </div>
                {ex.explanation && <p className="text-sm text-muted mt-2">{ex.explanation}</p>}
              </section>
            ))}

            <section>
              <h3 className="font-mono text-xs text-muted uppercase tracking-widest mb-2">Constraints</h3>
              <ul className="text-sm font-mono text-muted flex flex-col gap-1">
                {question.constraints?.map((c, i) => <li key={i}>• {c}</li>)}
              </ul>
            </section>

            <section>
              <h3 className="font-mono text-xs text-muted uppercase tracking-widest mb-2">
                Test cases ({question.test_cases?.length ?? 0})
              </h3>
              <div className="flex flex-col gap-1.5">
                {question.test_cases?.map((tc, i) => (
                  <div key={i} className="bg-ink rounded-lg p-2.5 font-mono text-xs flex flex-col gap-0.5">
                    <span className="text-muted">{tc.edge_case_type}</span>
                    <span>in: {JSON.stringify(tc.input)}</span>
                    <span>out: {JSON.stringify(tc.expected_output)}</span>
                  </div>
                ))}
              </div>
            </section>

            <SolutionViewer solutions={question.solutions} />
          </>
        )}
      </div>
    </div>
  )
}

function SolutionViewer({ solutions }) {
  const hasJava = Boolean(solutions?.java)
  const [lang, setLang] = useState('python')
  const code = lang === 'python' ? solutions?.python : solutions?.java

  return (
    <section>
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-mono text-xs text-muted uppercase tracking-widest">Solution</h3>
        <div className="flex gap-1">
          <button
            onClick={() => setLang('python')}
            className={`text-xs px-2 py-1 rounded ${lang === 'python' ? 'bg-surfaceRaised' : 'text-muted'}`}
          >
            Python
          </button>
          <button
            onClick={() => hasJava && setLang('java')}
            disabled={!hasJava}
            className={`text-xs px-2 py-1 rounded ${lang === 'java' ? 'bg-surfaceRaised' : 'text-muted'} ${!hasJava ? 'opacity-40' : ''}`}
          >
            Java{!hasJava ? ' (pending)' : ''}
          </button>
        </div>
      </div>
      <pre className="bg-ink rounded-lg p-3 font-mono text-xs overflow-x-auto whitespace-pre-wrap">
        {code || '// not yet verified'}
      </pre>
    </section>
  )
}