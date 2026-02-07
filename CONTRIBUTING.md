# Contributing to Ollama SDLC CrewAI Multi-Agent Orchestration

Thanks for your interest in contributing! Here's how to get started.

---

## 🛠️ Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/Ollama_SDLC_CrewAI_MultiAgent_Orchestration.git
cd Ollama_SDLC_CrewAI_MultiAgent_Orchestration

# 2. Create virtual environment
python -m venv ollama_env
ollama_env\Scripts\activate        # Windows
# source ollama_env/bin/activate   # Linux / macOS

# 3. Install dependencies (including dev tools)
pip install -r requirements.txt
```

## 📐 Code Style

- Follow **PEP 8** conventions
- Use **type hints** for all function signatures
- Format with `black` before committing:
  ```bash
  black .
  ```
- Lint with `flake8`:
  ```bash
  flake8 sdlc_agents/ crewai_sdlc/ flask_app/
  ```

## 🔀 Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes with clear, descriptive commits
3. Ensure code passes lint and formatting checks
4. Submit a PR against `main` with a description of what changed and why

## 🐛 Reporting Issues

Open an issue with:
- A clear title and description
- Steps to reproduce (if it's a bug)
- Your environment details (OS, Python version, GPU, Ollama version)

## 📂 Project Layout

| Directory | Purpose |
|-----------|---------|
| `sdlc_agents/` | Raw Ollama API implementation |
| `crewai_sdlc/` | CrewAI framework implementation |
| `flask_app/` | Web dashboard (Flask + SSE) |
| `crewai_output/` | Generated pipeline artifacts |

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.
