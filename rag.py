from pathlib import Path
from typing import List
from llama_index.readers.file import PyMuPDFReader
from dotenv import load_dotenv
import os
load_dotenv()
db_name = os.getenv("DB_NAME")
host = os.getenv("HOST")
password = os.getenv("PASSWORD")
port = os.getenv("PORT")
user = os.getenv("USER")
grop_api_key = os.getenv("GROP_API_KEY")

#Load
loader = PyMuPDFReader()
documents = loader.load(file_path ="./data/llama2.pdf")

#Split
from llama_index.core.node_parser import SentenceSplitter
text_parser = SentenceSplitter(chunk_size = 1024)

text_chunks =[]
doc_idxs = []
for doc_idx, doc in enumerate(documents):
    cur_text_chunks = text_parser.split_text(doc.text)
    text_chunks.extend(cur_text_chunks)
    doc_idxs.extend([doc_idx]*len(cur_text_chunks))

from llama_index.core.schema import TextNode
##Create nodes
nodes = []
for idx, text_chunk in enumerate(text_chunks):
    node = TextNode(
        text=text_chunk,
    )
    src_doc = documents[doc_idxs[idx]]
    node.metadata = src_doc.metadata
    nodes.append(node)

#Embedding
# sentence transformers
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")

for node in nodes:
    node_embedding = embed_model.get_text_embedding(
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding

#Store embedding
import psycopg2



# conn = psycopg2.connect(connection_string)
conn = psycopg2.connect(
    dbname="postgres",
    host=host,
    password=password,
    port=port,
    user=user,
)
conn.autocommit = True

with conn.cursor() as c:
    c.execute(f"DROP DATABASE IF EXISTS {db_name}")
    c.execute(f"CREATE DATABASE {db_name}")
    #c.execute(f"CREATE EXTENSION IF NOT EXISTS vector")

from sqlalchemy import make_url
from llama_index.vector_stores.postgres import PGVectorStore

vector_store = PGVectorStore.from_params(
    database=db_name,
    host=host,
    password=password,
    port=port,
    user=user,
    table_name="llama2_paper",
    embed_dim=384,  # openai embedding dimension
)



vector_store.add(nodes)

#Build Retrival
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from typing import Any, List, Optional
from llama_index.core.schema import NodeWithScore



class VectorDBRetriever(BaseRetriever):
    """Retriever over a postgres vector store."""

    def __init__(
        self,
        vector_store: PGVectorStore,
        embed_model: Any,
        query_mode: str = "default",
        similarity_top_k: int = 2,
    ) -> None:
        """Init params."""
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
        query_embedding = embed_model.get_query_embedding(
            query_bundle.query_str
        )
        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )
        query_result = vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        return nodes_with_scores
    
retriever = VectorDBRetriever(
    vector_store, embed_model, query_mode="default", similarity_top_k=2
)

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.groq import Groq


llm = Groq(model="mixtral-8x7b-32768", api_key=grop_api_key)
query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm)

query_str = "How does Llama 2 perform compared to other open-source models?"

response = query_engine.query(query_str)

print(str(response))

#print(response.source_nodes[0].get_content())