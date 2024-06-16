from llama_index.core import Document
from llama_index.core.schema import TextNode

from typing import List
def _create_nodes(text_chunks,doc_idxs,documents:List[Document])->List[TextNode]:
    #from llama_index.core.schema import TextNode
    nodes = []
    for idx, text_chunk in enumerate(text_chunks):
        node = TextNode(
            text = text_chunk,
        )
        src_doc = documents[doc_idxs[idx]]
        node.metadata = src_doc.metadata
        nodes.append(node)
    return nodes
def nodes_loader(documents:List[Document])->List[TextNode]:
    from llama_index.core.node_parser import SentenceSplitter
    text_parser = SentenceSplitter(chunk_size = 1024)

    text_chunks = []
    doc_idxs = []
    for doc_idx, doc in enumerate(documents):
        cur_text_chunks = text_parser.split_text(doc.text)
        text_chunks.extend(cur_text_chunks)
        doc_idxs.extend([doc_idx]*len(cur_text_chunks))
    nodes = _create_nodes(text_chunks=text_chunks,doc_idxs=doc_idxs,documents=documents)
    return nodes
  

def connect_db(host,password,port, user):
    import psycopg2
    
    print("Connecting to Database")
    conn = psycopg2.connect(
        dbname = "postgres",
        host = host,
        password=password,
        port = port,
        user = user
    )
    conn.autocommit = True
    conn.cursor()
    print("Connected to DB")
    return conn