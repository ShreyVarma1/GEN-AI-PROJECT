"""
Global pytest configuration.
Sets environment variables to prevent HuggingFace Hub network calls during tests.
"""
import os

# Prevent HuggingFace from making network calls during tests
# (cross-encoder reranker falls back gracefully when offline)
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
