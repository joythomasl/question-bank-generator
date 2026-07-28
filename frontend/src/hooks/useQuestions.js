import { useEffect, useState, useCallback } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export function useQuestions(params = {}) {
  const [questions, setQuestions] = useState([])
  const [total, setTotal] = useState(0)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isWakingUp, setIsWakingUp] = useState(false)

  const {
    sourceSite = 'All',
    category = 'All',
    difficulty = 'All',
    company = 'All',
    search = '',
    limit = 50,
    offset = 0
  } = params

  const checkHealthAndFetch = useCallback(async () => {
    setLoading(true)
    let cancelled = false
    let timerId = null

    // Show waking up notice if backend doesn't respond within 2 seconds
    timerId = setTimeout(() => {
      if (!cancelled) setIsWakingUp(true)
    }, 2000)

    const healthUrl = `${API_BASE_URL}/api/health`
    let isHealthy = false
    let attempts = 0
    const maxAttempts = 15 // Max retries before stopping loop

    while (!isHealthy && attempts < maxAttempts && !cancelled) {
      try {
        attempts++
        const controller = new AbortController()
        const timeout = setTimeout(() => controller.abort(), 3000)

        const res = await fetch(healthUrl, { signal: controller.signal })
        clearTimeout(timeout)

        if (res.ok) {
          isHealthy = true
          clearTimeout(timerId)
          setIsWakingUp(false)
        } else {
          throw new Error(`HTTP status ${res.status}`)
        }
      } catch (err) {
        if (cancelled) return
        if (attempts >= 2) setIsWakingUp(true)
        // Wait 3 seconds before next retry
        await new Promise((resolve) => setTimeout(resolve, 3000))
      }
    }

    if (cancelled) return

    // Fetch questions & stats once server responds or fallback
    try {
      const query = new URLSearchParams()
      if (sourceSite && sourceSite !== 'All') query.set('source_site', sourceSite)
      if (category && category !== 'All') query.set('category', category)
      if (difficulty && difficulty !== 'All') query.set('difficulty', difficulty)
      if (company && company !== 'All') query.set('company', company)
      if (search) query.set('search', search)
      query.set('limit', String(limit))
      query.set('offset', String(offset))

      const [qRes, statsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/questions?${query.toString()}`),
        fetch(`${API_BASE_URL}/api/stats`)
      ])

      if (qRes.ok) {
        const qData = await qRes.json()
        setQuestions(qData.items || [])
        setTotal(qData.total || 0)
      }

      if (statsRes.ok) {
        const sData = await statsRes.json()
        setStats(sData)
      }
    } catch (err) {
      console.error('[useQuestions] Error fetching questions:', err)
    } finally {
      if (!cancelled) {
        clearTimeout(timerId)
        setIsWakingUp(false)
        setLoading(false)
      }
    }
  }, [sourceSite, category, difficulty, company, search, limit, offset])

  useEffect(() => {
    checkHealthAndFetch()

    // Auto-refresh questions every 30 seconds so newly generated questions appear automatically
    const pollInterval = setInterval(() => {
      // Silent refetch (without toggling full page loading spinner)
      const fetchSilent = async () => {
        try {
          const query = new URLSearchParams()
          if (sourceSite && sourceSite !== 'All') query.set('source_site', sourceSite)
          if (category && category !== 'All') query.set('category', category)
          if (difficulty && difficulty !== 'All') query.set('difficulty', difficulty)
          if (company && company !== 'All') query.set('company', company)
          if (search) query.set('search', search)
          query.set('limit', String(limit))
          query.set('offset', String(offset))

          const [qRes, statsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/api/questions?${query.toString()}`),
            fetch(`${API_BASE_URL}/api/stats`)
          ])

          if (qRes.ok) {
            const qData = await qRes.json()
            setQuestions(qData.items || [])
            setTotal(qData.total || 0)
          }

          if (statsRes.ok) {
            const sData = await statsRes.json()
            setStats(sData)
          }
        } catch (e) {
          // Silent catch for background poll
        }
      }
      fetchSilent()
    }, 30000)

    return () => clearInterval(pollInterval)
  }, [checkHealthAndFetch, sourceSite, category, difficulty, company, search, limit, offset])

  return {
    questions,
    total,
    stats,
    loading,
    isWakingUp,
    refetch: checkHealthAndFetch
  }
}