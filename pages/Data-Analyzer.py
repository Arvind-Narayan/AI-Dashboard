import streamlit as st
import pandas as pd
import plotly.express as px
import agent
from utils import *
from openai import OpenAI

st.set_page_config(page_title="AI Data Analyzer", page_icon="📈")

#Hide header
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

openai_api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key = openai_api_key)

if 'analyzer_assist' not in st.session_state:
        st.session_state['analyzer_assist'] = ''

if 'analyzer_thread' not in st.session_state:
        st.session_state['analyzer_thread'] = ''

if 'analyzer_text' not in st.session_state:
        st.session_state['analyzer_text'] = ''

if 'analyzer_img' not in st.session_state:
        st.session_state['analyzer_img'] = ''

if 'multiselect_items' not in st.session_state:
        st.session_state['multiselect_items'] = []

st.title('📈 AI Data Analyzer')
st.write('---')

datasets = st.multiselect(
    label = "Datasets you want to analyze",
    options = ["Total_Inflation", "Category_Inflation"],
    default = st.session_state['multiselect_items'],
    on_change = multiselect_callback,
    key = 'dataset_select') # need to handle deafult state

analyzer_assist_id = ''

if len(datasets) == 1:
    if datasets[0] == 'Total_Inflation':
        analyzer_assist_id = st.secrets['analyzer_tot_assist_id']
    elif datasets[0] == 'Category_Inflation':
        analyzer_assist_id = st.secrets['analyzer_cat_assist_id']
elif len(datasets) == 2:
    analyzer_assist_id = st.secrets['analyzer_cat_tot_assist_id']

st.write(analyzer_assist_id)

query = st.text_area(
    "Analysis query:",
    )

if st.button(':green[Submit]'):
    with st.spinner("Generating response..."):

        if not datasets:
            st.info('Please select dataset')

        if not query:
            st.info('Please submit a query')

        if query and datasets:
            if st.session_state['analyzer_assist'] != analyzer_assist_id:
                    thread = client.beta.threads.create()
                    st.session_state['analyzer_thread'] = thread.id
                    st.session_state['analyzer_assist'] = analyzer_assist_id
            try:
            # get ai analysis
                st.session_state['analyzer_text'], st.session_state['analyzer_img'] = agent.get_analysis(client, thread_id = st.session_state['analyzer_thread'], 
                                                assist_id = st.session_state['analyzer_assist'],
                                                query = query)
            except Exception as e:
                 st.write(e)
                 st.error('Sorry something went wrong. Please Try again')

if st.session_state['analyzer_img']:
        st.image(st.session_state['analyzer_img'])

if st.session_state['analyzer_text']: 
        st.markdown(st.session_state['analyzer_text'])
                


# st.write(st.session_state['analyzer_assist'])
# st.write(st.session_state['analyzer_thread'])
# st.write(st.session_state['multiselect_items'])