# theme.py

import streamlit as st

def set_custom_theme():
    st.markdown(
        """
        <style>
        body {
            background-color: #121212;
            color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
