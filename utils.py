import streamlit as st

APP_VERSION = "V1.1.0"
year = 2026


def add_footer():
    """Add consistent footer with version to all pages"""
    st.divider()
    st.caption(f"🚀 HAR to JMX Converter | Version {APP_VERSION} | © {year} Muthuvinayagam")
