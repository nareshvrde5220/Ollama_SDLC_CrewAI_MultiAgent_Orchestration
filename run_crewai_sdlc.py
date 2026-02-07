#!/usr/bin/env python3
"""
CrewAI SDLC Pipeline — CLI Entry Point
========================================
Run the full SDLC pipeline using CrewAI + Ollama local models.

Usage:
    python run_crewai_sdlc.py
    python run_crewai_sdlc.py -r "Build a REST API for a todo app"
    python run_crewai_sdlc.py -f requirements.txt -o my_project_output

Models (all local, RTX 4090):
    gpt-oss:20b          → Analyst, Writer, DevOps, UI Designer
    qwen3-coder:30b      → Senior Developer, QA Engineer
    devstral-small-2:24b → Code Reviewer
"""

import sys
import argparse
import requests

from crewai_sdlc.config import OLLAMA_BASE_URL, AGENT_LLMS
from crewai_sdlc.crew import run_sdlc_pipeline


def check_ollama():
    """Verify Ollama server is running and required models are available."""
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/", timeout=5)
        if r.status_code != 200:
            print(f"ERROR: Ollama returned status {r.status_code}")
            return False
    except requests.ConnectionError:
        print(f"ERROR: Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print("  Start it with:  ollama serve")
        return False

    # Check models
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=30)
        installed = {m["name"] for m in resp.json().get("models", [])}
    except Exception:
        print("WARNING: Could not verify installed models")
        return True

    required_models = set()
    for llm in AGENT_LLMS.values():
        # Extract model name from "ollama/model:tag" format
        model_name = llm.model.replace("ollama/", "")
        required_models.add(model_name)

    missing = []
    for model in required_models:
        if not any(model in m for m in installed):
            missing.append(model)

    if missing:
        print("ERROR: Missing required models:")
        for m in missing:
            print(f"  ollama pull {m}")
        return False

    print(f"  Ollama    : {OLLAMA_BASE_URL} (OK)")
    print(f"  Models    : {len(required_models)} required, all installed")
    return True


def print_header():
    """Print the framework header."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     CrewAI SDLC Multi-Agent Framework — Ollama Local        ║
║                                                              ║
║     7 Agents × 3 Models × 7 Pipeline Phases                 ║
║     Powered by CrewAI + Ollama on RTX 4090                   ║
╚══════════════════════════════════════════════════════════════╝
""")
    agent_roles = {
        "Requirement Analyst":   "requirement_analyst",
        "Senior Developer":      "senior_developer",
        "Code Reviewer":         "code_reviewer",
        "Tech Writer":           "tech_writer",
        "QA Engineer":           "qa_engineer",
        "DevOps Agent":          "devops_agent",
        "UI Designer":           "ui_designer",
    }
    print("  Agent → Model Assignment:")
    print("  ─────────────────────────────────────────────────────")
    for display_name, key in agent_roles.items():
        model = AGENT_LLMS[key].model.replace("ollama/", "")
        print(f"    {display_name:<25} → {model}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="CrewAI SDLC Multi-Agent Framework — Ollama Local Models",
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
        default="crewai_output",
        help="Directory to save generated artifacts (default: crewai_output/)",
    )
    args = parser.parse_args()

    print_header()

    if not check_ollama():
        sys.exit(1)

    # Get requirement
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

    # Run CrewAI pipeline
    try:
        artifacts = run_sdlc_pipeline(requirement, output_dir=args.output_dir)
        print("  Pipeline completed successfully!")
        print(f"  Check the '{args.output_dir}/' folder for all generated files.\n")
    except KeyboardInterrupt:
        print("\n\n  Pipeline interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n  Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
