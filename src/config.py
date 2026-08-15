import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

COVERAGE_THRESHOLD = float(os.getenv("COVERAGE_THRESHOLD", "0.62"))
PARTIAL_THRESHOLD = float(os.getenv("PARTIAL_THRESHOLD", "0.45"))

CONTROLS_PATH = os.getenv("CONTROLS_PATH", "data/nist_csf_2_0_controls.json")
POLICIES_DIR = os.getenv("POLICIES_DIR", "data/sample_policies")
REPORT_PATH = os.getenv("REPORT_PATH", "data/report.json")
