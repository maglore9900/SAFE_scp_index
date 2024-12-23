from transformers import AutoTokenizer
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from datetime import datetime

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

model_name = "BAAI/bge-large-en-v1.5"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)


# Only used to get at token count, not necessary for the actual query
tokenizer = AutoTokenizer.from_pretrained(model_name)


load_start = datetime.now()
client = QdrantClient(path="qdb")

vectorstore = QdrantVectorStore(
    client=client,
    collection_name="scp_collection",
    embedding=embeddings,
)
# vectorstore = FAISS.load_local("backup", embeddings, allow_dangerous_deserialization=True)
load_finish = datetime.now()

search_start = datetime.now()

# results = vectorstore.similarity_search(
#     "scp-010",
#     k=2,
#     filter={"SCP_ID": "SCP-010"},
# )

results = vectorstore.similarity_search(
    "tell me about scp-002", k=2
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")
search_finish = datetime.now()

print(f"load time: {load_finish - load_start}\n search time: {search_finish - search_start}")
for result in results:
    print(len(result.page_content))
    print(len(tokenizer.encode(result.page_content)))
