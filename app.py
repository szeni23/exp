import os
import pandas as pd
import streamlit as st
from page1 import page1
from page2 import page2
from page3 import page3

# Set page config at the top of the script
st.set_page_config(
    page_title="ExpenseSplitter",
    layout="wide"
)

tabs = {
    "Expense Splitter": page1,
    "McCrocsMagicX AG Splitter": page2,
    "About": page3,
}

def main():
    if "update_sidebar" not in st.session_state:
        st.session_state.update_sidebar = False

    # Initialize separate session state variables for each page's persons list.
    if 'persons_page1' not in st.session_state:
        st.session_state.persons_page1 = []

    if 'persons_page2' not in st.session_state:
        predefined_persons = ["CEO", "Lieferant", "Technigger", "Verplaner", "Pirat", "Koch", "Kanadier", "Milchma", "Chef Geheimdienst"]
        st.session_state.persons_page2 = predefined_persons

    # Determine the current page selection
    selection = st.sidebar.radio(" ", list(tabs.keys()))

    if selection == "McCrocsMagicX AG Splitter":
        st.session_state.persons = st.session_state.persons_page2[:]
    else:
        st.session_state.persons = st.session_state.persons_page1[:]

    if 'expenses' not in st.session_state:
        st.session_state.expenses = []

    if 'transfers' not in st.session_state:
        st.session_state.transfers = []

    if 'previous_split_between' not in st.session_state:
        st.session_state.previous_split_between = []

    page = tabs[selection]
    with st.spinner(f"Load {selection}..."):
        page()


if __name__ == "__main__":
    main()
