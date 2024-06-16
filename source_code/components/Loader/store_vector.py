from source_code.utils import connect_db
from llama_index.vector_stores.postgres import PGVectorStore
from typing import List
from llama_index.core.schema import TextNode

class VectorDBLoader:
    
    #from utils import connect_db
    def __init__(self,host,password,port,user,db_name,table_name):
        self.conn = connect_db(host=host,password=password,port=port,user=user)
        self.vector_store = PGVectorStore.from_params(
                database=db_name,
                host=host,
                password=password,
                port=port,
                user=user,
                table_name=table_name,
                embed_dim=384,  # openai embedding dimension
                )
       
    def load(self,nodes:List[TextNode]):
        self.vector_store.add(nodes)
        self.conn.close()
