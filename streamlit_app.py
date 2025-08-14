#!/usr/bin/env python3
"""
Koenig Solutions Salary Reconciliation System
Streamlit Cloud Entry Point
"""

import streamlit as st
import sys
import os

# Set page config first (must be first Streamlit command)
st.set_page_config(
    page_title="Koenig Solutions - Salary Reconciliation",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import and run your dashboard
try:
    # Import your dashboard module
    import dashboard
    
    # If dashboard has a main function, call it
    if hasattr(dashboard, 'main'):
        dashboard.main()
    else:
        # Otherwise execute the dashboard file
        exec(open('dashboard.py').read())
        
except FileNotFoundError:
    st.error("❌ Dashboard file not found")
    st.info("Available files: " + str(os.listdir('.')))
except ImportError as e:
    st.error(f"❌ Import error: {str(e)}")
except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
    st.info("Please check the application logs for details.")
