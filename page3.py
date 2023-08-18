import streamlit as st


def page3():
    st.title("Admin Area")

    # Session state to check if user is authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    password_placeholder = st.empty()

    if not st.session_state.authenticated:
        password = password_placeholder.text_input("Enter Password", type='password')

        if password == "admin123":
            st.session_state.authenticated = True
            password_placeholder.empty()  # Remove password field
            show_admin_tools()
        elif password:
            st.error("Incorrect password. Please try again.")
    else:
        show_admin_tools()


def show_admin_tools():
    st.write("Welcome to the admin area!")
    st.write("Here, you can manage and configure your app settings and tools.")

