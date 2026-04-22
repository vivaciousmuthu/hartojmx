import streamlit as st
from utils import add_footer

st.set_page_config(page_title="Gallery - HAR to JMX Converter", page_icon="🎨", layout="wide")

st.title("🎨 Gallery & Examples")

st.write("""
Explore visual examples and use cases of the HAR to JMX Converter in action. 
This gallery showcases various conversion scenarios and best practices.
""")

st.divider()

st.subheader("📸 Converter Interface Screenshots")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Converter Main Page**
    
    Upload interface for HAR files with configuration options.
    """)
    st.info("📷 **Upload HAR File**\n\n")
    st.image("images/2_Upload_har.png", caption="Converter Interface")

with col2:
    st.markdown("""
    **Configuration Options**
    
    Customize your conversion with various toggles and settings.
    """)
    st.info("📷 **Script Configuration**\n\n")
    st.image("images/3_Script_Config.png", caption="Converter Interface")

st.divider()

st.subheader("📊 Conversion Examples")

# with st.expander("Example 1: Simple GET/POST Conversion", expanded=True):
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("""
#         **Input: HAR File**
        
#         - 5 HTTP requests
#         - Mix of GET and POST
#         - Multiple domains
#         - Various headers and parameters
#         """)
#         st.info("📷 **Before Screenshot Placeholder**")
    
#     with col2:
#         st.markdown("""
#         **Output: JMX File**
        
#         - Organized transaction controllers
#         - Preserved headers
#         - Parameter mapping
#         - Ready for JMeter
#         """)
#         st.info("📷 **After Screenshot Placeholder**")

with st.expander("Example 1: E-Commerce Application", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Input: E-Commerce HAR**
        
        - Launch Petstore app
        - Click on the Product "Fish"
        - Click on the Product ID "FI-SW-01"
        - Click on the Item Id "EST-1"
        - Add to Cart
        """)
        st.info("📷 **Input Screenshot - Har**")
        st.image("images/1_har_File.png", caption="E-Commerce Petstore HAR File")
    
    with col2:
        st.markdown("""
        **Output: Load Test Plan**
        
        - Header Configuration
        - Transaction grouping
        - Assertion points
        - Cookie handling
        - Time-gap grouping
        """)
        st.info("📷 **Output Screenshot - JMeter**")
        st.image("images/7_Sample_JMeter_Output.png", caption="jmeter Output file")

with st.expander("Example 2: API Request Conversion", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Input: GET API HAR**
        
        - REST API calls
        - JSON payloads
        - Authentication headers
        - FindByStatus endpoints
        """)
        st.info("📷 **Before Screenshot - API HAR**")
        st.image("images/8_Pet_API_GET_Req.png", caption="API HAR File")
    
    with col2:
        st.markdown("""
        **Output: GET API Test Plan**
        
        - Proper payload handling
        - Header preservation
        - Response assertions
        - Performance metrics
        """)
        st.info("📷 **After Screenshot - API JMeter**")
        st.image("images/9_PET_API_GET_JMeter.png", caption="API JMX Output")

st.divider()

st.subheader("✨ Feature Highlights")

#col1, col2, col3 = st.columns(3)
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔄 Transaction Grouping
    
    Automatically groups requests into logical transactions based on time gaps.
    
    """)
    st.info("📷 **Feature Screenshot Transaction**")
    st.image("images/4_Trans_controller.png", caption="Transaction Grouping Example")

with col2:
    st.markdown("""
    ### 📋 Header Management
    
    Preserves request headers for realistic load testing scenarios.
    
    """)
    st.info("📷 **Feature Screenshot Header**")
    st.image("images/5_Header_Config.png", caption="Header Configuration Example")

# with col3:
#     st.markdown("""
#     ### 🎯 Parameter Handling
    
#     Intelligently manages GET parameters and POST payloads.
    
#     *Example visualization coming soon*
#     """)
#     st.info("📷 **Feature Screenshot Placeholder**")

st.divider()

st.subheader("📈 Performance & Results")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Validate JMeter Script & Conduct a Run**
    
        - Validated a script multiple times with consistent results
        - Run a Single user test
        - Conduct a load test with respective user counts and durations
        - View aggregated metrics and performance results
    """)


with col2:
    st.markdown("""
    **During Run & Report Generation**
                
        - Monitor a load test and observe if any errors occur
        - Generate HTML reports with detailed analysis
        - Visualize response times, throughput, and error rates
        - Monitor the resource utilization of the system under test during load testing   
    """)


st.divider()

st.subheader("🎬 Video Tutorials (Coming Soon)")

st.write("""
Video tutorials demonstrating:
- How to record a HAR file
- Using the converter
- Loading JMX files in JMeter
- Running load tests
- Interpreting results

*Video links will be added soon*
""")

st.divider()

st.subheader("💡 Pro Tips Showcased")

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **✅ Tip 1: Transaction Naming**
        
        Use the S01, S02 prefix format for organized script naming
        """)
        st.success("""
        **✅ Tip 2: Social Media Filtering**
        
        Exclude tracking URLs for cleaner, faster tests
        """)
    
    with col2:
        st.success("""
        **✅ Tip 3: Non-GUI Mode**
        
        Use command-line mode for large-scale load tests
        """)
        st.success("""
        **✅ Tip 4: Multi-Protocol**
        
        The tool handles both HTTP and HTTPS automatically
        """)

st.divider()

st.info("""
🚧 **Gallery Updates Coming Soon!**

More screenshots, videos, and detailed examples will be added as new features are released.
Check back regularly for new content!
""")

add_footer()
