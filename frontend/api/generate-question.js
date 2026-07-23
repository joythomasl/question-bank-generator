/**
 * api/generate-question.js
 *
 * Vercel serverless function (also used as an Express route in devServer.js).
 * Exports a single default handler: (req, res) => void.
 *
 * Provider order (mirrors enrich_with_fallback in enrich.py):
 *   1. NVIDIA NIM  — meta/llama-3.3-70b-instruct  — 45s timeout
 *   2. Groq        — llama-3.3-70b-versatile       — 40s timeout
 * First success wins; if both fail the request errors.
 *
 * Time budget (hard, enforced by AbortController per fetch):
 *   Scrape phase: 20s total
 *   LLM call:     75s
 *   Total server: ~95s  (client adds its own 115s abort)
 */

import OpenAI from 'openai'

// ─── Constants ───────────────────────────────────────────────────────────────

const NVIDIA_MODEL = 'meta/llama-3.3-70b-instruct'
const GROQ_MODEL   = 'llama-3.3-70b-versatile'

const EDGE_CASE_TYPES = [
  'empty_or_minimal_input',
  'single_element',
  'all_duplicates',
  'sorted_ascending',
  'sorted_descending',
  'negative_numbers',
  'max_constraint_size',
  'boundary_value',
  'typical_case',
  'adversarial_case',
]

const CODING_SYSTEM_PROMPT = `You generate original coding interview questions for a curated question bank. You will be given a title, algorithm category, and difficulty, and possibly brief source text for grounding only (do not copy wording).

You MUST follow this exact JSON shape — here is a real example for a different problem, showing the required structure precisely:

{"problem_statement": "Given an array of integers, return indices of the two numbers that add up to a target.", "examples": [{"input": "nums=[2,7,11,15], target=9", "output": "[0,1]", "explanation": "nums[0]+nums[1]=9"}], "constraints": ["2 <= nums.length <= 10^4"], "test_cases": [{"input": {"nums": [2,7,11,15], "target": 9}, "expected_output": [0,1], "edge_case_type": "typical_case"}], "python_solution": "def solve(nums, target):\\n    seen = {}\\n    for i, n in enumerate(nums):\\n        if target - n in seen:\\n            return [seen[target-n], i]\\n        seen[n] = i"}

CRITICAL RULES — violating any of these will cause your output to be rejected:
- python_solution MUST define a function called EXACTLY \`solve\`. Not \`solution\`, not \`main\`, not the problem title, not anything else. The first line of python_solution must be \`def solve(\`.
- The parameters of \`solve\` must match the keys inside each test case's \"input\" object exactly.
- test_cases must have exactly 10 items, each with keys \"input\", \"expected_output\", \"edge_case_type\" — no other keys.
- Respond with ONLY a JSON object. No markdown fences, no prose, no explanation.
- SELF-CHECK: Before writing each expected_output, mentally run your solve() function on that input and confirm the output. If you are not 100% sure, use a simpler input where the answer is obvious. Wrong expected_output values are worse than wrong code.
- Prefer problems with small, easy-to-verify test inputs (single digit numbers, short strings) so expected outputs are easy to compute correctly.

Now generate for the given title/category/difficulty:
1. problem_statement: original, self-contained.
2. examples: exactly 1 object with \"input\", \"output\", \"explanation\" as STRINGS.
3. constraints: 2-3 short strings.
4. test_cases: exactly 10 objects covering: ${EDGE_CASE_TYPES.join(', ')}
5. python_solution: function named EXACTLY \`solve\` — no exceptions.`

