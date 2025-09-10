#!/usr/bin/env python3
"""
GSM8K Benchmark Module Entry Point

This module enables running the GSM8K benchmark using:
python -m benchmarks.gsm8k
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from benchmarks.gsm8k_main import main

if __name__ == "__main__":
    main()
