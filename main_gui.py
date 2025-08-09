#!/usr/bin/env python3
"""
System Health Checker - GUI Version
A modern dashboard for monitoring system resources in real-time.
"""

import sys
import os

# Add the current directory to the path to import ui modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.dashboard import main

if __name__ == "__main__":
    print("Starting System Health Checker Dashboard...")
    print("Press Ctrl+C to exit")
    main()
