#!/usr/bin/env python3
"""
Koenig Solutions Salary Reconciliation System
Entry point for Streamlit Cloud deployment
"""

import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import and run the main dashboard
try:
    from dashboard import main
    if __name__ == "__main__":
        main()
except ImportError:
    st.error("Dashboard module not found. Please check your deployment.")
except Exception as e:
    st.error(f"Error starting application: {str(e)}")
