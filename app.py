import os

import pandas as pd
import streamlit as st
from page1 import page1




# Seitennavigation
tabs = {
    "Standard": page1,
}


# Streamlit-App
def main():
    st.set_page_config(
        page_title="✂︎ Expense Splitter ✂︎",
        layout="wide"
    )

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio(" ", list(tabs.keys()))
    page = tabs[selection]
    with st.spinner(f"Lade {selection}..."):
        page()


if __name__ == "__main__":
    main()

