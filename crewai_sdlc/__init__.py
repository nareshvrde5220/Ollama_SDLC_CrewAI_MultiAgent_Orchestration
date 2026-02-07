"""
CrewAI SDLC Multi-Agent Framework
===================================
8 specialized agents orchestrating the full SDLC using CrewAI + Ollama.
"""

from .config import AGENT_LLMS, OLLAMA_BASE_URL, OUTPUT_DIR
from .crew import build_sdlc_crew, run_sdlc_pipeline

__all__ = [
    "AGENT_LLMS",
    "OLLAMA_BASE_URL",
    "OUTPUT_DIR",
    "build_sdlc_crew",
    "run_sdlc_pipeline",
]
