#!/usr/bin/env python3
"""
SDLC Multi-Agent Framework — CLI Entry Point
==============================================
Run the full SDLC pipeline from the command line.

Usage:
    python run_sdlc.py
    python run_sdlc.py --requirement "Build a REST API for a todo app"
    python run_sdlc.py --requirement-file my_requirements.txt
    python run_sdlc.py --output-dir my_project_output

Models Used (all local, RTX 4090 optimized):
    gpt-oss:20b          → Orchestrator, Analyst, Writer, DevOps, UI
    qwen3-coder:30b      → Developer, QA Engineer
    devstral-small-2:24b → Code Reviewer
"""

import sys
import argparse
import requests

from sdlc_agents.config import OLLAMA_BASE_URL, AGENT_MODELS
from sdlc_agents.orchestrator import SDLCOrchestrator


def check_ollama():
    """Verify Ollama server is running and required models are available."""
    # 1. Server check
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: Ollama returned status {r.status_code}")
            return False
    except requests.ConnectionError:
        print(f"ERROR: Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print("  Start it with:  ollama serve")
        return False

    # 2. Model check
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=30)
        installed = {m["name"] for m in resp.json().get("models", [])}
    except Exception:
        print("WARNING: Could not check installed models")
        return True

    required = set(AGENT_MODELS.values())
    missing = []
    for model in required:
        if not any(model in m for m in installed):
            missing.append(model)

    if missing:
        print("ERROR: Missing required models:")
        for m in missing:
            print(f"  ollama pull {m}")
        return False

    print(f"  Ollama    : {OLLAMA_BASE_URL} (OK)")
    print(f"  Models    : {len(required)} required, all installed")
    return True


def print_header():
    """Print the framework header."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          SDLC Multi-Agent Framework — Ollama Local          ║
║                                                              ║
║  8 Agents × 3 Models × 7 Pipeline Phases                    ║
║  100% Local on RTX 4090                                      ║
╚══════════════════════════════════════════════════════════════╝
""")
    print("  Agent → Model Assignment:")
    print("  ─────────────────────────────────────────────────────")
    roles = {
        "Orchestrator/Planner":  AGENT_MODELS["orchestrator"],
        "Requirement Analyst":   AGENT_MODELS["requirement_analyst"],
        "Senior Developer":      AGENT_MODELS["senior_developer"],
        "Code Reviewer":         AGENT_MODELS["code_reviewer"],
        "Tech Writer":           AGENT_MODELS["tech_writer"],
        "QA Engineer":           AGENT_MODELS["qa_engineer"],
        "DevOps Agent":          AGENT_MODELS["devops_agent"],
        "UI Designer":           AGENT_MODELS["ui_designer"],
    }
    for role, model in roles.items():
        print(f"    {role:<25} → {model}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="SDLC Multi-Agent Framework — Ollama Local Models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-r", "--requirement",
        help="Software requirement as a string",
    )
    parser.add_argument(
        "-f", "--requirement-file",
        help="Path to a .txt file containing the requirement",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="output",
        help="Directory to save generated artifacts (default: output/)",
    )
    args = parser.parse_args()

    print_header()

    # ── Check Ollama ─────────────────────────────────────────────────────
    if not check_ollama():
        sys.exit(1)

    # ── Get requirement ──────────────────────────────────────────────────
    requirement = None

    if args.requirement:
        requirement = args.requirement
    elif args.requirement_file:
        try:
            with open(args.requirement_file, "r", encoding="utf-8") as f:
                requirement = f.read().strip()
        except FileNotFoundError:
            print(f"ERROR: File not found: {args.requirement_file}")
            sys.exit(1)

    if not requirement:
        print("  Enter your software requirement (type END on a new line to finish):\n")
        lines = []
        try:
            while True:
                line = input("  > ")
                if line.strip().upper() == "END":
                    break
                lines.append(line)
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(0)

        requirement = "\n".join(lines).strip()

    if not requirement:
        print("ERROR: No requirement provided.")
        sys.exit(1)

    print(f"\n  Requirement ({len(requirement)} chars):")
    print(f"  {requirement[:200]}{'...' if len(requirement) > 200 else ''}\n")

    # ── Run pipeline ─────────────────────────────────────────────────────
    orchestrator = SDLCOrchestrator(output_dir=args.output_dir)

    try:
        artifacts = orchestrator.run(requirement)
        print("  Pipeline completed successfully!")
        print(f"  Check the '{args.output_dir}/' folder for all generated files.\n")
    except KeyboardInterrupt:
        print("\n\n  Pipeline interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n  Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
