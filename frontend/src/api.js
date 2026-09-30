const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (res.status === 204) return null
  const body = await res.json().catch(() => null)
  if (!res.ok) {
    let msg = `Permintaan gagal (${res.status})`
    if (body && typeof body.detail === 'string') msg = body.detail
    else if (body && Array.isArray(body.detail)) {
      msg = body.detail.map((d) => d.msg).join('; ')
    }
    throw new Error(msg)
  }
  return body
}

export const api = {
  list: ({ page, pageSize, search }) => {
    const p = new URLSearchParams({ page, page_size: pageSize, search })
    return request(`/sessions?${p}`)
  },
  create: (data) => request('/sessions', { method: 'POST', body: JSON.stringify(data) }),
  remove: (id) => request(`/sessions/${id}`, { method: 'DELETE' }),
}
