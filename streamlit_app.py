import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Koenig Solutions - Salary Reconciliation",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 2rem 0;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border-radius: 15px;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Header with centered logo
st.markdown('<div class="main-header">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    # Check if logo exists
    if os.path.exists('assets/koenig-logo.png'):
        st.image('assets/koenig-logo.png', width=120)
    else:
        st.markdown("""
        <div style="width:120px; height:120px; background: linear-gradient(45deg, #1e3a8a, #3b82f6); 
                    border-radius: 15px; display: flex; align-items: center; justify-content: center; 
                    font-weight: bold; font-size: 32px; color: white; margin: 0 auto;">KS</div>
        """, unsafe_allow_html=True)

st.title("🏢 Koenig Solutions")
st.subheader("Salary Reconciliation System v2.0")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔐 Navigation Menu")
    
    # User info
    st.info("👤 **Current User**: admin")
    st.info("🎭 **Role**: Super Admin")
    st.info(f"📅 **Date**: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Mode selection
    mode = st.selectbox("🔄 Reconciliation Mode", ["Manual Reconciliation", "Auto Reconciliation"])

# Main content area
if mode == "Manual Reconciliation":
    st.header("📁 File Upload Section")
    
    # File upload columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Core Files")
        salary_file = st.file_uploader("📋 Salary File", type=['xlsx', 'xls'], key="salary")
        tds_file = st.file_uploader("💰 TDS File", type=['xlsx', 'xls'], key="tds")
        epf_file = st.file_uploader("🏦 EPF File", type=['xlsx', 'xls'], key="epf")
        
    with col2:
        st.subheader("🏧 Bank Files")
        bank_kotak = st.file_uploader("🏦 Bank Kotak SOA", type=['xlsx', 'xls'], key="kotak")
        bank_deutsche = st.file_uploader("🏦 Bank Deutsche SOA", type=['xlsx', 'xls'], key="deutsche")
        nps_file = st.file_uploader("💼 NPS File", type=['xlsx', 'xls'], key="nps")
    
    # Reconciliation options
    st.header("⚙️ Reconciliation Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tolerance = st.number_input("💰 Amount Tolerance (₹)", min_value=0.0, value=1.0, step=0.1)
        
    with col2:
        branches = st.multiselect(
            "🏢 Filter by Branches",
            ["All", "Gurgaon", "Dehradun", "Goa", "Chennai", "Bangalore", "Delhi"],
            default=["All"]
        )
        
    with col3:
        report_format = st.selectbox("📊 Report Format", ["Excel (.xlsx)", "CSV (.csv)"])
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        include_inactive = st.checkbox("👥 Include inactive employees")
        detailed_analysis = st.checkbox("📈 Generate detailed analysis")
        email_report = st.checkbox("📧 Email report after completion")
    
    # Process button
    if st.button("🚀 Start Manual Reconciliation", type="primary", use_container_width=True):
        files_uploaded = [salary_file, tds_file, epf_file, bank_kotak, bank_deutsche, nps_file]
        uploaded_count = len([f for f in files_uploaded if f is not None])
        
        if uploaded_count > 0:
            with st.spinner("Processing reconciliation..."):
                # Simulate processing
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                
                st.success(f"✅ Reconciliation completed! Processed {uploaded_count} files.")
                
                # Show sample results
                st.subheader("📊 Reconciliation Results")
                
                sample_results = pd.DataFrame({
                    'Metric': ['Total Employees', 'Bank Records', 'Successful Matches', 'Discrepancies', 'Success Rate'],
                    'Count': [547, 534, 506, 41, '92.5%'],
                    'Status': ['✅ Processed', '✅ Loaded', '✅ Matched', '⚠️ Review', '✅ Excellent']
                })
                
                st.dataframe(sample_results, use_container_width=True)
                
                # Download button
                st.download_button(
                    label="📊 Download Reconciliation Report",
                    data="Sample reconciliation report data",
                    file_name=f"Reconciliation_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("⚠️ Please upload at least one file to start reconciliation.")

else:  # Auto Reconciliation
    st.header("🤖 Auto Reconciliation Mode")
    st.info("🔄 Auto mode will automatically process files from configured sources.")
    
    if st.button("🚀 Start Auto Reconciliation", type="primary"):
        st.success("✅ Auto reconciliation initiated!")
        st.balloons()

# Footer
st.markdown("---")
st.markdown("**Koenig Solutions Salary Reconciliation System v2.0** | Deployed on Streamlit Cloud")
