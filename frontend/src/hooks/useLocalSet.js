import { useCallback, useState } from 'react'

// A Set of question IDs persisted to localStorage — backs both "bookmarked"
// and "solved" tracking. Deliberately per-browser only (like the old admin
// overrides used to be): this is personal progress, not shared catalog
// state, so there's no server sync to build here.
export function useLocalSet(storageKey) {
  const [set, setSet] = useState(() => {
    try {
      const raw = localStorage.getItem(storageKey)
      return raw ? new Set(JSON.parse(raw)) : new Set()
    } catch {
      return new Set()
    }
  })

  const toggle = useCallback((id) => {
    setSet((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      localStorage.setItem(storageKey, JSON.stringify(Array.from(next)))
      return next
    })
  }, [storageKey])

  return { set, toggle }
}
