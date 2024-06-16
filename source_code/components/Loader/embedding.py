from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import TextNode
from typing import List
class Embedding:
    def __init__(self,embedding_model_name:str="BAAI/bge-small-en"):
        self.embed_model = HuggingFaceEmbedding(embedding_model_name)
    def __call__(self,nodes:List[TextNode])->None:
        for node in nodes:
            node_embedding = self.embed_model.get_text_embedding(
                node.get_content(metadata_mode="all")
            )
            node.embedding =node_embedding
    
        

