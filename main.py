import streamlit as st
import base64
import PyPDF2
import json
import docx
import ollama
import pandas as pd
import io
from zipfile import ZipFile
import re
import google.generativeai as genai

import key_page
import login_page
import web_app


if "key_verified" not in st.session_state:
    st.session_state["key_verified"] = False
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "web_app" not in st.session_state:
    st.session_state["web_app"] = False

if not st.session_state["key_verified"]:
    key_page.key_entry_page()
elif not st.session_state["authenticated"]:
    login_page.login_page()
elif not st.session_state["web_app"]:
    web_app.app_page()