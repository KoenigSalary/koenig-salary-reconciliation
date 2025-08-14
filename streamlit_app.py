#!/usr/bin/env python3
"""
Koenig Solutions Salary Reconciliation System
Streamlit Cloud Entry Point
"""

import streamlit as st
import os

# Set page config first
st.set_page_config(
    page_title="Koenig Solutions - Salary Reconciliation",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Execute dashboard.py directly
try:
    if os.path.exists('dashboard.py'):
        with open('dashboard.py', 'r') as f:
            dashboard_code = f.read()
        exec(dashboard_code)
    else:
        st.error("❌ Dashboard file not found")
        st.info("Available files: " + str(os.listdir('.')))
except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
    
    # Fallback simple interface
    st.title("🏢 Koenig Solutions")
    st.subheader("Salary Reconciliation System v2.0")
    st.info("Loading dashboard... Please check logs for details.")
    st.write("Error details:", str(e))
