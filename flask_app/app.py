"""
Flask SDLC Dashboard — Live Agent Streaming + History
=======================================================
  - Thread-aware stdout/stderr interceptor for real-time agent text
  - CrewAI task_callback for reliable phase transitions
  - Non-blocking Flask (debug=False, threaded=True)
  - Concurrent pipeline support with per-thread routing
"""

import os
import sys
import io
import json
import time
import uuid
import threading
import queue
import re
from datetime import datetime, timezone
from pathlib import Path

# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL THREAD-AWARE STDOUT/STDERR INTERCEPTOR
# Must be installed BEFORE any CrewAI / rich imports so that their Console
# objects capture our interceptor (not the raw fd).
# ═════════════════════════════════════════════════════════════════════════════

_original_stdout = sys.stdout
_original_stderr = sys.stderr


class OutputInterceptor(io.TextIOBase):
    """
    Drop-in replacement for sys.stdout / sys.stderr.
    - Always passes through to the original stream (terminal console).
    - Routes writes to per-thread PipelineHandler for SSE streaming.
    - Threads without a registered handler are unaffected.
    """

    def __init__(self, original, name="stdout"):
        super().__init__()
        self._original = original
        self._name = name
        self._handlers: dict[int, "PipelineHandler"] = {}
        self._lock = threading.Lock()

    # ── stream-protocol plumbing ────────────────────────────────────────
    @property
    def encoding(self):
        return getattr(self._original, "encoding", "utf-8")

    def fileno(self):
        return self._original.fileno()

    def isatty(self):
        return self._original.isatty()

    def readable(self):
        return False

    def writable(self):
        return True

    # ── core write ──────────────────────────────────────────────────────
    def write(self, text):
        # 1) Always pass through to real terminal
        if self._original:
            try:
                self._original.write(text)
                self._original.flush()
            except Exception:
                pass

        if not text:
            return 0

        # 2) Route to thread-specific handler (if any)
        tid = threading.get_ident()
        with self._lock:
            handler = self._handlers.get(tid)
        if handler:
            handler.process(text)

        return len(text)

    def flush(self):
        if self._original:
            try:
                self._original.flush()
            except Exception:
                pass

    # ── handler registration ────────────────────────────────────────────
    def register(self, thread_id, handler):
        with self._lock:
            self._handlers[thread_id] = handler

    def unregister(self, thread_id):
        with self._lock:
            handler = self._handlers.pop(thread_id, None)
            if handler:
                handler.flush_remaining()


class PipelineHandler:
    """
    Accumulates stdout text for one pipeline thread and pushes
    agent_output SSE events to the associated queue.
    Phase transitions are driven externally via set_phase().
    """

    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.current_phase_index = 0
        self.chunk_buffer: list[str] = []
        self.last_push = time.time()
        self._lock = threading.Lock()

    def process(self, text):
        if not text:
            return
        with self._lock:
            clean = self._clean(text)
            if clean.strip():
                self.chunk_buffer.append(clean)
                now = time.time()
                if now - self.last_push > 0.25 or len(self.chunk_buffer) >= 4:
                    self._flush()

    def set_phase(self, index):
        """Called by task_callback when phase changes."""
        with self._lock:
            self._flush()
            self.current_phase_index = index

    def _flush(self):
        if not self.chunk_buffer:
            return
        combined = "".join(self.chunk_buffer)
        self.chunk_buffer.clear()
        self.last_push = time.time()
        self.event_queue.put({
            "event": "agent_output",
            "phase_index": self.current_phase_index,
            "text": combined[-4000:],
        })

    @staticmethod
    def _clean(text):
        text = re.sub(r"\x1b\[[0-9;]*m", "", text)
        for old, new in [("╭", "+"), ("╰", "+"), ("╮", "+"), ("╯", "+"),
                         ("─", "-"), ("│", "|")]:
            text = text.replace(old, new)
        return text

    def flush_remaining(self):
        with self._lock:
            self._flush()


