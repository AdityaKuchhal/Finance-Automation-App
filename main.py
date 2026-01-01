import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import os

st.set_page_config(page_title="Finance Automation App", page_icon="💰", layout="wide")

category_file = "categories.json"

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }
    
if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)
        
def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transaction(df):
    df["Category"] = "Uncategorized"
    
    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue
        
        lowered_keywords = [kw.lower().strip() for kw in keywords]
        
        for idx, row in df.iterrows():
            details = row["Details"].lower().strip()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category
                
    return df
            

def load_transactions(file):
    try:
        df = pd.read_csv(file, dtype=str)
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].str.replace(",", "", regex=False).astype(float)
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
        
        return categorize_transaction(df)
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        # st.success(f"Added '{keyword}' to category '{category}'")
        return True
    return False

def main():
    st.title("Finance Dashboard")
    
    uploaded_file = st.file_uploader("Upload your statement (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        
        if df is not None:
            debits_df = df[df["Debit/Credit"] == "Debit"].copy()
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()
            
            st.session_state.debits_df = debits_df.copy()
        
            tab1, tab2 = st.tabs(["Expenses (Debit)", "Payments/Refunds (Credit)"])
            
            with tab1:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")
                
                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        # st.success(f"Added a new category: {new_category}")
                        st._rerun()
                        
                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.debits_df[["Date", "Details", "Amount", "Category"]],
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
                        "Details": st.column_config.TextColumn("Details"),
                        "Amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.categories.keys()),
                        ),
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor",
                )
                
                save_button = st.button("Apply Changes", type="primary")
                
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Category"]
                        if new_category == st.session_state.debits_df.at[idx, "Category"]:
                            continue
                        details = row["Details"]
                        st.session_state.debits_df.at[idx, "Category"] = new_category
                        add_keyword_to_category(new_category, details) 
                
            with tab2:
                st.write(credits_df)
        
main()