# Question bank generator

A pre-generated, machine-verified bank of interview questions (algorithmic +
bonus conceptual), browsable in a static web portal with checkbox-based JSON
export. Full project background and architecture: `docs/PROJECT_PLAN.md`.

## Structure

```
pipeline/     offline generation pipeline — run this first, once
frontend/     static React portal — run this second, and again any time
              you update the generated data
docs/         project plan and design notes
```

## 1. Run the pipeline (offline, once, produces the data)

```bash
cd pipeline
python -m venv venv && source venv/bin/activate   # or your preferred venv tool
pip install -r requirements.txt
cp .env.example .env                               # then fill in GROQ_API_KEY
```

Get a free Groq API key at https://console.groq.com/keys (no credit card
required).

Run each stage in order:

```bash
python scrape.py     # -> data/raw_items.json
python classify.py   # -> data/tagged_items.json   (fill in TODOs first)
python enrich.py      # -> data/enriched_items.json (fill in TODOs first)
python verify.py      # -> data/questions.db        (fill in TODOs first)
python export.py      # -> data/questions.json
```

`classify.py`, `enrich.py`, and `verify.py` are currently stubs — see the
`STATUS` note at the top of each file. Fill in the Groq prompts and the
subprocess sandbox logic before running them for real.

## 2. Wire the data into the frontend

Copy the exported file in, or fetch it at runtime instead of importing it:

```bash
cp pipeline/data/questions.json frontend/src/data/
```

Then update `frontend/src/components/UserPortal.jsx` and `AdminPortal.jsx`
to import from `questions.json` instead of `mockQuestions.js`.

## 3. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Default admin login password is `admin123` (set in
`frontend/src/components/LoginPage.jsx`) — this is a demo-scale gate, not
real authentication. Change it, or swap in real auth, before any public
deployment.

## Deploying

The frontend is a static build (`npm run build` → `frontend/dist/`) —
deploy it free on Vercel or Netlify. Nothing in the deployed app calls an
LLM or a backend server at runtime; all data is baked into `questions.json`
at build time.
