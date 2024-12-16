import environ
import faiss

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS


model_name = "BAAI/bge-small-en"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

vectorstore = FAISS.load_local("scp_data\db_0", embeddings, allow_dangerous_deserialization=True)

while True:
    query = input("Enter Search Criteria\n")
    results = vectorstore.similarity_search(
        query,
        k=2,
        # filter={"SCP_ID": "SCP-010"},
    )
    for res in results:
        print(f"* {res.page_content}")
