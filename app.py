import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard import create_dashboard

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Vehicle Registration Analytics",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    create_dashboard()

if __name__ == "__main__":
    main()
