import streamlit as st
from utils import add_footer

st.set_page_config(page_title="Feedback & Support - HAR to JMX Converter", page_icon="📧", layout="centered")

st.title("📧 Feedback & Support")

# Contact & Feedback
st.write("""
We'd love to hear from you! If you have suggestions, bug reports, or feature requests, 
please fill out the form below.
""")

with st.expander("📝 Feedback Form", expanded=False):
    st.info("""
    **🔗 Google Form for Feedback**
    
    [Submit Your Feedback Here](https://forms.gle/Scwrdrcax5PGjLbWA)
    
    """)

st.subheader("🙏 Thank You!")

st.markdown("""
Happy testing! 🚀
""")

add_footer()
