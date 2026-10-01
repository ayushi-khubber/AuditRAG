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
