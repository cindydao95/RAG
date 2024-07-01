from llama_index.vector_stores.postgres import PGVectorStore
import os
from source_code.utils import connect_db
from source_code.components.Retriver.VectorDB import VectorDBRetriever



class RetrivalPipeline:
    def __init__(self,host,password,port,user,db_name,table_name):
        self.host =host
        self.password = password
        self.port = port
        self.user = user
        self.db_name = db_name
        self.table_name = table_name
    def start_connect(self):
        conn = connect_db(host=self.host,password=self.password,port =self. port, user=self.user)
        return conn
    def _vector_sore(self):
        vector_store = PGVectorStore.from_params(
        database=self.db_name,
        host=self.host,
        password=self.password,
        port=self.port,
        user=self.user,
        table_name=self.table_name,
        embed_dim=384, ) # openai embedding dimension
        return vector_store
    def create_query_engine(self,embed_model:str,llm,similarity_top_k=2,):
        vector_store = self._vector_sore()
        retriever = VectorDBRetriever(
                        vector_store, embed_model, query_mode="default", similarity_top_k=similarity_top_k
                    )
        from llama_index.core.query_engine import RetrieverQueryEngine

        #llm = Groq(model=llm_model, api_key=grop_api_key)
        query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm)
        return query_engine