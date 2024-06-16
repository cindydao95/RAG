from llama_index.readers.file.flat.base import FlatReader
from llama_index.core import Document
from source_code.utils import nodes_loader

import os
from typing import Union,List
from pathlib import Path

# f_name ="post_06_14_24.txt"

# f_path = Path(os.path.join('data',f_name))


class DocLoaders:
    loader = FlatReader()
    def __init__(self,text_f_path:Union[str,Path]):
        if os.path.exists(text_f_path):
            self.docs = DocLoaders.loader.load_data(text_f_path)
        else:
            raise("File Path not exist")
    def nodes_loader(self)->List:
        nodes = nodes_loader(documents=self.docs)
        return nodes





