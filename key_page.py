import streamlit as st
from cryptography.fernet import Fernet
import re
import time
import os

def key_entry_page():
    st.title("Enter Decryption Key")
    st.markdown(
    """
    <style>
        .top-right-logo {
            position: absolute;
            top: 10px;
            right: 10px;
        }
    </style>
    <div class="top-right-logo">
        <img src="DhurinLogo.png" width="100">
    </div>
    """,
    unsafe_allow_html=True
    )
    st.write("Current working directory:", os.getcwd())
    st.write("Files in this directory:", os.listdir())

    key_input = st.text_input("Enter secret key to unlock the login page", type = "password")

    if st.button("Submit Key"):
        try:
            key = key_input.encode()
            if len(key) != 44:
                st.error("Invalid key format. Please check again")
                return
            fernet = Fernet(key)

            with open("creds.enc", "rb") as file:
                encrypted_data = file.read()

            with st.spinner("Verifying Key..."):
                decrypted = fernet.decrypt(encrypted_data).decode()
                username, password = decrypted.split(":")

            pattern = r"^Kn..D.{5}.V$"
            if re.match(pattern, username):
                st.session_state["correct_username"] = username
                st.session_state["correct_password"] = password
                st.session_state["decryption_key"] = key
                st.session_state["key_verified"] = True
                st.toast("Key Accepted! Proceeding to login in a sec.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Access Restricted. This key is not meant for you.")

        except Exception as e:
            st.error(e)

if __name__ == "__main__":
    key_entry_page()