# Install interceptors NOW — before any third-party import
_stdout_interceptor = OutputInterceptor(_original_stdout, "stdout")
_stderr_interceptor = OutputInterceptor(_original_stderr, "stderr")
sys.stdout = _stdout_interceptor
sys.stderr = _stderr_interceptor

# ═════════════════════════════════════════════════════════════════════════════
# IMPORTS (after interceptor is in place)
# ═════════════════════════════════════════════════════════════════════════════

from flask import (
    Flask, render_template, request, jsonify,
    Response, stream_with_context,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from crewai_sdlc.config import AGENT_LLMS, OLLAMA_BASE_URL, OUTPUT_DIR
from crewai_sdlc.crew import (
    create_agents, create_tasks, build_sdlc_crew,
    extract_code, save_artifact,
)

# ═════════════════════════════════════════════════════════════════════════════
# FLASK APP
# ═════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
app.secret_key = "sdlc-pipeline-dashboard-2026"

BASE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "crewai_output")
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# Active runs: run_id -> event queue
active_runs: dict[str, queue.Queue] = {}
runs_lock = threading.Lock()

# Phase definitions (matches crew.py task order)
PHASE_DEFS = [
    {"key": "specification", "file": "01_specification.md", "extract": False,
     "phase": "requirement_analysis", "agent": "Requirement Analyst",
     "icon": "fa-clipboard-list", "color": "#6366f1"},
    {"key": "code",          "file": "02_code.py",          "extract": True,
     "phase": "code_generation",     "agent": "Senior Developer",
     "icon": "fa-code", "color": "#8b5cf6"},
    {"key": "review",        "file": "03_review.md",        "extract": False,
     "phase": "code_review",         "agent": "Code Reviewer",
     "icon": "fa-magnifying-glass-chart", "color": "#a855f7"},
    {"key": "tests",         "file": "04_tests.py",         "extract": True,
     "phase": "test_generation",     "agent": "QA Engineer",
     "icon": "fa-flask-vial", "color": "#d946ef"},
    {"key": "documentation", "file": "05_documentation.md", "extract": False,
     "phase": "documentation",       "agent": "Tech Writer",
     "icon": "fa-book", "color": "#ec4899"},
    {"key": "devops_config", "file": "06_devops.md",        "extract": False,
     "phase": "devops_configuration", "agent": "DevOps Agent",
     "icon": "fa-gears", "color": "#f43f5e"},
    {"key": "ui_code",       "file": "07_ui_app.py",        "extract": True,
     "phase": "ui_design",           "agent": "UI Designer",
     "icon": "fa-palette", "color": "#f97316"},
]

AGENT_MODELS: dict[str, str] = {}
for _k, _llm in AGENT_LLMS.items():
    AGENT_MODELS[_k] = _llm.model.replace("ollama/", "")


# ═════════════════════════════════════════════════════════════════════════════
# PIPELINE CALLBACKS  (task_callback for phase transitions)
# ═════════════════════════════════════════════════════════════════════════════

def make_task_callback(event_queue, phases, handler):
    """
    Returns a function suitable for CrewAI's task_callback.
    Fires once when EACH task finishes → emits phase_complete + next phase_start.
    """
    task_counter = [0]  # mutable int

    def _on_task_done(task_output):
        try:
            idx = task_counter[0]
            raw = task_output.raw if hasattr(task_output, "raw") else str(task_output)
            agent_role = task_output.agent if hasattr(task_output, "agent") else ""

            if idx < len(phases):
                p = phases[idx]
                content = extract_code(raw) if p.get("extract") else raw

                # ── phase_complete ──────────────────────────────────────
                event_queue.put({
                    "event": "phase_complete",
                    "phase_index": idx,
                    "phase_id": p.get("phase_id", ""),
                    "phase": p.get("phase", ""),
                    "agent": p.get("agent", ""),
                    "content": content[:8000],
                    "content_length": len(content),
                    "file": p.get("file", ""),
                })

            task_counter[0] += 1
            next_idx = task_counter[0]

            # Update stdout handler's phase index
            handler.set_phase(next_idx)

            # ── phase_start for the next task ───────────────────────────
            if next_idx < len(phases):
                np = phases[next_idx]
                event_queue.put({
                    "event": "phase_start",
                    "phase_index": next_idx,
                    "phase_id": np.get("phase_id", ""),
                    "phase": np.get("phase", ""),
                    "agent": np.get("agent", ""),
                    "model": np.get("model", ""),
                    "icon": np.get("icon", ""),
                    "color": np.get("color", ""),
                })
        except Exception:
            pass

    return _on_task_done


