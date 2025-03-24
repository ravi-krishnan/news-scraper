import streamlit as st
import requests
import json
import base64

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
            st.success("Search completed successfully!")

            # Display company name
            st.header(f"Company: {result['Company']}")

            # Display articles
            st.subheader("Articles")
            for article in result['Articles']:
                st.markdown(f"## {article['Title']}")
                st.write(f"**Summary:** {article['Summary']}")
                
                st.write("**Topics:**")
                for topic in article['Topics']:
                    st.markdown(f"- {topic}")
                
                st.write(f"**Sentiment:** {article['Sentiment']}")
                st.markdown("---")

            # Display sentiment analysis
            st.subheader("Sentiment Analysis")
            st.write(f"**Comparative Sentiment Score:** {result['Comparative Sentiment Score']['Sentiment Distribution']}")

            st.subheader("Comparative Sentimental coverage")
            for i in result["Comparative Sentiment Score"]["Coverage Differences"]:
                st.write(f"**Comparison:**     {i["Comparison"]}")
                st.write(f"**Impact:**         {i["Impact"]}")
            st.markdown("---")
            # Display topic overlap
            st.subheader("Topic Overlap")
            for i in range(len(result["Comparative Sentiment Score"]["Topic Overlap"])):
                if i==0:
                    st.write(f"**Common Topics:** {', '.join(result['Comparative Sentiment Score']['Topic Overlap']['Common Topics'])}")
                else:
                    st.write(f"**Unique Topics in Article {i}:** ", result['Comparative Sentiment Score']['Topic Overlap'][f'Unique Topics in Article {i}'])
            st.markdown("---")

            # Display final sentiment
            st.subheader("Final Sentiment")
            st.write(result['Final Sentiment Analysis'])
            st.markdown("---")

            st.subheader("Hindi Audio")
            submitted = st.form_submit_button("Press here to play audio")
            st.markdown("---")
            if submitted:
                # Decode the base64 audio
                audio_bytes = base64.b64decode(result['Audio'])

                # Play the audio
                st.audio(audio_bytes, format="audio/mp3")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