// Hardcoded fallback seeds — used when all 4 scrape sources fail
const FALLBACK_SEEDS = [
  { title: 'Longest Palindromic Substring', category: 'Dynamic Programming', difficulty: 'Medium' },
  { title: 'Course Schedule', category: 'Backtracking', difficulty: 'Medium' },
  { title: 'Merge K Sorted Lists', category: 'Divide and Conquer', difficulty: 'Hard' },
  { title: 'Container With Most Water', category: 'Two Pointers', difficulty: 'Medium' },
  { title: 'Jump Game II', category: 'Greedy', difficulty: 'Medium' },
  { title: 'Word Break', category: 'Dynamic Programming', difficulty: 'Medium' },
  { title: 'Minimum Path Sum', category: 'Dynamic Programming', difficulty: 'Medium' },
  { title: 'Partition Equal Subset Sum', category: 'Dynamic Programming', difficulty: 'Medium' },
  { title: 'Gas Station', category: 'Greedy', difficulty: 'Medium' },
  { title: 'Palindrome Partitioning', category: 'Backtracking', difficulty: 'Medium' },
  { title: 'Find Median from Data Stream', category: 'Divide and Conquer', difficulty: 'Hard' },
  { title: 'Minimum Window Substring', category: 'Two Pointers', difficulty: 'Hard' },
]

const CATEGORIES = [
  'Dynamic Programming', 'Backtracking', 'Greedy',
  'Divide and Conquer', 'Two Pointers',
]

// ─── HTML stripping ───────────────────────────────────────────────────────────

function stripHtml(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s{2,}/g, ' ')
    .trim()
}

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}

// ─── Scrape sources ───────────────────────────────────────────────────────────

async function scrapeCodeforces(signal) {
  const apiRes = await fetch('https://codeforces.com/api/problemset.problems', { signal })
  if (!apiRes.ok) throw new Error(`CF API status ${apiRes.status}`)
  const data = await apiRes.json()
  const problems = data?.result?.problems
  if (!Array.isArray(problems) || problems.length === 0) throw new Error('CF: no problems')

  // Pick a problem that has tags (more interesting)
  const withTags = problems.filter(p => p.tags && p.tags.length > 0)
  const problem = randomItem(withTags.length > 0 ? withTags : problems)

  const { contestId, index, name, rating } = problem
  let rawText = ''
  try {
    const pageSignal = AbortSignal.timeout(8000)
    const pageRes = await fetch(`https://codeforces.com/problemset/problem/${contestId}/${index}`, { signal: pageSignal })
    if (pageRes.ok) {
      const html = await pageRes.text()
      // Extract the problem-statement div
      const match = html.match(/class="problem-statement"[^>]*>([\s\S]{0,3000})/)
      rawText = match ? stripHtml(match[1]).slice(0, 400) : ''
    }
  } catch {
    // Statement fetch failed — use name only, still valid
  }

  const difficulty = rating >= 2000 ? 'Hard' : rating >= 1400 ? 'Medium' : 'Easy'
  return {
    source: 'codeforces',
    title: name,
    category: randomItem(CATEGORIES),
    difficulty,
    rawText,
  }
}

async function scrapeCSES(signal) {
  const listRes = await fetch('https://cses.fi/problemset/list', { signal })
  if (!listRes.ok) throw new Error(`CSES list status ${listRes.status}`)
  const listHtml = await listRes.text()

  // Extract problem links: /problemset/task/<id>
  const linkMatches = [...listHtml.matchAll(/href="\/problemset\/task\/(\d+)"[^>]*>([^<]+)<\/a>/g)]
  if (linkMatches.length === 0) throw new Error('CSES: no problems found')

  const picked = randomItem(linkMatches)
  const taskId = picked[1]
  const taskName = picked[2].trim()

  let rawText = ''
  try {
    const pageSignal = AbortSignal.timeout(8000)
    const pageRes = await fetch(`https://cses.fi/problemset/task/${taskId}`, { signal: pageSignal })
    if (pageRes.ok) {
      const html = await pageRes.text()
      const bodyMatch = html.match(/<div class="content">([\s\S]{0,4000})/)
      rawText = bodyMatch ? stripHtml(bodyMatch[1]).slice(0, 400) : ''
    }
  } catch {
    // Page fetch failed — use title only
  }

  return {
    source: 'cses',
    title: taskName,
    category: randomItem(CATEGORIES),
    difficulty: 'Medium',
    rawText,
  }
}

