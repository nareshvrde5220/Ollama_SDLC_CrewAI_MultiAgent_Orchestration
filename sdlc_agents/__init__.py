"""
SDLC Multi-Agent Framework — Powered by Ollama Local Models
============================================================
8 specialized agents orchestrating the full Software Development Life Cycle.
"""

from .config import AGENT_MODELS, OLLAMA_BASE_URL
from .base_agent import BaseAgent
from .agents import (
    RequirementAnalyst,
    SeniorDeveloper,
    CodeReviewer,
    TechWriter,
    QAEngineer,
    DevOpsAgent,
    UIDesigner,
)
from .orchestrator import SDLCOrchestrator

__all__ = [
    "AGENT_MODELS",
    "OLLAMA_BASE_URL",
    "BaseAgent",
    "RequirementAnalyst",
    "SeniorDeveloper",
    "CodeReviewer",
    "TechWriter",
    "QAEngineer",
    "DevOpsAgent",
    "UIDesigner",
    "SDLCOrchestrator",
]
