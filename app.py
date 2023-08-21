import os
import pandas as pd
import streamlit as st
from page1 import page1
from page2 import page2
from page3 import page3

tabs = {
    "Expense Splitter": page1,
    "McCrocsMagicX AG edition": page2,
    "About": page3,
}
def main():
    st.set_page_config(
        page_title="ExpenseSplitter",
        layout="wide"
    )
    selection = st.sidebar.radio(" ", list(tabs.keys()))
    page = tabs[selection]
    with st.spinner(f"Load {selection}..."):
        page()


if __name__ == "__main__":
    main()
