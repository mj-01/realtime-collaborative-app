#!/usr/bin/env python3
"""
Agent Company ML Benchmark Module Entry Point

This module enables running the Agent Company ML benchmark using:
python -m benchmarks.agent_company_ml
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from benchmarks.agent_company_ml_main import main

if __name__ == "__main__":
    main()
