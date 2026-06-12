import streamlit as st
from pymongo import MongoClient

@st.cache_resource
def get_client():
    return MongoClient(st.secrets["MONGO_URI"])

def get_db():
    return get_client()["tredalq"]
