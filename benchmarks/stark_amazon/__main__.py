#!/usr/bin/env python3
"""
Stark Amazon Benchmark Module Entry Point

This module enables running the Stark Amazon benchmark using:
python -m benchmarks.stark_amazon
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from benchmarks.stark_amazon_main import main

if __name__ == "__main__":
    main()
