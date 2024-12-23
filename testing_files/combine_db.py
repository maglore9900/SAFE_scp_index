from time import sleep
from pathlib import Path
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS


model_name = "BAAI/bge-small-en"
# model_name = "BAAI/bge-base-en-v1.5"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vectorstore = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

def merge_db(dir):
    tmp_vectorstore = FAISS.load_local(str(dir), embeddings, allow_dangerous_deserialization=True)
    orig_vectorstore = FAISS.load_local("backup", embeddings, allow_dangerous_deserialization=True)
    orig_vectorstore.merge_from(tmp_vectorstore)
    orig_vectorstore.save_local(str("backup"))
    print("Merged and saved successfully.")


backup_path = Path('backup')

for item in backup_path.iterdir():
    if item.is_dir():
        print(f"Processing directory: {item.name}")
        merge_db(item)
        sleep(1)