async function scrapeGFG(signal) {
  // GFG is best-effort — fetch a "top interview problems" page, extract one title
  const urls = [
    'https://www.geeksforgeeks.org/top-interview-questions-asked-by-amazon/',
    'https://www.geeksforgeeks.org/must-do-coding-questions-for-companies-like-amazon-microsoft-adobe/',
  ]
  const url = randomItem(urls)
  const res = await fetch(url, {
    signal,
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; QuestionBotBot/1.0)' },
  })
  if (!res.ok) throw new Error(`GFG status ${res.status}`)
  const html = await res.text()

  // Extract article titles or h2/h3 headings
  const headings = [...html.matchAll(/<h[23][^>]*>([^<]{10,80})<\/h[23]>/g)]
    .map(m => stripHtml(m[1]).trim())
    .filter(t => t.length > 8 && !t.toLowerCase().includes('geeksforgeeks'))

  if (headings.length === 0) throw new Error('GFG: no titles found')

  return {
    source: 'geeksforgeeks',
    title: randomItem(headings),
    category: randomItem(CATEGORIES),
    difficulty: 'Medium',
    rawText: '',
  }
}

async function scrapeLeetCode(signal) {
  // LeetCode public GraphQL — title + difficulty metadata ONLY (no statement)
  const query = `{
    problemsetQuestionList(categorySlug: "", limit: 50, skip: ${Math.floor(Math.random() * 400)}, filters: {}) {
      questions {
        title
        difficulty
        titleSlug
      }
    }
  }`

  const res = await fetch('https://leetcode.com/graphql', {
    method: 'POST',
    signal,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!res.ok) throw new Error(`LC GraphQL status ${res.status}`)
  const data = await res.json()
  const questions = data?.data?.problemsetQuestionList?.questions
  if (!Array.isArray(questions) || questions.length === 0) throw new Error('LC: no questions')

  const picked = randomItem(questions)
  const diffMap = { Easy: 'Easy', Medium: 'Medium', Hard: 'Hard' }

  return {
    source: 'leetcode_metadata',
    title: picked.title,
    category: randomItem(CATEGORIES),
    difficulty: diffMap[picked.difficulty] ?? 'Medium',
    rawText: '', // intentionally empty — no statement scraping from LC
  }
}

// ─── Scrape orchestration ───────────────────────────────────────────────────

/**
 * Try sources in priority order: CSES first, then CF, LC, GFG.
 * Returns the first that succeeds. Falls back to hardcoded seeds if all fail.
 */
async function getSeed() {
  // Each source gets its own generous individual timeout
  const SCRAPE_TIMEOUT_MS = 15000

  const sourcePriority = [
    { name: 'CSES',         fn: scrapeCSES },
    { name: 'Codeforces',   fn: scrapeCodeforces },
    { name: 'LeetCode',     fn: scrapeLeetCode },
    { name: 'GeeksForGeeks',fn: scrapeGFG },
  ]

  for (const { name, fn } of sourcePriority) {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), SCRAPE_TIMEOUT_MS)
    try {
      const seed = await fn(controller.signal)
      console.log(`[generate-question] Seed from ${name}: "${seed.title}"`)
      return seed
    } catch (err) {
      console.warn(`[generate-question] ${name} scrape failed: ${err.message} — trying next`)
    } finally {
      clearTimeout(timer)
    }
  }

  // All sources failed — hardcoded fallback
  console.warn('[generate-question] All scrape sources failed — using hardcoded fallback seed')
  return { ...randomItem(FALLBACK_SEEDS), source: 'fallback', rawText: '' }
}

// ─── LLM generation ──────────────────────────────────────────────────────────

function buildUserPrompt(seed) {
  const lines = [
    `Title: ${seed.title}`,
    `Category: ${seed.category}`,
    `Difficulty: ${seed.difficulty}`,
  ]
  if (seed.rawText) {
    lines.push(`Source context (grounding only — do not copy wording):\n${seed.rawText.slice(0, 350)}`)
  }
  return lines.join('\n\n')
}

