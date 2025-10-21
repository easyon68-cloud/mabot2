
import streamlit as st
from openai import OpenAI
import re

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🛠️ Network and Server Troubleshoot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are a professional AI assistant specialized in network and server troubleshooting. "
                "Your role is to help users diagnose common issues related to connectivity, server performance, configuration errors, and system logs. "
                "You must clearly state that you are not a certified technician and do not provide emergency IT support. "
                "If a user asks about anything unrelated to IT troubleshooting, reply: "
                "'I'm here to help with network and server troubleshooting. Please ask about connectivity issues, server errors, or system configurations.' "
                "If a user describes critical infrastructure failure or data breach, respond: "
                "'This may indicate a serious issue. Please contact your IT department or cybersecurity team immediately.'"
            )
        }
    ]

# Display previous messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# File upload and log analysis
uploaded_file = st.file_uploader("📁 Upload a log file for automated analysis", type=["txt", "log", "csv"])

def analyze_log(content):
    lines = content.splitlines()
    summary = {
        "SSH Logins": [],
        "Cron Jobs": [],
        "Network Events": [],
        "HTTP Access": [],
        "HTTP Errors": [],
        "Connection Failures": [],
        "Database Issues": [],
        "Unhandled Exceptions": []
    }

    for line in lines:
        if "ssh" in line.lower() and "accepted" in line.lower():
            summary["SSH Logins"].append(line)
        if "cron" in line.lower() and ("executed" in line.lower() or "job" in line.lower()):
            summary["Cron Jobs"].append(line)
        if "eth0" in line.lower() or "network" in line.lower():
            summary["Network Events"].append(line)
        if re.search(r"GET|POST", line) and re.search(r"HTTP/\d\.\d", line):
            summary["HTTP Access"].append(line)
        if re.search(r"403|500|404", line):
            summary["HTTP Errors"].append(line)
        if "connection refused" in line.lower() or "upstream" in line.lower():
            summary["Connection Failures"].append(line)
        if "database" in line.lower() and ("fail" in line.lower() or "timeout" in line.lower()):
            summary["Database Issues"].append(line)
        if "exception" in line.lower() or "keyerror" in line.lower():
            summary["Unhandled Exceptions"].append(line)

    return summary

if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8")
    st.text_area("📄 Log File Content", file_content, height=200)

    summary = analyze_log(file_content)
    st.subheader("🔍 Automated Log Analysis Summary")

    for category, events in summary.items():
        st.markdown(f"**{category}**: {len(events)} event(s)")
        for event in events:
            st.markdown(f"- {event}")

# Chat input
user_input = st.chat_input("Describe your network or server issue...")

def get_response(messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = get_response(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Footer disclaimer
st.markdown("---")
st.markdown(
    "⚠️ **Disclaimer:** This chatbot does not provide certified IT support or emergency services. "
    "Always consult your IT administrator or support team for critical infrastructure issues.",
    unsafe_allow_html=True
)
