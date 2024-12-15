from modules import adapter
import environ

# env = environ.Env()
# environ.Env.read_env()

# ad = adapter.Adapter(env)

# results = ad.query_datastore("scp")
# print(results)

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
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
import faiss

index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))


# print(results)
# from langchain_community.vectorstores import FAISS
# vectorstore = FAISS(
#     embedding_function=embeddings,
#     index=index,
#     docstore="scp_data",
#     index_to_docstore_id={},
# )
vectorstore = FAISS.load_local("scp_data", embeddings, allow_dangerous_deserialization=True)

results = vectorstore.similarity_search(
    "a",
    k=2,
    filter={"SCP_ID": "SCP-010"},
)
# for res in results:
print(results)
#     print(f"* {res.page_content} [{res.metadata}]")