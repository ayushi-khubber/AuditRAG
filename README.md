# AuditRAG — RAG-Based Policy & Control Auditor

Maps organizational security policy documents against NIST CSF 2.0 controls and flags
coverage gaps, with a confidence score per control and an LLM-generated explanation.

## How it works

1. **Load** a set of NIST CSF 2.0 controls (`data/nist_csf_2_0_controls.json`) and your
   policy documents (`.txt` files in `data/sample_policies/`).
2. **Chunk** each policy document (LangChain `RecursiveCharacterTextSplitter`).
3. **Score**: every control description is compared against every policy chunk using
   Sentence-Transformers embeddings (`all-MiniLM-L6-v2`) and cosine similarity
   (scikit-learn). The highest-scoring chunk becomes the "best match" and its score
   becomes the confidence score. Thresholds turn that score into `Covered` /
   `Partial` / `Gap`.
4. **Retrieve**: a FAISS vector store (LangChain) retrieves the top-k relevant policy
   chunks for each control — this is the "R" in RAG.
5. **Generate**: those retrieved chunks are passed as context to Llama 3.3 70B (hosted
   on Groq's free API) to write a short, grounded gap-analysis narrative — the "G".
6. **Serve**: a Flask dashboard groups everything by NIST function (Govern, Identify,
   Protect, Detect, Respond, Recover) with color-coded status badges.

The LLM step is optional — set `--skip-llm` or leave `GROQ_API_KEY` empty and you still
get the similarity-based scoring, matched excerpts, and dashboard.

## Project structure

```
compliancegpt/
├── app.py                   Flask dashboard
├── run.py                   CLI: run pipeline, write data/report.json
├── requirements.txt
├── .env.example
├── data/
│   ├── nist_csf_2_0_controls.json
│   └── sample_policies/*.txt   ← replace with your real policies
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── chunking.py
│   ├── semantic_scorer.py   Sentence-Transformers + cosine similarity
│   ├── retriever.py         FAISS retrieval (RAG context)
│   ├── llm_analysis.py      Llama 3.3 70B via Groq
│   └── pipeline.py          orchestrates all of the above
├── templates/index.html
└── static/style.css
```

## Setup

```bash
# from inside the unzipped compliancegpt/ folder
python3 -m venv venv

# activate it
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate            # Windows (cmd)
# venv\Scripts\Activate.ps1      # Windows (PowerShell)

pip install --upgrade pip
pip install -r requirements.txt
```

Copy the env file and add a free Groq API key if you want the LLM narratives
(https://console.groq.com/keys — Llama 3.3 70B is free-tier there):

```bash
cp .env.example .env
# then edit .env and paste your GROQ_API_KEY
```

## Run it

**CLI (writes a JSON report, no server needed):**

```bash
python run.py                # full run, with LLM narratives
python run.py --skip-llm     # skip LLM calls, just similarity scoring
```

**Web dashboard:**

```bash
python app.py
# open http://127.0.0.1:5000
```

The first load runs the full pipeline and caches results in `data/report.json`. Click
"Re-run analysis" in the dashboard (or hit `/refresh`) to redo it — e.g. after editing
policy files.

To point it at your own policies, drop `.txt` files into `data/sample_policies/` (or
change `POLICIES_DIR` in `.env`) and re-run.

## Push to GitHub

```bash
cd compliancegpt
git init
git add .
git commit -m "Initial commit: AuditRAG RAG policy auditor"

# create an empty repo on GitHub first (via github.com or `gh repo create`), then:
git branch -M main
git remote add origin https://github.com/<your-username>/compliancegpt.git
git push -u origin main
```

`.env` and `venv/` are already in `.gitignore` so your API key won't get committed.

## Honest notes on the original resume bullets

You said it "kinda doesn't make sense" — here's what I'd actually tighten up before
putting this on a resume:

- **"Automate compliance gap analysis"** is a strong claim for what this really does:
  flag *semantic similarity* gaps between policy wording and control text. That's
  useful as a first-pass triage tool, but it isn't compliance automation — a human
  (ideally a GRC/security person) still has to validate every finding. Real compliance
  gap analysis also considers evidence of implementation, not just policy language.
- **"LLaMA 3.3-70B"**: worth being precise about how you accessed it — self-hosted,
  or via a provider like Groq/Together/AWS Bedrock. "Built a RAG pipeline... using
  LLaMA 3.3-70B" reads like you stood up the model yourself; if you used a hosted API
  (which this project does, via Groq), say so — it's still a legitimate and common
  approach, just more accurate.
- **Confidence scores from cosine similarity aren't calibrated probabilities.** A 0.55
  similarity score doesn't mean "55% compliant" — it means the text is moderately
  related. Worth a caveat in interviews so you don't overstate precision if pressed.
- A tighter version of the bullets might read something like:
  - *"Built a RAG pipeline (LangChain, FAISS, Llama 3.3 70B via Groq) that retrieves
    relevant policy text for each NIST CSF 2.0 control and generates a grounded gap
    analysis narrative."*
  - *"Implemented a Sentence-Transformers/cosine-similarity scoring layer to
    flag Covered/Partial/Gap status per control with a confidence score, surfaced
    through a Flask dashboard."*

That's more defensible in an interview because every clause maps to something you can
point at in the code and explain precisely.
