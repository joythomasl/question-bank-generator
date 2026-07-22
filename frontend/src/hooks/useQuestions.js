import { useEffect, useState } from 'react'
import { MOCK_QUESTIONS } from '../data/mockQuestions.js'

// Fetches the real generated dataset from /questions.json at runtime.
// Falls back to mock data if it's missing/empty/errors — so the site keeps
// working while generation is still running, and picks up the real file
// automatically the moment it's dropped into public/questions.json.
export function useQuestions() {
  const [questions, setQuestions] = useState(null)
  const [source, setSource] = useState(null) // 'live' | 'mock'

  useEffect(() => {
    let cancelled = false

    fetch('/questions.json')
      .then((res) => {
        if (!res.ok) throw new Error(`status ${res.status}`)
        return res.json()
      })
      .then((data) => {
        if (cancelled) return
        if (Array.isArray(data) && data.length > 0) {
          setQuestions(data)
          setSource('live')
        } else {
          throw new Error('empty questions.json')
        }
      })
      .catch((err) => {
        if (cancelled) return
        console.warn('Falling back to mock questions:', err.message)
        setQuestions(MOCK_QUESTIONS)
        setSource('mock')
      })

    return () => { cancelled = true }
  }, [])

  return { questions, source, loading: questions === null }
}