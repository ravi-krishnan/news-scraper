import streamlit as st
import requests
import json

st.title("News Search App")

with st.form("search_form"):
    search_query = st.text_input("Enter your search query:")
    submit_button = st.form_submit_button("Search")

    if submit_button:
        url = "http://127.0.0.1:8000/search"
        payload = {"search_query": search_query}
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            st.success("Search completed successfully!")
            st.json(result)
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
