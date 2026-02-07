"""
SDLC Pipeline Orchestrator
============================
Coordinates all 7 agents through the full software development lifecycle:
  Requirements → Code → Review (iterative) → Tests → Docs → DevOps → UI
"""

import os
import re
import time
from datetime import datetime

from .config import REVIEW_MAX_ITERATIONS
from .agents import (
    RequirementAnalyst,
    SeniorDeveloper,
    CodeReviewer,
    TechWriter,
    QAEngineer,
    DevOpsAgent,
    UIDesigner,
)


class SDLCOrchestrator:
    """
    Orchestrates the complete SDLC pipeline using 7 specialized agents
    powered by local Ollama models.
    """

    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Initialize all agents
        self.analyst = RequirementAnalyst()
        self.developer = SeniorDeveloper()
        self.reviewer = CodeReviewer()
        self.writer = TechWriter()
        self.qa = QAEngineer()
        self.devops = DevOpsAgent()
        self.ui_designer = UIDesigner()

        # Pipeline artifacts
        self.artifacts = {
            "requirement": "",
            "specification": "",
            "code": "",
            "review": "",
            "tests": "",
            "documentation": "",
            "devops_config": "",
            "ui_code": "",
        }
        self.review_iterations = 0

    def run(self, user_requirement):
        """
        Execute the full SDLC pipeline.

        Args:
            user_requirement: Natural-language description of the software.

        Returns:
            dict: All generated artifacts.
        """
        self.artifacts["requirement"] = user_requirement
        pipeline_start = time.time()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self._banner("SDLC PIPELINE STARTED")
        print(f"  Timestamp : {timestamp}")
        print(f"  Output    : {os.path.abspath(self.output_dir)}/")
        print()

        # ── Phase 1: Requirement Analysis ────────────────────────────
        self._phase("1/7", "REQUIREMENT ANALYSIS", self.analyst)
        self.artifacts["specification"] = self.analyst.analyze(user_requirement)
        self._save("01_specification.md", self.artifacts["specification"])

        # ── Phase 2: Code Generation ─────────────────────────────────
        self._phase("2/7", "CODE GENERATION", self.developer)
        self.artifacts["code"] = self.developer.develop(self.artifacts["specification"])
        self._save("02_code.py", self._extract_code(self.artifacts["code"]))

        # ── Phase 3: Code Review (iterative) ─────────────────────────
        self._phase("3/7", "CODE REVIEW", self.reviewer)
        for iteration in range(1, REVIEW_MAX_ITERATIONS + 1):
            self.review_iterations = iteration
            print(f"\n  Review iteration {iteration}/{REVIEW_MAX_ITERATIONS}")

            review = self.reviewer.review(
                self.artifacts["code"],
                self.artifacts["specification"],
            )
            self.artifacts["review"] = review

            if self._is_approved(review):
                print(f"  >>> APPROVED at iteration {iteration}")
                break

            if iteration < REVIEW_MAX_ITERATIONS:
                print(f"  >>> NEEDS REVISION — sending feedback to Developer")
                self.artifacts["code"] = self.developer.revise(review)
                self._save("02_code.py", self._extract_code(self.artifacts["code"]))

        self._save("03_review.md", self.artifacts["review"])

        # ── Phase 4: Test Generation ─────────────────────────────────
        self._phase("4/7", "TEST GENERATION", self.qa)
        self.artifacts["tests"] = self.qa.generate_tests(
            self.artifacts["specification"],
            self.artifacts["code"],
        )
        self._save("04_tests.py", self._extract_code(self.artifacts["tests"]))

        # ── Phase 5: Documentation ───────────────────────────────────
        self._phase("5/7", "DOCUMENTATION", self.writer)
        self.artifacts["documentation"] = self.writer.document(
            self.artifacts["specification"],
            self.artifacts["code"],
        )
        self._save("05_documentation.md", self.artifacts["documentation"])

        # ── Phase 6: DevOps Configuration ────────────────────────────
        self._phase("6/7", "DEVOPS CONFIGURATION", self.devops)
        self.artifacts["devops_config"] = self.devops.configure(
            self.artifacts["specification"],
            self.artifacts["code"],
        )
        self._save("06_devops.md", self.artifacts["devops_config"])

        # ── Phase 7: UI Design ───────────────────────────────────────
        self._phase("7/7", "UI DESIGN", self.ui_designer)
        self.artifacts["ui_code"] = self.ui_designer.design(
            self.artifacts["specification"],
            self.artifacts["code"],
        )
        self._save("07_ui_app.py", self._extract_code(self.artifacts["ui_code"]))

        # ── Pipeline Complete ────────────────────────────────────────
        elapsed = time.time() - pipeline_start
        self._banner("PIPELINE COMPLETE")
        print(f"  Total time     : {elapsed:.0f}s ({elapsed/60:.1f} min)")
        print(f"  Review rounds  : {self.review_iterations}")
        print(f"  Files saved    : {self.output_dir}/")
        print()
        self._list_output_files()

        return self.artifacts

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _phase(self, step, name, agent):
        """Print phase header."""
        print(f"\n{'='*60}")
        print(f"  Phase {step}: {name}")
        print(f"  Agent: {agent.name}  |  Model: {agent.model}")
        print(f"{'='*60}")

    def _banner(self, text):
        """Print a banner."""
        width = 60
        print()
        print(f"{'#'*width}")
        print(f"#  {text:<{width-4}} #")
        print(f"{'#'*width}")

    def _save(self, filename, content):
        """Save an artifact to the output directory."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  -> Saved: {filepath}")

    def _extract_code(self, response):
        """Extract code from markdown code blocks, or return as-is."""
        # Match ```python ... ``` or ``` ... ```
        blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", response, re.DOTALL)
        if blocks:
            return "\n\n".join(block.strip() for block in blocks)
        return response

    def _is_approved(self, review):
        """Check if the review verdict is APPROVED."""
        review_upper = review.upper()
        if "APPROVED" in review_upper and "NEEDS_REVISION" not in review_upper:
            return True
        # Check for score >= 7
        score_match = re.search(r"score[:\s]*(\d+)", review, re.IGNORECASE)
        if score_match and int(score_match.group(1)) >= 7:
            return True
        return False

    def _list_output_files(self):
        """List all files in the output directory."""
        print("  Output files:")
        for f in sorted(os.listdir(self.output_dir)):
            path = os.path.join(self.output_dir, f)
            size = os.path.getsize(path)
            print(f"    {f:<30} {size:>8,} bytes")
        print()