function cleanAndParseJson(rawContent) {
  let content = rawContent.trim()

  // 1. Direct parse attempt
  try {
    return JSON.parse(content)
  } catch (_) {}

  // 2. Structural repair (missing commas between objects/arrays, trailing commas)
  let text = content
    .replace(/```(?:python|json)?/gi, '')
    .replace(/\}\s*\{/g, '},{')
    .replace(/\]\s*\[/g, '],[')
    .replace(/"\s*\{/g, '",{')
    .replace(/\}\s*"/g, '},"')
    .replace(/,\s*([\}\]])/g, '$1')

  try {
    return JSON.parse(text)
  } catch (_) {}

  // 3. Fix unescaped linebreaks / tabs inside string literals
  let escapedStrings = text.replace(/"([^"\\]*(?:\\.[^"\\]*)*)"/gs, (match, p1) => {
    return '"' + p1.replace(/\r?\n/g, '\\n').replace(/\t/g, '\\t') + '"'
  })

  try {
    return JSON.parse(escapedStrings)
  } catch (_) {}

  // 4. Truncation repair (auto-close unclosed strings, brackets, braces)
  let openBraces = 0, openBrackets = 0, inString = false
  let repaired = ''
  for (let i = 0; i < escapedStrings.length; i++) {
    const ch = escapedStrings[i]
    if (ch === '"' && escapedStrings[i - 1] !== '\\') {
      inString = !inString
    }
    if (!inString) {
      if (ch === '{') openBraces++
      else if (ch === '}') openBraces = Math.max(0, openBraces - 1)
      else if (ch === '[') openBrackets++
      else if (ch === ']') openBrackets = Math.max(0, openBrackets - 1)
    }
    repaired += ch
  }

  if (inString) repaired += '"'
  repaired = repaired.replace(/,\s*$/, '')
  while (openBrackets > 0) { repaired += ']'; openBrackets--; }
  while (openBraces > 0) { repaired += '}'; openBraces--; }

  try {
    return JSON.parse(repaired)
  } catch (err) {
    console.error('[generate-question] JSON parse failed after repair attempts:', err.message)
    console.error('[generate-question] Raw content head:', rawContent.slice(0, 300))
    console.error('[generate-question] Raw content tail:', rawContent.slice(-300))
    throw err
  }
}

/**
 * Try one LLM provider, aborting after timeoutMs.
 * jsonMode=true  → use response_format:{type:'json_object'} (NVIDIA supports this well)
 * jsonMode=false → free-text response; extract outermost JSON object ourselves (Groq)
 * Returns parsed JSON or throws.
 */
async function callProvider(client, model, seed, timeoutMs, label, jsonMode) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    console.log(`[generate-question] Trying ${label} (${model}, ${timeoutMs / 1000}s, jsonMode=${jsonMode})…`)
    const createParams = {
      model,
      messages: [
        { role: 'system', content: CODING_SYSTEM_PROMPT },
        { role: 'user', content: buildUserPrompt(seed) },
      ],
      max_tokens: 3500,  // increased token limit so 10 test cases + solution don't truncate
      temperature: 0.2,  // lower = more consistent, fewer hallucinated expected_output values
    }
    if (jsonMode) createParams.response_format = { type: 'json_object' }

    const response = await client.chat.completions.create(createParams, { signal: controller.signal })

    let content = response.choices[0].message.content.trim()

    // Strip outer markdown fences if present
    if (content.startsWith('```')) {
      content = content.replace(/^```(?:json)?\s*/i, '').replace(/\s*```\s*$/i, '').trim()
    }

    // For non-json-mode providers, extract the outermost {...} block
    if (!jsonMode) {
      const start = content.indexOf('{')
      const end = content.lastIndexOf('}')
      if (start !== -1 && end !== -1 && end > start) {
        content = content.slice(start, end + 1)
      }
    }

    console.log(`[generate-question] ${label} responded ✓`)
    return cleanAndParseJson(content)
  } finally {
    clearTimeout(timer)
  }
}