# ═════════════════════════════════════════════════════════════════════════════
# PIPELINE RUNNER  (background thread)
# ═════════════════════════════════════════════════════════════════════════════

def run_pipeline_streaming(run_id, user_requirement, event_queue):
    """Execute the full SDLC pipeline with live SSE events."""
    thread_id = threading.get_ident()
    handler = PipelineHandler(event_queue)

    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        pipeline_start = time.time()
        output_dir = os.path.join(BASE_OUTPUT_DIR, run_id)
        os.makedirs(output_dir, exist_ok=True)

        # Assign UUIDs + model info to each phase
        phases = []
        for pdef in PHASE_DEFS:
            p = dict(pdef)
            p["phase_id"] = str(uuid.uuid4())
            # Lookup model via AGENT_LLMS key mapping
            llm_key = {
                "Requirement Analyst": "requirement_analyst",
                "Senior Developer": "senior_developer",
                "Code Reviewer": "code_reviewer",
                "QA Engineer": "qa_engineer",
                "Tech Writer": "tech_writer",
                "DevOps Agent": "devops_agent",
                "UI Designer": "ui_designer",
            }.get(p["agent"], "requirement_analyst")
            p["model"] = AGENT_LLMS[llm_key].model
            phases.append(p)

        # ── Register stdout/stderr capture for THIS thread ──────────────
        _stdout_interceptor.register(thread_id, handler)
        _stderr_interceptor.register(thread_id, handler)

        # ── pipeline_start event ────────────────────────────────────────
        event_queue.put({
            "event": "pipeline_start",
            "run_id": run_id,
            "timestamp": timestamp,
            "requirement": user_requirement,
            "phases": [
                {"phase_id": p["phase_id"], "phase": p["phase"],
                 "agent": p["agent"], "icon": p["icon"], "color": p["color"]}
                for p in phases
            ],
        })

        event_queue.put({"event": "status",
                         "message": "Building CrewAI agents and tasks..."})

        # ── Build crew WITH task_callback ───────────────────────────────
        on_task_done = make_task_callback(event_queue, phases, handler)
        crew, agents, tasks = build_sdlc_crew(
            user_requirement,
            task_callback=on_task_done,
        )

        event_queue.put({"event": "status",
                         "message": "Crew assembled — starting pipeline..."})

        # ── Emit phase_start for phase 0 manually ──────────────────────
        p0 = phases[0]
        event_queue.put({
            "event": "phase_start",
            "phase_index": 0,
            "phase_id": p0["phase_id"],
            "phase": p0["phase"],
            "agent": p0["agent"],
            "model": p0["model"],
            "icon": p0["icon"],
            "color": p0["color"],
        })

        # ── KICKOFF (blocking — but stdout is captured, callbacks fire) ─
        result = crew.kickoff()

        # ── Unregister interceptors ─────────────────────────────────────
        _stdout_interceptor.unregister(thread_id)
        _stderr_interceptor.unregister(thread_id)

        # ── Save artifacts to disk ──────────────────────────────────────
        task_outputs = (
            result.tasks_output if hasattr(result, "tasks_output") else []
        )
        conversation_log = []

        for i, p in enumerate(phases):
            if i < len(task_outputs):
                raw = str(task_outputs[i])
                content = extract_code(raw) if p["extract"] else raw
            else:
                raw = ""
                content = f"# {p['key']} — not generated"

            save_artifact(output_dir, p["file"], content,
                          phase_id=p["phase_id"])

            conversation_log.append({
                "phase_id": p["phase_id"],
                "phase": p["phase"],
                "agent": p["agent"],
                "model": p["model"],
                "input_context": (user_requirement[:500]
                                  if i == 0
                                  else f"(output from phase {i})"),
                "output_length": len(content),
                "output_file": p["file"],
            })

        # ── Save manifest + conversation log ────────────────────────────
        elapsed = time.time() - pipeline_start
        manifest = {
            "run_id": run_id,
            "timestamp": timestamp,
            "elapsed_seconds": round(elapsed, 1),
            "framework": "CrewAI + LiteLLM + Ollama",
            "user_requirement": user_requirement,
            "status": "completed",
            "phases": [
                {
                    "phase_id": p["phase_id"],
                    "phase_number": i + 1,
                    "phase_name": p["phase"],
                    "agent": p["agent"],
                    "model": p["model"],
                    "output_file": p["file"],
                }
                for i, p in enumerate(phases)
            ],
            "conversations": conversation_log,
        }
        with open(os.path.join(output_dir, "manifest.json"),
                  "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        with open(os.path.join(output_dir, "conversation_log.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"run_id": run_id, "timestamp": timestamp,
                        "conversations": conversation_log},
                      f, indent=2, ensure_ascii=False)

        # ── pipeline_complete ───────────────────────────────────────────
        event_queue.put({
            "event": "pipeline_complete",
            "run_id": run_id,
            "elapsed_seconds": round(elapsed, 1),
            "elapsed_display": f"{elapsed / 60:.1f} min",
            "files_count": len(os.listdir(output_dir)),
        })

    except Exception as exc:
        import traceback
        traceback.print_exc(file=_original_stderr)
        event_queue.put({"event": "error", "message": str(exc)})
    finally:
        _stdout_interceptor.unregister(thread_id)
        _stderr_interceptor.unregister(thread_id)
        event_queue.put({"event": "done"})
        with runs_lock:
            active_runs.pop(run_id, None)


