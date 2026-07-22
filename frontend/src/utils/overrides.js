// Admin curation is stored per-browser in localStorage — there is no backend
// database. This is intentional: the admin view is a one-operator curation
// tool used once before deployment, not a live multi-admin CMS. Use the
// "Export questions.json" button in the admin portal to bake curated
// removals/edits into the static file that ships to everyone else.

const OVERRIDES_KEY = 'admin_overrides_v1'

function loadOverrides() {
  try {
    const raw = localStorage.getItem(OVERRIDES_KEY)
    return raw ? JSON.parse(raw) : { removed: [], edits: {} }
  } catch {
    return { removed: [], edits: {} }
  }
}

function saveOverrides(overrides) {
  localStorage.setItem(OVERRIDES_KEY, JSON.stringify(overrides))
}

export function getCuratedQuestions(base) {
  const { removed, edits } = loadOverrides()
  return base
    .filter((q) => !removed.includes(q.id))
    .map((q) => (edits[q.id] ? { ...q, ...edits[q.id] } : q))
}

export function removeQuestion(id) {
  const overrides = loadOverrides()
  if (!overrides.removed.includes(id)) overrides.removed.push(id)
  saveOverrides(overrides)
}

export function editQuestion(id, fields) {
  const overrides = loadOverrides()
  overrides.edits[id] = { ...(overrides.edits[id] || {}), ...fields }
  saveOverrides(overrides)
}

export function resetOverrides() {
  localStorage.removeItem(OVERRIDES_KEY)
}
