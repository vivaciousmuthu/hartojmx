import streamlit as st
import json
from datetime import datetime
import os
from fileconvert import har_to_jmx, validate_thread_group_name
from utils import add_footer

st.set_page_config(page_title="HAR to JMX Converter - Converter", page_icon="🔄", layout="centered")

st.title("🔄 HAR to JMX Converter")
st.write("""
Upload a **browser generated** **.har** file to generate a standardized **.jmx (JMeter)** file 🚀🎯😊. 
After conversion, you can proceed with further script enhancements. 

**Note:** Please upload only one file at a time. We do not store any uploaded files on our server. 
Simply upload and export instantly.

**Browser Support:** Chrome, Firefox, Edge, and Safari browsers are supported for HAR file generation.
**Upcoming:** Fiddler HAR file support will be added in future releases.
""")
st.write("This tool is designed to save you time! I hope you find it helpful. Please feel free to reach out if you have any issues or suggestions.")

uploaded_file = st.file_uploader("Choose a recorded HAR file", type="har")

st.subheader("⏱️ Transaction Controller Grouped by Time Gap")
time_gap = st.slider("Time Gap Threshold (seconds)", min_value=1, max_value=15, value=5)

st.subheader("📋 Script Configuration")
thread_group_name = st.text_input(
    "Thread Group Name", 
    value="S01_ProjectName_Scenario_Name", 
    help="Enter script name in CamelCase format: S01_Petstore_API_FindbyStatus or S02_ECommerce_Checkout_Flow", 
    placeholder="S01_ProjectName_Scenario_Name"
)

st.subheader("⚙️ Optional Configuration Toggles")
col1, col2 = st.columns(2)

with col1:
    include_headers = st.toggle("Header Configuration (Cache, Cookie, Request Defaults)", value=False)
    include_listeners = st.toggle("Listeners Configuration (Results Tree, Summary, Aggregate)", value=False)

with col2:
    include_sampler = st.toggle("Sampler Configuration (Debug Sampler)", value=False)
    exclude_social_media = st.toggle("Exclude Social Media URLs", value=False)

if st.button("🚀 Convert to JMX", use_container_width=True):
    # First check: Validate if HAR file is uploaded
    if uploaded_file is None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.error("📤 Please upload a HAR file first before proceeding with conversion!")
        with col2:
            if st.button("Reset", key="reset_button_upload"):
                st.rerun()
    else:
        # Second check: Validate thread group name format
        is_valid, validation_message = validate_thread_group_name(thread_group_name)
        
        if not is_valid:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.error(validation_message)
            with col2:
                if st.button("Reset", key="reset_button_validation"):
                    st.rerun()
        else:
            try:
                with st.spinner("Converting..."):
                    har_content = json.load(uploaded_file)
                    jmx_content = har_to_jmx(
                        har_content,
                        time_gap_threshold=time_gap,
                        include_headers=include_headers,
                        include_listeners=include_listeners,
                        include_sampler=include_sampler,
                        script_name=thread_group_name,
                        exclude_social_media=exclude_social_media
                    )
                    original_name = os.path.splitext(uploaded_file.name)[0]
                    output_filename = f"{original_name}_Converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jmx"

                    st.download_button(
                        label="📥 Download JMX File",
                        data=jmx_content,
                        file_name=output_filename,
                        mime="application/xml",
                        use_container_width=True
                    )

                    st.success(f"✅ Conversion Completed! Click the button above to download your file.\n\n**{output_filename}**")
                    
            except json.JSONDecodeError as e:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.error(f"❌ Invalid HAR file format. Please ensure the file is a valid JSON file. Error: {str(e)}")
                with col2:
                    if st.button("Reset", key="reset_button_json"):
                        st.rerun()
                        
            except ValueError as e:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.error(f"""
❌ {str(e)}

**Tip:** The HAR file may have many incomplete or empty entries. Valid entries are being filtered automatically, 
but this file doesn't contain enough valid requests to convert.
                    """)
                with col2:
                    if st.button("Reset", key="reset_button_value"):
                        st.rerun()
                        
            except Exception as e:
                col1, col2 = st.columns([3, 1])
                with col1:
                    error_msg = str(e)
                    if "not well-formed" in error_msg or "invalid token" in error_msg:
                        st.error(f"""
❌ XML Parsing Error: The HAR file contains invalid characters or malformed data.

**Details:** {error_msg}

**Solution:** The converter automatically filters invalid entries and sanitizes data. 
If this error persists, the HAR file may be corrupted. Try recording a fresh HAR file.
                        """)
                    else:
                        st.error(f"""
❌ Conversion Error: {error_msg}

**Tip:** This might be due to unsupported data in the HAR file. 
The converter has skipped invalid entries and will use valid ones.
                        """)
                with col2:
                    if st.button("Reset", key="reset_button_conversion"):
                        st.rerun()

add_footer()
