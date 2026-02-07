"""
CrewAI SDLC Configuration — Agent-to-Model Mapping & Settings
===============================================================
RTX 4090 (24 GB VRAM) optimized. Uses CrewAI's native LLM class
with litellm Ollama integration (ollama/<model>).
"""

from crewai import LLM

# ── Ollama Settings ──────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"

# ── LLM Instances (one per model, shared across agents) ─────────────────────
# gpt-oss:20b        (13 GB) — reasoning, planning, writing
# qwen3-coder:30b    (18 GB) — code generation, MoE 30B-A3B, 256K context
# devstral-small-2   (15 GB) — code review, multi-file editing, 384K context

LLM_PLANNER = LLM(
    model="ollama/gpt-oss:20b",
    base_url=OLLAMA_BASE_URL,
    temperature=0.3,
)

LLM_CODER = LLM(
    model="ollama/qwen3-coder:30b",
    base_url=OLLAMA_BASE_URL,
    temperature=0.2,
)

LLM_REVIEWER = LLM(
    model="ollama/devstral-small-2:24b",
    base_url=OLLAMA_BASE_URL,
    temperature=0.3,
)

# ── Agent → LLM Mapping ─────────────────────────────────────────────────────
AGENT_LLMS = {
    "orchestrator":        LLM_PLANNER,
    "requirement_analyst": LLM_PLANNER,
    "senior_developer":    LLM_CODER,
    "code_reviewer":       LLM_REVIEWER,
    "tech_writer":         LLM_PLANNER,
    "qa_engineer":         LLM_CODER,
    "devops_agent":        LLM_PLANNER,
    "ui_designer":         LLM_PLANNER,
}

# ── Pipeline Settings ────────────────────────────────────────────────────────
REVIEW_MAX_ITERATIONS = 3
OUTPUT_DIR = "output"