# ═════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    agents_info = []
    role_map = {
        "requirement_analyst": "Requirement Analyst",
        "senior_developer":    "Senior Developer",
        "code_reviewer":       "Code Reviewer",
        "qa_engineer":         "QA Engineer",
        "tech_writer":         "Tech Writer",
        "devops_agent":        "DevOps Agent",
        "ui_designer":         "UI Designer",
    }
    for key, display in role_map.items():
        agents_info.append({
            "role": display,
            "model": AGENT_MODELS.get(key, "unknown"),
        })
    return render_template("index.html", agents=agents_info)


@app.route("/start", methods=["POST"])
def start_pipeline():
    data = request.get_json()
    requirement = data.get("requirement", "").strip()
    if not requirement:
        return jsonify({"error": "Requirement is required"}), 400

    run_id = str(uuid.uuid4())
    eq = queue.Queue()

    with runs_lock:
        active_runs[run_id] = eq

    t = threading.Thread(
        target=run_pipeline_streaming,
        args=(run_id, requirement, eq),
        daemon=True,
    )
    t.start()

    return jsonify({"run_id": run_id})


@app.route("/stream/<run_id>")
def stream(run_id):
    """SSE endpoint — streams pipeline events in real-time."""
    with runs_lock:
        eq = active_runs.get(run_id)

    if not eq:
        return Response(
            'data: {"event":"error","message":"Run not found or completed"}\n\n',
            mimetype="text/event-stream",
        )

    def generate():
        while True:
            try:
                event = eq.get(timeout=120)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("event") == "done":
                    break
            except queue.Empty:
                yield 'data: {"event":"heartbeat"}\n\n'

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route("/live/<run_id>")
def live(run_id):
    return render_template("live.html", run_id=run_id, phases=PHASE_DEFS)


