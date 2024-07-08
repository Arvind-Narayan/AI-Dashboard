from openai import OpenAI
import pandas as pd
import io
import streamlit as st
import re

def get_analysis(client, thread_id, assist_id, query ):
    message = client.beta.threads.messages.create( thread_id=thread_id,
                                                  role="user",
                                                  content= query)
    
    run = client.beta.threads.runs.create_and_poll( thread_id=thread_id,
                                                   assistant_id=assist_id
                                                   )
    
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(thread_id=thread_id)
    else:
        print(run.status)
    
    result = messages.data[0].content

    text = ''
    image_data_bytes = None
    pattern = r'\[[^\]]+\]\(.*?\.png\)'

    # st.write(result)

    for msg in result:
        if msg.type == 'text':
            text = msg.text.value
            text = re.sub(pattern, '', text)
        if msg.type == 'image_file':
            img_file_id = msg.image_file.file_id
            image_data = client.files.content(img_file_id)
            image_data_bytes = image_data.read()

    return text, image_data_bytes



def get_insights(df, description):
    openai_api_key = st.secrets["openai_api_key"]
    client = OpenAI(api_key = openai_api_key)
    assist_id = st.secrets["insights_assist_id"] 

    # df to file for upload
    bytes_io = io.BytesIO()
    df.to_csv(bytes_io)
    bytes_io.seek(0)
    buffered_reader = io.BufferedReader(bytes_io)

    file = client.files.create(file= buffered_reader,
                               purpose="assistants"
                               )

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create( thread_id=thread.id,
                                                  role="user",
                                                  content= description,
                                                  attachments = [
                                                                    {
                                                                        "file_id": file.id,
                                                                        "tools": [{"type": "code_interpreter"}]
                                                                    }

                                                                    ]
                                                                    )

    run = client.beta.threads.runs.create_and_poll( thread_id=thread.id,
                                                   assistant_id=assist_id
                                                   )
    
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(thread_id=thread.id)
    else:
        print(run.status)
    
    result = messages.data[0].content

    for msg in result:
        if msg.type == 'text':
            insights = msg.text.value
            return insights, result

