import streamlit as st
# streamlit: web based app making
# lite python framework

st.title("AI RESUME MAKER")
st.markdown("""# user can createor 
download AI created resume based on high ATS
SCORE""")



#===============AGENT CODE====================
# Step 2: Load modules
import os
import time
import langchain
import base64
from io import BytesIO
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader


#===================API KEY LOAD================================

GOOGLE_API_KEY=st.sidebar.text_input("GOOGLE_API_KEY",type = "password")
GROQ_API_KEY=st.sidebar.text_input("GROQ_API_KEY",type = "password")
TAVILY_API_KEY=st.sidebar.text_input("TAVILY_API_KEY",type = "password")

if not (GOOGLE_API_KEY) and not(GROQ_API_KEY) and not (TAVILY_API_KEY):
    st.sidebar.warning("PASS API KEY")
    st.stop()
else:
    st.success("API KEYS LOADED")


#==============MODEL BUILDING==================
model = ChatGoogleGenerativeAI(
    model = 'gemini-3.5-flash-lite',
    google_api_key = GOOGLE_API_KEY
)

#TOOL
def search_recent_news_jobs(query):
  """this function helps to search
  recent news or recent jobs
  related to given search query
  suppose user write python developer jobs
  it should return trending news and jobs links"""
  client = TavilyClient(
      api_key = TAVILY_API_KEY
  )
  return client.search(query)



# agent creation
from langchain.agents import create_agent

agent = create_agent(
    model = model,
    tools = [search_recent_news_jobs]
)


#=======PROMPT GENERATOR===============

def prompt_generator(agent = agent):
  """  This function help to givedetailed prompt
  followed by chain of thoughts and
  persona based prompting, main task is to give
  detailed prompt to build resume for
  students or experienced person
  based on the given personal information."""

  prompt = """You are senior HR resume analyzer,
  main task is to give
  detailed prompt to build resume for
  students or experienced person
  based on the given personal information.
  System instruction i want model to genarate resume
  in HTML format, include thatin prompt"""

  response = agent.invoke(prompt)
  file_name = 'prompt.py'
  with open(file_name,'w') as f:
    f.write(response.content[-1]['text'])
  return 'prompt file generated successfully,agent can read it!'

prompt_generator(model)
# tool 2:
def resumemaker_prompt():
  """this function just gives
  updated prompt fro model"""

  with open('prompt.py','r') as f:
    prompt = f.read()
  return prompt
resumemaker_prompt()

#===============UPLOAD IMAGE======================
uploaded_file = st.sidebar.file_uploader(
    "choose an image file",
    type=["jpg", "jpeg", "png", "webp"]
)
if uploaded_file is not None:
    try:
        from PIL import Image
        image = Image.open(uploaded_file)

        st.sidebar.image(image, caption="Uploaded Image", use_container_width=True)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        base_name = os.path.splitext(uploaded_file.name)[0]
        save_path = f"{base_name}.jpg"

        # 3. Save the image to the current working directory
        image.save(save_path, "JPEG")
        st.sidebar.success(f"🎉 Image successfully saved as'{save_path}'!")

    except Exception as e:
        st.error(f" Eror processing image:{e}")
        



#===============GENERATE RESUME==================
prompt = """ you are a helpful ai assistant
with job resume maker, your task is to give
HTML format resume,with proper designing using recent CSS  and JS
code, with professional design format.
user will upload data and return html format resume
ALWAYS USE DIFFERENT STYLING and designs"""

final = prompt + resumemaker_prompt()

user_info = st.text_input("Enter your information")

user_details = """user details: given below:
Reumse info: {user_info}
Photo: {uploaded_file}
Photo present in current directory with name as
uploaded_file, and once resume generated give
download button in same html code.
Dafault if not given: Give Python Developer REsume"
name: Gunpreet,
age:19,
profession :graphic designer,
education : 2012-2025 jmj sr. sec school 2026-present iitm,
gmail: gunpreet016@gmail.com,
contact: 9687814949,
SKILLS: CANVA PRO,
Layout and Grid Design,
Typography Mastery,
Software Proficiency,
Visual Communication, and Creative Problem-Solving.
"""

query = final + user_details

if st.button("Generate Resume"):
  with st.spinner("Running Agent......"):
    
    response = agent.invoke({'messages':[{'role':'user','content':query}]})
    code = response['messages'][-1].content[-1]['text']

    #st.markdown(code)
    st.html(code, width="stretch", unsafe_allow_javascript=True)
