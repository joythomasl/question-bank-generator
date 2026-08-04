// Admin curation goes through the backend now (see backend/main.py's
// /api/admin/* endpoints) so a removal or edit is visible to every client
// hitting /api/questions, not just the admin's own browser. These helpers
// are thin fetch wrappers; callers should refetch the question list after
// a successful call to pick up the new server state.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

async function request(path, options) {
  const res = await fetch(`${API_BASE_URL}${path}`, options)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed (${res.status})`)
  }
  return res.json().catch(() => ({}))
}

export function editQuestion(id, fields) {
  return request(`/api/admin/questions/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields),
  })
}

export function removeQuestion(id) {
  return request(`/api/admin/questions/${encodeURIComponent(id)}`, { method: 'DELETE' })
}

export function resetOverrides() {
  return request('/api/admin/reset', { method: 'POST' })
}
