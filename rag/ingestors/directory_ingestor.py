from pathlib import Path
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode


class DirectoryIngestor:
    def __init__(self, vector_store:any, embed_model, chunk_size: int = 1024):

        self.text_parser = SentenceSplitter(chunk_size=chunk_size)
        self.vector_store = vector_store
        self.embed_model = embed_model
    def ingest(self, path: Path):
        required_exts = [".md"]
        self.reader = SimpleDirectoryReader(
            input_dir=path,
            required_exts=required_exts,
            recursive=True,
        )
        documents = self.reader.load_data()
        text_chunks = []
        doc_idxs = []
        # Split the text into chunks
        for doc_idx, doc in enumerate(documents):
            cur_text_chunks = self.text_parser.split_text(doc.text)
            text_chunks.extend(cur_text_chunks)
            doc_idxs.extend([doc_idx] * len(cur_text_chunks))
        # Create TextNodes and add them to the vector store
        nodes = []
        for idx, text_chunk in enumerate(text_chunks):
            node = TextNode(
                text=text_chunk,
            )
            src_doc = documents[doc_idxs[idx]]
            node.metadata = src_doc.metadata
            nodes.append(node)
        for node in nodes:
            node_embedding = self.embed_model.get_text_embedding(
                node.get_content(metadata_mode="all")
            )
            node.embedding = node_embedding
        self.vector_store.add(nodes)