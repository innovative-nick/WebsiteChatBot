import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import time

# Configure Gemini Pro API
genai.configure(api_key="AIzaSyDnLRWR5q1Wdcdj1PmZXqKhuypwsrsKGb8")

# Web scraping function
def get_website_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        paragraphs = soup.find_all('p')
        lists = soup.find_all(['ul', 'ol'])
        
        content = '\n'.join([heading.get_text() for heading in headings])
        content += '\n'.join([para.get_text() for para in paragraphs])
        content += '\n'.join([li.get_text() for list_tag in lists for li in list_tag.find_all('li')])
        
        return content.strip() if content.strip() else None
    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

# Initialize chatbot
def initialize_chat(content):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.start_chat(history=[{"role": "model", "parts": [content]}])
    except Exception as e:
        return None, f"Chatbot initialization failed: {e}"

# Streamlit UI
st.set_page_config(page_title="AI Chatbot for Website", page_icon="💬")
st.sidebar.title("Website Chatbot")
st.sidebar.markdown("Enter a website URL to fetch content and chat about it.")

# User input for URL
url = st.sidebar.text_input("Enter Website URL", "https://madueke-portfolio.web.app")

if st.sidebar.button("Fetch Content"):
    with st.spinner("Fetching website content..."):
        content = get_website_content(url)
        if content and not content.startswith("Network error"):
            st.session_state["content"] = content
            st.success("Content successfully retrieved!")
        else:
            st.error(f"Failed to retrieve content: {content}")

# Chatbot section
if "content" in st.session_state:
    st.write("### Ask a question about the website content:")
    user_input = st.text_input("Your question:")
    
    if user_input:
        response_placeholder = st.empty()
        with response_placeholder:
            st.write("🤖 Typing...")
        time.sleep(2)
        
        chat = initialize_chat(st.session_state["content"])
        if chat:
            try:
                response = chat.send_message(user_input)
                response_placeholder.write(f"**🤖 AI Response:** {response.text}")
            except Exception as e:
                response_placeholder.write(f"Error during chatbot interaction: {e}")
        else:
            response_placeholder.write("Chatbot initialization failed.")
