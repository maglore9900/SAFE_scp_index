
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import environ
import re
from pathlib import Path

env = environ.Env()
environ.Env.read_env()

model_name = "BAAI/bge-large-en-v1.5"
# model_name = "BAAI/bge-small-en-v1.5"
model_kwargs = {"device": "cuda"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

base_dir = Path("qdb")
client = QdrantClient(path=base_dir)

try:
    client.create_collection(
        collection_name="scp_collection",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )
except:
    pass

vectorstore = QdrantVectorStore(
    client=client,
    collection_name="scp_collection",
    embedding=embeddings,
)

documents = []
entry = []
UUID = 0
db_count = 0
pattern = r"^Identifier: (SCP-\d+)$"

base_dir.mkdir(exist_ok=True)  # Ensure the base directory exists

with open('data.txt', 'r') as file:
    f = file.read()
    for g in f.split('",'):
        try:
            if UUID >= ((db_count -1) * 500):
                print(f"UUID {UUID}")
                print(len(g))
                scp_name = None
                lines = g.split('\n')
                for l in lines:
                    l = re.sub(r'^"', '', l)
                    entry.append(f"{l}\n")
                    match = re.match(pattern, l)
                    if match:
                        scp_name = match.group(1)
                content = ' '.join(entry)
                print(f"Setting document object for {scp_name}")
                document = Document(
                    page_content=content,
                    metadata={"SCP_ID": scp_name},
                )
                print(f"Document: {document}")
                documents.append(document)
                if UUID >= 0 and UUID % 200 == 0:
                    base_dir.mkdir(exist_ok=True)  
                    print(f"Writing batch {db_count}")                     
                    vectorstore.add_documents(documents=documents)
                    documents = []
                    entry = []
                    db_count += 1
            UUID += 1
        except Exception as e:
            print(f"An exception occured: {e}")

if documents:
    current_db_dir = base_dir / f"db_{db_count}"
    current_db_dir.mkdir(exist_ok=True)
    print(f"Writing final batch {db_count} to {current_db_dir}")
    base_dir.mkdir(exist_ok=True)  
    print(f"Writing batch {db_count}")                     
    vectorstore.add_documents(documents=documents)



        

