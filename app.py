import streamlit as st
import duckdb
from chatbot import chatbot
from llm_handler import test_connection
from ui_components import render_app

# Rest of your app.py code below...
if __name__ == "__main__":
    render_app()