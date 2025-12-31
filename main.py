import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import os

st.set_page_config(page_title="Finance Automation App", page_icon="💰", layout="wide")

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": {}
    }
    
if os.path.exists("categories.json"):
    with open("categories.json", "r") as f:
        st.session_state.categories = json.load(f)

def load_transactions(file):
    try:
        df = pd.read_csv(file, dtype=str)
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].str.replace(",", "", regex=False).astype(float)
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
        
        return df
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def main():
    st.title("Finance Dashboard")
    
    uploaded_file = st.file_uploader("Upload your statement (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        
        if df is not None:
            debits_df = df[df["Debit/Credit"] == "Debit"].copy()
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()
        
            tab1, tab2 = st.tabs(["Expenses (Debit)", "Payments/Refunds (Credit)"])
            
            with tab1:
                st.write(debits_df)
            with tab2:
                st.write(credits_df)
        
main()