/**
 * Try NVIDIA first (45s), fall back to Groq (40s).
 * Mirrors enrich_with_fallback() in enrich.py.
 */
async function generateWithFallback(seed) {
  const providers = []

  if (process.env.NVIDIA_API_KEY_LIVE) {
    providers.push({
      label: 'NVIDIA',
      model: NVIDIA_MODEL,
      timeoutMs: 120000,
      jsonMode: true,   // NVIDIA NIM supports json_object reliably
      client: new OpenAI({
        apiKey: process.env.NVIDIA_API_KEY_LIVE,
        baseURL: 'https://integrate.api.nvidia.com/v1',
      }),
    })
  }

  if (process.env.GROQ_API_KEY) {
    providers.push({
      label: 'Groq',
      model: GROQ_MODEL,
      timeoutMs: 90000,
      jsonMode: true,  // 70b-versatile handles json_object perfectly
      client: new OpenAI({
        apiKey: process.env.GROQ_API_KEY,
        baseURL: 'https://api.groq.com/openai/v1',
      }),
    })
  }

  if (providers.length === 0) {
    throw new Error('No LLM provider configured — set NVIDIA_API_KEY_LIVE or GROQ_API_KEY in .env')
  }

  let lastError
  for (const { label, model, timeoutMs, client, jsonMode } of providers) {
    try {
      return await callProvider(client, model, seed, timeoutMs, label, jsonMode)
    } catch (err) {
      const reason = err.name === 'AbortError' ? `timed out after ${timeoutMs / 1000}s` : err.message
      console.warn(`[generate-question] ${label} failed: ${reason} — trying next provider`)
      lastError = err
    }
  }

  throw lastError ?? new Error('All LLM providers failed')
}

// ─── Normalise + Validation ───────────────────────────────────────────────────

/**
 * If the model named the function something other than `solve`
 * (e.g. solution, answer, main, find_result), rename it everywhere in the
 * code so Pyodide can call solve(...) on the client side.
 */
