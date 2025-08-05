import streamlit as st
import time
import base64

def login_page():
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

    st.title("Login")

    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type = "password")

    if st.button("Login"):
        correct_username = st.session_state.get("correct_username")
        correct_password = st.session_state.get("correct_password")

        if username_input == correct_username and password_input == correct_password:
            st.success("Login successful!")
            st.session_state["authenticated"] = True
            time.sleep(1)
            st.rerun()
        else:
            st.error("Incorrect Username or Password")


if __name__ == "__main__":
    login_page()
