"""Pytest configuration and path setup for AI Engine tests."""

import sys
import os

# Ensure services/ai-engine is on sys.path
engine_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)
