"""
CrewAI SDLC Crew — Agents, Tasks & Pipeline
==============================================
Defines 7 specialized agents and their tasks, assembled into a CrewAI Crew
that runs the full SDLC pipeline sequentially.

UUID Tracking:
  - Each pipeline run gets a unique run_id (UUID)
  - Each SDLC phase gets its own phase_id (UUID)
  - All conversations are logged with UUIDs for traceability
  - A manifest.json ties everything together
"""

import os
import re
import json
import time
import uuid
from datetime import datetime, timezone

from crewai import Agent, Task, Crew, Process

from .config import AGENT_LLMS, REVIEW_MAX_ITERATIONS, OUTPUT_DIR


# ═════════════════════════════════════════════════════════════════════════════
# AGENTS
# ═════════════════════════════════════════════════════════════════════════════

def create_agents():
    """Create all 7 SDLC agents with their assigned Ollama models."""

    requirement_analyst = Agent(
        role="Requirement Analyst",
        goal=(
            "Transform the user's natural-language software description into a "
            "clear, structured specification document in Markdown format."
        ),
        backstory=(
            "You are an expert Requirement Analyst with 15 years of experience. "
            "You excel at extracting functional and non-functional requirements "
            "from vague descriptions and producing precise specifications."
        ),
        llm=AGENT_LLMS["requirement_analyst"],
        verbose=True,
        allow_delegation=False,
        max_iter=1,
    )

    senior_developer = Agent(
        role="Senior Python Developer",
        goal=(
            "Generate production-quality, clean Python code that fully implements "
            "the specification. Follow PEP 8, include type hints, docstrings, "
            "error handling, and a __main__ guard."
        ),
        backstory=(
            "You are a Senior Python Developer with 15+ years of experience. "
            "You write clean, modular, well-documented code. You always include "
            "type hints, proper error handling, and follow best practices."
        ),
        llm=AGENT_LLMS["senior_developer"],
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    code_reviewer = Agent(
        role="Code Reviewer",
        goal=(
            "Review code for correctness, security, performance, PEP 8 compliance, "
            "and edge cases. Provide a verdict (APPROVED/NEEDS_REVISION), a score "
            "(1-10), and specific actionable feedback."
        ),
        backstory=(
            "You are a meticulous Code Reviewer who catches bugs, security issues, "
            "and design flaws. You provide clear, actionable feedback with specific "
            "code fixes. A score of 7+ means APPROVED."
        ),
        llm=AGENT_LLMS["code_reviewer"],
        verbose=True,
        allow_delegation=False,
        max_iter=1,
    )

    tech_writer = Agent(
        role="Technical Writer",
        goal=(
            "Create comprehensive project documentation including README.md, "
            "usage examples, API reference, configuration guide, and troubleshooting."
        ),
        backstory=(
            "You are a Technical Writer specializing in developer documentation. "
            "You create clear, thorough docs that help developers get started "
            "quickly. You always include code examples."
        ),
        llm=AGENT_LLMS["tech_writer"],
        verbose=True,
        allow_delegation=False,
        max_iter=1,
    )

    qa_engineer = Agent(
        role="QA Engineer",
        goal=(
            "Generate a comprehensive pytest test suite with unit tests and "
            "integration tests. Cover all public functions, edge cases, boundary "
            "values, error paths. Aim for >90% coverage."
        ),
        backstory=(
            "You are a QA Engineer who writes thorough test suites using pytest. "
            "You use fixtures, parametrize, and test both happy paths and error cases."
        ),
        llm=AGENT_LLMS["qa_engineer"],
        verbose=True,
        allow_delegation=False,
        max_iter=1,
    )

    devops_agent = Agent(
        role="DevOps Engineer",
        goal=(
            "Create deployment configuration: Dockerfile (multi-stage), "
            "docker-compose.yml, requirements.txt, GitHub Actions CI/CD pipeline, "
            "and .env.example."
        ),
        backstory=(
            "You are a DevOps Engineer who creates production-ready deployment "
            "configs. You follow best practices: non-root containers, health "
            "checks, layer caching, and security scanning."
        ),
        llm=AGENT_LLMS["devops_agent"],
        verbose=True,
        allow_delegation=False,
        max_iter=1,
    )

    ui_designer = Agent(
        role="UI Designer",
        goal=(
            "Generate a modern Streamlit UI for the application. Use columns, "
            "tabs, expanders, sidebar, loading spinners, and proper feedback "
            "messages. Make it clean and responsive."
        ),
        backstory=(
            "You are a UI Designer specializing in Streamlit applications. "
            "You create beautiful, intuitive interfaces with modern design patterns."
        ),
        llm=AGENT_LLMS["ui_designer"],
        verbose=True,
        allow_delegation=False,
        max_iter=1,
    )

    return {
        "requirement_analyst": requirement_analyst,
        "senior_developer": senior_developer,
        "code_reviewer": code_reviewer,
        "tech_writer": tech_writer,
        "qa_engineer": qa_engineer,
        "devops_agent": devops_agent,
        "ui_designer": ui_designer,
    }


# ═════════════════════════════════════════════════════════════════════════════
# TASKS
# ═════════════════════════════════════════════════════════════════════════════

def create_tasks(agents, user_requirement):
    """Create all 7 SDLC tasks linked to their agents."""

    # Task 1: Requirement Analysis
    analyze_task = Task(
        description=(
            f"Analyze the following user requirement and produce a structured "
            f"specification document in Markdown format.\n\n"
            f"Include:\n"
            f"1. Project Title\n"
            f"2. Overview (one paragraph)\n"
            f"3. Functional Requirements (numbered list)\n"
            f"4. Non-Functional Requirements\n"
            f"5. Input/Output Specification\n"
            f"6. Constraints & Assumptions\n"
            f"7. Acceptance Criteria\n\n"
            f"USER REQUIREMENT:\n{user_requirement}"
        ),
        expected_output="A complete Markdown specification document.",
        agent=agents["requirement_analyst"],
    )

    # Task 2: Code Generation
    develop_task = Task(
        description=(
            "Based on the specification from the Requirement Analyst, write "
            "complete, production-ready Python code.\n\n"
            "Rules:\n"
            "- Follow PEP 8 and Python best practices\n"
            "- Include type hints on all function signatures\n"
            "- Write docstrings for all classes and functions\n"
            "- Add proper error handling with try/except\n"
            "- Use meaningful variable names\n"
            "- Include a __main__ guard\n"
            "- Wrap code in ```python ... ``` blocks"
        ),
        expected_output="Complete Python source code in markdown code blocks.",
        agent=agents["senior_developer"],
        context=[analyze_task],
    )

    # Task 3: Code Review
    review_task = Task(
        description=(
            "Review the code produced by the Senior Developer against the "
            "specification.\n\n"
            "Your review MUST include:\n"
            "1. **Verdict**: APPROVED or NEEDS_REVISION\n"
            "2. **Score**: 1-10 (7+ means APPROVED)\n"
            "3. **Issues Found** — numbered list with severity\n"
            "4. **Specific Fixes** — exact code changes needed\n"
            "5. **Positive Aspects** — what was done well"
        ),
        expected_output="A structured code review with verdict, score, and feedback.",
        agent=agents["code_reviewer"],
        context=[analyze_task, develop_task],
    )

    # Task 4: Test Generation
    test_task = Task(
        description=(
            "Write a comprehensive pytest test suite for the code.\n\n"
            "Rules:\n"
            "- Use pytest (not unittest)\n"
            "- Write unit tests and integration tests\n"
            "- Test all public functions and classes\n"
            "- Include edge cases, boundary values, error paths\n"
            "- Use fixtures and parametrize where appropriate\n"
            "- Aim for >90% code coverage\n"
            "- Wrap code in ```python ... ``` blocks"
        ),
        expected_output="Complete pytest test suite in markdown code blocks.",
        agent=agents["qa_engineer"],
        context=[analyze_task, develop_task],
    )

    # Task 5: Documentation
    doc_task = Task(
        description=(
            "Write comprehensive documentation for the project.\n\n"
            "Include:\n"
            "1. README.md — overview, installation, usage, API reference\n"
            "2. Code architecture explanation\n"
            "3. Usage examples with code\n"
            "4. Configuration guide\n"
            "5. Troubleshooting section"
        ),
        expected_output="Complete Markdown documentation.",
        agent=agents["tech_writer"],
        context=[analyze_task, develop_task],
    )

    # Task 6: DevOps Configuration
    devops_task = Task(
        description=(
            "Create deployment configuration for the project.\n\n"
            "Include:\n"
            "1. Dockerfile (multi-stage, minimal image)\n"
            "2. docker-compose.yml\n"
            "3. requirements.txt (pinned versions)\n"
            "4. .github/workflows/ci.yml (GitHub Actions)\n"
            "5. .env.example\n\n"
            "Use best practices: non-root user, health checks, layer caching."
        ),
        expected_output="Complete deployment configuration files.",
        agent=agents["devops_agent"],
        context=[analyze_task, develop_task],
    )

    # Task 7: UI Design
    ui_task = Task(
        description=(
            "Create a Streamlit UI for the application.\n\n"
            "Rules:\n"
            "- Use st.columns, st.tabs, st.expander for layout\n"
            "- Add page config (title, icon, wide layout)\n"
            "- Include sidebar for navigation\n"
            "- Add loading spinners and feedback messages\n"
            "- Handle errors gracefully\n"
            "- Wrap code in ```python ... ``` blocks"
        ),
        expected_output="Complete Streamlit app code in markdown code blocks.",
        agent=agents["ui_designer"],
        context=[analyze_task, develop_task],
    )

    return {
        "analyze": analyze_task,
        "develop": develop_task,
        "review": review_task,
        "test": test_task,
        "doc": doc_task,
        "devops": devops_task,
        "ui": ui_task,
    }


# ═════════════════════════════════════════════════════════════════════════════
# CREW BUILDER
# ═════════════════════════════════════════════════════════════════════════════

def build_sdlc_crew(user_requirement, step_callback=None, task_callback=None):
    """
    Build a CrewAI Crew with all 7 SDLC agents and tasks.

    Args:
        user_requirement: Natural-language description of the software.
        step_callback: Optional callback fired after each agent reasoning step.
        task_callback: Optional callback fired after each task completes.

    Returns:
        Tuple of (Crew, agents_dict, tasks_dict)
    """
    agents = create_agents()
    tasks = create_tasks(agents, user_requirement)

    crew = Crew(
        agents=list(agents.values()),
        tasks=[
            tasks["analyze"],
            tasks["develop"],
            tasks["review"],
            tasks["test"],
            tasks["doc"],
            tasks["devops"],
            tasks["ui"],
        ],
        process=Process.sequential,
        verbose=True,
        step_callback=step_callback,
        task_callback=task_callback,
    )

    return crew, agents, tasks


# ═════════════════════════════════════════════════════════════════════════════
# PIPELINE RUNNER
# ═════════════════════════════════════════════════════════════════════════════

def extract_code(response):
    """Extract code from markdown code blocks, or return as-is."""
    text = str(response)
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if blocks:
        return "\n\n".join(block.strip() for block in blocks)
    return text


def save_artifact(output_dir, filename, content, phase_id=None):
    """Save an artifact to the output directory with optional UUID header."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    # Prepend phase UUID as a trackable header
    header = ""
    if phase_id:
        ext = os.path.splitext(filename)[1]
        if ext in (".py",):
            header = f"# Phase UUID: {phase_id}\n\n"
        elif ext in (".md",):
            header = f"<!-- Phase UUID: {phase_id} -->\n\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + str(content))
    print(f"  -> Saved: {filepath}  (UUID: {phase_id or 'N/A'})")
    return filepath


def run_sdlc_pipeline(user_requirement, output_dir=None):
    """
    Run the full SDLC pipeline using CrewAI with UUID tracking.

    Each pipeline run gets a unique run_id. Each SDLC phase gets its own
    phase_id. All agent conversations are logged for full traceability.

    Args:
        user_requirement: Natural-language description of the software.
        output_dir: Directory to save generated artifacts.

    Returns:
        dict: All generated artifacts + manifest with UUIDs.
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR

    # ── Generate pipeline UUID ───────────────────────────────────────────
    run_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    pipeline_start = time.time()

    # Each run gets its own UUID-named subfolder under the base output dir
    output_dir = os.path.join(output_dir, run_id)
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'#'*60}")
    print(f"#  CREWAI SDLC PIPELINE STARTED                             #")
    print(f"{'#'*60}")
    print(f"  Run ID    : {run_id}")
    print(f"  Timestamp : {timestamp}")
    print(f"  Framework : CrewAI + Ollama (100% local)")
    print(f"  Output    : {os.path.abspath(output_dir)}/\n")

    # ── Phase definitions with UUID per phase ────────────────────────────
    phase_defs = [
        {"key": "specification", "file": "01_specification.md", "extract": False,
         "phase": "requirement_analysis", "agent": "Requirement Analyst",
         "model": AGENT_LLMS['requirement_analyst'].model},
        {"key": "code",          "file": "02_code.py",          "extract": True,
         "phase": "code_generation",     "agent": "Senior Developer",
         "model": AGENT_LLMS['senior_developer'].model},
        {"key": "review",        "file": "03_review.md",        "extract": False,
         "phase": "code_review",         "agent": "Code Reviewer",
         "model": AGENT_LLMS['code_reviewer'].model},
        {"key": "tests",         "file": "04_tests.py",         "extract": True,
         "phase": "test_generation",     "agent": "QA Engineer",
         "model": AGENT_LLMS['qa_engineer'].model},
        {"key": "documentation", "file": "05_documentation.md", "extract": False,
         "phase": "documentation",       "agent": "Tech Writer",
         "model": AGENT_LLMS['tech_writer'].model},
        {"key": "devops_config", "file": "06_devops.md",        "extract": False,
         "phase": "devops_configuration","agent": "DevOps Agent",
         "model": AGENT_LLMS['devops_agent'].model},
        {"key": "ui_code",       "file": "07_ui_app.py",        "extract": True,
         "phase": "ui_design",           "agent": "UI Designer",
         "model": AGENT_LLMS['ui_designer'].model},
    ]

    # Assign UUID to each phase
    for p in phase_defs:
        p["phase_id"] = str(uuid.uuid4())

    # ── Build and run the crew ───────────────────────────────────────────
    crew, agents, tasks = build_sdlc_crew(user_requirement)
    result = crew.kickoff()

    # ── Extract task outputs and save with UUIDs ─────────────────────────
    task_outputs = result.tasks_output if hasattr(result, "tasks_output") else []

    artifacts = {}
    conversation_log = []

    for i, pdef in enumerate(phase_defs):
        phase_start = time.time()

        if i < len(task_outputs):
            raw = str(task_outputs[i])
            content = extract_code(raw) if pdef["extract"] else raw
        else:
            raw = ""
            content = f"# {pdef['key']} — not generated"

        artifacts[pdef["key"]] = content
        save_artifact(output_dir, pdef["file"], content, phase_id=pdef["phase_id"])

        # Log conversation entry
        conversation_log.append({
            "phase_id": pdef["phase_id"],
            "phase": pdef["phase"],
            "agent": pdef["agent"],
            "model": pdef["model"],
            "input_context": user_requirement[:500] if i == 0 else f"(output from phase {i})",
            "output_length": len(content),
            "output_file": pdef["file"],
        })

    # ── Build manifest ───────────────────────────────────────────────────
    elapsed = time.time() - pipeline_start

    manifest = {
        "run_id": run_id,
        "timestamp": timestamp,
        "elapsed_seconds": round(elapsed, 1),
        "framework": "CrewAI + LiteLLM + Ollama",
        "user_requirement": user_requirement,
        "phases": [
            {
                "phase_id": p["phase_id"],
                "phase_number": i + 1,
                "phase_name": p["phase"],
                "agent": p["agent"],
                "model": p["model"],
                "output_file": p["file"],
            }
            for i, p in enumerate(phase_defs)
        ],
        "conversations": conversation_log,
    }

    # Save manifest
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  -> Saved: {manifest_path}  (Run ID: {run_id})")

    # Save conversation log
    conv_path = os.path.join(output_dir, "conversation_log.json")
    with open(conv_path, "w", encoding="utf-8") as f:
        json.dump({
            "run_id": run_id,
            "timestamp": timestamp,
            "conversations": conversation_log,
        }, f, indent=2, ensure_ascii=False)
    print(f"  -> Saved: {conv_path}")

    # ── Pipeline summary ─────────────────────────────────────────────────
    print(f"\n{'#'*60}")
    print(f"#  PIPELINE COMPLETE                                        #")
    print(f"{'#'*60}")
    print(f"  Run ID     : {run_id}")
    print(f"  Total time : {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"  Output     : {os.path.abspath(output_dir)}/")
    print(f"\n  Phase UUID Mapping:")
    for i, p in enumerate(phase_defs):
        print(f"    {i+1}. {p['phase']:<25} {p['phase_id']}")
    print(f"\n  Generated files:")
    for f in sorted(os.listdir(output_dir)):
        path = os.path.join(output_dir, f)
        size = os.path.getsize(path)
        print(f"    {f:<30} {size:>8,} bytes")
    print()

    artifacts["_manifest"] = manifest
    return artifacts
