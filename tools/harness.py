"""
This script sets up the Python path to include the parent directory
and then imports the xetrapal module.

This is likely used as a test harness or an entry point for running
xetrapal from within the 'tools' directory.
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import xetrapal
