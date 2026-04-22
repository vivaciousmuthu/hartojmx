import streamlit as st
from utils import add_footer

st.set_page_config(
    page_title="HAR to JMX Converter",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5em;
        color: #1f77b4;
        margin-bottom: 1em;
    }
    .feature-box {
        background-color: var(--secondary-primary-color);
        border: 2px solid #f0f2f6;
        padding: 1.5em;
        border-radius: 10px;
        margin: 1em 0;
        height: 200px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 HAR to JMX Converter</h1>', unsafe_allow_html=True)

st.write("""
Welcome to the **HAR to JMX Converter** - Your powerful tool for converting HTTP Archive files to JMeter test plans!

This application helps you:
- 🎯 **Convert HAR files** to standardized JMX format
- ⚡ **Save time** on manual script creation
- 🔧 **Customize configurations** for your needs
- 📊 **Enable advanced load testing** with JMeter
""")

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-box">
    <h3>🔄 Converter </h3> 
    <p>Upload HAR files and convert them to JMX format instantly.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Converter →", key="btn_converter", use_container_width=True):
        st.switch_page("pages/1_hartojmx.py")

with col2:
    st.markdown("""
    <div class="feature-box">
    <h3>ℹ️ About</h3>
    <p>Learn more about the creator and the motivation behind this tool.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to About →", key="btn_about", use_container_width=True):
        st.switch_page("pages/2_about.py")

with col3:
    st.markdown("""
    <div class="feature-box">
    <h3>💡 Tips & Release</h3>
    <p>Explore helpful tips, tricks, and release notes.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Tips & Release →", key="btn_tips", use_container_width=True):
        st.switch_page("pages/3_tips_and_release.py")

with col4:
    st.markdown("""
    <div class="feature-box">
    <h3>🎨 Gallery</h3>
    <p>See examples and visual previews of conversions.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Gallery →", key="btn_gallery", use_container_width=True):
        st.switch_page("pages/4_gallery.py")

st.divider()

st.subheader("🌟 Key Features")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ✨ **Time Gap Grouping** - Automatically group requests into transactions based on time gaps
    
    ✨ **Flexible Configuration** - Enable/disable headers, listeners, and samplers
    
    ✨ **Social Media Filtering** - Optionally exclude social media tracking URLs
    """)

with col2:
    st.markdown("""
    ✨ **XML Validation** - Automatic sanitization of malformed data
    
    ✨ **Header Management** - Preserve request headers for realistic testing
    
    ✨ **No Data Storage** - Your files are processed instantly and not stored
    """)

st.divider()

st.subheader("🚀 Quick Start")
st.write("""
1. Navigate to the **HartoJMX** page using the sidebar
2. Upload your HAR file
3. Configure your preferences
4. Click **Convert to JMX**
5. Download your generated JMX file
6. Use it with JMeter for load testing
""")

st.info("💡 **Tip:** Check out the Tips & Release page for JMeter setup instructions and best practices!")

add_footer()
