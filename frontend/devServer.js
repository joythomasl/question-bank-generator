/**
 * devServer.js
 *
 * Tiny Express development server that serves api/generate-question.js
 * as a local HTTP route, proxied by Vite during `npm run dev`.
 *
 * Run automatically via `npm run dev` (concurrently with Vite).
 * NOT used in production — Vercel handles api/ natively there.
 *
 * Usage:
 *   node devServer.js
 *   (or via `npm run dev` which uses concurrently)
 */

import 'dotenv/config'
import express from 'express'

const PORT = 3001
const app = express()

app.use(express.json())

// Dynamically import the serverless function with cache-busting so edits
// to api/generate-question.js take effect immediately without restarting.
async function loadHandler() {
  const mod = await import(`./api/generate-question.js?t=${Date.now()}`)
  return mod.default
}

app.all('/api/generate-question', async (req, res) => {
  try {
    const handler = await loadHandler()
    await handler(req, res)
  } catch (err) {
    console.error('[devServer] Unhandled error:', err)
    if (!res.headersSent) {
      res.status(500).json({ error: String(err.message) })
    }
  }
})

app.listen(PORT, () => {
  console.log(`[devServer] API proxy running on http://localhost:${PORT}`)
  console.log(`[devServer] NVIDIA_API_KEY_LIVE: ${process.env.NVIDIA_API_KEY_LIVE ? 'SET ✓' : 'NOT SET — add to frontend/.env'}`)
})
