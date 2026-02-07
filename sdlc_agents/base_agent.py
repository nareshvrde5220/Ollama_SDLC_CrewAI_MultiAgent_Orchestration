"""
Base Agent — Ollama OpenAI-Compatible API Client
==================================================
All SDLC agents inherit from this. Uses /v1/chat/completions
for tool-calling support.
"""

import json
import time
import requests
from .config import OLLAMA_BASE_URL, MAX_TOKENS, TEMPERATURE, REQUEST_TIMEOUT


class BaseAgent:
    """Base class for all SDLC agents."""

    def __init__(self, name, role, model, system_prompt):
        self.name = name
        self.role = role
        self.model = model
        self.system_prompt = system_prompt
        self.conversation = []

    def chat(self, user_message, temperature=None):
        """
        Send a message to the agent and get a response.
        Uses Ollama's OpenAI-compatible /v1/chat/completions endpoint.
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation)
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": MAX_TOKENS,
            "temperature": temperature if temperature is not None else TEMPERATURE,
            "stream": False,
        }

        start = time.time()
        try:
            resp = requests.post(
                f"{OLLAMA_BASE_URL}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            elapsed = time.time() - start

            if resp.status_code != 200:
                return f"[ERROR {resp.status_code}] {resp.text[:500]}"

            data = resp.json()
            content = data["choices"][0]["message"]["content"]

            # Save to conversation history
            self.conversation.append({"role": "user", "content": user_message})
            self.conversation.append({"role": "assistant", "content": content})

            self._log(f"responded in {elapsed:.1f}s ({len(content)} chars)")
            return content

        except requests.ConnectionError:
            return "[ERROR] Cannot connect to Ollama. Is it running? (ollama serve)"
        except requests.Timeout:
            return f"[ERROR] Request timed out after {REQUEST_TIMEOUT}s"
        except Exception as e:
            return f"[ERROR] {type(e).__name__}: {e}"

    def reset(self):
        """Clear conversation history."""
        self.conversation.clear()

    def _log(self, message):
        """Print a log message with agent name."""
        print(f"  [{self.name}] {message}")

    def __repr__(self):
        return f"<{self.name} ({self.model})>"
