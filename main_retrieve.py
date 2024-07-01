import streamlit as st
from dotenv import load_dotenv
import os
from source_code.pipeline.retrival_pipeline import RetrivalPipeline
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
load_dotenv()

grop_api_key = os.getenv("GROP_API_KEY")
host = os.getenv("HOST")
password = os.getenv("PASSWORD")
port = os.getenv("PORT")
user = os.getenv("USER")

db_name = os.getenv("DB_NAME")
llm_model = "mixtral-8x7b-32768"
embed_model = "BAAI/bge-small-en"
table_name="imm_law"

llm = Groq(model=llm_model, api_key=grop_api_key)
embed_model = HuggingFaceEmbedding(model_name = embed_model)

st.title("Welcome to my RAG Agent")
query_str = st.text_input("What would you like to ask")

if st.button("Submit"):
    if not query_str.strip():
        st.error("Please provide the question")
    else:
        try:
            retrieve_pipeline = RetrivalPipeline(host = host,user=user, password=password,port=port, db_name=db_name,table_name=table_name)
            conn  = retrieve_pipeline.start_connect()
            query_engine = retrieve_pipeline.create_query_engine(llm=llm,embed_model=embed_model)
            response = query_engine.query(query_str)
            
            st.success(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
