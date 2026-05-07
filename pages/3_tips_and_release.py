import streamlit as st
from utils import add_footer

st.set_page_config(page_title="Tips & Release - HAR to JMX Converter", page_icon="💡", layout="centered")

st.title("💡 Tips & Release Features")

st.write("""
This page provides comprehensive guidance for using the HAR to JMX Converter and understanding 
the latest updates and features.
""")

st.divider()

st.subheader("📖 Tips & Features")

# JMeter Prerequisites
with st.expander("🛠️ JMeter Pre-requisites", expanded=False):
    st.write("""
You must download and set up the appropriate version of JMeter on your local machine to run the generated JMX files.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Recommended Version: JMeter 5.6.3**")
        st.write("""
JMeter 5.6.3 is the target version for this converter. Using this version ensures full compatibility with 
the generated JMX files.
        """)
    
    with col2:
        st.write("""
**Download Links:**
- [Apache JMeter Binaries](https://jmeter.apache.org/download_jmeter.cgi)
- [JMeter Plugins](https://jmeter-plugins.org)
        """)
    
    st.warning("""
**⚠️ Important:** If you're using an older version of JMeter (less than 5.6.3), 
you may encounter compatibility issues with the generated JMX files. 
Please upgrade to JMeter 5.6.3 to avoid such issues.
    """)
    
    st.subheader("Installation Steps")
    st.markdown("""
    1. Download Apache JMeter from the official website
    2. Extract the binary to your preferred location
    3. Navigate to the `bin` directory
    4. Run `jmeter.sh` (macOS/Linux) or `jmeter.bat` (Windows)
    5. Wait for the GUI to launch
    6. You're ready to use your generated JMX files!
    """)


# Tips & Tricks
with st.expander("🎯 Tips & Tricks for JMeter", expanded=False):
    st.write("Here are some useful tips and tricks to help you get started with JMeter:")
    
    st.markdown("""
    **📚 Understand the Basics**
    - Familiarize yourself with JMeter's interface, components, and terminology
    - Knowing how to navigate the tool will make your experience smoother
    
    **👥 Use Thread Groups Wisely**
    - Thread Groups simulate user activity
    - Start with a small number of threads and gradually increase
    - Avoid overwhelming your system with too many threads at once
    
    **✅ Leverage Assertions**
    - Use assertions to validate responses
    - Ensure your application behaves as expected under load
    - Set up proper assertion types for your test scenarios
    
    **📊 Monitor Resource Usage**
    - Keep an eye on CPU, memory, and network usage during tests
    - Identify potential bottlenecks in your application
    - Use this data to optimize your infrastructure
    
    **👁️ Utilize Listeners**
    - Listeners provide valuable insights into test results
    - Use them to analyze performance metrics
    - Identify issues and performance bottlenecks
    
    **🔢 Parameterize Tests**
    - Use CSV Data Set Config to parameterize your tests
    - Allow for more realistic and varied scenarios
    - Simulate different user inputs and behaviors
    
    **⚡ Run in Non-GUI Mode**
    - For large-scale load tests, execute JMeter from the command line
    - Use non-GUI mode with `-n` and `-t` flags
    - This minimizes resource consumption and provides accurate results
    """)
    
    st.subheader("📋 Example Command for Non-GUI Execution")
    st.code("""
jmeter -n -t my_test.jmx -l results.jtl -e -o ./mytest_report_folder
    """, language="bash")
    
    st.info("""
**Note:** Ensure that 'mytest_report_folder' is empty or doesn't exist yet. 
This command:
- Runs your test plan in non-GUI mode
- Logs results to 'results.jtl'
- Generates an HTML report in the specified folder
    """)


# Release Notes
with st.expander("📢 Release Notes & Version History", expanded=False):
    st.subheader("V1.2.0 (Latest)")
    st.markdown("""
    **Released:** May 7, 2026
    
    **New Features:**
    - ✨ **Browser-Generated HAR Files Support** - Chrome, Firefox, Edge, Safari DevTools
    - ✨ **Domain-Based Social Media Filtering** - Accurate filtering with domain matching (not substring)
    - ✨ **Enhanced GraphQL Detection** - More precise GraphQL operation syntax validation
    
    **Improvements:**
    - 🔧 **Fixed Social Media Filter** - Now checks domain only, not file paths or parameters
    - 🔧 **Better GraphQL Detection** - Distinguishes actual GraphQL operations from REST APIs with 'query' fields
    - 🔧 **Improved Validation** - More accurate entry validation logic
    - 🔧 **User Guidance** - Clear documentation about browser-generated HAR files
    
    **Bug Fixes:**
    - 🐛 Fixed issue where legitimate APIs were filtered due to social media keywords in filenames
    - 🐛 Fixed false-positive GraphQL detection for REST APIs with JSON bodies
    - 🐛 Resolved substring matching issue in social media URL filtering
    - 🐛 Corrected subdomain prefix removal for domain validation
    
    **Limitations & Future Roadmap:**
    - ⚠️ **Fiddler HAR Files** - Not yet supported (planned for v1.3.0)
    - 📋 Currently optimized for browser DevTools HAR format
    - 🗓️ Fiddler support will be added based on community feedback
    """)
    
    st.subheader("V1.1.0")
    st.markdown("""
    **Released:** April 20, 2026
    
    **New Features:**
    - ✨ **Extended HTTP Methods Support** - HEAD, PUT, PATCH, DELETE, OPTIONS, TRACE
    - ✨ **GraphQL Request Support** - Automatic detection and conversion of GraphQL queries and mutations
    - ✨ **Thread Group Name Validation** - Enforces naming convention (SXX_ProjectName_ScenarioName)
    - ✨ **Feedback & Support Page** - Dedicated page for feedback, FAQs, and user support
    - ✨ **Interactive Feature Navigation** - Clickable feature boxes on home page
    - ✨ **Enhanced Documentation** - Updated tips and best practices
    
    **Improvements:**
    - 🔧 Refactored request processing with reusable helper functions
    - 🔧 Better code organization and maintainability
    - 🔧 Improved GraphQL variable extraction and preservation
    - 🔧 Enhanced user guidance and error messages
    - 🔧 Navigation improvements with proper page linking
    
    **Bug Fixes:**
    - 🐛 Improved handling of multiple HTTP methods
    - 🐛 Better query parameter extraction for all methods
    - 🐛 Enhanced GraphQL body parsing
    """)
    st.markdown("""
    **Released:** April 2026
    
    **Features:**
    - ✨ Multi-page application structure
    - ✨ About page with creator information
    - ✨ Comprehensive Tips & Release documentation
    - ✨ Gallery page for visual examples
    - ✨ Enhanced error messages and user guidance
    - 🔧 Better UI/UX with organized pages
    - 🔧 Improved documentation and tutorials
    - 🐛 Enhanced XML sanitization for edge cases
    - 🐛 Better handling of malformed HAR files
    """)
    
    st.subheader("V1.0.1")
    st.markdown("""
    **Features:**
    - Social media URL filtering
    - Debug sampler support
    - Header configuration options
    - Listener configuration options
    - Time-gap based transaction grouping
    """)
    
    st.subheader("V1.0.0 (Initial Release)")
    st.markdown("""
    **Features:**
    - Basic HAR to JMX conversion
    - HTTP request parsing
    - GET and POST method support
    - Header management
    - Query parameter handling
    """)


# Changelog
with st.expander("📝 Changelog", expanded=False):
    st.markdown("""
    **2026-05-07 (V1.2.0) - Latest**
    - Added browser-generated HAR file support (Chrome, Firefox, Edge, Safari)
    - Fixed social media filter to use domain-based matching instead of substring
    - Improved GraphQL detection to validate actual operation syntax
    - Fixed issue where legitimate APIs were filtered due to keywords in filenames
    - Fixed false-positive GraphQL detection for REST APIs with JSON bodies
    - Corrected subdomain prefix removal (www, m, mobile) for accurate domain validation
    - Added roadmap note for Fiddler support in v1.3.0
    - Updated user documentation and guidance
    
    **2026-04-20 (V1.1.0)**
    - Added support for all HTTP methods (HEAD, PUT, PATCH, DELETE, OPTIONS, TRACE)
    - Implemented GraphQL request detection and conversion
    - Added GraphQL body parsing with query, mutation, and variable extraction
    - Implemented thread group name validation with helpful error messages
    - Created dedicated Feedback & Support page
    - Added interactive navigation buttons in feature boxes on home page
    - Refactored request handling with reusable helper functions
    - Enhanced error handling and user guidance
    - Updated documentation with new feature information
    
    **2026-04-14 (V1.0.2)**
    - Added multi-page application structure
    - Created About page with creator bio
    - Created Tips & Release page with expandable sections
    - Added Gallery page framework
    - Enhanced footer with version information
    - Improved UI styling and layout
    - Better error messages and user guidance
    
    **2026-03-15 (V1.0.1)**
    - Added social media URL filtering option
    - Added debug sampler configuration
    - Improved header configuration UI
    - Added listener configuration options
    - Enhanced time-gap transaction grouping logic
    
    **2026-02-01 (V1.0.0)**
    - Initial release of HAR to JMX Converter
    - Core conversion functionality
    - GET and POST request support
    - XML generation and formatting
    - File upload and download functionality
    """)


# Troubleshooting
with st.expander("🆘 Troubleshooting & FAQ", expanded=False):
    st.subheader("Common Issues & Solutions")
    
    with st.container():
        st.markdown("""
        **Q: What types of HAR files are supported?**
        
        A: Currently, only **browser-generated HAR files** are fully supported. These include:
        - Chrome DevTools (Recommended)
        - Firefox DevTools
        - Safari DevTools
        - Edge DevTools
        
        **Upcoming:** Fiddler HAR file support will be added in v1.3.0 release.
        """)
        st.divider()
    
    with st.container():
        st.markdown("""
        **Q: I have a Fiddler HAR file. Can I use it?**
        
        A: Not yet. Currently, the converter is optimized for browser-generated HAR files only. 
        Fiddler HAR file support is planned for a future release (v1.3.0).
        
        **Workaround:** You can export your Fiddler capture as HAR and test it, but results may vary.
        We recommend using Chrome/Firefox DevTools for now to ensure best results.
        """)
        st.divider()
    
    with st.container():
        st.markdown("""
        **Q: I uploaded a HAR file but got an error about invalid format.**
        
        A: Ensure your file is a valid JSON file from a supported browser. HAR files are JSON-based. 
        The file might be corrupted, incomplete, or from an unsupported tool. 
        Try recording a fresh HAR file using Chrome/Firefox DevTools.
        """)
        st.divider()
    
    with st.container():
        st.markdown("""
        **Q: The converter says "No valid HTTP requests found".**
        
        A: Your HAR file may contain only incomplete entries or skeleton requests. 
        The converter filters out invalid entries automatically. 
        Try recording a more complete user session.
        """)
        st.divider()
    
    with st.container():
        st.markdown("""
        **Q: JMeter won't open my generated JMX file.**
        
        A: Check your JMeter version (should be 5.6.3 or higher). 
        If you're using an older version, upgrade and try again.
        """)
        st.divider()
    
    with st.container():
        st.markdown("""
        **Q: Can I edit the generated JMX file after conversion?**
        
        A: Yes! JMX files are XML-based. You can edit them in JMeter's GUI or with any text editor.
        The converter provides a solid foundation that you can further customize.
        """)
        st.divider()
    
    with st.container():
        st.markdown("""
        **Q: Are my uploaded files stored on the server?**
        
        A: No. All files are processed instantly in memory and not stored. 
        Your privacy is important to us.
        """)
        st.divider()
    
    with st.container():
        st.markdown("""
        **Q: What types of requests and HTTP methods does the converter support?**
        
        A: All HTTP methods are supported:
        - GET, HEAD, POST, PUT, PATCH, DELETE
        - OPTIONS, TRACE
        - GraphQL (automatic detection)
        
        The converter properly handles query parameters, request bodies, and headers for all methods.
        """)


st.divider()

st.subheader("❓ Frequently Asked Questions")

with st.expander("💾 How is my data handled?", expanded=False):
    st.markdown("""
    **We prioritize your privacy and security:**
    
    - All HAR files are processed **instantly** on our servers
    - Your files are **NOT stored** or saved in any database
    - Files are deleted immediately after conversion
    - No data is collected or tracked
    - Your information stays completely private
    """)

with st.expander("🔧 What versions of JMeter are supported?", expanded=False):
    st.markdown("""
    **Recommended Version: JMeter 5.6.3**
    
    The converter is optimized for JMeter 5.6.3 and generates JMX files fully compatible with this version.
    
    **Compatibility:**
    - ✅ JMeter 5.6.3 (Full support)
    - ✅ JMeter 5.5.x (Good compatibility)
    - ⚠️ JMeter 5.0 - 5.4 (May work with minor issues)
    - ❌ JMeter 4.x and older (Not recommended)
    
    For best results, use JMeter 5.6.3 or newer.
    """)

with st.expander("📁 What file formats are supported?", expanded=False):
    st.markdown("""
    **Supported Input Formats:**
    - ✅ **HAR (HTTP Archive)** - JSON-based format
    - ✅ Files recorded from browsers (Chrome, Firefox, Safari, Edge)
    - ✅ Files from tools like Postman, Insomnia
    
    **Output Format:**
    - ✅ **JMX (JMeter Test Plan)** - XML format ready for JMeter
    
    **Requirements:**
    - File must be a valid JSON file
    - Must have proper HAR structure with log entries
    - Each entry should have request information
    """)

with st.expander("⚡ What HTTP methods are supported?", expanded=False):
    st.markdown("""
    **All HTTP Methods Supported:**
    
    - ✅ **GET** - Query parameters automatically extracted
    - ✅ **HEAD** - Similar to GET with header support
    - ✅ **POST** - Form parameters and JSON body support
    - ✅ **PUT** - Full request body handling
    - ✅ **PATCH** - Partial update support
    - ✅ **DELETE** - With query parameters
    - ✅ **OPTIONS** - Pre-flight request support
    - ✅ **TRACE** - Request tracing support
    - ✅ **GraphQL** - Automatic detection and conversion
    
    Each method's parameters and headers are properly preserved.
    """)

with st.expander("🐛 I found a bug. How do I report it?", expanded=False):
    st.markdown("""
    **To Report a Bug:**
    
    1. **Describe the Issue** - Clear description of what went wrong
    2. **Steps to Reproduce** - How to recreate the problem
    3. **Expected Behavior** - What should have happened
    4. **Actual Behavior** - What actually happened
    5. **Environment** - Your OS, browser, and JMeter version
    6. **HAR File (Optional)** - Share the file if possible (without sensitive data)
    
    Please send bug reports with as much detail as possible to help us fix it quickly.
    
    **Report:** [Submit your Feedback](https://forms.gle/Scwrdrcax5PGjLbWA).
    """)
    

with st.expander("🚀 What features are planned for the future?", expanded=False):
    st.markdown("""
    **Upcoming Features (Roadmap):**
    
    - ✅ v1.2.0 (Current) - Browser-generated HAR files, improved filtering, better validation
    - 📋 v1.3.0 - **Fiddler HAR file support** (high priority)
    - 🔄 v1.4.0 - Request/Response correlation support
    - 📊 v1.5.0 - Enhanced performance metrics and reporting
    - 🔐 v1.6.0+ - Advanced authentication handling
    - 🎯 Future - Custom extraction and variable creation
    - 📝 Future - Parameter handling improvements
    - 🔔 Future - Real-time validation and suggestions
    - 🌐 Future - Web UI improvements and redesign
    - 📱 Future - Mobile app version
    
    We're continuously improving based on user feedback!
    """)

with st.expander("💪 How can I contribute or suggest features?", expanded=False):
    st.markdown("""
    **Ways to Contribute:**
    
    1. **Feature Suggestions** - Share your ideas for new features
    2. **Bug Reports** - Help us identify and fix issues
    3. **Documentation** - Help improve our guides and tutorials
    4. **Testing** - Test new versions and provide feedback
    5. **Sharing** - Tell others about this tool
    
    We value all contributions and feedback from our users. 
    Please feel free to reach out with any ideas!
    """)





st.divider()

add_footer()