@app.route("/history")
def history():
    runs = []
    if os.path.exists(BASE_OUTPUT_DIR):
        for entry in sorted(os.listdir(BASE_OUTPUT_DIR), reverse=True):
            run_path = os.path.join(BASE_OUTPUT_DIR, entry)
            manifest_path = os.path.join(run_path, "manifest.json")
            if os.path.isdir(run_path) and os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    runs.append({
                        "run_id": manifest.get("run_id", entry),
                        "timestamp": manifest.get("timestamp", ""),
                        "elapsed": manifest.get("elapsed_seconds", 0),
                        "requirement": manifest.get("user_requirement", "")[:120],
                        "status": manifest.get("status", "completed"),
                        "phases_count": len(manifest.get("phases", [])),
                    })
                except (json.JSONDecodeError, IOError):
                    pass
    return render_template("history.html", runs=runs)


@app.route("/detail/<run_id>")
def detail(run_id):
    run_path = os.path.join(BASE_OUTPUT_DIR, run_id)
    manifest_path = os.path.join(run_path, "manifest.json")
    if not os.path.exists(manifest_path):
        return render_template("404.html",
                               message=f"Run {run_id} not found"), 404

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    artifacts = []
    for phase in manifest.get("phases", []):
        filepath = os.path.join(run_path, phase["output_file"])
        content, size = "", 0
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            size = os.path.getsize(filepath)
        artifacts.append({
            **phase, "content": content, "size": size,
            "extension": os.path.splitext(phase["output_file"])[1],
        })

    conv_path = os.path.join(run_path, "conversation_log.json")
    conversations = []
    if os.path.exists(conv_path):
        with open(conv_path, "r", encoding="utf-8") as f:
            conversations = json.load(f).get("conversations", [])

    return render_template(
        "detail.html", manifest=manifest, artifacts=artifacts,
        conversations=conversations, phase_defs=PHASE_DEFS,
    )


@app.route("/api/runs")
def api_runs():
    runs = []
    if os.path.exists(BASE_OUTPUT_DIR):
        for entry in sorted(os.listdir(BASE_OUTPUT_DIR), reverse=True):
            mp = os.path.join(BASE_OUTPUT_DIR, entry, "manifest.json")
            if os.path.exists(mp):
                try:
                    with open(mp, "r", encoding="utf-8") as f:
                        runs.append(json.load(f))
                except (json.JSONDecodeError, IOError):
                    pass
    return jsonify(runs)


@app.route("/api/run/<run_id>")
def api_run(run_id):
    mp = os.path.join(BASE_OUTPUT_DIR, run_id, "manifest.json")
    if not os.path.exists(mp):
        return jsonify({"error": "Not found"}), 404
    with open(mp, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))


@app.route("/api/artifact/<run_id>/<filename>")
def api_artifact(run_id, filename):
    fp = os.path.join(BASE_OUTPUT_DIR, run_id, filename)
    if not os.path.exists(fp):
        return jsonify({"error": "Not found"}), 404
    with open(fp, "r", encoding="utf-8") as f:
        return jsonify({"content": f.read(), "filename": filename})


# ── Template filters ────────────────────────────────────────────────────────

@app.template_filter("timeago")
def timeago_filter(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        diff = datetime.now(timezone.utc) - dt
        s = int(diff.total_seconds())
        if s < 60:
            return "just now"
        if s < 3600:
            return f"{s // 60}m ago"
        if s < 86400:
            return f"{s // 3600}h ago"
        return f"{s // 86400}d ago"
    except Exception:
        return iso_str


@app.template_filter("format_ts")
def format_ts_filter(iso_str):
    try:
        return datetime.fromisoformat(iso_str).strftime(
            "%b %d, %Y %I:%M %p UTC"
        )
    except Exception:
        return iso_str


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    _original_stdout.write(
        "\n" + "=" * 60 + "\n"
        "  SDLC Pipeline Dashboard — Flask + SSE Live Streaming\n"
        "  http://localhost:5000\n"
        + "=" * 60 + "\n\n"
    )
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False,
    )
