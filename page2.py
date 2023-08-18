from PIL import Image
import streamlit as st

Image.MAX_IMAGE_PIXELS = None


def page2():
    st.image('0.jpg')
