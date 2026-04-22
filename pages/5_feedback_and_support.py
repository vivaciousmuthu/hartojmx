import streamlit as st
from utils import add_footer

st.set_page_config(page_title="Feedback & Support - HAR to JMX Converter", page_icon="📧", layout="centered")

st.title("📧 Feedback & Support")

# Contact & Feedback
st.write("""
We'd love to hear from you! If you have suggestions, bug reports, or feature requests, 
please fill out the form below or reach out using the contact information on the About page.
""")

with st.expander("📝 Feedback Google Form", expanded=False):
    st.info("""
    **🔗 Google Form for Feedback**
    
    [Submit Your Feedback Here](https://forms.gle/Scwrdrcax5PGjLbWA)
    
    """)

st.divider()

st.subheader("🙏 Thank You!")

st.markdown("""
Thank you for using the **HAR to JMX Converter**! Your support and feedback 
help us make this tool better every day. We appreciate your trust in our application.

Happy testing! 🚀
""")

add_footer()
