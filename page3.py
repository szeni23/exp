import streamlit as st
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def page3():
    st.write("""
        This app was created by Rico.
        
        
        The Expense Splitter is a project I built to simplify and visualize expense settlements among friends or groups. I hope you find it useful!
        """)
    st.image('0.jpg')
