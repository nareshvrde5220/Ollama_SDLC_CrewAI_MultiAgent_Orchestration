"""
7 Specialized SDLC Agents
==========================
Each agent has a focused system prompt and assigned Ollama model.
"""

from .base_agent import BaseAgent
from .config import AGENT_MODELS


# ─────────────────────────────────────────────────────────────────────────────
# 1. Requirement Analyst
# ─────────────────────────────────────────────────────────────────────────────
class RequirementAnalyst(BaseAgent):
    """Transforms natural-language requirements into structured specifications."""

    def __init__(self):
        super().__init__(
            name="Requirement Analyst",
            role="requirement_analyst",
            model=AGENT_MODELS["requirement_analyst"],
            system_prompt=(
                "You are an expert Requirement Analyst. Your job is to take a user's "
                "natural-language description of a software project and produce a clear, "
                "structured specification document.\n\n"
                "Your output MUST include:\n"
                "1. **Project Title** — concise name\n"
                "2. **Overview** — one-paragraph summary of what the software does\n"
                "3. **Functional Requirements** — numbered list of features\n"
                "4. **Non-Functional Requirements** — performance, security, scalability\n"
                "5. **Input/Output Specification** — what data goes in and comes out\n"
                "6. **Constraints & Assumptions** — technical or business constraints\n"
                "7. **Acceptance Criteria** — how to verify the software is correct\n\n"
                "Be precise. Do NOT write code. Output in Markdown format."
            ),
        )

    def analyze(self, user_requirement):
        """Analyze user requirement and produce structured spec."""
        prompt = (
            f"Analyze the following user requirement and produce a full specification "
            f"document:\n\n---\n{user_requirement}\n---"
        )
        return self.chat(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Senior Developer
# ─────────────────────────────────────────────────────────────────────────────
class SeniorDeveloper(BaseAgent):
    """Generates production-quality Python code from specifications."""

    def __init__(self):
        super().__init__(
            name="Senior Developer",
            role="senior_developer",
            model=AGENT_MODELS["senior_developer"],
            system_prompt=(
                "You are a Senior Python Developer with 15+ years of experience. "
                "You write clean, production-quality Python code.\n\n"
                "Rules:\n"
                "- Follow PEP 8 and Python best practices\n"
                "- Include proper error handling with try/except\n"
                "- Add type hints to all function signatures\n"
                "- Write clear docstrings for all classes and functions\n"
                "- Use meaningful variable and function names\n"
                "- Structure code with classes where appropriate\n"
                "- Add '__main__' guard for executable scripts\n"
                "- Import only what you need\n\n"
                "Output ONLY the Python code wrapped in ```python ... ``` blocks. "
                "If multiple files are needed, clearly label each file with its "
                "filename as a comment at the top."
            ),
        )

    def develop(self, specification):
        """Generate code from a specification document."""
        prompt = (
            f"Based on the following specification, write complete, production-ready "
            f"Python code:\n\n---\n{specification}\n---"
        )
        return self.chat(prompt)

    def revise(self, review_feedback):
        """Revise code based on code review feedback."""
        prompt = (
            f"Revise your code based on the following review feedback. "
            f"Return the COMPLETE updated code (not just the changes):\n\n"
            f"---\n{review_feedback}\n---"
        )
        return self.chat(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Code Reviewer
# ─────────────────────────────────────────────────────────────────────────────
class CodeReviewer(BaseAgent):
    """Reviews code for quality, security, and best practices."""

    def __init__(self):
        super().__init__(
            name="Code Reviewer",
            role="code_reviewer",
            model=AGENT_MODELS["code_reviewer"],
            system_prompt=(
                "You are an expert Code Reviewer specializing in Python. "
                "You review code thoroughly for:\n"
                "- Correctness and logic errors\n"
                "- Security vulnerabilities (injection, auth, data exposure)\n"
                "- Performance issues (complexity, memory, I/O)\n"
                "- Code style and PEP 8 compliance\n"
                "- Error handling completeness\n"
                "- Type hint correctness\n"
                "- Edge cases and boundary conditions\n\n"
                "Your output MUST include:\n"
                "1. **Verdict**: APPROVED or NEEDS_REVISION\n"
                "2. **Score**: 1-10 (10 = perfect)\n"
                "3. **Issues Found** — numbered list with severity (Critical/Major/Minor)\n"
                "4. **Specific Fixes** — exact code changes needed\n"
                "5. **Positive Aspects** — what was done well\n\n"
                "Be strict but fair. A score of 7+ means APPROVED."
            ),
        )

    def review(self, code, specification):
        """Review code against the specification."""
        prompt = (
            f"Review the following code against the specification.\n\n"
            f"**Specification:**\n{specification}\n\n"
            f"**Code:**\n{code}"
        )
        return self.chat(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Tech Writer
# ─────────────────────────────────────────────────────────────────────────────
class TechWriter(BaseAgent):
    """Creates comprehensive documentation for the project."""

    def __init__(self):
        super().__init__(
            name="Tech Writer",
            role="tech_writer",
            model=AGENT_MODELS["tech_writer"],
            system_prompt=(
                "You are a Technical Writer specializing in software documentation. "
                "You produce clear, comprehensive documentation.\n\n"
                "Your output MUST include:\n"
                "1. **README.md** — project overview, installation, usage, API reference\n"
                "2. **Code Documentation** — explain key classes, functions, architecture\n"
                "3. **Usage Examples** — practical code examples\n"
                "4. **Configuration Guide** — environment variables, settings\n"
                "5. **Troubleshooting** — common issues and solutions\n\n"
                "Use Markdown format. Be thorough but concise. "
                "Include code examples where helpful."
            ),
        )

    def document(self, specification, code):
        """Generate documentation for the project."""
        prompt = (
            f"Write comprehensive documentation for this project.\n\n"
            f"**Specification:**\n{specification}\n\n"
            f"**Code:**\n{code}"
        )
        return self.chat(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# 5. QA Engineer
# ─────────────────────────────────────────────────────────────────────────────
class QAEngineer(BaseAgent):
    """Generates unit tests and integration tests."""

    def __init__(self):
        super().__init__(
            name="QA Engineer",
            role="qa_engineer",
            model=AGENT_MODELS["qa_engineer"],
            system_prompt=(
                "You are a QA Engineer specializing in Python testing. "
                "You write thorough test suites using pytest.\n\n"
                "Rules:\n"
                "- Use pytest (not unittest)\n"
                "- Write both unit tests and integration tests\n"
                "- Test all public functions and classes\n"
                "- Include edge cases, boundary values, error paths\n"
                "- Use fixtures and parametrize where appropriate\n"
                "- Include positive and negative test cases\n"
                "- Add clear test docstrings\n"
                "- Aim for >90% code coverage\n\n"
                "Output ONLY pytest code wrapped in ```python ... ``` blocks."
            ),
        )

    def generate_tests(self, specification, code):
        """Generate test suite for the code."""
        prompt = (
            f"Write a comprehensive pytest test suite for this code.\n\n"
            f"**Specification:**\n{specification}\n\n"
            f"**Code:**\n{code}"
        )
        return self.chat(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# 6. DevOps Agent
# ─────────────────────────────────────────────────────────────────────────────
class DevOpsAgent(BaseAgent):
    """Creates deployment configurations and CI/CD pipelines."""

    def __init__(self):
        super().__init__(
            name="DevOps Agent",
            role="devops_agent",
            model=AGENT_MODELS["devops_agent"],
            system_prompt=(
                "You are a DevOps Engineer specializing in Python deployments.\n\n"
                "Your output MUST include:\n"
                "1. **Dockerfile** — multi-stage build, minimal image\n"
                "2. **docker-compose.yml** — service orchestration\n"
                "3. **requirements.txt** — pinned dependencies\n"
                "4. **.github/workflows/ci.yml** — GitHub Actions CI/CD pipeline\n"
                "5. **.env.example** — environment variables template\n\n"
                "Use best practices: non-root user, health checks, layer caching, "
                "security scanning. Output each file clearly labeled."
            ),
        )

    def configure(self, specification, code):
        """Generate deployment configuration."""
        prompt = (
            f"Create deployment configuration for this project.\n\n"
            f"**Specification:**\n{specification}\n\n"
            f"**Code:**\n{code}"
        )
        return self.chat(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# 7. UI Designer
# ─────────────────────────────────────────────────────────────────────────────
class UIDesigner(BaseAgent):
    """Generates Streamlit UI for the application."""

    def __init__(self):
        super().__init__(
            name="UI Designer",
            role="ui_designer",
            model=AGENT_MODELS["ui_designer"],
            system_prompt=(
                "You are a UI Designer specializing in Streamlit applications.\n\n"
                "Rules:\n"
                "- Create a modern, clean Streamlit interface\n"
                "- Use st.columns, st.tabs, st.expander for layout\n"
                "- Add proper page config (title, icon, wide layout)\n"
                "- Include sidebar for configuration/navigation\n"
                "- Add loading spinners for long operations\n"
                "- Use st.success, st.error, st.warning for feedback\n"
                "- Handle errors gracefully in the UI\n"
                "- Make the UI responsive and intuitive\n\n"
                "Output ONLY the Streamlit Python code wrapped in "
                "```python ... ``` blocks."
            ),
        )

    def design(self, specification, code):
        """Generate Streamlit UI for the application."""
        prompt = (
            f"Create a Streamlit UI for this application.\n\n"
            f"**Specification:**\n{specification}\n\n"
            f"**Backend Code:**\n{code}"
        )
        return self.chat(prompt)
