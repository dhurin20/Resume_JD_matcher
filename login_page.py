import streamlit as st
import time

def login_page():
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