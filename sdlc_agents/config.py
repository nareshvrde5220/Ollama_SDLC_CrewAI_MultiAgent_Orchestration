"""
Configuration — Agent-to-Model Mapping & Ollama Settings
=========================================================
RTX 4090 (24 GB VRAM) optimized. Only 1 model loaded at a time.
"""

OLLAMA_BASE_URL = "http://localhost:11434"

# ── Agent → Model mapping ───────────────────────────────────────────────────
# gpt-oss:20b        (13 GB) — reasoning, planning, writing
# qwen3-coder:30b    (18 GB) — code generation, MoE 30B-A3B, 256K context
# devstral-small-2   (15 GB) — code review, multi-file editing, 384K context

AGENT_MODELS = {
    "orchestrator":        "gpt-oss:20b",
    "requirement_analyst": "gpt-oss:20b",
    "senior_developer":    "qwen3-coder:30b",
    "code_reviewer":       "devstral-small-2:24b",
    "tech_writer":         "gpt-oss:20b",
    "qa_engineer":         "qwen3-coder:30b",
    "devops_agent":        "gpt-oss:20b",
    "ui_designer":         "gpt-oss:20b",
}

# ── Generation settings ─────────────────────────────────────────────────────
MAX_TOKENS = 8192
TEMPERATURE = 0.3          # Low for deterministic code output
REVIEW_MAX_ITERATIONS = 3  # Code review ↔ revision loop limit
REQUEST_TIMEOUT = 600      # 10 min per agent call (large models are slow)
