import streamlit as st
from utils import add_footer

st.set_page_config(page_title="About - HAR to JMX Converter", page_icon="ℹ️", layout="centered")

st.title("ℹ️ About Me")

# col1, col2 = st.columns([2,1])

# with col1:
st.subheader("👋 Hello, I'm Muthuvinayagam!")
    
st.write("""
I am Muthu Vinayagam and working as a Software Performance Engineer in a Tech company. I am also an avid learner developing my skills for my work which I love. I am passionate about building and creating products with a own interest and self-motivation. \n\n
This HAR to JMX Converter is one such initiative born out of a desire to simplify the JMeter script development purpose. \n\n
I have developed small gaming app, music app, fitness app and rocerylist app and I used to travel a lot and exploring ancient temple, enjoy food and tea for sure wherever I go. I am enjoying my run, cycle, workout as well as yoga.

    """)

st.divider()

# st.subheader("🎯 My Passion & Mission")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     ### 💡 **Innovation**
#     Thinking about new products and exploring innovative solutions that solve real-world problems.
#     """)

# with col2:
#     st.markdown("""
#     ### 🏃 **Explorer**
#     An avid learner constantly exploring new technologies, tools, and methodologies to stay ahead in the tech world.
#     """)

# with col3:
#     st.markdown("""
#     ### 🛠️ **Builder**
#     Passionate about developing applications that are truly useful and make life easier for others.
#     """)

# st.divider()

st.subheader("📚 What Drives Me")

st.write("""
- **User-Centric Design:** Building tools that solve real problems for users
- **Continuous Learning:** Staying curious and exploring emerging technologies
- **Quality & Excellence:** Striving for high-quality, maintainable, and scalable solutions
- **Community Impact:** Creating open-source tools that benefit the broader community
""")

st.divider()

st.subheader("🚀 This Project: HAR to JMX Converter")

st.write("""
This converter was created to address a pain point I experienced: manually converting HTTP Archive (HAR) files 
to JMeter test plans is time-consuming and error-prone. 

By automating this process, I aimed to:
- ⏱️ **Save time** for testers and developers
- 🎯 **Reduce errors** in script generation
- 🔧 **Provide flexibility** with customizable configurations
- 📈 **Enable better load testing** practices

The tool is evolving continuously based on feedback and new feature requests!
""")

st.divider()

st.subheader("🤝 Let's Connect")

st.write("""
**I appreciate your feedback and suggestions!** 

If you find this tool helpful or have ideas for improvements, please use the Feedback form or reach out.

- 🔗 Check out the **Tips & Release** page for more information
- 📊 Visit the **Gallery** to see examples
- 🔄 Explore the **Converter** to experience it yourself

Thank you for using the HAR to JMX Converter! 🙏
""")

add_footer()
