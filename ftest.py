

from time import sleep
from pathlib import Path
import re
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import environ
import re
from langchain.schema import Document
from pathlib import Path
from time import sleep

env = environ.Env()
environ.Env.read_env()

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




documents = []
entry = []
UUID = 0
db_count = 6
pattern = r"^Identifier: (SCP-\d+)$"
base_dir = Path("scp_data")
base_dir.mkdir(exist_ok=True)  # Ensure the base directory exists

with open('data.txt', 'r') as file:
    f = file.read()
    for g in f.split('",'):
        try:
            if UUID >= (db_count * 500):
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
                documents.append(document)
                if UUID >= 0 and UUID % 500 == 0:
                    print("writing to datastore")
                    current_db_dir = base_dir / f"db_{db_count}"
                    current_db_dir.mkdir(exist_ok=True)  
                    
                    print(f"Writing batch {db_count}")
                    if not (current_db_dir / "index.faiss").exists():
                        # Create a new FAISS vector store
                        vectorstore = FAISS.from_documents(documents, embeddings)
                        vectorstore.save_local(str(current_db_dir))
                    else:
                        # Load and merge with the existing vector store
                        old_vectorstore = FAISS.load_local(str(current_db_dir), embeddings, allow_dangerous_deserialization=True)
                        tmp_vectorstore = FAISS.from_documents(documents, embeddings)
                        old_vectorstore.merge_from(tmp_vectorstore)
                        old_vectorstore.save_local(str(current_db_dir))
                    documents = []
                    db_count += 1
            UUID += 1
        except Exception as e:
            print(f"An exception occured: {e}")

# Save remaining documents to the last database if not yet saved
if documents:
    current_db_dir = base_dir / f"db_{db_count}"
    current_db_dir.mkdir(exist_ok=True)
    print(f"Writing final batch {db_count} to {current_db_dir}")
    if not (current_db_dir / "index.faiss").exists():
        vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local(str(current_db_dir))
    else:
        old_vectorstore = FAISS.load_local(str(current_db_dir), embeddings, allow_dangerous_deserialization=True)
        tmp_vectorstore = FAISS.from_documents(documents, embeddings)
        old_vectorstore.merge_from(tmp_vectorstore)
        old_vectorstore.save_local(str(current_db_dir))


        

