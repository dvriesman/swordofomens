import streamlit as st
import os
import google.generativeai as genai
import requests
from requests.auth import HTTPBasicAuth
from typing import List

def retrive_jira_data() -> List[str]:
    
    user = os.environ['JIRA_USER'] 
    password = os.environ['JIRA_PASSWORD']
    jira_base_url = os.environ['JIRA_BASE_URL']
    headers =  {"Content-Type":"application/json"}
    api_url = jira_base_url + "/rest/api/latest/search?jql=project%20%3D%20OTR%20and%20issuetype%20in%20%28bug%2C%20defect%2C%20sub-task%29%20and%20status%20in%20%28%22To%20Do%22%2C%20%22In%20Progress%22%2C%20%22In%20Review%22%29%20and%20assignee%20is%20not%20empty%20order%20by%20assignee&fields=key,summary,assignee,status,issuetype,duedate,customfield_10015"
    response = requests.get(url=api_url, headers=headers, auth=HTTPBasicAuth(user, password))
    result = response.json()
    data = []
    data.append("key,summary,assignee,status,issue type,start date,due date")

    for element in result["issues"]:
        due_date = element["fields"]["duedate"]
        start_date = element["fields"]["customfield_10015"]
        if start_date is None:
            start_date = ""

        if due_date is None:
            due_date = ""

        data.append(element["key"] + "," + 
                    element["fields"]["summary"] + "," +
                    element["fields"]["assignee"]["displayName"] + "," +
                    element["fields"]["status"]["name"] + "," +
                    element["fields"]["issuetype"]["name"] + "," +
                    start_date + "," +
                    due_date) 
        
    return data



def init_chat(data) -> any:
    genai.configure(api_key = os.environ['GOOGLE_API_KEY'])

    # Set up the model
    generation_config = {
    "temperature": 0.8,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 4000,
    }


    model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config)

    prompt = "here is your csv, comma delimiter, data source: '"
    for line in data:
        prompt = prompt + line + "\n"

    prompt = prompt + "'.\n"
    prompt = prompt + ". First row you can find the header."


    convo = model.start_chat(history=[
        {
            "role": "user",
            "parts": [prompt]
        },
        {
            "role": "model",
            "parts": ["Sure, I read and parsed the csv file, now I can answer questions about who is working on each tasks according to respective status. " +
                      "I identified those columns: key, summary, assignee, status, issue type, due date and start date"]
        },
        {
            "role": "user",
            "parts": ["When I ask what someone is working on, consider only tasks with status in progress"]
        },
        {
            "role": "model",
            "parts": ["Sure, I'll filter for status in progress when you ask that"]
        },
        
    ])

    return convo


# Process and store Query and Response
def llm_function(convo, query):

    convo.send_message(query)
    response = convo.last

    # Displaying the Assistant Message
    with st.chat_message("model"):
        st.markdown(response.text)

    # Storing the User Message
    st.session_state.messages.append(
        {
            "role":"user",
            "content": query
        }
    )

    # Storing the User Message
    st.session_state.messages.append(
        {
            "role":"model",
            "content": response.text
        }
    )


def main():
    data = retrive_jira_data()
    convo = init_chat(data)
    st.title("Sword of Omens, give me sight beyond sight!")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role":"manager",
                "content":"How could I help you?"
            }
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])        


    query = st.chat_input("What's up?")

    # Calling the Function when Input is Provided
    if query:
        # Displaying the User Message
        with st.chat_message("user"):
            st.markdown(query)

        llm_function(convo, query)


if __name__ == "__main__":
    main()




