"""Thin wrapper around the local Ollama HTTP API with retries."""

import time
import requests

MODEL_MAP = {
    "qwen": "qwen3:1.7b",
    "llama": "llama3.2:1b",
    "gemma": "gemma3:1b",
}


class OllamaClient:
    def __init__(self, model_name, api_base="http://localhost:11434", max_retries=3):
        if model_name not in MODEL_MAP:
            raise ValueError(f"Unknown model '{model_name}', expected one of {list(MODEL_MAP)}")
        self.model_name = model_name
        self.ollama_model = MODEL_MAP[model_name]
        self.api_base = api_base
        self.max_retries = max_retries

    def generate(self, prompt, system=None, temperature=0.0, num_predict=20):
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "think": False,
            "options": {"temperature": temperature, "num_predict": num_predict},
        }
        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                res = requests.post(f"{self.api_base}/api/generate", json=payload, timeout=120)
                res.raise_for_status()
                return res.json()["response"].strip()
            except (requests.RequestException, KeyError) as e:
                last_err = e
                time.sleep(2 * attempt)
        raise RuntimeError(f"Ollama request failed after {self.max_retries} attempts: {last_err}")
