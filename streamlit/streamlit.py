import streamlit as st
import pandas as pd
import snowflake.connector
from langchain.llms import OpenAI
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
import sqlite3
from langchain.chains import create_sql_query_chain
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
 
# from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType

# Function to create a connection to Snowflake
def create_snowflake_connection():
    conn_params = {
    "account": "LIPSJZQ-RSB74087",
    "user": "shruti",
    "password": "Kuchtoh77",
    "warehouse": "BIG_WH",
    "database": "BIG_DB",
    "schema": "HARMONIZED"
    }

    conn = snowflake.connector.connect(**conn_params)

    return conn

def snowflake_conn():
    conn = create_snowflake_connection()
# Example query
    query1 = "SELECT * FROM BIG_DB.HARMONIZED.BLS_EMPLOYMENT_V"
    query2 = "SELECT * FROM BIG_DB.HARMONIZED.CPI_RENT_VIEW"
    query3 = "SELECT * FROM BIG_DB.HARMONIZED.GEO_VIEW"
    query4 = "SELECT * FROM BIG_DB.HARMONIZED.HOME_MORTGAGE_VIEW"
    query6 = "SELECT * FROM BIG_DB.HARMONIZED.URBAN_CRIME_STATISTICS_V LIMIT 100000"
    query7 = "SELECT * FROM BIG_DB.HARMONIZED.US_POI_V LIMIT 100000"
    querysp1 = "SELECT * FROM BIG_DB.ANALYTICS.CRIME_UNEMPLOYMENT_RATIO_V"
    querysp2 = "SELECT * FROM BIG_DB.ANALYTICS.EMPLOYMENT_POI_ANALYSIS_V"
    querysp3 = "SELECT * FROM BIG_DB.ANALYTICS.HOME_PURCHASE_DATA_VIEW"
    # Fetching data into a pandas DataFrame
    dfsp1 = pd.read_sql(querysp1, conn)
    dfsp2 = pd.read_sql(querysp2, conn)
    dfsp3 = pd.read_sql(querysp3, conn)

    # Fetching data into a pandas DataFrame
    df1 = pd.read_sql(query1, conn)
    df2 = pd.read_sql(query2, conn)
    df3 = pd.read_sql(query3, conn)
    df4 = pd.read_sql(query4, conn)
    df6 = pd.read_sql(query6, conn)
    df7 = pd.read_sql(query7, conn)

    conn.close()

    connection = sqlite3.connect('harmonize.db')
    df1.to_sql('BLS_EMPLOYMENT_V', connection, if_exists='replace', index=False)
    df2.to_sql('CPI_RENT_VIEW', connection, if_exists='replace', index=False)
    df3.to_sql('GEO_VIEW', connection, if_exists='replace', index=False)
    df4.to_sql('HOME_MORTGAGE_VIEW', connection, if_exists='replace', index=False)
    df6.to_sql('URBAN_CRIME_STATISTICS_V', connection, if_exists='replace', index=False)
    df7.to_sql('US_POI_V', connection, if_exists='replace', index=False)
    dfsp1.to_sql('CRIME_UNEMPLOYMENT_RATIO_V', connection, if_exists='replace', index=False)
    dfsp2.to_sql('EMPLOYMENT_POI_ANALYSIS_V', connection, if_exists='replace', index=False)
    dfsp3.to_sql('HOME_PURCHASE_DATA_VIEW', connection, if_exists='replace', index=False)
    connection.close()

        # Connect to the SQLite database
    db = SQLDatabase.from_uri("sqlite:///harmonize.db")
    llm_with_key = OpenAI(openai_api_key='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', temperature=0, verbose=True)
 
    agent_executor = create_sql_agent(
        llm=llm_with_key,
        toolkit=SQLDatabaseToolkit(db=db, llm=llm_with_key),
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )

    return agent_executor

# Establish connection to Snowflake
conn = create_snowflake_connection()

# Set page configuration for a darker theme
st.set_page_config(page_title="LocateSmart AI", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    .chat-container {
        display: flex;
        flex-direction: column-reverse;
        padding-bottom: 20px;
    }
    .message-box {
        border-radius: 0px;
        padding: 30px;
        margin: 0px 0;
        font-family: 'Roboto', sans-serif;
    }
    .user-message {
        background-color: #141414;
        color: white;
        text-align: left;
    }
    .bot-message {
        background-color: #262625;
        color: white;
        text-align: left;
    }
    .stTextInput > label {
        color: white;
        font-family: 'Roboto', sans-serif;
    }
    body {
        color: #D8E9A8;
        background-color: #121212;
        font-family: 'Roboto', sans-serif;
    }
    .title {
        color: #e9e9a8; 
        font-family: 'Roboto', sans-serif;
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)


# Function to get bot response
def get_bot_response(user_input):
    agent_executor = snowflake_conn()
    a = agent_executor.run(f"{user_input}")

    return a

# Streamlit UI
tab1, tab2 = st.tabs(["Chat with AI", "Know More About Our Data"])

with tab1:
    st.markdown("<h1 class='title'>LocateSmart AI: Discover Your Ideal Place to Live</h1>", unsafe_allow_html=True)

    # Session state to store conversation
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Chat interface at the end
    user_input = st.text_input("Type your question here...", key="user_input", placeholder="Type here and press enter")

    if user_input:
        st.session_state.conversation.append(("user", user_input))
        bot_reply = get_bot_response(user_input)
        st.session_state.conversation.append(("bot", bot_reply))

    # Display chat messages
    with st.container():
        for sender, message in reversed(st.session_state.conversation):
            if sender == "user":
                st.markdown(f"<div class='message-box user-message'>You: {message}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='message-box bot-message'>LocateSmart AI: {message}</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<h1 class='title'>Know more about the data</h1>", unsafe_allow_html=True)
    # Add content or explanations about your data here
