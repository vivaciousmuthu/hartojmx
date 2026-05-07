import streamlit as st
from utils import add_footer

st.set_page_config(page_title="About - HAR to JMX Converter", page_icon="ℹ️", layout="centered")

st.title("ℹ️ About Me")

# col1, col2 = st.columns([2,1])

# with col1:
st.subheader("👋 Hello, I'm Muthuvinayagam!")
    
st.write("""
I am Muthu Vinayagam, a Software Performance Engineer with experience in the tech industry. I am an enthusiastic learner who continuously works on improving my skills because I genuinely enjoy what I do. I am passionate about building products driven by curiosity, self-motivation, and personal interest. \n\n
In November 2025, I was laid off as part of a company restructuring decision made for business growth. While it was a challenging phase, I chose to view it as an opportunity rather than a setback. I stayed motivated and focused on transforming my ideas into meaningful products that could help others. \n\n
One of my first initiatives was developing a JMeter script conversion tool for performance testers. The HAR to JMX Converter was created with the goal of simplifying JMeter script development and making the process more efficient for testing professionals. This project reflects my determination to reinvent myself during a difficult period and continue creating value through technology. \n\n
Apart from this, I have also developed small applications including gaming, music, fitness, and grocery list apps. I love traveling and exploring ancient temples, and I never miss the chance to enjoy good food and tea wherever I go. \n\n
Outside of work, I actively enjoy running, cycling, workouts, and yoga, which help me maintain both physical and mental balance.

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
