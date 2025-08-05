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
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image("DhurinLogo.png")

st.markdown(
    f"""
    <style>
        .logo-container {{
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 100;
        }}
    </style>
    <div class="logo-container">
        <img src="data:image/png;base64,{img_base64}" width="100">
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.image("DhurinLogo.png", width = 50)

st.title("Profile Matcher")

def app_page():
    ################################################   Session State   ################################################

    if 'jd_uploaded_names' not in st.session_state:
        st.session_state.jd_uploaded_names = {}
    if 'cv_uploaded_names' not in st.session_state:
        st.session_state.cv_uploaded_names = {}
        
    if 'jd_uploaded_texts' not in st.session_state:
        st.session_state.jd_uploaded_texts = {}
    if 'cv_uploaded_texts' not in st.session_state:
        st.session_state.cv_uploaded_texts = {}
    
    if 'progress_text' not in st.session_state:
        st.session_state.progress_text = ""
    
    if 'genai_model_name' not in st.session_state:
        st.session_state.genai_model_name = "Gemini"
    if 'genAi_APIKey' not in st.session_state:
        st.session_state.genAi_APIKey = "AIzaSyBVkAYNxv3xtseGJqKrz8c8sbi9AJ9cH6k"
        
    if 'log_error_cv_file_name' not in st.session_state:
        st.session_state.log_error_cv_file_name = []
    if 'log_error_jd_file_name' not in st.session_state:
        st.session_state.log_error_jd_file_name = []
    if 'log_file' not in st.session_state:
        st.session_state.log_file = []
    if 'log_counter' not in st.session_state:
        st.session_state.log_counter = 1
        
    def process(jd_name, cv_name, jd_text, cv_text):
        content = f"""
        Given a resume and Job description(JD), I want to find the key requirements of the JD and know if the resume is fit for that work.
        Analyze the Requirements from JD, what it requires like data scientist or data engineering or analytics or web development, etc as well as the tech stacks.
        Analyze the resume and find the tech stacks that he/she has worked on as well as the role of projects done by he/she.
    
        After analyzing, I want you to find a matching percentage, focusing more on tech stacks.
    
        Also, do not give information which is not present in the Resume or JD, simply fill null or NA.
    
        Job Description: {jd_text}
    
        Resume: {cv_text}
        """ + """
        I want you to fill and return only the below json format.
        {
            "Name": ,
            "PhoneNumber": ,
            "EmailID": ,
            "Location": ,
            "Matching_percent": ,
            "Keywords_in_JD": [],
            "Keywords_in_Resume": [],
            "Keywords_matching_with_JD": [],
            "Keywords_missing_in_Resume": []
        }
        """
    
        try:
            if st.session_state.genai_model_name  == "Gemini":
                genai.configure(api_key=st.session_state.genAi_APIKey)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(content)
                return response.text
            else:
                response = ollama.chat(
                    model = st.session_state.genai_model_name,
                    messages = [{'role': 'user', 'content': content}],
                    options = {"temperature": 0.1, "top_p": 0.8, "top_k": 40, "repeat_penalty": 1.1}
                )
                return response['message']['content']
        except Exception as e:
            st.session_state.log_file.append([st.session_state.log_counter,f"While calling Model: {jd_name} -> {cv_name}", str(e)])
            st.session_state.log_counter += 1
            st.session_state.log_error_cv_file_name.append(cv_name)
    
    ####### Extract JD pdf to text using pyPdf ##########
    
    def extraction_jd():
        if st.session_state.jd_uploaded_names:
            for jd_file, file_obj in st.session_state.jd_uploaded_names.items():
                try:
                    file_type = jd_file.split('.')[-1].lower()
    
                    if file_type == "pdf":
                        reader = PyPDF2.PdfReader(file_obj)
                        st.session_state.jd_uploaded_texts[jd_file] = "".join(
                            [page.extract_text() or "" for page in reader.pages]
                        )
    
                    elif file_type == "docx":
                        doc = docx.Document(file_obj)
                        st.session_state.jd_uploaded_texts[jd_file] = "\n".join(
                            [para.text for para in doc.paragraphs]
                        )
    
                    elif file_type == "txt":
                        file_obj.seek(0)
                        st.session_state.jd_uploaded_texts[jd_file] = file_obj.read().decode("utf-8")
    
                    else:
                        st.session_state.jd_uploaded_texts[jd_file] = ""
                        st.session_state.log_file.append([f"Unsupported JD file type: {jd_file}", ""])
                        st.session_state.log_error_jd_file_name.append(jd_file)
                        
                except Exception as e:
                    st.session_state.log_file.append([st.session_state.log_counter, f"While extracting Job Description: {jd_file}", str(e)])
                    st.session_state.log_counter += 1
                    st.session_state.log_error_jd_file_name.append(jd_file)
                    continue
    
    
    ####### Extract CV pdf to text using pyPdf ##########
    
    def extraction_cv():
        if st.session_state.cv_uploaded_names:
            for cv_file, file_obj in st.session_state.cv_uploaded_names.items():
                try:
                    file_type = cv_file.split('.')[-1].lower()
    
                    if file_type == "pdf":
                        reader = PyPDF2.PdfReader(file_obj)
                        st.session_state.cv_uploaded_texts[cv_file] = "".join(
                            [page.extract_text() or "" for page in reader.pages]
                        )
    
                    elif file_type == "docx":
                        doc = docx.Document(file_obj)
                        st.session_state.cv_uploaded_texts[cv_file] = "\n".join(
                            [para.text for para in doc.paragraphs]
                        )
    
                    elif file_type == "txt":
                        file_obj.seek(0)
                        st.session_state.cv_uploaded_texts[cv_file] = file_obj.read().decode("utf-8")
    
                    else:
                        st.session_state.cv_uploaded_texts[cv_file] = ""
                        st.session_state.log_file.append([f"Unsupported CV file type: {cv_file}", ""])
                        st.session_state.log_error_cv_file_name.append(cv_file)
    
                except Exception as e:
                    st.session_state.log_file.append([st.session_state.log_counter, f"While extracting Resume: {cv_file}", str(e)])
                    st.session_state.log_counter += 1
                    st.session_state.log_error_cv_file_name.append(cv_file)
                    continue
    
    
    ####### Extract Json from Model output ##########
    
    def extract_json_return_df(jd_name, cv_name, text):
        try:
            # Use regex to safely find the first JSON block
            json_match = re.search(r'\{.*?\}', text, re.DOTALL)
    
            if not json_match:
                st.session_state.log_file.append([st.session_state.log_counter, f"While Extracting JSON, {jd_name} -> {cv_name}", "No JSON block found in text"])
                st.session_state.log_counter += 1
                st.session_state.log_error_cv_file_name.append(cv_name)
                st.session_state.log_error_jd_file_name.append(jd_name)
                return None
    
            json_str = json_match.group(0).replace("NA", '"NA"')
    
            try:
                json_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                st.session_state.log_file.append([st.session_state.log_counter, f"While Extracting JSON, {jd_name} -> {cv_name}", f"JSON Decode Error: {e}"])
                st.session_state.log_counter += 1
                st.session_state.log_error_cv_file_name.append(cv_name)
                st.session_state.log_error_jd_file_name.append(jd_name)
                return None
    
            flat_data = {
                "JD_File_Name": jd_name,
                "Resume_File_Name": cv_name,
                "Name": json_data.get("Name", ""),
                "PhoneNumber": json_data.get("PhoneNumber", ""),
                "EmailID": json_data.get("EmailID", ""),
                "Location": json_data.get("Location", ""),
                "Matching_percent": json_data.get("Matching_percent", ""),
                "Keywords_in_JD": ", ".join(json_data.get("Keywords_in_JD", [])),
                "Keywords_in_Resume": ", ".join(json_data.get("Keywords_in_Resume", [])),
                "Keywords_matching_with_JD": ", ".join(json_data.get("Keywords_matching_with_JD", [])),
                "Keywords_missing_in_Resume": ", ".join(json_data.get("Keywords_missing_in_Resume", [])),
            }
    
            return pd.DataFrame([flat_data])
    
        except Exception as e:
            st.session_state.log_file.append([st.session_state.log_counter, f"While Extracting JSON, {jd_name} -> {cv_name}", f"Unexpected Error: {e}"])
            st.session_state.log_counter += 1
            st.session_state.log_error_cv_file_name.append(cv_name)
            st.session_state.log_error_jd_file_name.append(jd_name)
            return None
    
    
    ################################################   TABS   ################################################
    
    home, upload, view, process_tab, log_tab = st.tabs(["HOME", "UPLOAD", "VIEW", "PROCESS", "LOG"])
    log = []
    
    
    ################################################   HOME TAB   ################################################
    
    with home:
        st.subheader("Welcome to the Resume Matcher App! \U0001F3AF")
        st.markdown("""
        This web application helps you **match resumes with job descriptions** by analyzing content and highlighting relevant skills and keywords.
    
        ### \U0001F9ED Navigation Overview:
        There are five main sections in this app:
        1. **Home** – You're here! An overview of the app and its features.
        2. **Upload** – Upload your **Job Description** and **Resume** (PDF only).
        3. **View** – Preview the uploaded documents before processing.
        4. **Process** – Run the matching logic and view the results.
        5. **Log** – Review error logs, if any, for debugging and transparency.
    
        \U0001F4CC **Note:** Currently, we support **PDF files only**. Support for additional formats and new features will be added in future updates. Stay tuned! ☺
        """)
    
    
    ################################################   UPLOAD TAB   ################################################
    
    with upload:
        try:
            jd_files = st.file_uploader("Upload Job Description", type=["pdf", "txt", "docx"], accept_multiple_files=True, key="jd_uploader")
            if jd_files:
                new_jds = []
                for file in jd_files:
                    if file.name not in st.session_state.jd_uploaded_names:
                        st.session_state.jd_uploaded_names[file.name] = file
                        new_jds.append(file.name)
                if new_jds:
                    for name in new_jds:
                        st.toast(f"✅ Job Description '{name}' uploaded successfully!")
        except Exception as e:
            st.session_state.log_file.append([st.session_state.log_counter, "Error uploading Job Descriptions", str(e)])
            st.session_state.log_counter += 1
            
        # Resume uploader
        try:
            cv_files = st.file_uploader("Upload Resume", type=["pdf", "txt", "docx"], accept_multiple_files=True, key="cv_uploader")
            if cv_files:
                new_cvs = []
                for file in cv_files:
                    if file.name not in st.session_state.cv_uploaded_names:
                        st.session_state.cv_uploaded_names[file.name] = file
                        new_cvs.append(file.name)
                if new_cvs:
                    for name in new_cvs:
                        st.toast(f"✅ Resume '{name}' uploaded successfully!")
        except Exception as e:
            st.session_state.log_file.append([st.session_state.log_counter, "Error uploading Resumes", str(e)])
            st.session_state.log_counter += 1
            
    
    ################################################   VIEW TAB   ################################################
    
    with view:
        view_options = []
    
        if st.session_state.jd_uploaded_names:
            for jd_file in st.session_state.jd_uploaded_names:
                view_options.append(f"Job Description: {jd_file}")
    
        if st.session_state.cv_uploaded_names:
            for cv_file in st.session_state.cv_uploaded_names:
                view_options.append(f"Resume: {cv_file}")
    
        if not view_options:
            st.info("No files uploaded.")
        else:
            selected = st.selectbox("Select a document to view", view_options, index=0)
    
            def display_pdf(file_obj):
                file_obj.seek(0)
                base64_pdf = base64.b64encode(file_obj.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
    
            if selected.startswith("Job Description: "):
                filename = selected.replace("Job Description: ", "")
                file_obj = st.session_state.jd_uploaded_names.get(filename)
            elif selected.startswith("Resume: "):
                filename = selected.replace("Resume: ", "")
                file_obj = st.session_state.cv_uploaded_names.get(filename)
            else:
                file_obj = None
    
            if file_obj and file_obj.name.lower().endswith(".pdf"):
                display_pdf(file_obj)
            else:
                st.info("PDF preview is only supported for PDF files.")
    
    
    ################################################   SIDEBAR   ################################################
    
    # model_names = st.sidebar.radio(
    #     "Choose the Model",
    #     ["llama3.2", "gemma3", "deepseek-r1", "Gemini"],
    #     captions=[
    #         "3b Model",
    #         "4b Model",
    #         "7b Model",
    #         "gemini-1.5-flash-latest",
    #     ],
    # )
    # if model_names == "llama3.2":
    #     st.session_state.genai_model_name = "llama3.2:3b"
    # elif model_names == "deepseek-r1":
    #     st.session_state.genai_model_name = "deepseek-r1:7b"
    # elif model_names == "gemma3":
    #     st.session_state.genai_model_name = "gemma3:4b"
    # elif model_names == "Gemini":
        # st.sidebar.warning("Note: Gemini is a paid service")
    
    st.session_state.genai_model_name = "Gemini"
    
    st.sidebar.markdown(f"Selected Model: {st.session_state.genai_model_name}")
    
    selected_jd = None
    selected_resume = None
    if st.session_state.jd_uploaded_names:
        selected_jd = st.sidebar.multiselect("Select Job Descriptions", list(st.session_state.jd_uploaded_names.keys()), placeholder="All Resume are selected")
    if st.session_state.cv_uploaded_names:
        selected_resume = st.sidebar.multiselect("Select Resumes", list(st.session_state.cv_uploaded_names.keys()), placeholder="All Resume are selected")
    
    if selected_jd:
            st.sidebar.markdown(f"You have selected: {selected_jd}")
    if selected_resume:
            st.sidebar.markdown(f"You have selected: {selected_resume}")
    
    
    ################################################   PROCESS TAB   ################################################
        
    with process_tab:
        extraction_jd()
        extraction_cv()
        
        col1, col2 = st.columns(2)
        with col1:
            run_button = st.button("▶️ Run Processing")
    
        with col2:
            stop_button = st.button("⏹️ Stop")
    
        if run_button:
            match_result_df = pd.DataFrame()
            jd_to_process = selected_jd if selected_jd else list(st.session_state.jd_uploaded_texts.keys())
            resume_to_process = selected_resume if selected_resume else list(st.session_state.cv_uploaded_texts.keys())
    
            if jd_to_process and resume_to_process:
                
                total_combinations = len(jd_to_process) * len(resume_to_process)
                status_text = st.empty()
                progress_bar = st.progress(0)
                process_text = st.empty()
                progress_count = 0
                status_count = 0
            
                for jd in jd_to_process:
                    temp_df = pd.DataFrame()
                    for resume in resume_to_process:
                        
                        progress_count += 0.2
                        status_count += 1
                        status_text.markdown(f"🔍 Matching **{jd}** with **{resume}** ({status_count}/{total_combinations})...")
                        process_text.markdown("📌 Starting model execution...")
                        progress_bar.progress(progress_count / total_combinations)
                        
                        output_text = process(jd, resume, st.session_state.jd_uploaded_texts[jd], st.session_state.cv_uploaded_texts[resume])
                        process_text.markdown("🔄 Extracting structured data from model output...")
                        progress_count += 0.3
                        progress_bar.progress(progress_count / total_combinations)
                        
                        temp_df = extract_json_return_df(jd, resume, output_text)
                        progress_count += 0.4
                        progress_bar.progress(progress_count / total_combinations)
                        process_text.markdown("✅ Finalizing this pair...")
                        
                        if temp_df is not None:
                            match_result_df = pd.concat([match_result_df, temp_df], ignore_index=True)
                        progress_count += 0.1
                        progress_bar.progress(progress_count / total_combinations)
                        process_text.empty()
                        
                progress_bar.empty()
                status_text.empty()
                
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    match_result_df.to_excel(writer, index=False, sheet_name='Match Summary')
                excel_buffer.seek(0)
                st.session_state["excel_download_data"] = excel_buffer.read()
                st.session_state["match_result_df"] = match_result_df  # Optional: keep for display
            else:
                st.info("No Job Description and Resume uploaded")
            
        if "excel_download_data" in st.session_state:
            st.download_button(
                label="📥 Download Excel Summary",
                data=st.session_state["excel_download_data"],
                file_name="match_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
        if "match_result_df" in st.session_state:
            st.subheader("Match Summary Table")
            st.dataframe(st.session_state["match_result_df"], use_container_width=True)
    
    
    ################################################   LOG TAB   ################################################
    
    with log_tab:
        if st.session_state.log_file:
            st.subheader("Error Logs")
    
            # Convert log list to a DataFrame
            log_df = pd.DataFrame(st.session_state.log_file, columns=["SrNo." ,"Context", "Error"])
    
            # Display error logs
            st.dataframe(log_df, use_container_width=True)
    
            # Create Excel download of logs
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                log_df.to_excel(writer, index=False, sheet_name='Error Logs')
            excel_buffer.seek(0)
            st.session_state["log_excel_data"] = excel_buffer.read()
    
            # Download button for error log
            st.download_button(
                label="📥 Download Error Log",
                data=st.session_state["log_excel_data"],
                file_name="error_log.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
            # --- Deduplicated Resume ZIP ---
            zip_cv_buffer = io.BytesIO()
            added_cv_files = set()
            
            with ZipFile(zip_cv_buffer, 'w') as zip_cv_file:
                for fname in st.session_state.log_error_cv_file_name:
                    if fname in st.session_state.cv_uploaded_names and fname not in added_cv_files:
                        f = st.session_state.cv_uploaded_names[fname]
                        f.seek(0)
                        zip_cv_file.writestr(fname, f.read())
                        added_cv_files.add(fname)
            
            zip_cv_buffer.seek(0)
            st.download_button(
                label="📥 Download Error Files (Resumes)",
                data=zip_cv_buffer,
                file_name="cv_error_files.zip",
                mime="application/zip"
            )
            
            # --- Deduplicated JD ZIP ---
            zip_jd_buffer = io.BytesIO()
            added_jd_files = set()
            
            with ZipFile(zip_jd_buffer, 'w') as zip_jd_file:
                for fname in st.session_state.log_error_jd_file_name:
                    if fname in st.session_state.jd_uploaded_names and fname not in added_jd_files:
                        f = st.session_state.jd_uploaded_names[fname]
                        f.seek(0)
                        zip_jd_file.writestr(fname, f.read())
                        added_jd_files.add(fname)
            
            zip_jd_buffer.seek(0)
            st.download_button(
                label="📥 Download Error Files (JDs)",
                data=zip_jd_buffer,
                file_name="jd_error_files.zip",
                mime="application/zip"
            )
    
        else:
            st.info("✅ No errors encountered during this session.")
