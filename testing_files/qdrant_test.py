from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from datetime import datetime

from langchain_huggingface import HuggingFaceEmbeddings
# model_name = "BAAI/bge-small-en-v1.5"
model_name = "BAAI/bge-large-en-v1.5"
model_kwargs = {"device": "cuda"}
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)


# url = "localhost:6333"
# docs = []  # put docs here
# qdrant = QdrantVectorStore.from_documents(
#     docs,
#     embedding,
#     url=url,
#     prefer_grpc=True,
#     collection_name="my_documents",
# )
load_start = datetime.now()
client = QdrantClient(path="qdb")

vectorstore = QdrantVectorStore(
    client=client,
    collection_name="scp_collection",
    embedding=embeddings,
)
load_finish = datetime.now()


search_start = datetime.now()

results = vectorstore.similarity_search(
    "scp-002", 
    k=2,
    collection_name="scp_collection",
)
search_finish = datetime.now()

# with open('scp-002.txt', 'w') as file:
#     file.write(str(results))
# for res in results:
#     print(f"* {res.page_content} [{res.metadata}]")
# print(results)

results = vectorstore.similarity_search(
    "scp-002",
    k=2,
    collection_name="scp_collection",
    filter=models.Filter(
        must=[
            models.FieldCondition(
                    key="metadata.SCP_ID",
                    match=models.MatchValue(
                        value="SCP-002",
                ),
            ),
        ]
    )
)
print(results)
print(f"load time: {load_finish - load_start}\n search time: {search_finish - search_start}")