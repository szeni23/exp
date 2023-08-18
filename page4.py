import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import csv
import os
from io import BytesIO, StringIO
import base64
import networkx as nx
import matplotlib.pyplot as plt
import requests


def page4():

    st.write("""
        This app was created by Rico.
        
        
        The Expense Splitter is a project I built to simplify and visualize expense settlements among friends or groups. I hope you find it useful!
        """)
