from source_code.components.Loader.textloader import DocLoaders
from source_code.components.Loader.embedding import Embedding
from source_code.components.Loader.store_vector import VectorDBLoader
from pathlib import Path
import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

class Load:
    def __init__(self,f_names:List[str]):
        self.f_names = f_names
    def start_load_docs(self):
        self.nodes =[]
        for f in self.f_names:
            f_path = Path(os.path.join('data',f))
            loader = DocLoaders(text_f_path=f_path)
            cur_nodes = loader.nodes_loader()
            self.nodes.extend(cur_nodes)

    def start_embedding(self):
        print("Start Embedding")
        embedder = Embedding()
        embedder(nodes=self.nodes)
        print("Finish Embedding")
    def start_storage(self,host,password,port,user,db_name,table_name):
        vector_storage = VectorDBLoader(host=host,password=password,
                                port=port,user=user,db_name=db_name,
                                table_name=table_name)
        print("Start Loading Embedding to VectorStorage")
        vector_storage.load(nodes=self.nodes)
        print("Finish Loading Embedding")
    