function normalizePythonSolution(code, testCases) {
  if (!code) return code

  // 1. Strip markdown fences if the model put them INSIDE the JSON string value
  if (code.includes('```')) {
    code = code.replace(/^```(?:python)?\s*/i, '').replace(/\s*```\s*$/, '').trim()
    console.log('[generate-question] Stripped inner markdown fences from python_solution')
  }

  // 2. Already correct
  if (code.includes('def solve(')) return code

  // 3. Another function name — rename it
  const fnMatch = code.match(/def\s+(\w+)\s*\(/)
  if (fnMatch) {
    const originalName = fnMatch[1]
    const renamed = code.replace(new RegExp(`\\b${originalName}\\b`, 'g'), 'solve')
    console.log(`[generate-question] Renamed function '${originalName}' → 'solve'`)
    return renamed
  }

  // 4. No function at all — synthesize def solve(...): wrapper from test_case input keys
  if (testCases && testCases.length > 0 && testCases[0].input) {
    const params = Object.keys(testCases[0].input).join(', ')
    const indented = code.split('\n').map(l => '    ' + l).join('\n')
    const wrapped = `def solve(${params}):\n${indented}`
    console.log(`[generate-question] No function found — auto-wrapped as def solve(${params})`)
    return wrapped
  }

  // 5. Truly unrecoverable — return as-is, validation will surface it
  console.warn('[generate-question] python_solution has no def and no test_cases to infer params from')
  return code
}

function validateGeneration(result) {
  const raw = (result.python_solution || '').trim()
  console.log(`[generate-question] Raw python_solution (first 120 chars): ${raw.slice(0, 120).replace(/\n/g, '\\n')}`)
  const pythonSolution = normalizePythonSolution(raw, result.test_cases)
  const testCases = result.test_cases || []

  if (!pythonSolution || !pythonSolution.includes('def solve(')) {
    return { ok: false, reason: 'wrong_function_name_or_empty', normalizedSolution: null }
  }
  if (testCases.length < 10) {
    return { ok: false, reason: `incomplete_generation: only ${testCases.length} test cases`, normalizedSolution: null }
  }
  if (!testCases.every(tc => typeof tc === 'object' && 'input' in tc && 'expected_output' in tc)) {
    return { ok: false, reason: 'wrong_test_case_schema', normalizedSolution: null }
  }

  const uniqueInputs = new Set(
    testCases.map(tc => {
      const inp = tc.input || {}
      return JSON.stringify(inp, Object.keys(inp).sort())
    }),
  )
  if (uniqueInputs.size < 7) {
    return { ok: false, reason: 'duplicate_test_cases', normalizedSolution: null }
  }

  return { ok: true, normalizedSolution: pythonSolution }
}

// ─── ID generation ────────────────────────────────────────────────────────────

function generateId(seed) {
  const prefixMap = {
    'Dynamic Programming': 'dp',
    'Backtracking': 'bt',
    'Greedy': 'gr',
    'Divide and Conquer': 'dc',
    'Two Pointers': 'tp',
  }
  const prefix = prefixMap[seed.category] || 'lv'
  const suffix = Date.now().toString(36).slice(-4)
  return `${prefix}-live-${suffix}`
}

// ─── Main handler ─────────────────────────────────────────────────────────────

export default async function handler(req, res) {
  if (req.method !== 'POST' && req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const startTime = Date.now()

  try {
    // Phase 1: Scrape
    console.log('[generate-question] Starting scrape phase...')
    const seed = await getSeed()
    const scrapeMs = Date.now() - startTime
    console.log(`[generate-question] Seed acquired in ${scrapeMs}ms — source: ${seed.source}, title: "${seed.title}"`)

    // Phase 2: Generate
    console.log('[generate-question] Calling LLM (NVIDIA → Groq fallback)...')
    const llmStart = Date.now()
    const result = await generateWithFallback(seed)
    const llmMs = Date.now() - llmStart
    console.log(`[generate-question] LLM responded in ${llmMs}ms`)

    // Phase 3: Validate (with one automatic retry if the schema is wrong)
    let validation = validateGeneration(result)
    if (!validation.ok) {
      console.warn(`[generate-question] Validation failed (${validation.reason}) — retrying LLM once...`)
      const retryResult = await generateWithFallback(seed)
      validation = validateGeneration(retryResult)
      if (!validation.ok) {
        console.warn(`[generate-question] Retry also failed: ${validation.reason}`)
        return res.status(422).json({ error: `Generation validation failed after retry: ${validation.reason}` })
      }
      // Use retry result
      Object.assign(result, retryResult)
    }

    const question = {
      id: generateId(seed),
      title: seed.title,
      category: seed.category,
      difficulty: seed.difficulty,
      company: 'Live Generated',
      source: seed.source,
      seed_source: seed.source,
      item_type: 'coding',
      type: 'coding',
      verified: false, // Pyodide sets this on the client after passing all 10 test cases
      problem_statement: result.problem_statement,
      examples: result.examples,
      constraints: result.constraints,
      test_cases: result.test_cases.slice(0, 10),
      solutions: { python: validation.normalizedSolution, java: null },
      generated_at: new Date().toISOString(),
      total_ms: Date.now() - startTime,
    }

    console.log(`[generate-question] Done in ${question.total_ms}ms — returning question "${question.title}"`)
    return res.status(200).json(question)
  } catch (err) {
    const elapsed = Date.now() - startTime
    if (err.name === 'AbortError' || err.message?.includes('abort')) {
      console.error(`[generate-question] Timed out after ${elapsed}ms`)
      return res.status(504).json({ error: 'Generation timed out — please try again' })
    }
    console.error(`[generate-question] Error after ${elapsed}ms:`, err)
    return res.status(500).json({ error: err.message || 'Internal server error' })
  }
}
